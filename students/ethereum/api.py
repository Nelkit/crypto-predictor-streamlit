import requests
import pandas as pd
import streamlit as st
from students.ethereum.constants import COINGECKO_API_URL, CRYPTONEWS_API_URL, CRYPTONEWS_API_KEY, PREDICTOR_API_URL

class CryptoForecastApi:
    """Wrapper class for fetching cryptocurrency price predictions."""

    def __init__(self):
        self.session = requests.Session()
        self.base_url = PREDICTOR_API_URL

    @st.cache_data
    def fetch_price_prediction(_self, coin_id: str = "ETH") -> dict:
        """Fetch price prediction for a specific cryptocurrency."""
        endpoint = f"{_self.base_url}/predict/{coin_id}"

        try:
            response = _self.session.get(endpoint, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data

        except requests.exceptions.HTTPError:
            st.error(f"HTTP {response.status_code} error while fetching price prediction for {coin_id}.")
            return {}

        except requests.exceptions.Timeout:
            st.error("⏰ Request timed out. Please check your connection or try again later.")
            return {}

        except requests.exceptions.RequestException:
            st.error(f"Unexpected network error while fetching price prediction for {coin_id}.")
            return {}

        except Exception as e:
            st.error(f"Unexpected error fetching price prediction for {coin_id}: {e}")
            return {}

class CoinGeckoApi:
    """Wrapper class for fetching cryptocurrency data from the CoinGecko API."""

    def __init__(self):
        self.session = requests.Session()
        self.base_url = COINGECKO_API_URL

    # --- Helper para manejo de errores uniforme ---
    @staticmethod
    def handle_api_error(response, coin_id, context):
        """Handle common API errors with user-friendly messages."""
        if response is not None and hasattr(response, "status_code"):
            if response.status_code == 429:
                st.warning("⚠️ Rate limit reached. Please wait a few seconds before trying again.")
            elif response.status_code >= 500:
                st.error("🚨 Server error from CoinGecko. Try again later.")
            else:
                st.error(f"HTTP {response.status_code} error while fetching {context} for {coin_id}.")
        else:
            st.error(f"Unexpected network error while fetching {context} for {coin_id}.")

    # --- Fetch merged daily data ---
    @st.cache_data
    def fetch_merged_daily_data(_self, _coin_id: str, _vs_currency: str = "usd",
                                days: int = 30, _interval: str = "daily") -> pd.DataFrame:
        """
        Fetch daily market data for a specific coin using the /market_chart endpoint.
        Derives OHLC from price data, and merges with volume and market cap.
        """
        endpoint = f"{_self.base_url}/coins/{_coin_id}/market_chart"
        params = {"vs_currency": _vs_currency, "days": days, "interval": _interval}

        try:
            response = _self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # === Parse datasets ===
            prices = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
            market_caps = pd.DataFrame(data["market_caps"], columns=["timestamp", "market_cap"])
            volumes = pd.DataFrame(data["total_volumes"], columns=["timestamp", "volume"])

            # === Convert timestamps ===
            prices["timestamp"] = pd.to_datetime(prices["timestamp"], unit="ms")
            market_caps["timestamp"] = pd.to_datetime(market_caps["timestamp"], unit="ms")
            volumes["timestamp"] = pd.to_datetime(volumes["timestamp"], unit="ms")

            # === Derive OHLC ===
            prices["date"] = prices["timestamp"].dt.date
            ohlc = (
                prices.groupby("date")["price"]
                .agg(open="first", high="max", low="min", close="last")
                .reset_index()
            )
            ohlc["timestamp"] = pd.to_datetime(ohlc["date"])
            ohlc.drop(columns="date", inplace=True)

            # === Merge datasets ===
            df = ohlc.merge(market_caps, on="timestamp", how="inner")
            df = df.merge(volumes, on="timestamp", how="inner")
            df = df.sort_values("timestamp").reset_index(drop=True)

            return df

        except requests.exceptions.HTTPError:
            _self.handle_api_error(response, _coin_id, "merged daily data")
            return pd.DataFrame()

        except requests.exceptions.Timeout:
            st.error("⏰ Request timed out. Please check your connection or try again later.")
            return pd.DataFrame()

        except requests.exceptions.RequestException:
            _self.handle_api_error(None, _coin_id, "merged daily data")
            return pd.DataFrame()

        except Exception as e:
            st.error(f"Unexpected error fetching merged daily data for {_coin_id}: {e}")
            return pd.DataFrame()

    # --- Fetch OHLC data ---
    @st.cache_data
    def fetch_ohlc_data(_self, _coin_id: str, _vs_currency: str = "usd", days=30):
        """Fetch OHLC data directly from /coins/{id}/ohlc endpoint."""
        endpoint = f"{_self.base_url}/coins/{_coin_id}/ohlc"
        params = {"vs_currency": _vs_currency, "days": days}

        try:
            response = _self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            return df

        except requests.exceptions.HTTPError:
            _self.handle_api_error(response, _coin_id, "OHLC data")
            return pd.DataFrame()

        except requests.exceptions.Timeout:
            st.error("⏰ Request timed out. Please check your connection or try again later.")
            return pd.DataFrame()

        except requests.exceptions.RequestException:
            _self.handle_api_error(None, _coin_id, "OHLC data")
            return pd.DataFrame()

        except Exception as e:
            st.error(f"Unexpected error fetching OHLC data for {_coin_id}: {e}")
            return pd.DataFrame()

    # --- Fetch coin info ---
    @st.cache_data
    def fetch_coin_info(_self, _coin_id: str) -> dict:
        """Fetch detailed information about a specific cryptocurrency."""
        endpoint = f"{_self.base_url}/coins/{_coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false"
        }

        try:
            response = _self.session.get(endpoint, params=params, timeout=30)
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
            return info

        except requests.exceptions.HTTPError:
            _self.handle_api_error(response, _coin_id, "coin info")
            return {}

        except requests.exceptions.Timeout:
            st.error("⏰ Request timed out. Please check your connection or try again later.")
            return {}

        except requests.exceptions.RequestException:
            _self.handle_api_error(None, _coin_id, "coin info")
            return {}

        except Exception as e:
            st.error(f"Unexpected error fetching coin info for {_coin_id}: {e}")
            return {}

