# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class Supporter(Item):
	supporter_name = Field()
	supporter_url = Field()
	supporter_ico = Field()
	supporter_time = Field()
	supporter_amount = Field()
	supporter_total_support = Field()
	
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
	
	
