import scrapy
from market_data.items import CompanyItem

class CompanyspiderSpider(scrapy.Spider):
    name = "companyspider"
    allowed_domains = ["www.african-markets.com"]
    start_urls = ["https://www.african-markets.com/en/"]

    def parse(self, response):
        indices = response.css('div.mega-inner ul li a.menu-market-link')
        
        for indice in indices:
            market = indice.css('a::text').get()
            relative_index_url = indice.css('a ::attr(href)').get()

            if 'en/' in relative_index_url:
                indice_url = 'https://www.african-markets.com/' + relative_index_url + '/' + 'listed-companies'
                print(indice_url)
            else:
                indice_url = 'https://www.african-markets.com/fr/' + relative_index_url + '/' + 'listed-companies'

            # Directly use callback=self.parse_indice_page here
            yield response.follow(indice_url, callback=self.parse_listed_page, meta={'market': market})
        
    
    def parse_listed_page(self, response):
        
        market = response.meta['market'] 
        # Select the rows in the company table
        company_rows = response.css('table.tabtable-rs_01k0jris tbody tr') 
        indice_item = CompanyItem() 
        
        listed_exhange = {}
        
        company_data = {}
        
       
        
        for row in company_rows: 
            company_name = row.css('td.tabcol.col_width_1 a::text').get()
            sector = row.css('td.tabcol.col_width_2::text').get()
            price = row.css('td.tabcol.col_width_3::text').get()
            one_day = row.css('td.tabcol.col_width_4::text').get()
            ytd_change = row.css('td.tabcol.col_width_5::text').get()
            market_cap =  row.css('td.tabcol.col_width_6::text').get()
            date = row.css('td.tabcol.col_width_7::text').get()
                
            indice_item['company_name'] = company_name
            indice_item['sector'] = sector
            indice_item['price'] = price
            indice_item['one_day'] = one_day
            indice_item['ytd'] = ytd_change
            indice_item['market_cap'] = market_cap
            indice_item['date'] = date
            company_data[market] = indice_item
                

                

                # Clean up extracted data if needed (e.g., remove extra spaces, '%' signs)

            yield company_data


        
        
                
            