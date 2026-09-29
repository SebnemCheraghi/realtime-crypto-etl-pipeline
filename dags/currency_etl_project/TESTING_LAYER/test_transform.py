import pytest
from datetime import datetime
from EXTRACTION_LAYER.SRC.transformer import CurrencyTransformer

def test_transform_valid_data():
    """
    Validation, cleaning, and conversion test for accurate currency market data
    """
    raw_input = [
        {
            "id": "ethereum",
            "symbol": "eth",
            "name": "Ethereum",
            "current_price": 3000.5,
            "market_cap": 350000000000,
            "total_volume": 12000000000,
            "high_24h": 3100.0,
            "low_24h": 2900.0,
            "price_change_percentage_24h": -2.1
        }
    ]

    transformed = CurrencyTransformer.transform(raw_input)

    assert isinstance(transformed, list)
    assert len(transformed) == 1
    
    item = transformed[0]
    assert item["currency_id"] == "ethereum"
    assert item["symbol"] == "eth"
    assert item["name"] == "Ethereum"
    assert item["current_price"] == 3000.5
    assert isinstance(item["timestamp"], datetime)
    assert item["market_cap"] == 350000000000

def test_transform_missing_fields():
    """
    Testing default values ​​based on whether fields are empty or absent in the raw API response.
    """
    raw_input = [
        {
            "id": "unknown-coin",
        }
    ]

    transformed = CurrencyTransformer.transform(raw_input)

    assert len(transformed) == 1
    item = transformed[0]
    assert item["currency_id"] == "unknown-coin"
    assert item["current_price"] == 0.0
    assert item["market_cap"] == 0