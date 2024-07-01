from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from google.cloud.bigquery import SchemaField
from google.oauth2.service_account import Credentials
import logging
from google.cloud import storage
from market_data.extract_to_json import extract_data_to_json
import json

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'market_data_dag',
    default_args=default_args,
    description='A DAG to scrape market data, store in PostgreSQL, move to GCS, and load to BigQuery',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
)

start_task = DummyOperator(task_id='start', dag=dag)

scrape_indices = BashOperator(
    task_id='scrape_indices',
    bash_command='cd /opt/airflow/dags/market_data && scrapy crawl marketspider',
    dag=dag
)

scrape_companies = BashOperator(
    task_id='scrape_companies',
    bash_command='cd /opt/airflow/dags/market_data && scrapy crawl companyspider',
    dag=dag
)

def verify_postgres_connection():
    try:
        pg_hook = PostgresHook(postgres_conn_id='ingest_db_conn_id')
        pg_hook.get_conn().cursor()
        logging.info("Postgres connection is working.")
    except Exception as e:
        logging.error("Error connecting to Postgres: %s", e)
        raise

verify_connection = PythonOperator(
    task_id='verify_postgres_connection',
    python_callable=verify_postgres_connection,
    dag=dag
)

def extract_and_return_paths(**kwargs):
    postgres_conn_id = kwargs.get('postgres_conn_id', 'ingest_db_conn_id')
    print(f"Using postgres_conn_id: {postgres_conn_id}")
    indices_path, companies_path = extract_data_to_json(postgres_conn_id)
    print(f"Extracted data to {indices_path} and {companies_path}")
    
    # Add file size checks
    import os
    indices_size = os.path.getsize(indices_path)
    companies_size = os.path.getsize(companies_path)
    print(f"Indices file size: {indices_size} bytes")
    print(f"Companies file size: {companies_size} bytes")
    
    if indices_size == 0:
        print("Warning: Indices file is empty!")
    if companies_size == 0:
        print("Warning: Companies file is empty!")
    
    kwargs['ti'].xcom_push(key='indices_path', value=indices_path)
    kwargs['ti'].xcom_push(key='companies_path', value=companies_path)

extract_task = PythonOperator(
    task_id='extract_data_to_json',
    python_callable=extract_and_return_paths,
    op_kwargs={'postgres_conn_id': 'ingest_db_conn_id'},
    provide_context=True,
    dag=dag
)


def check_postgres_data(**kwargs):
    pg_hook = PostgresHook(postgres_conn_id='ingest_db_conn_id')
    indices_count = pg_hook.get_first("SELECT COUNT(*) FROM market_data.indices")[0]
    companies_count = pg_hook.get_first("SELECT COUNT(*) FROM market_data.companies")[0]
    print(f"Number of rows in market_data.indices: {indices_count}")
    print(f"Number of rows in market_data.companies: {companies_count}")

check_data_task = PythonOperator(
    task_id='check_postgres_data',
    python_callable=check_postgres_data,
    dag=dag
)


upload_indices_to_gcs = LocalFilesystemToGCSOperator(
    task_id='upload_indices_to_gcs',
    src='{{ task_instance.xcom_pull(task_ids="extract_data_to_json", key="indices_path") }}',
    dst='scraped_data/indices_{{ ds_nodash }}.json',
    bucket='african_market_data_lake_african-indices-420410',
    gcp_conn_id='google_cloud_default',
    dag=dag
)

upload_companies_to_gcs = LocalFilesystemToGCSOperator(
    task_id='upload_companies_to_gcs',
    src='{{ task_instance.xcom_pull(task_ids="extract_data_to_json", key="companies_path") }}',
    dst='scraped_data/companies_{{ ds_nodash }}.json',
    bucket='african_market_data_lake_african-indices-420410',
    gcp_conn_id='google_cloud_default',
    dag=dag
)

