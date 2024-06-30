import json
import os
from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime

def extract_data_to_json():
    db_uri = f'postgresql+psycopg2://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@postgres/{os.environ.get("POSTGRES_INGEST_DB")}'
    engine = create_engine(db_uri)
    
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    indices_path = f'/opt/airflow/dags/market_data/indices_{current_time}.json'
    companies_path = f'/opt/airflow/dags/market_data/companies_{current_time}.json'
    
    # Query the data from PostgreSQL and save to JSON
    indices_query = "SELECT * FROM market_data.indices"
    companies_query = "SELECT * FROM market_data.companies"
    
    indices_df = pd.read_sql(indices_query, engine)
    companies_df = pd.read_sql(companies_query, engine)
    
    indices_df.to_json(indices_path, orient='records', lines=True)
    companies_df.to_json(companies_path, orient='records', lines=True)
    
    return indices_path, companies_path
    
    
    
    
    

    