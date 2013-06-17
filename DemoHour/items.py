# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field
import re


from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, MapCompose, Join

class Supporter(Item):
	supporter_name = Field()
	supporter_url = Field()
	supporter_icon = Field()
	supporter_support_time = Field()
	supporter_support_amount = Field()
	supporter_total_support_proj = Field()
	
	def clean_supporter_url(self, url):
		"""
		Return complete url
		"""
		return "http://www.demohour.com" + url
	
	def clean_supporter_icon(self, icon):
		"""
		clean icon level
		support adge level: level is 1 -- > 1
		"""
		return icon[-1:]
		
	def clean_supporter_support_time(self, support_time):
		"""
		clean the support support time, remove the trailing 4 chinese characters and first \n
		"""
		time = support_time[1:-5]
		return time
	
	def clean_supporter_total_support_proj(self, total_support_proj_cnt):
		"""
		clean the supporter total support proj, keep only the number of total support projs
		[u'\nTA\u603b\u5171\u652f\u6301\u4e862\u4e2a\u9879\u76ee'] --> u4e86(2)
		"""
		count = re.search('[0-9]+', total_support_proj_cnt);
		return count.group(0)

"""
class SupporterLoader(ItemLoader):
	supporter_url = MapCompose(clean_supporter_url, ItemLoader.supporter_url)
	supporter_icon = MapCompose(clean_supporter_icon, ItemLoader.supporter_icon)
	supporter_support_time = MapCompose(clean_supporter_support_time, ItemLoader.supporter_support_time)
	supporter_total_support_proj = MapCompose(clean_supporter_total_support_proj, ItemLoader.supporter_total_support_proj)	
"""
class RewardOption(Item):
	# section of proj reward options
	projs_reward_support_amount = Field()
	projs_reward_supporter_count = Field()
	projs_reward_supporter_limit = Field()
	
class DemohourItem(Item):
    # define the fields for your item here like:
    # name = Field()
	owner = Field()
	link = Field()
	last_update = Field()
	# section of proj intro
	projs_project_intro_video = Field()
	projs_project_intro_img = Field()
	
	#section of proj sidebar funding
	projs_sidebar_money_raised_num_t = Field()
	projs_sidebar_money_raised_num = Field()
	projs_sidebar_percentage_progress_span =Field()
	projs_sidebar_number_days_1 = Field()
	projs_sidebar_number_days_m = Field()
	projs_sidebar_number_days_r = Field()
	
	#section of proj owner info
	projs_by_img_r_author = Field()
	projs_by_img_r_author_url = Field()
	projs_by_last_time = Field()
	proj_by_post_support = Field()
	
	
