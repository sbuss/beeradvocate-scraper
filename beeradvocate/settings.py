# Scrapy settings for beeradvocate project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'beeradvocate'

SPIDER_MODULES = ['beeradvocate.spiders']
NEWSPIDER_MODULE = 'beeradvocate.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'beeradvocate (+http://www.yourdomain.com)'

BASE_URL = 'http://beeradvocate.com'
