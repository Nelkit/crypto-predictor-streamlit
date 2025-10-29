import streamlit as st
import students.ethereum.components.sidebar as sidebar
import students.ethereum.components.content as content
from students.ethereum.controller import (
    fetch_ethereum_daily_data,
    fetch_ethereum_info,
    fetch_ethereum_ohlc,
    fetch_ethereum_related_news,
    fetch_ethereum_forecast,
)

from importlib import reload
reload(sidebar)
reload(content)

def render_tab():
    sidebar_col, main_col = st.columns([1, 3], vertical_alignment="top")
    selected_days = st.session_state.get("selected_period", 7)

    # Fetch daily data
    daily_df = fetch_ethereum_daily_data(days=selected_days)
    if daily_df.empty:
        latest_row = None
    else:
        latest_row = daily_df.iloc[-1]

    # Fetch coin metadata and OHLC data
    coin_metadata = fetch_ethereum_info()

    # Fetch OHLC data for the selected period
    ohlc_df = fetch_ethereum_ohlc(days=selected_days)

    # fetch latest news (not used in this view but could be integrated later)
    news_df = fetch_ethereum_related_news(limit=10)

    #fetch High next day price prediction data (not used in this view but could be integrated later)
    forecast_data = fetch_ethereum_forecast(days=selected_days)


    with sidebar_col:
        sidebar.render_view(latest_row, coin_metadata, forecast_data)
    with main_col:
        content.render_view(coin_metadata, ohlc_df, daily_df, news_df)