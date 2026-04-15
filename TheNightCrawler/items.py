# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class parsedItem(scrapy.Item):
    URL = scrapy.Field()
    CAPTCHATYPE = scrapy.Field()
    StatusCode = scrapy.Field()
    ContentLength = scrapy.Field()
