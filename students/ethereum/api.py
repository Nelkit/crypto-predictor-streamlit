import requests
import pandas as pd
import streamlit as st
import logging
from students.ethereum.constants import COINGECKO_API_URL, COINGECKO_API_KEY, CRYPTONEWS_API_URL, CRYPTONEWS_API_KEY, PREDICTOR_API_URL

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class CryptoForecastApi:
    """
    Wrapper class for fetching cryptocurrency price predictions from the ML prediction API.
    
    This class provides methods to interact with the FastAPI prediction service that uses
    machine learning models to predict next-day high prices for cryptocurrencies.
    
    Attributes:
        session (requests.Session): HTTP session for making API requests.
        base_url (str): Base URL of the prediction API service.
    
    Example:
        ```python
        api = CryptoForecastApi()
        prediction = api.fetch_price_prediction("ETH")
        if "error" not in prediction:
            print(f"Predicted price: ${prediction['next_day_high_predicted']}")
        ```
    """

    def __init__(self):
        """
        Initialize the CryptoForecastApi instance.
        
        Creates a new requests Session and sets the base URL from constants.
        """
        self.session = requests.Session()
        self.base_url = PREDICTOR_API_URL

    @st.cache_data(ttl=600)
    def fetch_price_prediction(_self, _coin_id: str = "ETH", force_refresh_key: float = 0) -> dict:
        """
        Fetch the next-day high price prediction for a specific cryptocurrency.

        This method calls the ML prediction API to get a forecast of the next day's
        high price for the specified cryptocurrency. Results are cached for 10 minutes
        to reduce API calls.

        Args:
            _coin_id (str): The cryptocurrency symbol/ID. Defaults to "ETH".
                           Currently supported: "ETH" (Ethereum).
            force_refresh_key (float): A key to force refresh the cached data.
                                      Changing this value will bypass the cache.
                                      Defaults to 0.

        Returns:
            dict: A dictionary containing prediction data or error information.
                  On success (200), returns a dict with keys:
                  - next_day_high_predicted (float): Predicted high price
                  - next_day_high_date (str): Date of the prediction
                  - model (str): Name of the ML model used
                  On error, returns a dict with:
                  - error (str): Error type/message

        Handles all possible FastAPI response codes:
            - 200: Success → returns prediction dictionary
            - 400: Invalid token → returns {"error": "Invalid token"}
            - 422: Validation error → returns {"error": "Validation error"}
            - 500: Internal server/model error → returns {"error": "Model error"}
            - 503: API unavailable (CoinGecko fetch failed) → returns {"error": "External API unavailable"}

        Raises:
            Does not raise exceptions; all errors are caught and returned as error dicts.

        Example:
            ```python
            api = CryptoForecastApi()
            # Normal usage
            result = api.fetch_price_prediction("ETH")
            
            # Force refresh cache
            result = api.fetch_price_prediction("ETH", force_refresh_key=1.0)
            
            # Check for errors
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Prediction: ${result['next_day_high_predicted']}")
            ```
        """
        logger.info(f"Fetching price prediction for {_coin_id}")
        endpoint = f"{_self.base_url}/predict/{_coin_id}"

        try:
            response = _self.session.get(endpoint, timeout=30)
            data = response.json() if response.content else {}

            # === Handle specific API status codes ===
            if response.status_code == 200:
                logger.info(f"Successfully fetched price prediction for {_coin_id}")
                return data

            elif response.status_code == 400:
                logger.warning(f"Invalid token for {_coin_id}")
                st.error("🚫 Invalid token or unsupported cryptocurrency. Please use 'ETH'.")
                return {"error": "Invalid token"}

            elif response.status_code == 422:
                logger.warning(f"Validation error for {_coin_id}")
                st.warning("⚠️ Validation error — please check input parameters.")
                if "detail" in data:
                    st.caption(f"Details: {data['detail']}")
                return {"error": "Validation error"}

            elif response.status_code == 500:
                logger.error(f"Internal server error for {_coin_id}")
                st.error("💥 Internal server error during model prediction. Please try again later.")
                if "detail" in data:
                    st.caption(f"Details: {data['detail']}")
                return {"error": "Model error"}

            elif response.status_code == 503:
                logger.warning(f"Service unavailable for {_coin_id}")
                if "detail" in data:
                    st.warning(f"🌐 {data['detail']}")
                else:
                    st.warning("🌐 Service unavailable — failed to fetch data from CoinGecko. Try again in 1 or 2 minutes.")
                return {"error": "External API unavailable"}

            else:
                logger.error(f"Unexpected status {response.status_code} for {_coin_id}")
                st.error(f"❓ Unexpected response ({response.status_code}). Please try again later.")
                return {"error": f"Unexpected status {response.status_code}"}

        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching prediction for {_coin_id}")
            st.error("⏰ Request timed out. Please check your internet connection or try again later.")
            return {"error": "Timeout"}

        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error fetching prediction for {_coin_id}")
            st.error("🌐 Connection error — unable to reach the prediction server.")
            return {"error": "Connection error"}

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching prediction for {_coin_id}: {e}")
            st.error(f"🚨 Network error: {e}")
            return {"error": "Network error"}

        except Exception as e:
            logger.error(f"Unexpected error fetching price prediction for {_coin_id}: {e}")
            st.error(f"❌ Unexpected error fetching price prediction for {_coin_id}: {e}")
            return {"error": "Unknown error"}

