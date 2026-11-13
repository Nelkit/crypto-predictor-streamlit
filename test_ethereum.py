"""
Test suite for the Ethereum module.

This test suite covers:
- Utility functions (helpers.py)
- Controller functions (controller.py)
- API classes (api.py)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import requests
from datetime import datetime
import pytest
import streamlit as st

# Import the modules to test
from students.ethereum.utils.helpers import (
    format_currency_short,
    format_iso_date,
    format_datetime,
)
from students.ethereum.controller import (
    fetch_ethereum_ohlc,
    fetch_ethereum_info,
    fetch_ethereum_related_news,
    fetch_ethereum_forecast,
)
from students.ethereum.api import (
    CoinGeckoApi,
    CryptoNewsApi,
    CryptoForecastApi,
)
from students.ethereum.constants import (
    ETH_LOGO,
    COINGECKO_API_URL,
    CRYPTONEWS_API_URL,
    PREDICTOR_API_URL,
)


@pytest.fixture(autouse=True)
def clear_streamlit_cache():
    """Clear the Streamlit cache before each test"""
    if hasattr(st, 'cache_data'):
        try:
            if hasattr(st.cache_data, 'clear'):
                st.cache_data.clear()
        except:
            pass
    yield
    try:
        if hasattr(st.cache_data, 'clear'):
            st.cache_data.clear()
    except:
        pass


@pytest.fixture(autouse=True)
def mock_streamlit_cache():
    """Mock the Streamlit cache to avoid persistence issues"""
    with patch('students.ethereum.api.st.cache_data', lambda func: func):
        yield


class TestHelpers(unittest.TestCase):
    """Test cases for utility functions in helpers.py"""

    def test_format_currency_short_small_value(self):
        """Test formatting small currency values (less than 1000)"""
        result = format_currency_short(500.50)
        self.assertEqual(result, "$500.50")

    def test_format_currency_short_thousands(self):
        """Test formatting values in thousands"""
        result = format_currency_short(1500)
        self.assertIn("K", result)  # 1500 becomes 1.50K

    def test_format_currency_short_millions(self):
        """Test formatting values in millions"""
        result = format_currency_short(1250000)
        self.assertIn("M", result)

    def test_format_currency_short_billions(self):
        """Test formatting values in billions"""
        result = format_currency_short(470114180844)
        self.assertIn("B", result)

    def test_format_currency_short_invalid_value(self):
        """Test formatting invalid values"""
        result = format_currency_short("invalid")
        self.assertEqual(result, "N/A")

    def test_format_currency_short_none(self):
        """Test formatting None value"""
        result = format_currency_short(None)
        self.assertEqual(result, "N/A")

    def test_format_iso_date_valid(self):
        """Test formatting valid ISO date"""
        result = format_iso_date("2024-01-15T10:30:00Z")
        self.assertEqual(result, "2024-01-15")

    def test_format_iso_date_invalid(self):
        """Test formatting invalid ISO date"""
        result = format_iso_date("invalid-date")
        self.assertIn("⚠️", result)

    def test_format_datetime_int_timestamp(self):
        """Test formatting integer timestamp"""
        result = format_datetime(1705320600)  # Jan 15, 2024 10:30:00
        self.assertIn("2024", result)
        self.assertIn("Jan", result)

    def test_format_datetime_pandas_timestamp(self):
        """Test formatting pandas Timestamp"""
        ts = pd.Timestamp("2024-01-15 10:30:00")
        result = format_datetime(ts)
        self.assertIn("2024", result)
        self.assertIn("Jan", result)

    def test_format_datetime_invalid(self):
        """Test formatting invalid datetime"""
        result = format_datetime("invalid")
        self.assertEqual(result, "Unknown date")


class TestController(unittest.TestCase):
    """Test cases for controller functions"""

    @patch("students.ethereum.controller.CoinGeckoApi")
    def test_fetch_ethereum_ohlc_success(self, mock_api_class):
        """Test successful OHLC data fetch"""
        # Setup mock
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        
        expected_df = pd.DataFrame({
            "timestamp": [pd.Timestamp("2024-01-15")],
            "open": [2500.0],
            "high": [2600.0],
            "low": [2400.0],
            "close": [2550.0],
        })
        mock_api.fetch_ohlc_data.return_value = expected_df

        # Execute
        result = fetch_ethereum_ohlc(days=7)

        # Assert
        self.assertFalse(result.empty)
        self.assertEqual(len(result), 1)
        mock_api.fetch_ohlc_data.assert_called_once_with("ethereum", days=7)

    @patch("students.ethereum.controller.CoinGeckoApi")
    def test_fetch_ethereum_ohlc_empty(self, mock_api_class):
        """Test OHLC data fetch with empty response"""
        # Setup mock
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        mock_api.fetch_ohlc_data.return_value = pd.DataFrame()

        # Execute
        result = fetch_ethereum_ohlc(days=7)

        # Assert
        self.assertTrue(result.empty)

    @patch("students.ethereum.controller.CoinGeckoApi")
    def test_fetch_ethereum_info_success(self, mock_api_class):
        """Test successful coin info fetch"""
        # Setup mock
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        
        expected_info = {
            "name": "Ethereum",
            "symbol": "eth",
            "current_price": 2500.0,
            "market_cap": 300000000000,
        }
        mock_api.fetch_coin_info.return_value = expected_info

        # Execute
        result = fetch_ethereum_info()

        # Assert
        self.assertEqual(result["name"], "Ethereum")
        self.assertEqual(result["symbol"], "eth")
        mock_api.fetch_coin_info.assert_called_once_with("ethereum")

    @patch("students.ethereum.controller.CryptoNewsApi")
    def test_fetch_ethereum_related_news_success(self, mock_api_class):
        """Test successful news fetch"""
        # Setup mock
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        
        expected_df = pd.DataFrame({
            "title": ["Test News"],
            "body": ["Test body"],
            "url": ["https://example.com"],
        })
        mock_api.fetch_latest_news.return_value = expected_df

        # Execute
        result = fetch_ethereum_related_news(limit=5)

        # Assert
        self.assertFalse(result.empty)
        self.assertEqual(len(result), 1)
        mock_api.fetch_latest_news.assert_called_once_with(coin_id="ETH", limit=5)

    @patch("students.ethereum.controller.CryptoForecastApi")
    def test_fetch_ethereum_forecast_success(self, mock_api_class):
        """Test successful forecast fetch"""
        # Setup mock
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        
        expected_forecast = {
            "next_day_high_predicted": 2600.0,
            "next_day_high_date": "2024-01-16",
            "model": "LSTM",
        }
        mock_api.fetch_price_prediction.return_value = expected_forecast

        # Execute
        result = fetch_ethereum_forecast(coin_id="ETH", force_refresh_key=0)

        # Assert
        self.assertEqual(result["next_day_high_predicted"], 2600.0)
        self.assertEqual(result["model"], "LSTM")
        mock_api.fetch_price_prediction.assert_called_once_with("ETH", 0)


class TestCoinGeckoApi(unittest.TestCase):
    """Test cases for CoinGeckoApi class"""

    def setUp(self):
        """Set up test fixtures"""
        self.api = CoinGeckoApi()

    @patch("students.ethereum.api.st.cache_data", lambda func: func)
    def test_fetch_ohlc_data_success(self):
        """Test successful OHLC data fetch"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            [1705320600000, 2500.0, 2600.0, 2400.0, 2550.0],
        ]
        mock_response.raise_for_status = Mock()
        
        # Create a new API instance and mock its session
        api = CoinGeckoApi()
        api.session.get = Mock(return_value=mock_response)
        
        # Execute
        result = api.fetch_ohlc_data("ethereum", days=7)

        # Assert
        self.assertFalse(result.empty)
        self.assertEqual(len(result), 1)
        self.assertIn("timestamp", result.columns)
        self.assertIn("open", result.columns)
        self.assertIn("high", result.columns)
        self.assertIn("low", result.columns)
        self.assertIn("close", result.columns)

    @patch("students.ethereum.api.st.cache_data", lambda func: func)
    def test_fetch_ohlc_data_empty_response(self):
        """Test OHLC data fetch with empty response"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()

        # Create a new API instance and mock its session
        api = CoinGeckoApi()
        api.session.get = Mock(return_value=mock_response)
        
        # Execute
        result = api.fetch_ohlc_data("ethereum", days=7)

        # Assert
        self.assertTrue(result.empty)

    @patch("students.ethereum.api.st.cache_data", lambda func: func)
    def test_fetch_ohlc_data_http_error(self):
        """Test OHLC data fetch with HTTP error"""
        # Setup mock response with error
        mock_response = Mock()
        mock_response.status_code = 404
        
        # Create HTTPError with response
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        
        # Make raise_for_status raise the error
        mock_response.raise_for_status = Mock(side_effect=http_error)
        
        # Create a new API instance and mock its session
        api = CoinGeckoApi()
        api.session.get = Mock(return_value=mock_response)
        
        # Execute
        result = api.fetch_ohlc_data("ethereum", days=7)

        # Assert
        self.assertTrue(result.empty)

    @patch("students.ethereum.api.st.cache_data", lambda func: func)
    def test_fetch_coin_info_success(self):
        """Test successful coin info fetch"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "Ethereum",
            "symbol": "eth",
            "hashing_algorithm": "Ethash",
            "categories": ["Smart Contract Platform"],
            "description": {"en": "Ethereum description"},
            "links": {
                "homepage": ["https://ethereum.org"],
                "blockchain_site": ["https://etherscan.io"],
            },
            "market_data": {
                "current_price": {"usd": 2500.0},
                "market_cap": {"usd": 300000000000},
                "total_volume": {"usd": 10000000000},
                "last_updated": "2024-01-15T10:30:00Z",
            },
        }
        mock_response.raise_for_status = Mock()

        # Create a new API instance and mock its session
        api = CoinGeckoApi()
        api.session.get = Mock(return_value=mock_response)
        
        # Execute
        result = api.fetch_coin_info("ethereum")

        # Assert
        self.assertEqual(result["name"], "Ethereum")
        self.assertEqual(result["symbol"], "eth")
        self.assertEqual(result["current_price"], 2500.0)
        self.assertEqual(result["market_cap"], 300000000000)

    @patch("students.ethereum.api.st.cache_data", lambda func: func)
    def test_fetch_coin_info_timeout(self):
        """Test coin info fetch with timeout"""
        # Create a new API instance and mock its session
        api = CoinGeckoApi()
        api.session.get = Mock(side_effect=requests.exceptions.Timeout())

        # Execute
        result = api.fetch_coin_info("ethereum")

        # Assert
        self.assertEqual(result, {})


