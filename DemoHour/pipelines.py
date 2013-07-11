# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from scrapy import signals
from scrapy.exceptions import DropItem
from scrapy import log
from scrapy.contrib.exporter import CsvItemExporter
from scrapy.xlib.pydispatch import dispatcher
# ref: http://doc.scrapy.org/en/0.14/topics/exporters.html

import time
import datetime
import MySQLdb.cursors
from twisted.enterprise import adbapi

class DemohourPipeline(object):
    def process_item(self, item, spider):
        return item

class DefaultValuesPipeline(object):
	def process_item(self,item, spider):
		item_type = type(item).__name__
		
		if item_type == "Proj_Item":
			item.setdefault('proj_leftover_time_unit', 'unset')
			
		elif item_type == "Proj_Owner_Item":
			item.setdefault('proj_owner_star_level', 0)
			
		elif item_type == "Proj_Topic":
		# topic_proj_owner_name,topic_proj_category,topic_proj_id,topic_down_count,topic_proj_location,topic_total_buzz_count,topic_announcement_count,topic_question_count,topic_up_count
			item.setdefault('topic_up_count', 0)
			item.setdefault('topic_down_count', 0)
			item.setdefault('topic_proj_category', 'unset')
			item.setdefault('topic_proj_location', 'unset')
			
		elif item_type == "Proj_Incentive_Options_Item":
		# incentive_expect_support_amount,incentive_proj_id,incentive_reward_shipping_time,incentive_total_allowable_supporter_count,incentive_reward_shipping_method,incentive_description,incentive_current_supporter_count
			item.setdefault('incentive_total_allowable_supporter_count', None)
			item.setdefault('incentive_current_supporter_count', 0)
			item.setdefault('incentive_reward_shipping_time', 'N/A')
			item.setdefault('incentive_reward_shipping_method', 'N/A')
			
		elif item_type == "Proj_Supporter":
		# supporter_name,supporter_support_time,supporter_support_amount,supporter_proj_id,supporter_icon,supporter_total_support_proj,supporter_id
			item.setdefault('supporter_icon', 0)
			
		return item
		
		
class DuplicatesPipeline(object):	
    def __init__(self):
        self.Proj_ids_seen_for_Proj_table = set()
        self.Proj_ids_seen_for_Proj_Owner_table = set()
	self.user_ids_seen_for_user_table = set()
		
    def process_item(self, item, spider):
        # print(" my type is %s" %type(item).__name__)
        item_type = type(item).__name__
        # we do dedup for Proj_Owner_Item, proj_Item and User_item for now
        if item_type != "Proj_Owner_Item" and item_type != "Proj_Item" and item_type != "User_Item":
            return item
        elif item_type == "Proj_Owner_Item":
            if item['proj_owner_proj_id'][0] in self.Proj_ids_seen_for_Proj_Owner_table:
                raise DropItem("Duplicate proj owner item found: %s" % item)
            else:
                self.Proj_ids_seen_for_Proj_Owner_table.add(item['proj_owner_proj_id'][0])
                return item
        elif item_type == "Proj_Item":
            if item['proj_id'][0] in self.Proj_ids_seen_for_Proj_table:
                raise DropItem("Duplicate proj item found: %s" % item)
            else:
                self.Proj_ids_seen_for_Proj_table.add(item['proj_id'][0])
                return item
        elif item_type == "User_Item":
            if item['user_id'][0] in self.user_ids_seen_for_user_table:
                raise DropItem("Duplicate user item found: %s" % item)
            else:
                self.user_ids_seen_for_user_table.add(item['user_id'][0])
                return item