class CryptoNewsApi:
    """Wrapper class for fetching cryptocurrency news data."""

    def __init__(self):
        # CryptoCompare News API base URL
        self.base_url = CRYPTONEWS_API_URL
        self.session = requests.Session()

    @st.cache_data
    def fetch_latest_news(_self, coin_id: str = "ETH", lang: str = "EN", limit: int = 10) -> pd.DataFrame:
        """
        Fetch the latest cryptocurrency news using a NewsData-like API.
        Returns only articles whose titles contain the given categories (e.g. 'Ethereum').
        """
        endpoint = f"{_self.base_url}/crypto"
        params = {
            "apikey": CRYPTONEWS_API_KEY,
            "language": lang.lower(),
            "size": limit,
            "coin": coin_id
        }

        try:
            response = _self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if "results" not in data:
                raise ValueError("No 'results' field found in API response")

            results = data["results"]
            if not results:
                return pd.DataFrame()

            # Create DataFrame
            df = pd.DataFrame(results)

            # Map keys to unified column names
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

            # Keep only the relevant columns
            expected_cols = ["id", "source", "title", "body", "url", "published_on", "tags"]
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = None

            df = df[expected_cols]

            # Convert date
            if "published_on" in df.columns:
                df["published_on"] = pd.to_datetime(df["published_on"], errors="coerce")

            # Sort by publication date
            df = df.sort_values("published_on", ascending=False, na_position="last").reset_index(drop=True)

            return df

        except Exception as e:
            raise Exception(f"Failed to fetch latest news: {str(e)}")