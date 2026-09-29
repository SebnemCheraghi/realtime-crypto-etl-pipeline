from datetime import datetime
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CurrencyTransformer:
    @staticmethod
    def transform(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Cleaning, structuring, and adding timestamps to raw currency market data.
        """
        transformed_data = []
        current_time = datetime.utcnow()  

        for item in raw_data:
            try:
                # Extraction and mapping of required fields according to the ClickHouse structure
                processed_item = {
                    "timestamp": current_time,
                    "currency_id": str(item.get("id", "")),
                    "symbol": str(item.get("symbol", "")).lower(),
                    "name": str(item.get("name", "")),
                    "current_price": float(item.get("current_price") or 0.0),
                    "market_cap": int(item.get("market_cap") or 0),
                    "total_volume": int(item.get("total_volume") or 0),
                    "high_24h": float(item.get("high_24h") or 0.0),
                    "low_24h": float(item.get("low_24h") or 0.0),
                    "price_change_percentage_24h": float(item.get("price_change_percentage_24h") or 0.0)
                }
                transformed_data.append(processed_item)
            except Exception as e:
                logger.error(f"Error processing record for currency {item.get('id', 'Unknown')}:{e}")
                continue

        logger.info(f"{len(transformed_data)} records were successfully processed and transformed.")
        return transformed_data

# Local Test Sample
if __name__ == "__main__":
    sample_raw = [{
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "current_price": 65000.5,
        "market_cap": 1200000000000,
        "total_volume": 25000000000,
        "high_24h": 66000.0,
        "low_24h": 64000.0,
        "price_change_percentage_24h": 1.5
    }]
    
    transformer = CurrencyTransformer()
    result = transformer.transform(sample_raw)
    print("transformed data")
    print(result[0])