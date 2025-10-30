import streamlit as st
import students.ethereum.components.sidebar as sidebar
import students.ethereum.components.content as content
from students.ethereum.controller import (
    fetch_ethereum_ohlc,
    fetch_ethereum_info,
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
    ohlc_df = fetch_ethereum_ohlc(days=selected_days)
    if ohlc_df.empty:
        latest_row = None
    else:
        latest_row = ohlc_df.iloc[-1]

    # Fetch coin metadata
    coin_metadata = fetch_ethereum_info()

    # fetch latest news (not used in this view but could be integrated later)
    news_df = fetch_ethereum_related_news(limit=10)

    #fetch High next day price prediction data (not used in this view but could be integrated later)
    forecast_data = fetch_ethereum_forecast(days=selected_days)


    with sidebar_col:
        sidebar.render_view(latest_row, coin_metadata, forecast_data)
    with main_col:
        content.render_view(coin_metadata, ohlc_df, news_df)