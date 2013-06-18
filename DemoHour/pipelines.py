# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from scrapy import signals
from scrapy.exceptions import DropItem

from scrapy import log
from twisted.enterprise import adbapi

import time
import MySQLdb.cursors

class DemohourPipeline(object):
    def process_item(self, item, spider):
        return item
		
class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['supporter_name'][0] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['supporter_name'][0])
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