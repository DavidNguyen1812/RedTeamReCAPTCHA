# Scrapy settings for TheNightCrawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from dotenv import load_dotenv
import os
from shutil import which

load_dotenv()

BOT_NAME = "TheNightCrawler"

SPIDER_MODULES = ["TheNightCrawler.spiders"]
NEWSPIDER_MODULE = "TheNightCrawler.spiders"
SCRAPEOPSAPI = os.environ.get("SCRAPEOPSAPI")
SCRAPEOPSBROWSERHEADERSACTIVE = True
SCRAPEOPSBROWSERHEADERSNUMRESULTS = 50
SCRAPEOPSPROXYENABLED = True
PROXYRETRYATTEMPTS = 3
SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = which('chromedriver')
LOG_LEVEL = 'INFO'


ADDONS = {}

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Concurrency and throttling settings
#CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_DELAY = 2

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False


# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
    # "TheNightCrawler.middlewares.ThenightcrawlerSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # "TheNightCrawler.middlewares.ScrapeOpsFakeBrowserHeaderMiddleware": 400,
    # "TheNightCrawler.middlewares.ScrapeOpsProxyMiddleware": 410,
    # "TheNightCrawler.middlewares.SeleniumWithNothingMiddleware": 420,
    # "TheNightCrawler.middlewares.SeleniumWithScrapeOpsBrowserHeader": 420,
    "TheNightCrawler.middlewares.SeleniumWithScrapeOpsProxy": 420,
    # "TheNightCrawler.middlewares.SeleniumWithUndetectedBrowser": 420,
    # "TheNightCrawler.middlewares.SeleniumWithScrapeOpsProxyMiddleware": 420,
    # "TheNightCrawler.middlewares.SeleniumWithScrapeOpsProxyV2": 420,
    "TheNightCrawler.downloadermiddlewares.retry.RetryMiddleware": None
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
  "TheNightCrawler.pipelines.TheNightCrawlerPipeline": 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"



FEEDS = {
    # 'Pure-Selenium.csv': {
    # 'Non-Mobile-Browser-Headers-Selenium.csv': {
    # 'Mobile-Browser-Headers-Selenium.csv': {
    'ScrapeOPS-Proxy-Selenium.csv':{
    # 'Undetected-Browser-Selenium.csv': {
        'format': 'csv',
        'encoding': 'utf8',
        'overwrite': True
    }
}




