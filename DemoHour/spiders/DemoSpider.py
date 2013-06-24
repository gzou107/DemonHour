from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from DemoHour.items import Proj_Item, Proj_Owner_Item, Proj_Supporter, Proj_Topic, Proj_Incentive_Options
from scrapy.http.request import Request


from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.loader import XPathItemLoader
import re
from decimal import *

class DemoSpider(CrawlSpider):
	name = 'DemoHourSpider'
	domain = ['demohour.com']
	start_urls = [
	'http://www.demohour.com/projects/318262'
	]
	# , 'http://www.demohour.com/projects/317769']
	# SgmlLinkExtractor(allow=('demohour.com/projects/[0-9]+/backers'))
	# 318262 320144
	# http://www.demohour.com/projects/317272
	# backers_extractor = SgmlLinkExtractor(allow=('/projects/318262/backers',), deny=('page=1$',))
	# 			supporter_name = backer.select(".//div[@class='supportersmeta']/div[@class='supportersmeta-t']/a[@class='supportersmeta-t-a']/text()").extract()
	# deny=('page=1$',)
	backers_table_extractor = SgmlLinkExtractor(allow=('/projects/318262/backers?',),deny=('page=1$',),  )
	# '/projects/309168$', '/projects/320084$', '/projects/319703$'  deny=('page=1$',)
	proj_table_extractor = SgmlLinkExtractor(allow=('/projects/318262',),deny=('page=1$',) )
	# proj_sidebar_funding = SgmlLinkExtractor(allow=('/projects/318262/posts$',), )
	
	rules = (	
		# Extract link matching 'backers?page= and parse them with the spider's method, parse_one_supporters_page
		# allow=('backers?page=')
		Rule(backers_table_extractor, callback='parse_backers_links', follow = True), # This must comes before next one in order to extract all the backer information
		Rule(proj_table_extractor, callback = 'parse_proj_info',follow = False),

		# Rule(proj_sidebar_funding, callback = 'parse_sidebar_funding',follow = False),
		# Extract link matching 
		)
	

		
		
	def add_url_prefix(self, url):
		return "www.demohour.com" + url
	
	def parse_proj_info(self, response):
		"""
		 maybe we should return a dict and then in the item pipeline, we will handle the processing based on keys
		 we will also need the persistent strategies now.
		"""
		hxs = HtmlXPathSelector(response)
		
		##################################################################################################################
		# section of proj table
		# (proj_url, proj_id(PK), proj_name, proj_funding_target, proj_current_funding_amount, proj_current_funding_percentage, proj_status, proj_left_over_time, proj_owner_name, 
		#   proj_owner_location, proj_supporter_count, proj_surfer_count, proj_topic_count)
		###################################################################################################################
		proj = Proj_Item()
		# get proj url, add prefix to get the complete url
		proj_url = hxs.select("//div[@class='ui-tab']/div[@class='ui-tab-top']/h1/a/@href").extract()		
		if len(proj_url) != 1:
			self.log("Parse the proj url error. %s" %response.url)
		else:
			proj['proj_url'] = self.add_url_prefix(proj_url[0])
		
		# one very important id -->Proj_Id
		PROJ_ID = proj_url[0].split('/')
		if len(PROJ_ID) != 3:
			self.log("Parse Proj_id error. %s" %response.url)
		else:
			PROJ_ID = PROJ_ID[len(PROJ_ID) - 1]
			proj['proj_id'] = PROJ_ID
		
		
		# get the proj name
		proj_title = hxs.select("//div[@class='ui-tab']/div[@class='ui-tab-top']/h1/a/text()").extract()
		if len(proj_title) != 1:
			self.log("Parse the proj name error. %s" %response.url)
		else:
			proj['proj_name'] = proj_title[0]
		

		projs_sidebar_funding = hxs.select("//div[@class='sidebar-funding']")
		if len(projs_sidebar_funding) == 0:
			projs_sidebar_funding = hxs.select("//div[@class='sidebar-warming']")
			if len(projs_sidebar_funding) == 0:
				projs_sidebar_funding = hxs.select("//div[@class='sidebar-success']")
				if len(projs_sidebar_funding) == 0:
					projs_sidebar_funding = hxs.select("//div[@class='sidebar-failure']")
					
		if(len(projs_sidebar_funding) != 1):
			self.log("Parse the proj table error. %s" %response.url)
			print "Parse the proj table error. %s" %response.url
		else:
			# get proj_funding_target		
			p = projs_sidebar_funding[0]
			proj_funding_target = p.select(".//div[@class='sidebar-money-raised-num-t']").select(".//b/text()").extract()
			print proj_funding_target
			proj['proj_funding_target'] = proj_funding_target
			# get proj_current_funding_amount	
			proj_current_funding_amount = p.select(".//div[@class='sidebar-money-raised-num']").select(".//b/text()").extract()
			print proj_current_funding_amount
			proj['proj_current_funding_amount'] = proj_current_funding_amount
			
			# get proj_current_funding_percentage	
			proj_current_funding_percentage = p.select(".//span[@class='sidebar-percentage-progress-span']/text()").extract()
			print proj_current_funding_percentage
			if len(proj_current_funding_percentage) != 1:
				self.log("Parse the proj_current_funding_percentage at url = %s" %response.url)
			else:
				percentage = re.search('[0-9]+.[0-9]+', proj_current_funding_percentage[0])
				if percentage == None:
					self.log("Parse the proj_current_funding_percentage at url = %s" %response.url)
				else:
					percentage = percentage.group(0)
					proj['proj_current_funding_percentage'] = Decimal(percentage.strip('"'))/100

			# this is how many people support this proj
			proj_supporter_count = p.select(".//div[@class='sidebar-number-days-l']/b/b/text()").extract()
			print "support num:", proj_supporter_count
			proj['proj_supporter_count'] = proj_supporter_count
				
			# this is how many people view this proj
			proj_surfer_count = p.select(".//div[@class='sidebar-number-days-m']/b/b/text()").extract()
			print "people view ", proj_surfer_count
			proj['proj_surfer_count'] = proj_surfer_count
			
			# get topic of the proj
			topic_count = hxs.select("//ul[@class='ui-tab-menu']/li/a/span[@id='posts_count']/text()").extract()
			if len(topic_count) != 1:
				self.log("Parse topic count error. %s" %response.url)
				print "Parse topic count error. %s" %response.url
			else:
				proj['proj_topic_count'] = topic_count
				
			# get the proj_status
			proj_status = p.select(".//div[@class='sidebar-number-days-r']/span/text()").extract()
			if len(proj_status) != 1:
				self.log("Parse proj status error. %s" %response.url)
				print "Parse proj status error. %s" %response.url
			else:
				proj['proj_status'] = proj_status[0]
				
			# get how many days left
			proj_leftover_time = p.select(".//div[@class='sidebar-number-days-r']/b/b/text()").extract()
			print "days left ", proj_leftover_time		
			proj['proj_leftover_time'] = proj_leftover_time	

			# get the unit of left_over
			proj_leftover_time_units = p.select(".//div[@class='sidebar-number-days-r']/b/text()").extract()
			if len(proj_leftover_time_units) == 1:
				proj['proj_left_over_time_unit'] = 0  # proj complete
			elif len(proj_leftover_time_units) == 2:
				proj['proj_left_over_time_unit'] = proj_leftover_time_units[1]
			else:
				self.log("Parse proj left over time error. %s" %response.url)
				print "Parse proj left over time error. %s" %response.url
		
		# get proj_owner information
		projs_owner = hxs.select("//div[@class='project-by']")
		if len(projs_owner) != 1:
			self.log("Parse proj owner error. %s" %response.url)
		else:
			p = projs_owner[0]
			proj_owner_owner_name = p.select(".//a[@class='project-by-img-r-author']/text()").extract()
			proj['proj_owner_name'] = proj_owner_owner_name
			
		# get proj_location --> this wil be extracted in another table
		# reason is this information may not be available at back page, only exist in main page
		"""
		projs_locations = hxs.select("//div[@class='projects-home-left-seat']/a[@target='_blank']/text()").extract()
		if len(projs_locations) != 3:
			self.log("Parse proj location error. %s" %response.url)
			print "Parse proj location error. %s" %response.url
		else:
			proj['proj_location'] = projs_locations[2]
		"""
		
		yield proj
		# end of section of proj table
		##################################################################################################################
		
		##################################################################################################################
		# section of section of proj_owner_table
	    # (proj_owner_owner_id(PK), proj_owner_proj_id(PK), proj_owner_owner_name, proj_owner_star_level, proj_owner_last_log_in_time, 
		#  proj_owner_own_proj_count, proj_owner_support_proj_count )
        ##################################################################################################################
		projs_owner = hxs.select("//div[@class='project-by']")
		if len(projs_owner) != 1:
			self.log("Parse the proj_owner error. %s" %response.url)
			print "Parse the proj_owner error. %s" %response.url
		else:
			p = projs_owner[0]
			proj_owner = Proj_Owner_Item()
			
			proj_owner_owner_id = p.select(".//a[@class='project-by-img-r-author']/@href").extract()
			print "proj name url: ", proj_owner_owner_id
			if len(proj_owner_owner_id) != 1:
				self.log("Parse proj owner id from page %s error" %response.url)
			else:
				owner_id = re.search('[0-9]+$', proj_owner_owner_id[0])
				if owner_id ==  None:
					self.log("Extract the proj owner id from url = %s error" %response.url)
				else:	
					proj_owner['proj_owner_owner_id'] = owner_id.group(0)
			
			proj_owner['proj_owner_proj_id'] = PROJ_ID
			
			proj_owner_owner_name = p.select(".//a[@class='project-by-img-r-author']/text()").extract()
			print "proj name: ", proj_owner_owner_name
			proj_owner['proj_owner_owner_name'] = proj_owner_owner_name
			
			proj_owner_star_level = p.select(".//div[@class='project-by-img-r']/div[@class='icon-sun-m']/a/text()").extract()
			print "proj proj_owner_star_level: ", proj_owner_star_level
			proj_owner['proj_owner_star_level'] = proj_owner_star_level
			
			proj_owner_last_log_in_time = p.select(".//div[@class='project-by-last-time']/text()").extract()
			print "proj last update time,", proj_owner_last_log_in_time
			log_in = re.search('[\d]+/[\d]+/[\d]+', proj_owner_last_log_in_time[0])
			if log_in == None:
				self.log("parse proj owner proj_owner_last_log_in_time error at page %s" %response.url)
			else:
				proj_owner['proj_owner_last_log_in_time'] = log_in.group(0)
			
			proj_by_post_support_list = p.select(".//div[@class='project-by-post']/a[@target='_blank']/span/text()").extract()
			proj_owner_support_proj_count = 0
			proj_owner_own_proj_count = 0
			if len(proj_by_post_support_list) >= 1:
				proj_owner_support_proj_count = proj_by_post_support_list[0]
				proj_owner['proj_owner_own_proj_count'] = proj_by_post_support_list[0]
			if len(proj_by_post_support_list) >= 2:
				proj_owner_own_proj_count = proj_by_post_support_list[1]
				proj_owner['proj_owner_support_proj_count'] = proj_by_post_support_list[0]
			print "proj owner supports:", proj_owner_support_proj_count
			print "proj owner owns:", proj_owner_own_proj_count

			yield proj_owner
		# end of section of proj_owner_table
		##################################################################################################################

		##################################################################################################################
        # section of donation table, we need to follow the link within the donor page (pagination)
		##########################################################################################
		#u'/projects/318262/backers'                                                             # 
		# >>> response.url                                                                       #
		# 'http://www.demohour.com/projects/318262'                                              # 
		##########################################################################################
		
		backers = hxs.select("//div[@class='ui-tab-layout']/ul[@class='ui-tab-menu']/li/a/@href")
		if len(backers) == 3: # we have current tab, posts and backers tab
			backer_relative_urls = backers[2].extract().split('/')
			backer_relative_url = backer_relative_urls[len(backer_relative_urls) - 1]
			backers_full_url = response.url + '/' + backer_relative_url
			yield Request(backers_full_url, self.parse_backers_links)
	
			for supporter in self.parse_backers_links(response): # we have supporter information here
				print "supporter name:", supporter['supporter_name']
				print "supporter url:", supporter['supporter_url']
				print "supporter icon:", supporter['supporter_icon'] 
				print "supporter support time", supporter['supporter_support_time']
				print "supporter support amount", supporter['supporter_support_amount'] 
				print "supporter support total proj count", supporter['supporter_total_support_proj']
				supporter['supporter_proj_id'] =  PROJ_ID
				yield supporter
		# end of section of donation table
		##################################################################################################################
		
				###################################################################################################################################
		# section of Topic table
		# (topic_proj_id(PK), topic_total_buzz_count, topic_announcement_count, topic_question_count, topic_up_count, topic_down_count, topic_proj_category, topic_proj_location )
		###################################################################################################################################
		
		projs_topic = hxs.select("//div[@class='projects-home-left']")
		if len(projs_topic) == 1:
			#self.log("Parse the topic at the end of the page error at url = %s" %response.url)
		#else:
			proj_topic = Proj_Topic()
			
			proj_topic['topic_proj_id'] = PROJ_ID
			
			# get the topic_total_buzz_count
			topic_total_buzz_count = projs_topic.select(".//li/a[@id='filter_all']/span/text()").extract()
			if len(topic_total_buzz_count) != 1:
				self.log("Parse topic_total_buzz_count error at url = %s" %response.url)
			else:
				proj_topic['topic_total_buzz_count'] = topic_total_buzz_count[0]
		
			topic_all_count =  projs_topic.select(".//li/a[@date-remote='true']/span/text()").extract()
			if len(topic_all_count) < 5:
				self.log("Parse other buzz count error at url = %s" %response.url)
			else:
				proj_topic['topic_announcement_count'] = topic_all_count[1]
				proj_topic['topic_question_count'] = topic_all_count[2]
				proj_topic['topic_up_count'] = topic_all_count[3]
				proj_topic['topic_down_count'] = topic_all_count[4]			
		
			# now we will get the proj tags, e.g., category, location
			projs_tag = hxs.select(".//div[@class='projects-home-left-seat']/a[@target='_blank']/text()").extract()
			if len(projs_tag) !=  3:
				self.log("Parse proj tag error at url = %s" %response.url)
			else:
				proj_topic['topic_proj_category'] = projs_tag[0]
				proj_topic['topic_proj_owner_name'] = projs_tag[1]
				proj_topic['topic_proj_location'] = projs_tag[2]
			
			yield proj_topic
		
		# yield item
		
	def parse_backers_links(self, response):
		hxs = HtmlXPathSelector(response)
		
		current_page = hxs.select("//div[@class='ui-pagination-current']/ul/li/a/@href")
		# current_page = hxs.select("//div[@class='ui-pagination-next']/ul/li/a/@href")

		if not not current_page:
			yield Request(current_page[0], self.parse_one_supporters_page)

		for item in self.parse_one_supporters_page(response):
			yield item
			
	def parse_one_supporters_page(self, response):
		
		hxs = HtmlXPathSelector(response)
		# titles = hxs.select("//span[@class='pl']")
		# avoid double parse here???
		backer_url = re.search('[0-9]+', response.url)
		PROJ_ID = -1
		if backer_url != None:
		#	self.log('parse the proj_id in backer page error in %s' %response.url)
		#else:
			PROJ_ID = backer_url.group(0)
			
		backers = hxs.select("//div[@class='projects-backers-left']/div[@class='supporters']")
		items = []		
		
		for backer in backers:
			item = Proj_Supporter()			
			supporter_name = backer.select(".//div[@class='supportersmeta']/div[@class='supportersmeta-t']/a[@class='supportersmeta-t-a']/text()").extract()
			supporter_url = backer.select(".//div[@class='supportersmeta']/div[@class='supportersmeta-t']/a[@class='supportersmeta-t-a']/@href").extract()
			supporter_icon = backer.select(".//div[@class='supportersmeta']/div[@class='supportersmeta-t']/div[@class='icon-sun-ms']/a/text()").extract()
			supporter_total_support_proj= backer.select(".//div[@class='supportersmeta']/text()[4]").extract()
			supporter_support_time = backer.select(".//div[@class='supportersmeta']/text()[2]").extract()
			supporter_support_amount = backer.select(".//div[@class='supportersmeta']/text()[3]").extract()
			#print "supporter name", supporter_name
			#print "supporter url", supporter_url
			#print "supporter icon level ", supporter_icon
			#print "supporter_total_support_proj ", supporter_total_support_proj
			#print "supporter_support_time ", supporter_support_time
			#print "supporter total support", supporter_support_amount
			item['supporter_name'] = supporter_name
			item['supporter_url'] = item.clean_supporter_url(supporter_url[0])
			item['supporter_icon'] = item.clean_supporter_icon(supporter_icon[0])
			item['supporter_support_time']= item.clean_supporter_support_time(supporter_support_time[0])
			item['supporter_support_amount'] = supporter_support_amount
			item['supporter_total_support_proj'] = item.clean_supporter_total_support_proj(supporter_total_support_proj[0])
			item['supporter_proj_id'] = PROJ_ID
			items.append(item)

		for item in items:
			yield item
		
		# return items
		"""
		projs_time = hxs.select("//div[@class='project-by-last-time']")
		
		item = DemonHourItem()	
		# section of proj homepage, determine if we have video or image
		# if video, set flag =1, save the flash url
		# if image, set flag = 0, save the image url
		projs_project_intro_video = hxs.select("//div[@class='projects-home-synopsis']/div[@class='projects-home-left-top']/embed[@src]/text()").extract()
		print "proj intro video:", projs_project_intro_video
		# item['projs_project_intro_video'] = projs_project_intro_video
		projs_project_intro_img = hxs.select("//div[@class='projects-home-synopsis']/div[@class='projects-home-left-top']/img[@src]/text()").extract()
		print "proj intro img:", projs_project_intro_img
		# item['projs_project_intro_img'] = projs_project_intro_img
		# end of section proj home page
		
		# section of div.sidebar-funding
		projs_sidebar_funding = hxs.select("//div[@class='sidebar-funding']")
		for p in projs_sidebar_funding:
			projs_sidebar_money_raised_num_t = p.select(".//div[@class='sidebar-money-raised-num-t']").select(".//b/text()").extract()
			print projs_sidebar_money_raised_num_t
			# item['projs_sidebar_money_raised_num_t'] = projs_sidebar_money_raised_num_t
			
			projs_sidebar_money_raised_num = p.select(".//div[@class='sidebar-money-raised-num']").select(".//b/text()").extract()
			print projs_sidebar_money_raised_num
			# item['projs_sidebar_money_raised_num'] = projs_sidebar_money_raised_num
			
			projs_sidebar_percentage_progress_span = p.select(".//span[@class='sidebar-percentage-progress-span']/text()").extract()
			print projs_sidebar_percentage_progress_span
			# item['projs_sidebar_percentage_progress_span'] = projs_sidebar_percentage_progress_span
			
			# this is how many people support this proj
			projs_sidebar_number_days_1 = p.select(".//div[@class='sidebar-number-days-l']/b/b/text()").extract()
			print "support num:", projs_sidebar_number_days_1
			# item['projs_sidebar_number_days_1'] = projs_sidebar_number_days_1
			
			# this is how many people view this proj
			projs_sidebar_number_days_m = p.select(".//div[@class='sidebar-number-days-m']/b/b/text()").extract()
			print "people view ", projs_sidebar_number_days_m
			# item['projs_sidebar_number_days_m'] = projs_sidebar_number_days_m
			
			# this is how many days left
			projs_sidebar_number_days_r = p.select(".//div[@class='sidebar-number-days-r']/b/b/text()").extract()
			print "days left ", projs_sidebar_number_days_r		
			# item['projs_sidebar_number_days_r'] = projs_sidebar_number_days_r
			
		# end of section div.sidebar-funding
		
		# section of proj-by where we have the proj owner information
		projs_by = hxs.select("//div[@class='project-by']")
		for p in projs_by:
			projs_by_img_r_author = p.select(".//a[@class='project-by-img-r-author']/text()").extract()
			print "proj name: ", projs_by_img_r_author
			# item['projs_by_img_r_author'] = projs_by_img_r_author
			
			projs_by_img_r_author_url = p.select(".//a[@class='project-by-img-r-author']/@href").extract()
			print "proj name url: ", projs_by_img_r_author_url
			# item['projs_by_img_r_author_url'] = projs_by_img_r_author_url
			
			projs_by_last_time = p.select(".//div[@class='project-by-last-time']/text()").extract()
			print "proj last update time,", projs_by_last_time
			# item['projs_by_last_time'] = projs_by_last_time
			
			proj_by_post_support = p.select(".//div[@class='project-by-post']/a[@target='_blank']/span/text()").extract()
			print "proj owner owns:", proj_by_post_support
			# item['proj_by_post_support'] = proj_by_post_support
			
			# for p_sub in proj_by_post:
				# proj_support_and_own = proj_by_post.select(".//span/text()/").extract()
				# print "proj owner support or own:", proj_support_and_own
		# end of section of proj-by where we have the proj owner information
		
		# section div class="reward-options" save all the reward options, and the main information
		# support amount and current supporter number projs_reward_supporter_count
		projs_reward_options = hxs.select("//div[@class='reward-options']/ul")
		reward = []
		for p in projs_reward_options:
			reward = RewardOption()
			projs_reward_support_amount = p.select(".//li[@class='support-amount']/text()[2]").extract()
			print "support amount: ", projs_reward_support_amount
			reward['projs_reward_support_amount'] = projs_reward_support_amount
			
			projs_reward_supporter_count = p.select(".//li[@class='support-amount']/span/text()").extract()
			print "supporter number:", projs_reward_supporter_count
			reward['projs_reward_supporter_count'] = projs_reward_supporter_count
			
			projs_reward_supporter_limit = p.select(".//li[@class='supporter-number']/div[@class='supporter-limit']/p/text()").extract()
			print "supporter number limit:", projs_reward_supporter_limit
			reward['projs_reward_supporter_limit'] = projs_reward_supporter_limit
			
			# item['projs_rewardOptions'].extend(reward)
			
			
		# end of reward-option section
		items = []	
		for i in range(1): 
		# we will do only once since for each projs we are expected to have one value for below items
		# in xpath all elements start with index 1 rather than 0
			#item = DemonHourItem()	
			for projs in projs:
				
				item["owner"] = projs.select("a/text()").extract()
				item["link"] = projs.select("a/@href").extract() 
				# print owner, link
				for projs_time in projs_time:
					item["last_update"] = projs_time.select("text()").extract()
				# print last_update
				items.append(item)
			
		return items
		"""
		