class TestCryptoNewsApi(unittest.TestCase):
    """Test cases for CryptoNewsApi class"""

    def setUp(self):
        """Set up test fixtures"""
        self.api = CryptoNewsApi()

    @patch("students.ethereum.api.st.cache_data", lambda func: func)
    def test_fetch_latest_news_success(self):
        """Test successful news fetch"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "article_id": "123",
                    "source_id": "source1",
                    "title": "Ethereum News",
                    "description": "News description",
                    "link": "https://example.com/news",
                    "pubDate": "2024-01-15T10:30:00Z",
                    "keywords": ["ethereum", "crypto"],
                }
            ]
        }

        # Create a new API instance and mock its session
        api = CryptoNewsApi()
        api.session.get = Mock(return_value=mock_response)
        
        # Execute
        result = api.fetch_latest_news(coin_id="ETH", limit=10)

        # Assert
        self.assertFalse(result.empty)
        self.assertEqual(len(result), 1)
        self.assertIn("title", result.columns)
        self.assertIn("url", result.columns)

    @patch("students.ethereum.api.st.cache_data", lambda func: func)
    def test_fetch_latest_news_empty_response(self):
        """Test news fetch with empty response"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}

        # Create a new API instance and mock its session
        api = CryptoNewsApi()
        api.session.get = Mock(return_value=mock_response)
        
        # Execute
        result = api.fetch_latest_news(coin_id="ETH", limit=10)

        # Assert
        self.assertTrue(result.empty)

    @patch("students.ethereum.api.st.cache_data", lambda func: func)
    def test_fetch_latest_news_non_200_status(self):
        """Test news fetch with non-200 status"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 404

        # Create a new API instance and mock its session
        api = CryptoNewsApi()
        api.session.get = Mock(return_value=mock_response)
        
        # Execute
        result = api.fetch_latest_news(coin_id="ETH", limit=10)

        # Assert
        self.assertTrue(result.empty)

    @patch("students.ethereum.api.st.cache_data", lambda func: func)
    def test_fetch_latest_news_timeout(self):
        """Test news fetch with timeout"""
        # Create a new API instance and mock its session
        api = CryptoNewsApi()
        api.session.get = Mock(side_effect=requests.exceptions.Timeout())
        
        # Execute
        result = api.fetch_latest_news(coin_id="ETH", limit=10)

        # Assert
        self.assertTrue(result.empty)


class TestCryptoForecastApi(unittest.TestCase):
    """Test cases for CryptoForecastApi class"""

    def setUp(self):
        """Set up test fixtures"""
        self.api = CryptoForecastApi()

    @patch("students.ethereum.api.st.cache_data", lambda func: func)
    def test_fetch_price_prediction_success(self):
        """Test successful price prediction fetch"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"next_day_high_predicted": 2600.0, "model": "LSTM"}'
        mock_response.json.return_value = {
            "next_day_high_predicted": 2600.0,
            "model": "LSTM",
        }

        # Create a new API instance and mock its session
        api = CryptoForecastApi()
        api.session.get = Mock(return_value=mock_response)
        
        # Execute
        result = api.fetch_price_prediction("ETH", force_refresh_key=0)

        # Assert
        self.assertEqual(result["next_day_high_predicted"], 2600.0)
        self.assertEqual(result["model"], "LSTM")

    @patch("students.ethereum.api.st.cache_data", lambda func: func)
    def test_fetch_price_prediction_status_400(self):
        """Test price prediction with 400 status"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.content = b'{"error": "Invalid token"}'
        mock_response.json.return_value = {"error": "Invalid token"}

        # Create a new API instance and mock its session
        api = CryptoForecastApi()
        api.session.get = Mock(return_value=mock_response)
        
        # Execute
        result = api.fetch_price_prediction("ETH", force_refresh_key=0)

        # Assert
        self.assertEqual(result["error"], "Invalid token")

    @patch("students.ethereum.api.st.cache_data", lambda func: func)
    def test_fetch_price_prediction_status_500(self):
        """Test price prediction with 500 status"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.content = b'{"error": "Model error"}'
        mock_response.json.return_value = {"error": "Model error"}

        # Create a new API instance and mock its session
        api = CryptoForecastApi()
        api.session.get = Mock(return_value=mock_response)
        
        # Execute
        result = api.fetch_price_prediction("ETH", force_refresh_key=0)

        # Assert
        self.assertEqual(result["error"], "Model error")

    @patch("students.ethereum.api.st.cache_data", lambda func: func)
    def test_fetch_price_prediction_status_503(self):
        """Test price prediction with 503 status"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.content = b'{"error": "External API unavailable"}'
        mock_response.json.return_value = {"error": "External API unavailable"}

        # Create a new API instance and mock its session
        api = CryptoForecastApi()
        api.session.get = Mock(return_value=mock_response)
        
        # Execute
        result = api.fetch_price_prediction("ETH", force_refresh_key=0)

        # Assert
        self.assertEqual(result["error"], "External API unavailable")

    @patch("students.ethereum.api.st.cache_data", lambda func: func)
    def test_fetch_price_prediction_timeout(self):
        """Test price prediction with timeout"""
        # Create a new API instance and mock its session
        api = CryptoForecastApi()
        api.session.get = Mock(side_effect=requests.exceptions.Timeout())
        
        # Execute
        result = api.fetch_price_prediction("ETH", force_refresh_key=0)

        # Assert
        self.assertEqual(result["error"], "Timeout")

    @patch("students.ethereum.api.st.cache_data", lambda func: func)
    def test_fetch_price_prediction_connection_error(self):
        """Test price prediction with connection error"""
        # Create a new API instance and mock its session
        api = CryptoForecastApi()
        api.session.get = Mock(side_effect=requests.exceptions.ConnectionError())
        
        # Execute
        result = api.fetch_price_prediction("ETH", force_refresh_key=0)

        # Assert
        self.assertEqual(result["error"], "Connection error")


class TestConstants(unittest.TestCase):
    """Test cases for constants"""

    def test_constants_defined(self):
        """Test that all constants are defined"""
        self.assertIsNotNone(ETH_LOGO)
        self.assertIsNotNone(COINGECKO_API_URL)
        self.assertIsNotNone(CRYPTONEWS_API_URL)
        self.assertIsNotNone(PREDICTOR_API_URL)
        self.assertIsInstance(ETH_LOGO, str)
        self.assertIsInstance(COINGECKO_API_URL, str)


if __name__ == "__main__":
    unittest.main()

