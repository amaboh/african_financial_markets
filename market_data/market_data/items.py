# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MarketDataItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    pass

class IndiceItem(scrapy.Item):
    index_abbreviation =  scrapy.Field()
    indice_name = scrapy.Field() 
    current_date = scrapy.Field()
    index_percentage_change = scrapy.Field()
    index_value = scrapy.Field()
    index_change = scrapy.Field()
    time_periods = scrapy.Field()
    market_summary = scrapy.Field()