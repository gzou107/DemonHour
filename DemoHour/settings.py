# Scrapy settings for DemoHour project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'DemoHour'

SPIDER_MODULES = ['DemoHour.spiders']
NEWSPIDER_MODULE = 'DemoHour.spiders'

SER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:7.0.1) Gecko/20100101 Firefox/7.7'

DOWNLOAD_DELAY = 0.25 

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'DemoHour (+http://www.yourdomain.com)'
ITEM_PIPELINES = [
	'DemoHour.pipelines.DemohourPipeline',
	'DemoHour.pipelines.DefaultValuesPipeline',
	'DemoHour.pipelines.DuplicatesPipeline',
	'DemoHour.pipelines.MultiCSVItemPipeline',
    # 'DemoHour.pipelines.DuplicatesPipeline',
	'DemoHour.pipelines.MySQLStorePipeline',
]