class MySQLStorePipeline(object):
	def __init__(self):
		"""
		hard code db connection string
		"""
		self.dbpool = adbapi.ConnectionPool('MySQLdb',
			db = 'demohour1',
			user = 'root',
			passwd = 'yxq860630',
			cursorclass = MySQLdb.cursors.DictCursor,
			charset = 'utf8',
			use_unicode = True
			)
			
	# def item_type(self, item):
	# 	return type(item).__name__.replace('_Item','') # Proj_Item -->Proj
		
	def process_item(self, item, spider):
		item_type = type(item).__name__
		if item_type == "Proj_Item":
			print "find one proj item"
		query = self.dbpool.runInteraction(self.conditional_insert, item)
		query.addErrback(self.handle_error)
		return item
	
	def conditional_insert(self, tx, item):
		what = type(item).__name__
		# what = self.item_type(item)
		print "in sql pipeline with type : %s \n" %what
        # insert proj owner item
		if what == "Proj_Supporter":
			# find a way to dedup the supporter
			result = False
			print "Proj supporter content is: %s" %item
			if result:
				log.msg("Item proj_supporter in the db: %s", item)
			else:
				tx.execute(\
						"INSERT INTO demohour_supporter(supporter_name,supporter_support_time,supporter_support_amount,supporter_proj_id,supporter_icon,supporter_total_support_proj,supporter_id) "
						"values (%s, %s, %s, %s, %s, %s, %s)",
						(
						item['supporter_name'],
						item['supporter_support_time'],
						item['supporter_support_amount'],
						item['supporter_proj_id'],
						item['supporter_icon'],
						item['supporter_total_support_proj'],
						item['supporter_id']
						)
						)
						
        	elif what == "Proj_Item":
			tx.execute("SELECT * from demohour_project where proj_id = %s\n", (item['proj_id'],))
			result = tx.fetchone()
			if result:
				log.msg("Item already stored in db: %s" %item, level = log.DEBUG)
			else:
				tx.execute(\
						"INSERT INTO demohour_project(proj_id, proj_funding_target, proj_url, proj_name, proj_current_funding_amount, proj_current_funding_percentage, proj_status, proj_leftover_time, proj_left_over_time_unit, proj_surfer_count, proj_topic_count, proj_supporter_count, proj_owner_name) "
						"values (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)",
						(
						item['proj_id'],
						item['proj_funding_target'],
						item['proj_url'],
						item['proj_name'],
						item['proj_current_funding_amount'],
						item['proj_current_funding_percentage'],
						item['proj_status'],
						item['proj_leftover_time'],
						item['proj_leftover_time_unit'],
						item['proj_surfer_count'],
						item['proj_topic_count'],
						item['proj_supporter_count'],
						item['proj_owner_name']
						)
						)
					#tx.commit()
				log.msg("Item stored in db: %s" %item, level = log.DEBUG)
		elif what == "Proj_Owner_Item":
			tx.execute("SELECT * FROM demohour_project_owner WHERE proj_owner_owner_id = %s and proj_owner_proj_id = %s\n", (item['proj_owner_owner_id'],item['proj_owner_proj_id']))
			result = tx.fetchone()
			if result:
				log.msg("Item of proj_onwe_item already stored in db: %s" %item, level = log.DEBUG)
			else:
				tx.execute(\
						"INSERT INTO demohour_project_owner(proj_owner_owner_name,proj_owner_owner_id,proj_owner_last_log_in_time,proj_owner_own_proj_count,proj_owner_support_proj_count,proj_owner_proj_id,proj_owner_star_level) "
						"values (%s, %s, %s, %s, %s, %s,%s)",
						(
						item['proj_owner_owner_name'],
						item['proj_owner_owner_id'],
						item['proj_owner_last_log_in_time'],
						item['proj_owner_own_proj_count'],
						item['proj_owner_support_proj_count'],
						item['proj_owner_proj_id'],
						item['proj_owner_star_level']
						)
						)
		elif what == "Proj_Topic":
			tx.execute("SELECT * FROM demohour_project_topic WHERE topic_proj_id = %s\n", (item['topic_proj_id'],))
			result = tx.fetchone()
			if result:
				log.msg("Item of proj_topic_item already stored in db: %s" %item, level = log.DEBUG)
			else:
				tx.execute(\
						"INSERT INTO demohour_project_topic(topic_proj_owner_name,topic_proj_category,topic_proj_id,topic_down_count,topic_proj_location,topic_total_buzz_count,topic_announcement_count,topic_question_count,topic_up_count) "
						"values (%s, %s, %s, %s, %s, %s,%s, %s, %s)",
						(
						item['topic_proj_owner_name'],
						item['topic_proj_category'],
						item['topic_proj_id'],
						item['topic_down_count'],
						item['topic_proj_location'],
						item['topic_total_buzz_count'],
						item['topic_announcement_count'],
						item['topic_question_count'],
						item['topic_up_count']
						)
						)
		elif what == "Proj_Incentive_Options_Item":
			# TODO: find a proper keys to determine duplication.
			tx.execute("SELECT * FROM demohour_proj_incentive_options WHERE incentive_proj_id = %s and incentive_expect_support_amount = %s", (item['incentive_proj_id'], item['incentive_expect_support_amount'])) 
			result = tx.fetchone()
			if result:
				log.msg("Item of Proj_Incentive_Options_Item already stored in db: %s" %item, level = log.DEBUG)
			else:
				tx.execute(\
							"INSERT INTO demohour_proj_incentive_options(incentive_expect_support_amount,incentive_proj_id,incentive_reward_shipping_time,incentive_total_allowable_supporter_count,incentive_reward_shipping_method,incentive_description,incentive_current_supporter_count) "
							"values (%s, %s, %s, %s, %s, %s, %s)",
							(
							item['incentive_expect_support_amount'],
							item['incentive_proj_id'],
							item['incentive_reward_shipping_time'],
							item['incentive_total_allowable_supporter_count'],
							item['incentive_reward_shipping_method'],
							item['incentive_description'],
							item['incentive_current_supporter_count']
							)
							)			
	def handle_error(self, e):
		print "SQL pipeline error is %s" %e
		log.err(e)
		
