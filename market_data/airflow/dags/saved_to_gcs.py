from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.hooks.gcs_hook import GoogleCloudStorageHook
from airflow.hooks.postgres_hook import PostgresHook
from datetime import datetime, timedelta
import json

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def save_to_gcs():
    gcs_hook = GoogleCloudStorageHook(google_cloud_storage_conn_id='your_gcs_conn_id')
    
    # Load data from Postgres using PostgresHook
    postgres_hook = PostgresHook(postgres_conn_id='your_postgres_conn_id')
    
    # Fetch market data from Postgres
    market_data = postgres_hook.get_records(sql="SELECT * FROM market_data_table")
    market_data_json = json.dumps(market_data)
    
    # Save market data to GCS
    gcs_hook.upload('your_bucket_name', 'market_data.json', market_data_json)
    
    # Fetch company data from Postgres
    company_data = postgres_hook.get_records(sql="SELECT * FROM company_data_table")
    company_data_json = json.dumps(company_data)
    
    # Save company data to GCS
    gcs_hook.upload('your_bucket_name', 'company_data.json', company_data_json)

dag = DAG(
    'saved_to_gcs',
    default_args=default_args,
    description='Save data from Postgres to Google Cloud Storage',
    schedule_interval=timedelta(days=1),
)

save_to_gcs_task = PythonOperator(
    task_id='save_to_gcs',
    python_callable=save_to_gcs,
    dag=dag,
)