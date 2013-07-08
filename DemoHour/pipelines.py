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
		item_type_info = type(item).__name__
		# what = self.item_type(item)
		print "in sql pipeline with type : %s \n" %item_type_info
		if item_type_info == "Proj_Item":
			print "find one proj item"
		query = self.dbpool.runInteraction(self.conditional_insert, item)
		query.addErrback(self.handle_error)
		print "finish processing one item in sql pipeline."
		return item
	
	def conditional_insert(self, tx, item):
		item_type_info = type(item).__name__
		# what = self.item_type(item)
		print "in sql pipeline with type : %s \n" %item_type_info
		
        # insert proj owner item
		"""
        if item_type_info != "Proj_Item":
			print "item match in sql pipeline with item : %s \n" %item['proj_id']
			tx.execute("SELECT * from demohour_project where proj_id = %s\n", (item['proj_id'],))
			result = tx.fetch()
			print "finish executing select."
			if result:
				log.msg("Item already stored in db: %s" %item, level = log.DEBUG)
			else:
				print "ready to insert.\n"
				tx.execute(\
					"INSERT INTO demohour_project(proj_id, proj_funding_target, proj_url, proj_name, proj_current_funding_amount, proj_current_funding_percentage, proj_status, proj_leftover_time, proj_left_over_time_unit, proj_surfer_count, proj_topic_count, proj_supporter_count, proj_owner_name) "
					"values (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s)",
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
				tx.commit()
				log.msg("Item stored in db: %s" %item, level = log.DEBUG)
		"""
		
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