import time

class MultiCSVItemPipeline(object):
	"""
	This class is used to persistent different items into differnet CSV files per its type
	TBD: we will write another pipeline which will save the results into DB after we can verify that the scrapy works
	, 'User_Item'
	"""
	SaveTypes = ['Proj', 'Proj_Owner', 'Proj_Topic', 'Proj_Supporter', 'Proj_Incentive_Options']
	CSVDir = 'C:\\laopo\\DemonHour\\'
	scrapyTime = time.localtime()
	def item_type(self, item):
		return type(item).__name__.replace('_Item','') # Proj_Item -->Proj
		
	def __init__(self):

		dispatcher.connect(self.spider_opened, signal = signals.spider_opened)
		dispatcher.connect(self.spider_closed, signal = signals.spider_closed)
		
	def spider_opened(self, spider):
		scrapyTime = time.localtime()
		time_postfix = '_' + str( scrapyTime.tm_year) + '_' + str(scrapyTime.tm_mon) + '_' + str(scrapyTime.tm_mday )+ '_' + str(scrapyTime.tm_hour) +'_' + str( scrapyTime.tm_min)
		# self.files = dict([ ( name, open(self.CSVDir + name + time_postfix + '.csv', 'r+')) for name in self.SaveTypes])
		self.files = dict([ ( name, open(self.CSVDir + name  + '.csv', 'w+b')) for name in self.SaveTypes])
		self.exporters = dict([ (name, CsvItemExporter(self.files[name], include_headers_line = True, encoding = 'utf-8')) for name in self.SaveTypes])
		[e.start_exporting() for e in self.exporters.values()]
		
	def spider_closed(self, spider):
		[e.finish_exporting() for e in self.exporters.values()]
		[f.close() for f in self.files.values()]
		
	def process_item(self, item, spider):
		# print item
		print(" my type is %s" %type(item).__name__)
		what = self.item_type(item)
		#if what in set(self.SaveTypes):
		self.exporters[what].export_item(item)
		return item
