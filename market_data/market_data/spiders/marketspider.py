import scrapy


class MarketspiderSpider(scrapy.Spider):
    name = "marketspider"
    allowed_domains = ["www.african-markets.com"]
    start_urls = ["https://www.african-markets.com/en/"]

    def parse(self, response):
        indices = response.css('div.mega-inner ul li a.menu-market-link')
        
        for indice in indices:
            market = indice.css('a::text').get()
            relative_index_url = indice.css('a ::attr(href)').get()

            if 'en/' in relative_index_url:
                indice_url = 'https://www.african-markets.com/' + relative_index_url
            else:
                indice_url = 'https://www.african-markets.com/fr/' + relative_index_url

            # Directly use callback=self.parse_indice_page here
            yield response.follow(indice_url, callback=self.parse_indice_page) 
            
    
    def parse_indice_page(self, response):
        content_div = response.css('div#mod-custom749')
        

        # Index Name
        indice_name = content_div.css('font[size="1"] span::text').get()
        
        # Current Date
        current_date = current_date_text = content_div.css('font[size="1"]::text').get()
        
        if current_date_text:
            # Example: "BSE DOMESTIC COMPANIES INDEX | As of 03-Apr-2024"
            date_part = current_date_text.split("As of")[-1].strip()  # Get the part after "As of"
            current_date = date_part
        else:
            current_date = "Date not found"


        # Index Value and Change 
        value_and_change = content_div.css('span[style*="font-weight:bold;font-size: 22pt"]::text').extract()
        index_value = value_and_change[0].strip() if len(value_and_change) >= 1 else "Data not found"
        index_change = value_and_change[1].strip() if len(value_and_change) >= 2 else "Data not found"
        
        # Time Periods Table
        time_periods_table = response.css('table.tabtable-rs_c4try72e') 

        # Extract keys (time periods)
        keys = time_periods_table.css('tr.tr_ht1 td::text').extract()

        # Extract values (percentage changes)
        values = time_periods_table.css('tr.tabrow p::text').extract()

        # Combine into dictionary
        time_periods = dict(zip(keys, values))
        
        
        
        # Index Percentage Change
        index_percentage_change = content_div.css('font > span[style*="color: #ff0000;"]::text').getall()[0].strip()

        # Market Summary Table
        summary_table = response.css('table.tabtable-gr_alterora_elemental_2_grey_1s2')
        summary_data = {}  # Use a dictionary instead of a list
        for row in summary_table.css('tr.tabrow'):
            cells = row.css('td')
            for cell in cells:  # Iterate over each cell in a row
                key = cell.css('span:first-child::text').get().strip()
                value = cell.css('span:last-child::text').get().strip()
                summary_data[key] = value 

        yield {
            'indice_name': indice_name,
            "current_date": current_date,
            'index_percentage_change': index_percentage_change,
            'index_value': index_value,
            'index_change': index_change,
            'time_periods': time_periods,
            'market_summary': summary_data
        }

        
        
                
            