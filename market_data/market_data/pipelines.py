import psycopg2
import json
from itemadapter import ItemAdapter
import re

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

class PostgresIndicePipeline:
    def __init__(self):
        hostname = 'localhost'
        username = 'ama'
        password = 'password'
        database = 'african_financial_markets'
        self.conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.curr = self.conn.cursor()
        self.create_table_statement = """
            CREATE TABLE IF NOT EXISTS indices (
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
        self.curr.execute(self.create_table_statement)
        self.conn.commit()
        self.insert_statement = """
            INSERT INTO indices (
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

    def process_item(self, item, spider):
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

            self.curr.execute(self.insert_statement, (
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

        return item

    def close_spider(self, spider):
        self.curr.close()
        self.conn.close()
