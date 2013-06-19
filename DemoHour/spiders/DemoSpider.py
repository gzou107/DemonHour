from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from DemoHour.items import DemohourItem
from DemoHour.items import RewardOption
from DemoHour.items import Supporter
from scrapy.http.request import Request


from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.loader import XPathItemLoader
import re

class DemoSpider(CrawlSpider):
	name = 'DemoHourSpider'
	domain = ['demohour.com']
	start_urls = [
	'http://www.demohour.com/projects/318262'
	]
	# , 'http://www.demohour.com/projects/317769']
	# SgmlLinkExtractor(allow=('demohour.com/projects/[0-9]+/backers'))
	# 318262 320144
	# backers_extractor = SgmlLinkExtractor(allow=('/projects/318262/backers',), deny=('page=1$',))
	# 			supporter_name = backer.select(".//div[@class='supportersmeta']/div[@class='supportersmeta-t']/a[@class='supportersmeta-t-a']/text()").extract()
	backers_table_extractor = SgmlLinkExtractor(allow=('/projects/318262/backers?',), deny=('page=1$',) )
	proj_table_extractor = SgmlLinkExtractor(allow=('/projects/318262$',), deny=('page=1$',) )
	# proj_sidebar_funding = SgmlLinkExtractor( allow=('/projects/320144/posts$',), )
	
	rules = (	
		# Extract link matching 'backers?page= and parse them with the spider's method, parse_one_page
		# allow=('backers?page=')
		# Rule(backers_table_extractor, callback='parse_backers_links', follow = True),
		Rule(proj_table_extractor, callback = 'parse_sidebar_funding',follow = False),
		# Rule(proj_sidebar_funding, callback = 'parse_sidebar_funding',follow = False),
		# Extract link matching 
		)
	
	def parse_backers_links(self, response):
		hxs = HtmlXPathSelector(response)
		
		current_page = hxs.select("//div[@class='ui-pagination-current']/ul/li/a/@href")
		
		if not not current_page:
			yield Request(current_page[0], self.parse_one_page)
		"""	
		links = hxs.select("//div[@class='ui-pagination']/ul/li/a/@href")
		for link in links:
			link_url = link.extract()
			self.log("I am in link %s" %link_url)
	
			if re.search('page=1$', link_url):
				self.log('match rule: %s' %link_url)
				print link_url
			else:
				yield Request(link_url, self.parse_one_page)
		"""
		for item in self.parse_one_page(response):
			yield item
		
		
	
	
	def parse_sidebar_funding(self, response):
		"""
		This will parse the side bar and return the info for side bar funding
		"""
		hxs = HtmlXPathSelector(response)
		
		item = DemohourItem()
		
		##################################################################################################################
		# section of proj table
		projs_sidebar_funding = hxs.select("//div[@class='sidebar-funding']")
		for p in projs_sidebar_funding:
			proj_funding_target = p.select(".//div[@class='sidebar-money-raised-num-t']").select(".//b/text()").extract()
			print proj_funding_target
			item['proj_funding_target'] = proj_funding_target
			
			proj_current_funding_amount = p.select(".//div[@class='sidebar-money-raised-num']").select(".//b/text()").extract()
			print proj_current_funding_amount
			item['proj_current_funding_amount'] = proj_current_funding_amount
			
			proj_current_funding_percentage = p.select(".//span[@class='sidebar-percentage-progress-span']/text()").extract()
			print proj_current_funding_percentage
			item['proj_current_funding_percentage'] = proj_current_funding_percentage
			
			# this is how many people support this proj
			proj_supporter_count = p.select(".//div[@class='sidebar-number-days-l']/b/b/text()").extract()
			print "support num:", proj_supporter_count
			item['proj_supporter_count'] = proj_supporter_count
			
			# this is how many people view this proj
			proj_surfer_count = p.select(".//div[@class='sidebar-number-days-m']/b/b/text()").extract()
			print "people view ", proj_surfer_count
			item['proj_surfer_count'] = proj_surfer_count
			
			# this is how many days left
			proj_leftover_time = p.select(".//div[@class='sidebar-number-days-r']/b/b/text()").extract()
			print "days left ", proj_leftover_time		
			item['proj_leftover_time'] = proj_leftover_time	
		# end of section of proj table
		##################################################################################################################
		
		##################################################################################################################
		# section of section of proj_owner_table
		projs_owner = hxs.select("//div[@class='project-by']")
		for p in projs_owner:
			proj_owner_owner_name = p.select(".//a[@class='project-by-img-r-author']/text()").extract()
			print "proj name: ", proj_owner_owner_name
			item['proj_owner_owner_name'] = proj_owner_owner_name
			
			proj_owner_owner_id = p.select(".//a[@class='project-by-img-r-author']/@href").extract()
			print "proj name url: ", proj_owner_owner_id
			item['proj_owner_owner_id'] = proj_owner_owner_id
			
			proj_owner_last_log_in_time = p.select(".//div[@class='project-by-last-time']/text()").extract()
			print "proj last update time,", proj_owner_last_log_in_time
			item['proj_owner_last_log_in_time'] = proj_owner_last_log_in_time
			
			proj_by_post_support_list = p.select(".//div[@class='project-by-post']/a[@target='_blank']/span/text()").extract()
			proj_owner_support_proj_count = 0
			proj_owner_own_proj_count = 0
			if len(proj_by_post_support_list) >= 1:
				proj_owner_support_proj_count = proj_by_post_support_list[0]
			if len(proj_by_post_support_list) >= 2:
				proj_owner_own_proj_count = proj_by_post_support_list[1]
			print "proj owner supports:", proj_owner_support_proj_count
			print "proj owner owns:", proj_owner_own_proj_count
		# end of section of proj_owner_table
		##################################################################################################################

		##################################################################################################################
        # section of donation table, we need to follow the link within the donor page (pagination)
		backers = hxs.select("//div[@class='ui-tab-layout']/ul[@class='ui-tab-menu']/li/a/@href")
		if len(backers) == 3: # we have current tab, posts and backers tab
		###
		#u'/projects/318262/backers'
		# >>> response.url
		# 'http://www.demohour.com/projects/318262'
		###
			backer_relative_urls = backers[2].extract().split('/')
			backer_relative_url = backer_relative_urls[len(backer_relative_urls) - 1]
			backers_full_url = response.url + '/' + backer_relative_url
			yield Request(backers_full_url, self.parse_backers_links)
	
			for item2 in self.parse_backers_links(response):
				# we have supporter information here
				yield item2
				print "supporter name:", item2['supporter_name']
				print "supporter url:", item2['supporter_url']
				print "supporter icon:", item2['supporter_icon'] 
				print "supporter support time", item2['supporter_support_time']
				print "supporter support amount", item2['supporter_support_amount'] 
				print "supporter support total proj count", item2['supporter_total_support_proj'] 

		# end of section of donation table
		##################################################################################################################
		
		# yield item
	"""
	def parse(self, response):
		self.log('hi, this is an item page! %s' %response.url)
		
		if response.meta['depth'] > 5:
			self.log('reach depth of 5 when at page %s' % response.url)
			
		hxs = HtmlXPathSelector(response)

		# firstly get the total backer count so that we know the pagination number
		count_str = hxs.select("//a[@class='ui-tab-current']/span[@id='backer_count']/text()").extract()
		print "total supporter count: ", count_str
		count = int(count_str[0])
		backer_per_page = 40
		
		current_page = hxs.select("//div[@class='ui-pagination']/ul/li[@class = 'ui-pagination-current']/a/@href").extract()
		for i in range(1, count/backer_per_page + 2):
			page_url_base = current_page[0].split('?')
			page_url_prefix = page_url_base[0]
			page_url = page_url_prefix + '?' + 'page='+ str(i)
			yield Request(page_url, self.parse_one_page)
		
		
		visited_page = set()
		for page in pages:
			if not page in visited_page:
				visited_page.add(page)
				yield Request(page, self.parse_one_page)
		
	"""	
	def parse_one_page(self, response):
		
		hxs = HtmlXPathSelector(response)
		# titles = hxs.select("//span[@class='pl']")
		# avoid double parse here???
		backers = hxs.select("//div[@class='projects-backers-left']/div[@class='supporters']")
		items = []
		
		loader = XPathItemLoader(item = Supporter(), response = response)
		
		"""
		for backer in backers:
			loader.add_xpath('supporter_name', ".//div[@class='supportersmeta']/div[@class='supportersmeta-t']/a[@class='supportersmeta-t-a']/text()")
			loader.add_xpath('supporter_url', ".//div[@class='supportersmeta']/div[@class='supportersmeta-t']/a[@class='supportersmeta-t-a']/@href")
			loader.add_xpath('supporter_icon',".//div[@class='supportersmeta']/div[@class='supportersmeta-t']/div[@class='icon-sun-ms']/a/text()")
			loader.add_xpath('supporter_support_time', ".//div[@class='supportersmeta']/text()[2]")
			loader.add_xpath('supporter_total_support_proj', ".//div[@class='supportersmeta']/text()[4]")
			loader.add_xpath('supporter_support_amount', ".//div[@class='supportersmeta']/text()[3]")
			items.append(loader.load_item())
		return items
		"""
		
		for backer in backers:
			item = Supporter()			
			# div.supporters:nth-child(5) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > a:nth-child(1)
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
		