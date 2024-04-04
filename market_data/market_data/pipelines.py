# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re 


class MarketDataPipeline:
    def process_item(self, item, spider):
        
        adapter = ItemAdapter(item)


        ## Extract index abbreviation
        if 'index_abbreviation' in adapter:
            value = adapter['index_abbreviation']
            if value:
                abbreviation_match = re.search(r'\((.*?)\)', value)
                if abbreviation_match:
                    adapter['index_abbreviation'] = abbreviation_match.group(1)
                else:  # Handle cases where the regex doesn't find a match
                    adapter['index_abbreviation'] = 'Abbreviation not found'
            
            
        return item