class CoinGeckoApi:
    """
    Wrapper class for fetching cryptocurrency data from the CoinGecko API.
    
    This class provides methods to interact with the CoinGecko API to fetch:
    - OHLC (Open, High, Low, Close) price data
    - Detailed coin information and metadata
    
    Attributes:
        session (requests.Session): HTTP session for making API requests.
        base_url (str): Base URL of the CoinGecko API.
    
    Example:
        ```python
        api = CoinGeckoApi()
        # Fetch OHLC data
        ohlc = api.fetch_ohlc_data("ethereum", days=7)
        # Fetch coin info
        info = api.fetch_coin_info("ethereum")
        ```
    """

    def __init__(self):
        """
        Initialize the CoinGeckoApi instance.
        
        Creates a new requests Session and sets the base URL from constants.
        """
        self.session = requests.Session()
        self.base_url = COINGECKO_API_URL

    @staticmethod
    def handle_api_error(response, coin_id, context):
        """
        Handle common CoinGecko API errors with user-friendly Streamlit messages.
        
        This static method processes HTTP errors from the CoinGecko API and displays
        appropriate error messages to the user via Streamlit.
        
        Args:
            response (requests.Response | None): The HTTP response object that caused
                                                the error, or None if no response available.
            coin_id (str): The cryptocurrency ID that was being queried.
            context (str): A description of what operation was being performed
                         (e.g., "OHLC data", "coin info").
        
        Note:
            This method displays warnings/errors directly using Streamlit's st.warning()
            and st.error() functions. It also logs errors using the module logger.
        
        Example:
            ```python
            try:
                response = session.get(url)
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                CoinGeckoApi.handle_api_error(response, "ethereum", "OHLC data")
            ```
        """
        if response is not None and hasattr(response, "status_code"):
            if response.status_code == 429:
                logger.warning(f"Rate limit reached for {context} of {coin_id}")
                st.warning("⚠️ Rate limit reached. Please wait a few seconds before trying again.")
            elif response.status_code >= 500:
                logger.error(f"Server error from CoinGecko for {context} of {coin_id}")
                st.error("🚨 Server error from CoinGecko. Try again later.")
            else:
                logger.error(f"HTTP {response.status_code} error for {context} of {coin_id}")
                st.error(f"HTTP {response.status_code} error while fetching {context} for {coin_id}.")
        else:
            logger.error(f"Unexpected network error for {context} of {coin_id}")
            st.error(f"Unexpected network error while fetching {context} for {coin_id}.")

    @st.cache_data
    def fetch_ohlc_data(_self, _coin_id: str, _vs_currency: str = "usd", days: int = 30) -> pd.DataFrame:
        """
        Fetch OHLC (Open, High, Low, Close) data from the CoinGecko API.

        Retrieves historical price data for a cryptocurrency in OHLC format.
        Results are cached using Streamlit's cache to optimize API calls.

        Args:
            _coin_id (str): CoinGecko ID of the cryptocurrency.
                          Examples: 'bitcoin', 'ethereum', 'solana', 'ripple'.
            _vs_currency (str): The target currency to compare against.
                              Defaults to 'usd'. Other options include 'eur', 'gbp', etc.
            days (int): Number of past days to fetch. Valid options are:
                      1, 7, 14, 30, 90, 180, 365, or 'max' for maximum available.
                      Defaults to 30.

        Returns:
            pd.DataFrame: A DataFrame containing OHLC data with columns:
                - timestamp (datetime): Date and time of the data point
                - open (float): Opening price
                - high (float): Highest price of the period
                - low (float): Lowest price of the period
                - close (float): Closing price
                
                Returns an empty DataFrame if:
                - No data is available
                - API request fails
                - Network error occurs

        Raises:
            Does not raise exceptions; all errors are caught and handled.
            Returns empty DataFrame on error.

        Note:
            Data is sorted chronologically by timestamp in ascending order.

        Example:
            ```python
            api = CoinGeckoApi()
            # Fetch 7 days of OHLC data
            df = api.fetch_ohlc_data("ethereum", days=7)
            
            if not df.empty:
                print(f"Latest close price: ${df.iloc[-1]['close']}")
                print(f"Highest price: ${df['high'].max()}")
            ```
        """
        logger.info(f"Fetching OHLC data for {_coin_id}, vs_currency {_vs_currency}, days {days}")
        endpoint = f"{_self.base_url}/coins/{_coin_id}/ohlc"
        params = {"vs_currency": _vs_currency, "days": days}
        headers = {
            "x-cg-demo-api-key": COINGECKO_API_KEY
        }

        try:
            response = _self.session.get(endpoint, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Validate and convert data
            if not isinstance(data, list) or len(data) == 0:
                st.warning(f"No OHLC data returned for {_coin_id}.")
                return pd.DataFrame()

            df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df = df.sort_values("timestamp").reset_index(drop=True)

            logger.info(f"Successfully fetched OHLC data for {_coin_id}")
            return df

        except requests.exceptions.HTTPError:
            logger.error(f"HTTP error fetching OHLC data for {_coin_id}: {response.status_code}")
            _self.handle_api_error(response, _coin_id, "OHLC data")
            return pd.DataFrame()

        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching OHLC data for {_coin_id}")
            st.error("⏰ Request timed out. Please check your connection or try again later.")
            return pd.DataFrame()

        except requests.exceptions.RequestException:
            logger.error(f"Request exception fetching OHLC data for {_coin_id}")
            _self.handle_api_error(None, _coin_id, "OHLC data")
            return pd.DataFrame()

        except Exception as e:
            logger.error(f"Unexpected error fetching OHLC data for {_coin_id}: {e}")
            st.error(f"Unexpected error fetching OHLC data for {_coin_id}: {e}")
            return pd.DataFrame()


    @st.cache_data
    def fetch_coin_info(_self, _coin_id: str) -> dict:
        """
        Fetch detailed coin information and metadata from the CoinGecko API.

        Retrieves comprehensive information about a cryptocurrency including
        current market data, description, links, and technical details.
        Results are cached using Streamlit's cache to optimize API calls.

        Args:
            _coin_id (str): CoinGecko ID of the cryptocurrency.
                          Examples: 'bitcoin', 'ethereum', 'solana', 'ripple'.

        Returns:
            dict: A dictionary containing coin metadata with the following keys:
                - name (str): Full name of the cryptocurrency
                - symbol (str): Ticker symbol (e.g., 'eth')
                - hashing_algorithm (str): Algorithm used (e.g., 'Ethash')
                - categories (list): List of categories the coin belongs to
                - description (str): English description of the cryptocurrency
                - homepage (str): Official website URL
                - blockchain_site (str): Blockchain explorer URL
                - current_price (float): Current price in USD
                - market_cap (float): Market capitalization in USD
                - total_volume (float): 24h trading volume in USD
                - last_updated (str): ISO timestamp of last data update
                
                Returns an empty dictionary ({}) if:
                - API request fails
                - Network error occurs
                - Invalid coin_id provided

        Raises:
            Does not raise exceptions; all errors are caught and handled.
            Returns empty dict on error.

        Example:
            ```python
            api = CoinGeckoApi()
            info = api.fetch_coin_info("ethereum")
            
            if info:
                print(f"Name: {info['name']}")
                print(f"Current Price: ${info['current_price']}")
                print(f"Market Cap: ${info['market_cap']:,}")
            ```
        """
        logger.info(f"Fetching coin info for {_coin_id}")
        endpoint = f"{_self.base_url}/coins/{_coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false"
        }
        headers = {
            "x-cg-demo-api-key": COINGECKO_API_KEY
        }

        try:
            response = _self.session.get(endpoint, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            info = {
                "name": data.get("name"),
                "symbol": data.get("symbol"),
                "hashing_algorithm": data.get("hashing_algorithm"),
                "categories": data.get("categories"),
                "description": data.get("description", {}).get("en"),
                "homepage": data.get("links", {}).get("homepage", [None])[0],
                "blockchain_site": data.get("links", {}).get("blockchain_site", [None])[0],
                "current_price": data.get("market_data", {}).get("current_price", {}).get("usd"),
                "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd"),
                "total_volume": data.get("market_data", {}).get("total_volume", {}).get("usd"),
                "last_updated": data.get("market_data", {}).get("last_updated", None),
            }
            logger.info(f"Successfully fetched coin info for {_coin_id}")
            return info

        except requests.exceptions.HTTPError:
            logger.error(f"HTTP error fetching coin info for {_coin_id}: {response.status_code}")
            _self.handle_api_error(response, _coin_id, "coin info")
            return {}

        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching coin info for {_coin_id}")
            st.error("⏰ Request timed out. Please check your connection or try again later.")
            return {}

        except requests.exceptions.RequestException:
            logger.error(f"Request exception fetching coin info for {_coin_id}")
            _self.handle_api_error(None, _coin_id, "coin info")
            return {}

        except Exception as e:
            logger.error(f"Unexpected error fetching coin info for {_coin_id}: {e}")
            st.error(f"Unexpected error fetching coin info for {_coin_id}: {e}")
            return {}

