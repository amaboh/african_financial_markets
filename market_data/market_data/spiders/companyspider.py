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
            relative_index_url = indice.css('a::attr(href)').get()
            
            if relative_index_url:
                if 'en/' in relative_index_url:
                    indice_url = f"https://www.african-markets.com{relative_index_url}/listed-companies"
                else:
                    indice_url = f"https://www.african-markets.com/fr{relative_index_url}/listed-companies"

                yield response.follow(indice_url, callback=self.parse_listed_page, meta={'market': market})
    
    def parse_listed_page(self, response):
        market = response.meta['market'] 
        company_rows = response.css('table.tabtable-rs_01k0jris tbody tr') 
        for row in company_rows: 
            company_item = CompanyItem()
            company_item['market_name'] = market
            company_item['company_name'] = row.css('td.tabcol.col_width_1 a::text').get()
            company_item['sector'] = row.css('td.tabcol.col_width_2::text').get()
            company_item['price'] = row.css('td.tabcol.col_width_3::text').get()
            company_item['one_day'] = row.css('td.tabcol.col_width_4::text').get()
            company_item['ytd'] = row.css('td.tabcol.col_width_5::text').get()
            company_item['market_cap'] = row.css('td.tabcol.col_width_6::text').get()
            company_item['date'] = row.css('td.tabcol.col_width_7::text').get()

            yield company_item
