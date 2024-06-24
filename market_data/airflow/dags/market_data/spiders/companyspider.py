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
            company_name = row.css('td.col_width_1 a::text').get()
            company_item['company_name'] = company_name.strip() if company_name else 'N/A'
            sector = row.css('td.col_width_2::text').get()
            company_item['sector'] = sector.strip() if sector else 'N/A'
            price = row.css('td.col_width_3::text').get()
            company_item['price'] = price.strip() if price else 'N/A'

            # check both font and p tags
            one_day = row.css('td.col_width_4 font::text').get()
            if not one_day:
                one_day = row.css('td.col_width_4 p::text').get()
            company_item['one_day'] = one_day.strip() if one_day else 'N/A'
            
            #check both font and p tags
            ytd = row.css('td.col_width_5 font::text').get()
            if not ytd:
                ytd = row.css('td.col_width_5 p::text').get()
            company_item['ytd'] = ytd.strip() if ytd else 'N/A'

            market_cap = row.css('td.col_width_6::text').get()
            company_item['market_cap'] = market_cap.strip() if market_cap else 'N/A'
            date = row.css('td.col_width_7::text').get()
            company_item['date'] = date.strip() if date else 'N/A'

            yield company_item
