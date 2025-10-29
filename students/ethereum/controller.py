from students.ethereum.api import CoinGeckoApi, CryptoNewsApi, CryptoForecastApi
import pandas as pd

def fetch_ethereum_daily_data(coin_id: str = "ethereum", days: int = 7) -> pd.DataFrame:
    api = CoinGeckoApi()
    ohlc_data = api.fetch_merged_daily_data(coin_id, days=days)
    return ohlc_data

def fetch_ethereum_info() -> dict:
    api = CoinGeckoApi()
    metadata = api.fetch_coin_info("ethereum")
    return metadata

def fetch_ethereum_ohlc(coin_id: str = "ethereum", days = 7) -> pd.DataFrame:
    api = CoinGeckoApi()
    ohlc_data = api.fetch_ohlc_data(coin_id, days=days)
    return ohlc_data

def fetch_ethereum_related_news(limit) -> pd.DataFrame:
    api = CryptoNewsApi()
    news = api.fetch_latest_news(coin_id="ETH",limit=limit)
    return news

def fetch_ethereum_forecast(coin_id: str = "ETH", days: int = 7) -> dict:
    api = CryptoForecastApi()
    forecast_data = api.fetch_price_prediction(coin_id)
    return forecast_data