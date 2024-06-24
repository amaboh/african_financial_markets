from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
import logging

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
    description='A DAG to scrape market data and store in PostgreSQL',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
)

start_task = DummyOperator(task_id='start', dag=dag)

scrape_indices = BashOperator(
    task_id='scrape_indices',
    bash_command='cd /opt/airflow/scrapy_project && scrapy crawl marketspider',
    dag=dag
)

scrape_companies = BashOperator(
    task_id='scrape_companies',
    bash_command='cd /opt/airflow/scrapy_project && scrapy crawl companyspider',
    dag=dag
)

def verify_postgres_connection():
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
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

end_task = DummyOperator(task_id='end', dag=dag)

# Task dependencies
start_task >> verify_connection >> [scrape_indices, scrape_companies] >> end_task
