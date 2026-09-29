import requests
import logging
from typing import List, Dict, Any

# Basic logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CurrencyExtractor:
    def __init__(self, vs_currency: str = "usd", per_page: int = 20):
        self.url = "https://api.coingecko.com/api/v3/coins/markets"
        self.params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": 1,
            "sparkline": "false"
        }
        self.headers = {
            "accept": "application/json"
        }

    def fetch_market_data(self) -> List[Dict[str, Any]]:
        """
        Retrieving currency exchange rate data from the CoinGecko API
        """
        try:
            logger.info(f"Sending request to the CoinGecko API: {self.url}")
            response = requests.get(self.url, params=self.params, headers=self.headers, timeout=10)
            
            # Reviewing the Response Status
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully retrieved {len(data)} records from the API.")
            return data

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err} - Server response: {response.text}")
            raise
        except requests.exceptions.ConnectionError as conn_err:
            logger.error(f"Network connection error: {conn_err}")
            raise
        except requests.exceptions.Timeout as timeout_err:
            logger.error(f"Timeout : {timeout_err}")
            raise
        except Exception as err:
            logger.error(f"An unexpected error occurred: {err}")
            raise

# Sample local test script
if __name__ == "__main__":
    extractor = CurrencyExtractor()
    market_data = extractor.fetch_market_data()
    if market_data:
        print("Sample received data (first currency):")
        print(market_data[0])