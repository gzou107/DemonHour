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
	proj_reward_support_amount = Field()
	proj_reward_supporter_count = Field()
	proj_reward_supporter_limit = Field()

class proj_sidebar_Funding(Item):
	#section of proj sidebar funding
	proj_sidebar_money_raised_num_t = Field()
	proj_sidebar_money_raised_num = Field()
	proj_sidebar_percentage_progress_span =Field()
	proj_sidebar_number_days_1 = Field()
	proj_sidebar_number_days_m = Field()
	proj_sidebar_number_days_r = Field()
	
class DemohourItem(Item):
	###################################################################################################################################
    # section of proj table
	# (proj_url, proj_id(PK), proj_name, proj_target, proj_current_funding, proj_funding_percentage, proj_left_over_time, proj_crator_name, proj_crator_location)
	###################################################################################################################################
	proj_url = Field()      	# proj url, www.demohour.com/projects/proj_id
	proj_id = Field()       	# proj id  
	proj_name = Field()     	# proj title
	proj_funding_target = Field()     	# how much money to be raised
	proj_current_funding_amount = Field()
	proj_current_funding_percentage = Field()
	proj_leftover_time = Field()
	proj_owner_name = Field()
	proj_owner_location = Field()	
	proj_status = Field()
	# proj related feature
	proj_hasVideo = Field()
	proj_hasImage = Field()
	proj_supporter_count = Field()
	proj_surfer_count = Field()
	proj_topic_count = Field()
	
	###################################################################################################################################	
	# section of proj_owner_table
	# (proj_owner_owner_id(PK), proj_owner_proj_id(PK), proj_owner_owner_name, proj_owner_star_level, proj_owner_last_log_in_time, proj_owner_own_proj_count, proj_owner_support_proj_count )
	###################################################################################################################################	
	proj_owner_owner_id = Field()
	proj_owner_proj_id = Field()
	proj_owner_owner_name = Field()
	proj_owner_star_level = Field()
	proj_owner_last_log_in_time = Field()
	proj_owner_own_proj_count = Field()
	proj_owner_support_proj_count = Field()
	###################################################################################################################################	
	# section of post table
	# (proj_id(PK), proj_post_id(PK), proj_post_timestamp
	###################################################################################################################################
	post_proj_id = Field() # same as proj_id
	post_id = Field()
	post_timestamp = Field()
	
	###################################################################################################################################
	# section of donation table
	# ( id(PK), donate_proj_id, donate_donor_id, donate_donor_star_level, donate_donator_location, donate_donate_amount, donate_donate_time)
	####################################################################################################################################
	donate_proj_id = Field() # same as proj_id
	donate_donor_id = Field()
	donate_donor_star_level = Field()
	donate_donator_location = Field()
	donate_donate_amount = Field()
	donate_donate_time = Field()
	donate_donor_lists = set()
	###################################################################################################################################
	# section of Topic table
	# (topic_proj_id(PK), topic_announcement_count, topic_question_count, topic_up_count, topic_down_count)
	###################################################################################################################################
	topic_proj_id = Field() # same as proj_id
	topic_announcement_count = Field()
	topic_question_count = Field()
	topic_up_count = Field()
	topic_down_count = Field()
	
	###################################################################################################################################	
	# section of incentive table
	# (incentive_proj_id(PK), incentive_id(PK), incentive_amount, incentive_number_of_limited_donor,incentive_description)
	###################################################################################################################################	
	incentive_proj_id = Field()
	incentive_id = Field()
	incentive_amount = Field()
	incentive_number_of_limited_donor = Field()
	incentive_description = Field()
	
	###################################################################################################################################	
	# section of user table
	# ( user_id(PK), user_name, user_star_level, user_join_time, user_location, user_own_proj_count, user_support_proj_count)
	###################################################################################################################################	
	user_id = Field()
	user_name = Field()
	user_start_level = Field()
	user_join_time = Field()
	user_location = Field()
	user_own_proj_count = Field()
	user_support_proj_count = Field()
	
	"""
	# section of proj_owner table
	# (proj_owner_id
	# section of proj reward options
	proj_reward_support_amount = Field()
	proj_reward_supporter_count = Field()
	proj_reward_supporter_limit = Field()
	
	#section of proj sidebar funding
	proj_sidebar_money_raised_num_t = Field()
	proj_sidebar_money_raised_num = Field()
	proj_sidebar_percentage_progress_span =Field()
	proj_sidebar_number_days_1 = Field()
	proj_sidebar_number_days_m = Field()
	proj_sidebar_number_days_r = Field()
	
	#section of proj owner info
	proj_by_img_r_author = Field()
	proj_by_img_r_author_url = Field()
	proj_by_last_time = Field()
	proj_by_post_support = Field()
	"""
	proj_supporter_name = Field()
	proj_supporter_url = Field()
	proj_supporter_icon = Field()
	proj_supporter_support_time = Field()
	proj_supporter_support_amount = Field()
	proj_supporter_total_support_proj = Field()
	
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
