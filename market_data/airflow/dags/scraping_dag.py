from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'scraping_dag',
    default_args=default_args,
    description='DAG for web scraping using Scrapy',
    schedule_interval=timedelta(days=1),
)

scrapy_command = 'scrapy crawl marketspider companyspider'

scrapy_task = BashOperator(
    task_id='run_scrapy',
    bash_command=scrapy_command,
    cwd='/app/my_project',
    dag=dag,
)

save_to_gcs_task = BashOperator(
    task_id='save_to_gcs',
    bash_command='python /app/airflow/dags/saved_to_gcs.py',
    dag=dag,
)

scrapy_task >> save_to_gcs_task