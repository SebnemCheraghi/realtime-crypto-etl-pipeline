import logging
from typing import List, Dict, Any
import clickhouse_connect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClickHouseLoader:
    def __init__(self, host: str = "clickhouse_server", port: int = 8123, user: str = "admin", password: str = "admin", database: str = "crypto_db"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def get_client(self, database: str = None):
        """
        Establishing and restoring the connection to ClickHouse
        """
        return clickhouse_connect.get_client(
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
            database=database or self.database
        )

    def create_table_if_not_exists(self) -> None:
        """
        Automatically creates the database and table in ClickHouse if they don't exist.
        """
        temp_client = None
        client = None
        try:
            # 1. Connect without database to create the database if it doesn't exist
            temp_client = self.get_client(database=None)
            temp_client.command(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            
            # 2. Connect to the target database and create the table if it doesn't exist
            client = self.get_client()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS crypto_prices
            (
                timestamp DateTime,
                currency_id LowCardinality(String),
                symbol LowCardinality(String),
                name String,
                current_price Float64,
                market_cap Float64,
                total_volume Float64,
                high_24h Float64,
                low_24h Float64,
                price_change_percentage_24h Float64
            )
            ENGINE = MergeTree()
            ORDER BY (timestamp, currency_id);
            """
            client.command(create_table_query)
            logger.info("ClickHouse database and table checked/created successfully.")

        except Exception as e:
            logger.error(f"Error while ensuring database/table exist in ClickHouse: {e}")
            raise
        finally:
            if temp_client:
                temp_client.close()
            if client:
                client.close()

    def load(self, data: List[Dict[str, Any]]) -> None:
        """
        Inserting a list of dictionaries into a ClickHouse table
        """
        if not data:
            logger.warning("No data has been sent for insertion into ClickHouse.")
            return

        # Ensure database and table exist before inserting data
        self.create_table_if_not_exists()

        client = None
        try:
            client = self.get_client()
            
            # Preparing data in the appropriate format for batch insertion
            # The column order must exactly match the table structure.
            columns = [
                "timestamp", "currency_id", "symbol", "name", 
                "current_price", "market_cap", "total_volume", 
                "high_24h", "low_24h", "price_change_percentage_24h"
            ]
            
            rows = []
            for item in data:
                row = (
                    item.get("timestamp"),
                    item.get("currency_id"),
                    item.get("symbol"),
                    item.get("name"),
                    item.get("current_price"),
                    item.get("market_cap"),
                    item.get("total_volume"),
                    item.get("high_24h"),
                    item.get("low_24h"),
                    item.get("price_change_percentage_24h")
                )
                rows.append(row)

            logger.info(f"Inserting {len(rows)} records into the ClickHouse table...")
            client.insert("crypto_prices", rows, column_names=columns)
            logger.info("Data was successfully stored in ClickHouse.")

        except Exception as e:
            logger.error(f"Error while inserting data into ClickHouse: {e}")
            raise
        finally:
            if client:
                client.close()

# Local Test Sample
if __name__ == "__main__":
    from datetime import datetime
    sample_data = [{
        "timestamp": datetime.utcnow(),
        "currency_id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "current_price": 65000.5,
        "market_cap": 1200000000000,
        "total_volume": 25000000000,
        "high_24h": 66000.0,
        "low_24h": 64000.0,
        "price_change_percentage_24h": 1.5
    }]
    
    # loader = ClickHouseLoader()
    # loader.load(sample_data)