class CryptoNewsApi:
    """
    Wrapper class for fetching cryptocurrency news data from the CryptoNews API.
    
    This class provides methods to retrieve the latest news articles related to
    specific cryptocurrencies. News data is cached for 1 hour to reduce API calls.
    
    Attributes:
        base_url (str): Base URL of the CryptoNews API.
        session (requests.Session): HTTP session for making API requests.
    
    Example:
        ```python
        api = CryptoNewsApi()
        news = api.fetch_latest_news("ETH", limit=10)
        for article in news.itertuples():
            print(f"{article.title}: {article.url}")
        ```
    """

    def __init__(self):
        """
        Initialize the CryptoNewsApi instance.
        
        Creates a new requests Session and sets the base URL from constants.
        """
        self.base_url = CRYPTONEWS_API_URL
        self.session = requests.Session()

    @st.cache_data(ttl=3600)
    def fetch_latest_news(_self, coin_id: str = "ETH", lang: str = "EN", limit: int = 10) -> pd.DataFrame:
        """
        Fetch the latest cryptocurrency news articles safely.

        Retrieves news articles related to the specified cryptocurrency from the
        CryptoNews API. Results are cached for 1 hour to optimize API calls.
        Handles API errors gracefully and always returns a DataFrame (empty on error).

        Args:
            coin_id (str): The cryptocurrency symbol/ID to search for in article titles.
                         Defaults to "ETH" (Ethereum). Examples: "BTC", "ETH", "SOL".
            lang (str): Language code for articles. Defaults to "EN" (English).
                       Other options: "ES", "FR", "DE", etc.
            limit (int): Maximum number of news articles to fetch. Defaults to 10.

        Returns:
            pd.DataFrame: A DataFrame containing news articles with columns:
                - id (str): Unique article identifier
                - source (str): News source name
                - title (str): Article title
                - body (str): Article description/body text
                - url (str): Link to the full article
                - published_on (datetime): Publication date and time
                - tags (str/list): Article keywords/tags
                
                Returns an empty DataFrame if:
                - No articles are found
                - API request fails
                - Network error occurs
                - Invalid API response format

        Raises:
            Does not raise exceptions; all errors are caught and handled.
            Returns empty DataFrame on error.

        Note:
            Articles are sorted by publication date in descending order (newest first).
            Datetime parsing errors are handled gracefully using pandas' errors='coerce'.

        Example:
            ```python
            api = CryptoNewsApi()
            # Fetch latest Ethereum news
            news = api.fetch_latest_news("ETH", limit=5)
            
            if not news.empty:
                for idx, row in news.iterrows():
                    print(f"{row['title']} - {row['url']}")
            else:
                print("No news articles found")
            ```
        """
        logger.info(f"Fetching latest news for {coin_id}, lang {lang}, limit {limit}")
        endpoint = f"{_self.base_url}/crypto"
        params = {
            "apikey": CRYPTONEWS_API_KEY,
            "language": lang.lower(),
            "size": limit,
            "qInTitle": coin_id
        }

        try:
            response = _self.session.get(endpoint, params=params, timeout=30)

            # Handle non-200 responses gracefully
            if response.status_code != 200:
                logger.warning(f"News API returned status {response.status_code} for {coin_id}")
                st.warning(f"⚠️ News API returned status {response.status_code}. Showing fallback data.")
                return pd.DataFrame()

            data = response.json()

            if "results" not in data or not data["results"]:
                logger.info(f"No news articles available for {coin_id}")
                st.info("ℹ️ No news articles available for this cryptocurrency.")
                return pd.DataFrame()

            df = pd.DataFrame(data["results"])

            column_mapping = {
                "article_id": "id",
                "source_id": "source",
                "title": "title",
                "description": "body",
                "link": "url",
                "pubDate": "published_on",
                "keywords": "tags",
            }
            df = df.rename(columns=column_mapping)

            expected_cols = ["id", "source", "title", "body", "url", "published_on", "tags"]
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = None

            # Safe datetime conversion
            df["published_on"] = pd.to_datetime(df["published_on"], errors="coerce")
            df = df.sort_values("published_on", ascending=False, na_position="last").reset_index(drop=True)

            logger.info(f"Successfully fetched {len(df)} news articles for {coin_id}")
            return df

        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching news for {coin_id}")
            st.error("⏰ The request to the news API timed out. Please try again later.")
            return pd.DataFrame()

        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error fetching news for {coin_id}")
            st.error("🌐 Connection error: Unable to reach the news service.")
            return pd.DataFrame()

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching news for {coin_id}: {e}")
            st.error(f"🚫 Unexpected network error: {e}")
            return pd.DataFrame()

        except ValueError as e:
            logger.error(f"Invalid data format fetching news for {coin_id}: {e}")
            st.error(f"⚠️ Invalid data format received from API: {e}")
            return pd.DataFrame()

        except Exception as e:
            logger.error(f"Unexpected error fetching news for {coin_id}: {e}")
            st.error(f"❌ Unexpected error fetching news: {e}")
            return pd.DataFrame()