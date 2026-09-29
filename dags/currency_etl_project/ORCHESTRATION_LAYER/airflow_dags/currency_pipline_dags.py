from datetime import datetime, timedelta
import sys
import os

from airflow import DAG
from airflow.operators.python import PythonOperator

# Adding the project path to Python's path to import internal modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from EXTRACTION_LAYER.SRC.extractor import CurrencyExtractor
from EXTRACTION_LAYER.SRC.transformer import CurrencyTransformer
from EXTRACTION_LAYER.SRC.loader import ClickHouseLoader
from LOG_LAYER.telegram_notifier import TelegramNotifier
from LOG_LAYER.logger import setup_logger

logger = setup_logger("airflow_currency_dag", log_file="logs/airflow_pipeline.log")
notifier = TelegramNotifier()

def task_failure_alert(context):
    """
    Callback function to send error alarms to Telegram if any task fails
    """
    task_id = context.get('task_instance').task_id
    dag_id = context.get('task_instance').dag_id
    exec_date = context.get('execution_date')
    
    error_message = (
        f"🚨 *Error in Currency ETL Pipeline*\n\n"
        f"📌 *DAG:* `{dag_id}`\n"
        f"⚙️ *Task:* `{task_id}`\n"
        f"📅 *Execution Time:* `{exec_date}`\n\n"
        f"Please check the logs!"
    )
    notifier.send_message(error_message)

def run_extraction(**context):
    """API data extraction task"""
    logger.info("Starting data extraction from CoinGecko...")
    extractor = CurrencyExtractor()
    raw_data = extractor.fetch_market_data()
    # Storing raw data in XCom for use in the next task
    context['ti'].xcom_push(key='raw_currency_data', value=raw_data)
    logger.info("Extraction was successfully completed, and the data was placed in XCom.")

def run_transformation(**context):
    """Data cleaning and transformation task"""
    logger.info("Starting data transformation and cleaning...")
    ti = context['ti']
    raw_data = ti.xcom_pull(task_ids='extract_data_task', key='raw_currency_data')
    
    if not raw_data:
        raise ValueError("No data was received from the previous task!")
        
    transformed_data = CurrencyTransformer.transform(raw_data)
    ti.xcom_push(key='transformed_currency_data', value=transformed_data)
    logger.info("Data conversion completed successfully.")

def run_loading(**context):
    """Data insertion task in ClickHouse"""
    logger.info("Starting data loading into ClickHouse...")
    ti = context['ti']
    transformed_data = ti.xcom_pull(task_ids='transform_data_task', key='transformed_currency_data')
    
    if not transformed_data:
        raise ValueError("No data available to insert into the database!")
        
    loader = ClickHouseLoader()
    loader.load(transformed_data)
    logger.info("Data loading into ClickHouse completed successfully.")


default_args = {
    'owner': 'sara',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': task_failure_alert,
}


with DAG(
    dag_id='currency_etl_pipeline',
    default_args=default_args,
    description='Exchange rate ETL pipeline connecting to CoinGecko and storing data in ClickHouse.',
    schedule_interval='@hourly',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['crypto', 'etl', 'clickhouse', 'airflow'],
) as dag:

    extract_task = PythonOperator(
        task_id='extract_data_task',
        python_callable=run_extraction,
        provide_context=True,
    )

    transform_task = PythonOperator(
        task_id='transform_data_task',
        python_callable=run_transformation,
        provide_context=True,
    )

    load_task = PythonOperator(
        task_id='load_data_task',
        python_callable=run_loading,
        provide_context=True,
    )

    
    extract_task >> transform_task >> load_task