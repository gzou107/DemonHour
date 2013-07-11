# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field
import re


from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, MapCompose, Join

class Proj_Item(Item):
	###################################################################################################################################
    # section of proj table
	# (proj_url, proj_id(PK), proj_name, proj_funding_target, proj_current_funding_amount, proj_current_funding_percentage,proj_status, proj_left_over_time, proj_leftover_time_unit(day, or hour, or empty if proj expire),
	#   proj_owner_name, proj_location,proj_supporter_count, proj_surfer_count, proj_topic_count)
	###################################################################################################################################
	proj_url = Field()      	# proj url, www.demohour.com/projects/318262
	proj_id = Field()       	# proj id , 318262 
	proj_name = Field()     	# proj title, SmartWallit
	proj_funding_target = Field()     	# how much money to be raised
	proj_current_funding_amount = Field()
	proj_current_funding_percentage = Field()
	proj_status = Field()
	proj_leftover_time = Field()
	proj_leftover_time_unit = Field()
	proj_owner_name = Field()
	# proj_location = Field()	
	proj_supporter_count = Field()
	proj_surfer_count = Field()
	proj_topic_count = Field()
	
	def clean_proj_funding_target(self, support_count):
		return self.__clean_money(support_count)

	def clean_proj_current_funding_amount(self, support_count):
		return self.__clean_money(support_count)

	def __clean_money(self, amount):
		res = re.findall('[\d]+', amount)
		if len(res) == 1:
			return int(res[0])
		if len(res) == 2:
			count = 1000* int(res[0]) + int(res[1])
			return count
		if len(res) == 3:
			count = 1000 * 1000 * int(res[0]) + 1000 * int(res[1]) + int(res[2])
			return count
		if len(res) == 4:
			count = 1000 * 1000 * 1000 * int(res[0]) + 1000 * 1000 * int(res[1]) + 1000 * int(res[2]) + int(res[3])
			return count
		if len(res) == 5:
			count = 1000 * 1000 * 1000 * 1000 * int(res[0]) + 1000 * 1000 * 1000 * int(res[1]) + 1000 * 1000 * int(res[2]) + 1000 * int(res[3]) + int(res[4])
			return count			
		return -1 # parse error.		
	
class Proj_Supporter(Item):
	supporter_proj_id = Field()
	supporter_name = Field()
	supporter_id = Field()           # this is equivalent og supporter_id
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
	
	def clean_supporter_id(self, supporter_id):
		"""
		clean the supporter id
		"""
		a = re.search('[\d]+', supporter_id)
		if a != None:
			return a.group(0)
		return -1
	
	def clean_supporter_total_support_proj(self, total_support_proj_cnt):
		"""
		clean the supporter total support proj, keep only the number of total support projs
		[u'\nTA\u603b\u5171\u652f\u6301\u4e862\u4e2a\u9879\u76ee'] --> u4e86(2)
		"""
		count = re.search('[0-9]+', total_support_proj_cnt);
		return count.group(0)

class Proj_Topic(Item):
	###################################################################################################################################
	# section of Topic table
	# (topic_proj_id(PK), topic_total_buzz_count, topic_announcement_count, topic_question_count, topic_up_count, topic_down_count, Proj_Supporter, topic_proj_category)
	###################################################################################################################################
	topic_proj_id = Field() # same as proj_id
	topic_total_buzz_count = Field()
	topic_announcement_count = Field()
	topic_question_count = Field()
	topic_up_count = Field()
	topic_down_count = Field()
	topic_proj_category = Field()
	topic_proj_owner_name = Field()	
	topic_proj_location = Field()

class User_Item(Item):
	###################################################################################################################################	
	# section of incentive table
	# (user_id, user_join_time, user_support_proj_count, user_own_proj_count, user_star_level)
	# this models the regestered user, we do not track the detail proj information, but only the count information, as the support information is kept in the supporter table
	# and ownership information is kept in the proj_owner_table
	###################################################################################################################################		
	user_id = Field()
	user_name = Field()
	user_join_time = Field()
	user_support_proj_count = Field()
	user_own_proj_count = Field()
	user_star_level = Field()
	
class Proj_Incentive_Options_Item(Item):
	###################################################################################################################################	
	# section of incentive table
	# (incentive_proj_id(PK), incentive_id(PK), incentive_expect_support_amount, incentive_current_supporter_count, incentive_total_allowable_supporter_count,
	#   incentive_description, incentive_reward_shipping_method, incentive_reward_shipping_time)
	###################################################################################################################################	
	incentive_proj_id = Field()
	# incentive_id = Field()
	incentive_expect_support_amount = Field()
	incentive_current_supporter_count = Field()
	incentive_total_allowable_supporter_count = Field() # optional
	incentive_description = Field()
	incentive_reward_shipping_method = Field()
	incentive_reward_shipping_time = Field()
	
	def clean_total_allowable_supporter_count(self, allowable_quote):
		res = re.findall('[\d]+', allowable_quote)
		return res
	
	def clean_reward_shipping_time(self, shipping_info):
		res = re.findall('[\d]+', shipping_info)
		return res
		
	def clean_current_supporter_count(self, supporter_count):
		res = re.findall('[\d]+', supporter_count)
		return res
	
	def clean_incentive_descriptions(self, incentive_descriptions):
		return incentive_descriptions[:100]
		
	def clean_expect_support_amount(self, support_count):
		res = re.findall('[\d]+', support_count)
		if len(res) == 1:
			return int(res[0])
		if len(res) == 2:
			count = 1000* int(res[0]) + int(res[1])
			return count
		if len(res) == 3:
			count = 1000 * 1000 * int(res[0]) + 1000 * int(res[1]) + res[2]
			return count
		return -1 # parse error.
		
class Proj_Owner_Item(Item):
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

"""	
class proj_sidebar_Funding(Item):
	#section of proj sidebar funding
	proj_sidebar_money_raised_num_t = Field()
	proj_sidebar_money_raised_num = Field()
	proj_sidebar_percentage_progress_span =Field()
	proj_sidebar_number_days_1 = Field()
	proj_sidebar_number_days_m = Field()
	proj_sidebar_number_days_r = Field()
"""
	
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