def print_gcs_file_content(**kwargs):
    gcs_hook = GCSHook(gcp_conn_id='google_cloud_default')
    bucket_name = 'african_market_data_lake_african-indices-420410'
    object_name = f"scraped_data/indices_{kwargs['ds_nodash']}.json"
    
    print(f"Attempting to access bucket: {bucket_name}, object: {object_name}")
    
    # Get the connection details
    connection = gcs_hook.get_connection('google_cloud_default')
    print(f"Retrieved connection: {connection}")
    
    # Create credentials from the keyfile path
    key_path = '/opt/airflow/keys/gcp-creds.json'
    print(f"Using key path: {key_path}")
    credentials = Credentials.from_service_account_file(key_path)
    print("Created credentials from service account file")

    # Create the storage client with the credentials
    project_id = json.loads(connection.extra).get('project_id')
    print(f"Using project ID: {project_id}")
    client = storage.Client(credentials=credentials, project=project_id)
    print("Created storage client")
    
    # Get the bucket and blob
    bucket = client.get_bucket(bucket_name)
    print(f"Retrieved bucket: {bucket}")
    blob = bucket.blob(object_name)
    print(f"Created blob object: {blob}")
    
    # Download the content
    file_content = blob.download_as_text()
    
    print(f"Content of {object_name}:")
    print(file_content)

    if not file_content.strip():
        print("Warning: The file is empty!")
    else:
        print(f"File size: {len(file_content)} bytes")

print_file_content_task = PythonOperator(
    task_id='print_gcs_file_content',
    python_callable=print_gcs_file_content,
    provide_context=True,
    dag=dag
)

def check_gcs_file_size(**kwargs):
    gcs_hook = GCSHook(gcp_conn_id='google_cloud_default')
    bucket_name = 'african_market_data_lake_african-indices-420410'
    object_name = f"scraped_data/indices_{kwargs['ds_nodash']}.json"
    size = gcs_hook.get_size(bucket_name=bucket_name, object_name=object_name)
    print(f"Size of {object_name} in GCS: {size} bytes")

check_gcs_size_task = PythonOperator(
    task_id='check_gcs_file_size',
    python_callable=check_gcs_file_size,
    provide_context=True,
    dag=dag
)



indices_schema_fields = [
    {"name": "id", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "current_date", "type": "STRING", "mode": "NULLABLE"},
    {"name": "index_abbreviation", "type": "STRING", "mode": "NULLABLE"},
    {"name": "index_change", "type": "FLOAT", "mode": "NULLABLE"},
    {"name": "index_percentage_change", "type": "FLOAT", "mode": "NULLABLE"},
    {"name": "index_value", "type": "FLOAT", "mode": "NULLABLE"},
    {"name": "indice_name", "type": "STRING", "mode": "NULLABLE"},
    {"name": "market_summary", "type": "JSON", "mode": "NULLABLE"},
    {"name": "time_periods", "type": "JSON", "mode": "NULLABLE"}
]

companies_schema_fields = [
    {"name": "id", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "company_name", "type": "STRING", "mode": "NULLABLE"},
    {"name": "sector", "type": "STRING", "mode": "NULLABLE"},
    {"name": "price", "type": "FLOAT", "mode": "NULLABLE"},
    {"name": "one_day", "type": "FLOAT", "mode": "NULLABLE"},
    {"name": "ytd", "type": "FLOAT", "mode": "NULLABLE"},
    {"name": "market_cap", "type": "FLOAT", "mode": "NULLABLE"},
    {"name": "date", "type": "STRING", "mode": "NULLABLE"},
    {"name": "market_name", "type": "STRING", "mode": "NULLABLE"}
]

load_indices_to_bq = GCSToBigQueryOperator(
    task_id='load_indices_to_bq',
    bucket='african_market_data_lake_african-indices-420410',
    source_objects=['scraped_data/indices_{{ ds_nodash }}.json'],
    destination_project_dataset_table='african-indices-420410.market_indice.indices',
    source_format='NEWLINE_DELIMITED_JSON',
    write_disposition='WRITE_TRUNCATE',
    schema_fields=indices_schema_fields,
    autodetect=False,
    gcp_conn_id='google_cloud_default',
    dag=dag
)

load_companies_to_bq = GCSToBigQueryOperator(
    task_id='load_companies_to_bq',
    bucket='african_market_data_lake_african-indices-420410',
    source_objects=['scraped_data/companies_{{ ds_nodash }}.json'],
    destination_project_dataset_table='african-indices-420410.market_indice.companies',
    source_format='NEWLINE_DELIMITED_JSON',
    write_disposition='WRITE_TRUNCATE',
    schema_fields=companies_schema_fields,
    autodetect=False,
    gcp_conn_id='google_cloud_default',
    dag=dag
)

end_task = DummyOperator(task_id='end', dag=dag)

# Task dependencies
start_task >> verify_connection >> scrape_indices >> scrape_companies >> check_data_task >> extract_task
extract_task >> upload_indices_to_gcs >>  check_gcs_size_task >> print_file_content_task >> load_indices_to_bq
extract_task >> upload_companies_to_gcs >>  check_gcs_size_task >> print_file_content_task >>  load_companies_to_bq
[load_indices_to_bq, load_companies_to_bq] >> end_task