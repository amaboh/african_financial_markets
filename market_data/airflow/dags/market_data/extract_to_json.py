from airflow.hooks.postgres_hook import PostgresHook
import pandas as pd
from datetime import datetime

def extract_data_to_json(postgres_conn_id):
    try:
        pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        conn = pg_hook.get_conn()
        
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        indices_path = f'/opt/airflow/dags/market_data/indices_{current_time}.json'
        companies_path = f'/opt/airflow/dags/market_data/companies_{current_time}.json'
        
        indices_query = "SELECT * FROM market_data.indices"
        companies_query = "SELECT * FROM market_data.companies"
        
        indices_df = pd.read_sql(indices_query, conn)
        companies_df = pd.read_sql(companies_query, conn)
        
        indices_df.to_json(indices_path, orient='records', lines=True)
        companies_df.to_json(companies_path, orient='records', lines=True)
        
        return indices_path, companies_path
    except Exception as e:
        print(f"An error occurred: {e}")
        raise