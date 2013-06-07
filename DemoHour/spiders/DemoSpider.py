from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from DemoHour.items import DemohourItem
from DemoHour.items import RewardOption
from DemoHour.items import Supporter

class DemoSpider(BaseSpider):
	name = 'DemoHourSpider'
	domain = ['www.demohour.com']
	start_urls = ['http://www.demohour.com/projects/318262/backers']
	# , 'http://www.demohour.com/projects/317769']
	
	def parse(self, response):
		hxs = HtmlXPathSelector(response)
		# titles = hxs.select("//span[@class='pl']")
		backers = hxs.select("//div[@class='projects-backers-left']/div[@class='supporters']")
		
		items = []
		for backer in backers:
			item = Supporter()
			supporter_name = backer.select(".//div[@class='supportersmeta']/div[@class='supportersmeta-t']/a[@class='supportersmeta-t-a']/text()").extract()
			supporter_url = backer.select(".//div[@class='supportersmeta']/div[@class='supportersmeta-t']/a[@class='supportersmeta-t-a']/@href").extract()
			supporter_ico = backer.select(".//div[@class='supportersmeta']/div[@class='supportersmeta-t']/div[@class='icon-sun-ms']/a/text()").extract()
			supporter_all= backer.select(".//div[@class='supportersmeta']/text()").extract()
			supporter_time = backer.select(".//div[@class='supportersmeta']/text()[2]").extract()[0:-4]
			supporter_amount = backer.select(".//div[@class='supportersmeta']/text()[3]").extract()
			supporter_total_support = backer.select(".//div[@class='supportersmeta']/text()[4]").extract()
			print "supporter name", supporter_name
			print "supporter url", supporter_url
			print "supporter icon level", supporter_ico
			print "supporter_all", supporter_all
			print "supporter time", supporter_time
			print "supporter total support", supporter_total_support
			item['supporter_name'] = supporter_name
			item['supporter_url'] = supporter_url
			item['supporter_ico'] = supporter_ico
			item['supporter_time']= supporter_time
			item['supporter_amount'] = supporter_amount
			item['supporter_total_support'] = supporter_total_support
			items.append(item)
		return items
		
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
		