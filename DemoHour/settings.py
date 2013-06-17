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

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'DemoHour (+http://www.yourdomain.com)'
ITEM_PIPELINES = [
	'DemoHour.pipelines.DemohourPipeline',
    # 'DemoHour.pipelines.DuplicatesPipeline',
	# 'DemoHour.pipelines.MySQLStorePipeline',
]