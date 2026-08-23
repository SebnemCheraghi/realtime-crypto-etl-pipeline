from datetime import datetime, timedelta
from airflow import DAG
from operators.sqlserver_to_clickhouse import SQLServerToClickHouseOperator
from utils.sql_queries import SERVER_LEVEL_QUERIES, PERFORMANCE_QUERIES

default_args = {
    "owner": "sara",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(seconds=20),
}

with DAG(
    dag_id="sqlserver_performance_dag",
    default_args=default_args,
    description="Near real-time extraction of Server level metrics, Disk I/O, Wait Stats, and Blocking",
    schedule_interval="* * * * *",  # اجرای هر ۱ دقیقه
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["monitoring", "sqlserver", "realtime"],
) as dag:

    task_server_metrics = SQLServerToClickHouseOperator(
        task_id="collect_server_metrics",
        sql_query=SERVER_LEVEL_QUERIES["server_metrics"],
        target_table="metrics_server",
    )

    task_disk_io = SQLServerToClickHouseOperator(
        task_id="collect_disk_io",
        sql_query=SERVER_LEVEL_QUERIES["disk_io_metrics"],
        target_table="metrics_disk_io",
    )

    task_wait_stats = SQLServerToClickHouseOperator(
        task_id="collect_wait_stats",
        sql_query=PERFORMANCE_QUERIES["wait_statistics"],
        target_table="metrics_wait_stats",
    )

    task_active_requests = SQLServerToClickHouseOperator(
        task_id="collect_active_requests",
        sql_query=PERFORMANCE_QUERIES["active_requests"],
        target_table="metrics_active_requests",
    )

    [task_server_metrics, task_disk_io, task_wait_stats, task_active_requests]