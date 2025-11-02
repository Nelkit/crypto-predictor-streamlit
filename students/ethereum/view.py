import streamlit as st
from students.ethereum.constants import ETH_LOGO
from students.ethereum.controller import (
    fetch_ethereum_ohlc,
    fetch_ethereum_info,
)
from students.ethereum.components import (
    forecast_stats,
    chart,
    historical_data,
    news,
    about,
)

# Reload modules to reflect any changes during development
from importlib import reload
reload(forecast_stats)
reload(chart)
reload(historical_data)
reload(news)
reload(about)


def render_header(coin_name, coin_symbol):
    """
    Renders the header section with coin name and logo.

    This function displays an HTML header with the Ethereum logo, coin name, and symbol.

    Args:
        coin_name (str): The name of the cryptocurrency (e.g., "Ethereum").
        coin_symbol (str): The symbol of the cryptocurrency (e.g., "ETH").

    Returns:
        None: This function renders UI elements directly using Streamlit.
    """
    st.markdown(
        f"""
        <h1 style='margin-bottom:0.2rem; font-size:2rem;'>
            <img src="{ETH_LOGO}" width="60" style="vertical-align:middle; margin-right:4px;"/>
            {coin_name} <small style="color:grey;">({coin_symbol})</small>
        </h1>
        """,
        unsafe_allow_html=True,
    )


def render_view():
    """
    Renders the Ethereum page view.

    This function fetches OHLC data and coin metadata, renders the header,
    and displays tabs for forecast stats, chart, historical data, news, and about sections.

    Returns:
        None: This function renders UI elements directly using Streamlit.
    """
    selected_days = st.session_state.get("selected_period", 7)

    # Fetch daily data
    ohlc_df = fetch_ethereum_ohlc(days=selected_days)
    if ohlc_df.empty:
        latest_row = None
    else:
        latest_row = ohlc_df.iloc[-1]

    # Fetch coin metadata
    coin_metadata = fetch_ethereum_info()

    coin_name = coin_metadata.get("name", "Unknown")
    coin_symbol = coin_metadata.get("symbol", "N/A").upper()

    # --- Header ---
    render_header(coin_name, coin_symbol)

    # --- Main Content ---
    with st.container(horizontal_alignment="center"):

        tabs = st.tabs([
            "📈 Trend & Forecast",
            "📉 Price History (OHLC)",
            "📰 Market News",
            "📘 Cryptocurrency Overview",
        ])
        with tabs[0]:
            forecast_stats.render_view(latest_row, coin_metadata)
            chart.render_view("📈 Price Trend Analysis", ohlc_df)
        with tabs[1]:
            historical_data.render_view("📉 Price History (OHLC)", ohlc_df)
        with tabs[2]:
            news.render_view("📰 Market News")
        with tabs[3]:
            about.render_view("📘 Cryptocurrency Overview", coin_metadata)
