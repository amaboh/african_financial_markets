from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
import logging
from market_data.extract_to_json import extract_data_to_json  # Ensure this path is correct

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
    indices_path, companies_path = extract_data_to_json()
    kwargs['ti'].xcom_push(key='indices_path', value=indices_path)
    kwargs['ti'].xcom_push(key='companies_path', value=companies_path)

extract_task = PythonOperator(
    task_id='extract_data_to_json',
    python_callable=extract_and_return_paths,
    provide_context=True,
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

load_indices_to_bq = GCSToBigQueryOperator(
    task_id='load_indices_to_bq',
    bucket='african_market_data_lake_african-indices-420410',
    source_objects=['scraped_data/indices_{{ ds_nodash }}.json'],
    destination_project_dataset_table='african_indices-420410.market_indice.indices',
    source_format='NEWLINE_DELIMITED_JSON',
    write_disposition='WRITE_TRUNCATE',
    dag=dag
)

load_companies_to_bq = GCSToBigQueryOperator(
    task_id='load_companies_to_bq',
    bucket='african_market_data_lake_african-indices-420410',
    source_objects=['scraped_data/companies_{{ ds_nodash }}.json'],
    destination_project_dataset_table='african_indices-420410.market_indice.companies',
    source_format='NEWLINE_DELIMITED_JSON',
    write_disposition='WRITE_TRUNCATE',
    gcp_conn_id='google_cloud_default',
    dag=dag
)

end_task = DummyOperator(task_id='end', dag=dag)

# separation of parallel tasks
scrape_tasks = [scrape_indices, scrape_companies]
upload_tasks = [upload_indices_to_gcs, upload_companies_to_gcs]
load_tasks = [load_indices_to_bq, load_companies_to_bq]

start_task >> verify_connection

verify_connection.set_downstream(scrape_tasks)

for task in scrape_tasks:
    task >> extract_task

extract_task.set_downstream(upload_tasks)

for upload_task, load_task in zip(upload_tasks, load_tasks):
    upload_task >> load_task

load_tasks >> end_task