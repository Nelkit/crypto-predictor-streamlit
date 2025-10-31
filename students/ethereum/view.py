import streamlit as st
import students.ethereum.components.sidebar as sidebar
import students.ethereum.components.content as content
from students.ethereum.controller import (
    fetch_ethereum_ohlc,
    fetch_ethereum_info,
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


    with sidebar_col:
        sidebar.render_view(latest_row, coin_metadata)
    with main_col:
        content.render_view(ohlc_df, coin_metadata)