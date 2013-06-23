# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from scrapy import signals
from scrapy.exceptions import DropItem

from scrapy import log
from twisted.enterprise import adbapi

from scrapy.contrib.exporter import CsvItemExporter
from scrapy.xlib.pydispatch import dispatcher
# ref: http://doc.scrapy.org/en/0.14/topics/exporters.html

import time
# import MySQLdb.cursors

class DemohourPipeline(object):
    def process_item(self, item, spider):
        return item


class DuplicatesPipeline(object):	
    def __init__(self):
        self.Proj_ids_seen_for_Proj_table = set()
        self.Proj_ids_seen_for_Proj_Owner_table = set()

    def process_item(self, item, spider):
        # print(" my type is %s" %type(item).__name__)
        item_type = type(item).__name__
        # we do dedup for Proj_Owner_Item and proj_Item only, since we need proj_owner appear only once in the proj owner tanle
        # even the owner has multiple projs
        if item_type != "Proj_Owner_Item" and item_type != "Proj_Item":
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

class MySQLStorePipeline(object):
	def __init__(self):
		"""
		hard code db connection string
		"""
		self.dbpool = adbapi.ConnectionPool('MySQLdb',
			db = 'sql56',
			user = 'root',
			passws = '',
			cursorclass = MySQLdb.cursor.DictCursor,
			charset = 'utf-8',
			use_unicode = True
			)
			
	def process_item(self, item, spider):
		"""
		create record if does not exist. all this block run on it
		own thread
			supporter_name = Field()
	supporter_url = Field()
	supporter_icon = Field()
	supporter_support_time = Field()
	supporter_support_amount = Field()
	supporter_total_support_proj = Field()
		"""
		tx.execute("SELECT * from backers where backer_name = %s and back_support_time = %s", (item['support_name'],item['supporter-support_time'],))
		result = tx.fetch()
		if result:
			log.msg("Item already stored in db: %s" %item, level = log.DEBUG)
		else:
			tx.execute(\
				"Insert into supporters(supporter_name, supporter_url, supporter_icon, supporter_support_time, supporter_support_amount, supporter_total_support_proj) "
				"values (%s, %s, %d, %s, %d, %d)",
				(
				item['supporter_name'][0],
				item['supporter_url'][0],
				item['supporter_icon'][0],
				item['supporter_support_time'][0],
				item['supporter_total_support_proj'][0]
				)
				)
			log.msg("Item stored in db: %s" %item, level = log.DEBUG)
			
	def handle_error(self, e):
		log.err(e)
		
import time
class MultiCSVItemPipeline(object):
	"""
	This class is used to persistent different items into differnet CSV files per its type
	TBD: we will write another pipeline which will save the results into DB after we can verify that the scrapy works
	"""
	SaveTypes = ['Proj_Owner', 'Proj', 'Proj_Supporter']
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
		self.files = dict([ ( name, open(self.CSVDir + name + time_postfix + '.csv', 'w+b')) for name in self.SaveTypes])
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