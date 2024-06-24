import scrapy
from market_data.items import IndiceItem

class MarketspiderSpider(scrapy.Spider):
    name = "marketspider"
    allowed_domains = ["www.african-markets.com"]
    start_urls = ["https://www.african-markets.com/en/"]

    def parse(self, response):
        indices = response.css('div.mega-inner ul li a.menu-market-link')
        
        for indice in indices:
            market = indice.css('a::text').get()
            relative_index_url = indice.css('a::attr(href)').get()

            # Ensure the URL is correctly constructed
            if relative_index_url.startswith('/en/'):
                indice_url = 'https://www.african-markets.com' + relative_index_url
            elif relative_index_url.startswith('/fr/'):
                indice_url = 'https://www.african-markets.com' + relative_index_url
            else:
                # Check the language of the start URL to determine the base URL
                if 'en/' in self.start_urls[0]:
                    indice_url = 'https://www.african-markets.com/en/' + relative_index_url
                else:
                    indice_url = 'https://www.african-markets.com/fr/' + relative_index_url

            yield response.follow(indice_url, callback=self.parse_indice_page, meta={'market': market})
        
    def parse_indice_page(self, response):
        market = response.meta['market'] 
        content_div = response.xpath('/html/body/div[1]/div[2]/div[2]/div/div[1]/div[2]/div/div[2]/div[1]/div')
        
        indice_item = IndiceItem()

        # Index Name
        if response.css('h1.page-subtitle small.subheading-category'):  # Check if element exists
            indice_name = response.css('h1.page-subtitle small.subheading-category::text').get().strip()
        else:
            indice_name = "Index Name Not Found"  # Assign a default value

        # Current Date
        current_date_text = content_div.css('font[size="1"]::text').get() 
            
        if current_date_text:
            date_part = current_date_text.split("As of")[-1].strip()
            current_date = date_part
        else:
            current_date = "Date not found"

        # Index Value and Change 
        value_and_change = content_div.css('span[style*="font-weight:bold;font-size: 22pt"]::text').extract()
        index_value = value_and_change[0].strip() if len(value_and_change) >= 1 else "Data not found"
        index_change = value_and_change[1].strip() if len(value_and_change) >= 2 else "Data not found"
        
        # Time Periods Table
        time_periods_table = response.css('table.tabtable-rs_c4try72e')
        keys = time_periods_table.css('tr.tr_ht1 td::text').extract()
        values = time_periods_table.css('tr.tabrow p::text').extract()
        time_periods = dict(zip(keys, values))
        
        # Index Percentage Change
        index_percentage_change_elements = content_div.css('font > span[style*="color: #ff0000;"]::text').getall()
        if index_percentage_change_elements:
            index_percentage_change = index_percentage_change_elements[0].strip()
        else:
            index_percentage_change = "Change not found"

        # Market Summary Table
        summary_table = response.css('table.tabtable-gr_alterora_elemental_2_grey_1s2')
        summary_data = {}
        for row in summary_table.css('tr.tabrow'):
            cells = row.css('td')
            for cell in cells:
                key = cell.css('span:first-child::text').get().strip()
                value = cell.css('span:last-child::text').get().strip()
                summary_data[key] = value

        indice_item['index_abbreviation'] = market
        indice_item['indice_name'] = indice_name
        indice_item["current_date"] = current_date
        indice_item['index_percentage_change'] = index_percentage_change
        indice_item['index_value'] = index_value
        indice_item['index_change'] = index_change
        indice_item['time_periods'] = time_periods
        indice_item['market_summary'] = summary_data
        
        yield indice_item
