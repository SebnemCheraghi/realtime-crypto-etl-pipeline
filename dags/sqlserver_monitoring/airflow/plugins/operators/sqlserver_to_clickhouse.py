# plugins/operators/sqlserver_to_clickhouse.py

from airflow.models import BaseOperator
from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook
from utils.clickhouse_client import insert_dataframe
import pandas as pd


class SQLServerToClickHouseOperator(BaseOperator):

    template_fields = ('sql_query', 'target_table')

    def __init__(
        self,
        sql_query: str,
        target_table: str,
        mssql_conn_id: str = "mssql_default",
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.sql_query = sql_query
        self.target_table = target_table
        self.mssql_conn_id = mssql_conn_id

    def execute(self, context):
        self.log.info(f"Extracting data from SQL Server using query: {self.sql_query}")
        
        mssql_hook = MsSqlHook(mssql_conn_id=self.mssql_conn_id)
        conn = mssql_hook.get_conn()
        
        df = pd.read_sql(self.sql_query, conn)
        
        if df.empty:
            self.log.info("No data fetched from SQL Server.")
            return

        df['created_at'] = pd.Timestamp.now()
        
        self.log.info(f"Inserting {len(df)} rows into ClickHouse table: {self.target_table}")
        insert_dataframe(self.target_table, df)
        self.log.info("Transfer completed successfully.")