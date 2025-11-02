from students.ethereum.api import CoinGeckoApi, CryptoNewsApi, CryptoForecastApi
import pandas as pd

def fetch_ethereum_ohlc(coin_id: str = "ethereum", days: int = 7) -> pd.DataFrame:
    """
    Fetches OHLC (Open, High, Low, Close) data for Ethereum from the CoinGecko API.

    Args:
        coin_id (str, optional): The CoinGecko ID for the cryptocurrency. Defaults to "ethereum".
        days (int, optional): Number of past days to fetch data for. Defaults to 7.

    Returns:
        pd.DataFrame: A DataFrame containing OHLC data with columns like timestamp, open, high, low, close.
    """
    api = CoinGeckoApi()
    ohlc_data = api.fetch_ohlc_data(coin_id, days=days)
    return ohlc_data

def fetch_ethereum_info() -> dict:
    """
    Fetches metadata for Ethereum from the CoinGecko API.

    This includes information like current price, market cap, volume, description, etc.

    Returns:
        dict: A dictionary containing Ethereum metadata.
    """
    api = CoinGeckoApi()
    metadata = api.fetch_coin_info("ethereum")
    return metadata

def fetch_ethereum_related_news(limit) -> pd.DataFrame:
    """
    Fetches news related to Ethereum from the CryptoNews API.

    Args:
        limit (int): The maximum number of news articles to fetch.

    Returns:
        pd.DataFrame: A DataFrame containing news articles with columns like title, body, url, published_on, etc.
    """
    api = CryptoNewsApi()
    news = api.fetch_latest_news(coin_id="ETH",limit=limit)
    return news

def fetch_ethereum_forecast(coin_id: str = "ETH", force_refresh_key = 0) -> dict:
    """
    Fetches forecast data for Ethereum from the forecast API.

    Args:
        coin_id (str, optional): The cryptocurrency ID. Defaults to "ETH".
        force_refresh_key: A key to force refresh the cached data.

    Returns:
        dict: A dictionary containing forecast data, such as next-day high prediction.
    """
    api = CryptoForecastApi()
    forecast_data = api.fetch_price_prediction(coin_id, force_refresh_key)
    return forecast_data