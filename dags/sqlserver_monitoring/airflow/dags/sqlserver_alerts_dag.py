from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from utils.clickhouse_client import query_clickhouse

default_args = {
    "owner": "sara",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 0,
}

with DAG(
    dag_id="sqlserver_alerts_dag",
    default_args=default_args,
    description="Evaluates ClickHouse stored metrics and triggers alert notifications",
    schedule_interval="*/5 * * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["monitoring", "alerts"],
) as dag:

    def check_high_cpu_usage():
        query = """
            SELECT server_name, avg(sql_cpu_utilization) as avg_cpu
            FROM metrics_server
            WHERE created_at >= now() - INTERVAL 5 MINUTE
            GROUP BY server_name
            HAVING avg_cpu > 85
        """
        records = query_clickhouse(query)
        for server, cpu in records:
            print(f"[ALERT] High CPU utilization on {server}: {cpu}%")

    def check_blocking_queries():
        query = """
            SELECT server_name, count() as blocking_count
            FROM metrics_active_requests
            WHERE created_at >= now() - INTERVAL 5 MINUTE
              AND blocking_session_id <> 0
            GROUP BY server_name
        """
        records = query_clickhouse(query)
        for server, count in records:
            print(f"[ALERT] Active blocking detected on {server}! Count: {count}")

    task_alert_cpu = PythonOperator(
        task_id="check_high_cpu_usage",
        python_callable=check_high_cpu_usage,
    )

    task_alert_blocking = PythonOperator(
        task_id="check_blocking_queries",
        python_callable=check_blocking_queries,
    )

    [task_alert_cpu, task_alert_blocking]