import pytest
from unittest.mock import patch, MagicMock
from EXTRACTION_LAYER.SRC.extractor import CurrencyExtractor

@patch("EXTRACTION_LAYER.SRC.extractor.requests.get")
def test_fetch_market_data_success(mock_get):
    """
    Successful test of data retrieval from the CoinGecko API
    """
    # Simulating a successful server response (Status 200 and mock data)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 60000.0}
    ]
    mock_get.return_value = mock_response

    extractor = CurrencyExtractor()
    data = extractor.fetch_market_data()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == "bitcoin"
    assert data[0]["current_price"] == 60000.0
    mock_get.assert_called_once()

@patch("EXTRACTION_LAYER.SRC.extractor.requests.get")
def test_fetch_market_data_failure(mock_get):
    """
   Testing system behavior in the event of an HTTP error from the API.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("API Error 500")
    mock_get.return_value = mock_response

    extractor = CurrencyExtractor()
    
    with pytest.raises(Exception):
        extractor.fetch_market_data()