from datetime import datetime, timedelta
from airflow import DAG
from operators.sqlserver_to_clickhouse import SQLServerToClickHouseOperator
from utils.sql_queries import DATABASE_LEVEL_QUERIES

default_args = {
    "owner": "sara",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="sqlserver_inventory_dag",
    default_args=default_args,
    description="Daily/Hourly metadata, database sizes, missing indexes, and fragmentation",
    schedule_interval="0 2 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["monitoring", "sqlserver", "inventory"],
) as dag:

    task_db_inventory = SQLServerToClickHouseOperator(
        task_id="collect_database_inventory",
        sql_query=DATABASE_LEVEL_QUERIES["database_inventory"],
        target_table="metrics_database",
    )

    task_table_index_health = SQLServerToClickHouseOperator(
        task_id="collect_table_and_index_health",
        sql_query=DATABASE_LEVEL_QUERIES["table_and_index_health"],
        target_table="metrics_table_index_health",
    )

    task_missing_indexes = SQLServerToClickHouseOperator(
        task_id="collect_missing_indexes",
        sql_query=DATABASE_LEVEL_QUERIES["missing_indexes"],
        target_table="metrics_missing_indexes",
    )

    task_fragmentation = SQLServerToClickHouseOperator(
        task_id="collect_index_fragmentation",
        sql_query=DATABASE_LEVEL_QUERIES["index_fragmentation"],
        target_table="metrics_index_fragmentation",
    )

    [task_db_inventory, task_table_index_health] >> task_missing_indexes >> task_fragmentation