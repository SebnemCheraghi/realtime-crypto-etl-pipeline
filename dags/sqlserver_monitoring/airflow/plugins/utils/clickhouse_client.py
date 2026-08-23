# plugins/utils/clickhouse_client.py

import os
import pandas as pd
from clickhouse_driver import Client
from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", 9000))
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB", "sqlserver_monitoring")


def get_client():
    return Client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        user=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
        database=CLICKHOUSE_DB
    )


def insert_dataframe(table_name: str, df: pd.DataFrame):
    
    if df.empty:
        return
    
    client = get_client()
    data = df.to_dict('records')
    columns = ", ".join(df.columns)
    query = f"INSERT INTO {table_name} ({columns}) VALUES"
    client.execute(query, data)


def query_clickhouse(query: str):
    
    client = get_client()
    return client.execute(query)


def execute_and_transfer(
    sql_query: str, 
    target_table: str, 
    mssql_conn_id: str = "mssql_default"
):
    
    mssql_hook = MsSqlHook(mssql_conn_id=mssql_conn_id)
    
    conn_config = mssql_hook.get_connection(mssql_conn_id)
    server_name = conn_config.host or "SQL_Server_Instance"

    conn = mssql_hook.get_conn()
    df = pd.read_sql(sql_query, conn)
    
    if not df.empty:
        df['server_name'] = server_name
        df['created_at'] = pd.Timestamp.now()
        
        insert_dataframe(target_table, df)