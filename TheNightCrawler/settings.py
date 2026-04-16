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
CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_DELAY = 2

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # "TheNightCrawler.middlewares.SeleniumWithNothingMiddleware": 420,
    # "TheNightCrawler.middlewares.SeleniumWithScrapeOpsBrowserHeader": 420,
    # "TheNightCrawler.middlewares.SeleniumWithScrapeOpsProxy": 420,
    # "TheNightCrawler.middlewares.SeleniumWithUndetectedBrowser": 420,
    "TheNightCrawler.downloadermiddlewares.retry.RetryMiddleware": None
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
  "TheNightCrawler.pipelines.TheNightCrawlerPipeline": 300,
}

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

FEEDS = {
    # 'Pure-Selenium.csv': {
    # 'Non-Mobile-Browser-Headers-Selenium.csv': {
    # 'Mobile-Browser-Headers-Selenium.csv': {
    # 'ScrapeOPS-Proxy-Selenium.csv':{
    # 'Undetected-Browser-Selenium.csv': {
        'format': 'csv',
        'encoding': 'utf8',
        'overwrite': True
    }
}




