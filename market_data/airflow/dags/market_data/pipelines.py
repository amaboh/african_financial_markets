import psycopg2
import json
from itemadapter import ItemAdapter
import re
from market_data.items import IndiceItem, CompanyItem  

class MarketDataPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if 'index_abbreviation' in adapter:
            value = adapter['index_abbreviation']
            if value:
                abbreviation_match = re.search(r'\((.*?)\)', value)
                if abbreviation_match:
                    adapter['index_abbreviation'] = abbreviation_match.group(1)
                else:
                    adapter['index_abbreviation'] = 'Abbreviation not found'
        return item

class PostgresPipeline:
    def __init__(self):
        hostname = 'postgres'
        username = 'airflow'
        password = 'airflow'
        database = 'ingest_db'
        self.conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.curr = self.conn.cursor()
        self.create_schema()
        self.create_indices_table()
        self.create_companies_table()
        self.insert_indice_statement = """
            INSERT INTO market_data.indices (
                "current_date", 
                index_abbreviation,
                index_change,  
                index_percentage_change,  
                index_value, 
                indice_name,
                market_summary,  
                time_periods
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.insert_company_statement = """
            INSERT INTO market_data.companies (
                company_name,
                sector,
                price,
                one_day,
                ytd,
                market_cap,
                date,
                market_name
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

    def create_schema(self):
        create_schema_statement = "CREATE SCHEMA IF NOT EXISTS market_data"
        self.curr.execute(create_schema_statement)
        self.conn.commit()
        
    def create_indices_table(self):
        create_table_statement = """
            CREATE TABLE IF NOT EXISTS market_data.indices (
                id SERIAL PRIMARY KEY,
                "current_date" TEXT,
                index_abbreviation TEXT,
                index_change NUMERIC,
                index_percentage_change NUMERIC,
                index_value NUMERIC,
                indice_name VARCHAR(255),
                market_summary JSONB,
                time_periods JSONB
            )
        """
        self.curr.execute(create_table_statement)
        self.conn.commit()

    def create_companies_table(self):
        create_table_statement = """
            CREATE TABLE IF NOT EXISTS market_data.companies (
                id SERIAL PRIMARY KEY,
                company_name VARCHAR(255),
                sector VARCHAR(255),
                price NUMERIC,
                one_day NUMERIC,
                ytd NUMERIC,
                market_cap NUMERIC,
                date TEXT,
                market_name VARCHAR(255)
            )
        """
        self.curr.execute(create_table_statement)
        self.conn.commit()

    def process_item(self, item, spider):
        if isinstance(item, IndiceItem):
            self.process_indice(item)
        elif isinstance(item, CompanyItem):
            self.process_company(item)
        return item

    def process_indice(self, item):
        try:
            index_value = item.get('index_value', None)
            if index_value and index_value != 'Data not found':
                index_value = index_value.replace(',', '')
            else:
                index_value = None

            index_change = item.get('index_change', None)
            if index_change and index_change != 'Data not found':
                index_change = index_change.replace(',', '')
            else:
                index_change = None

            index_percentage_change = item.get('index_percentage_change', None)
            if index_percentage_change and index_percentage_change != 'Change not found':
                index_percentage_change = index_percentage_change.replace(',', '')
            else:
                index_percentage_change = None

            market_summary_json = json.dumps(item.get('market_summary', {}))
            time_periods_json = json.dumps(item.get('time_periods', {}))

            self.curr.execute(self.insert_indice_statement, (
                item.get('current_date'),
                item.get('index_abbreviation'),
                float(index_change) if index_change else None,
                float(index_percentage_change) if index_percentage_change else None,
                float(index_value) if index_value else None,
                item.get('indice_name'),
                market_summary_json,  
                time_periods_json     
            ))

            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def process_company(self, item):
        try:
            price = item.get('price', None)
            if price and price != 'N/A':
                price = price.replace(',', '')
            else:
                price = None

            one_day = item.get('one_day', None)
            if one_day and one_day != 'N/A':
                one_day = one_day.replace(',', '').replace('%', '')
            else:
                one_day = None

            ytd = item.get('ytd', None)
            if ytd and ytd != 'N/A':
                ytd = ytd.replace(',', '').replace('%', '')
            else:
                ytd = None

            market_cap = item.get('market_cap', None)
            if market_cap and market_cap != 'N/A':
                market_cap = market_cap.replace(',', '')
            else:
                market_cap = None

            self.curr.execute(self.insert_company_statement, (
                item.get('company_name'),
                item.get('sector'),
                float(price) if price else None,
                float(one_day) if one_day else None,
                float(ytd) if ytd else None,
                float(market_cap) if market_cap else None,
                item.get('date'),
                item.get('market_name')
            ))

            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def close_spider(self, spider):
        self.curr.close()
        self.conn.close()
