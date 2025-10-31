import requests
import pandas as pd
import streamlit as st
import logging
from students.ethereum.constants import COINGECKO_API_URL, COINGECKO_API_KEY, CRYPTONEWS_API_URL, CRYPTONEWS_API_KEY, PREDICTOR_API_URL

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class CryptoForecastApi:
    """Wrapper class for fetching cryptocurrency price predictions from the FastAPI service."""

    def __init__(self):
        self.session = requests.Session()
        self.base_url = PREDICTOR_API_URL

    @st.cache_data(ttl=600)
    def fetch_price_prediction(_self, _coin_id: str = "ETH", force_refresh_key: float = 0) -> dict:
        """
        Fetch the next-day high price prediction for a specific cryptocurrency.

        Handles all possible FastAPI response codes:
        - 200: Success → returns prediction dictionary
        - 400: Invalid token
        - 422: Validation error
        - 500: Internal server/model error
        - 503: API unavailable (CoinGecko fetch failed)
        """
        logger.info(f"Fetching price prediction for {_coin_id}")
        endpoint = f"{_self.base_url}/predict/{_coin_id}"
        print("================= Fetching data from Prediction API =================")

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
    """Wrapper class for fetching cryptocurrency data from the CoinGecko API."""

    def __init__(self):
        self.session = requests.Session()
        self.base_url = COINGECKO_API_URL

    @staticmethod
    def handle_api_error(response, coin_id, context):
        """Handle common API errors with user-friendly messages."""
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

    # --- Fetch fetch ohlc metrics ---
    @st.cache_data(ttl=300)
    def fetch_ohlc_data(_self, _coin_id: str, _vs_currency: str = "usd", days: int = 30) -> pd.DataFrame:
        """
        Fetch OHLC data directly from the CoinGecko /coins/{id}/ohlc endpoint.

        Args:
            _coin_id (str): CoinGecko ID (e.g., 'bitcoin', 'ethereum', 'solana', 'ripple')
            _vs_currency (str): The target currency to compare against (default: 'usd')
            days (int): Number of past days to fetch (valid options: 1, 7, 14, 30, 90, 180, 365, 'max')

        Returns:
            pd.DataFrame: A DataFrame containing timestamp, open, high, low, and close columns.
        """
        logger.info(f"Fetching OHLC data for {_coin_id}, vs_currency {_vs_currency}, days {days}")
        endpoint = f"{_self.base_url}/coins/{_coin_id}/ohlc"
        params = {"vs_currency": _vs_currency, "days": days}
        headers = {
            "x-cg-demo-api-key": COINGECKO_API_KEY
        }
        print("================= Fetching data from CoinGecko API - ohlc =================")

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


    # --- Fetch coin info ---
    @st.cache_data
    def fetch_coin_info(_self, _coin_id: str) -> dict:
        """
        Fetch detailed coin information from the CoinGecko /coins/{id} endpoint.
        Args:
            _coin_id (str): CoinGecko ID (e.g., 'bitcoin', '
        ethereum', 'solana', 'ripple')
        Returns:
            dict: A dictionary containing coin metadata.
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

        print("================= Fetching data from CoinGecko API - coin info =================")

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
    """Wrapper class for fetching cryptocurrency news data."""

    def __init__(self):
        self.base_url = CRYPTONEWS_API_URL
        self.session = requests.Session()

    @st.cache_data(ttl=3600)
    def fetch_latest_news(_self, coin_id: str = "ETH", lang: str = "EN", limit: int = 10) -> pd.DataFrame:
        """
        Fetch the latest cryptocurrency news safely.
        Handles API errors gracefully and always returns a DataFrame.
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