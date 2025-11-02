import streamlit as st
import pandas as pd
from random import random
from students.ethereum.utils.helpers import (
    format_iso_date,
    format_currency_short
)
from students.ethereum.controller import fetch_ethereum_forecast

def render_view(latest_row: pd.Series, metadata: dict = None):
    """
    Renders the Ethereum forecast stats section in the sidebar.

    This function displays the next-day high price prediction, current price,
    and 24-hour market performance metrics for Ethereum. It fetches forecast
    data from the controller and handles error states gracefully.

    Args:
        latest_row (pd.Series): The latest OHLC data row for Ethereum, containing
            high, low, open, close values.
        metadata (dict, optional): Dictionary with market data such as current_price,
            market_cap, total_volume, and last_updated timestamp. Defaults to None.

    Returns:
        None: This function renders UI elements directly using Streamlit.
    """

    current_price = metadata.get("current_price", 0)
    market_cap = metadata.get("market_cap", 0)
    volume = metadata.get("total_volume", 0)
    last_updated = metadata.get("last_updated", "N/A")
    formatted_last_updated = format_iso_date(last_updated)

    prediction_col, ohlc_col = st.columns([3, 2], vertical_alignment="top")

    # === Prediction Section ===
    with prediction_col:
        st.markdown("**🎯 Overview & Next-Day Forecast**")
        with st.container(border=True):

            if "refresh_prediction_request" not in st.session_state:
                st.session_state["refresh_prediction_request"] = 0.0

            with st.spinner("Fetching latest forecast..."):
                forecast_data = fetch_ethereum_forecast(
                    coin_id="ETH",
                    force_refresh_key=st.session_state["refresh_prediction_request"],
                )

                predicted_price = float(forecast_data.get("next_day_high_predicted", 0))
                predicted_date = forecast_data.get("next_day_high_date", "N/A")
                model_name = forecast_data.get("model", "N/A")

                request_failed = (
                    not forecast_data
                    or "error" in forecast_data
                    or predicted_price == 0
                )

                if request_failed:
                    st.write(f"📈 Next-Day High Forecast")

                    st.error("Forecast unavailable. Retry below.")
                    refresh = st.button("🔄 Retry Forecast", use_container_width=True)
                    if refresh:
                        st.session_state["refresh_prediction_request"] = random()
                        st.toast("Fetching new forecast...", icon="⏳")
                        st.rerun()
                else:
                    if current_price > 0:
                        predicted_change = ((predicted_price - current_price) / current_price) * 100
                    else:
                        predicted_change = 0.0

                    st.markdown(
                        f"<p style='margin-bottom:-150px; font-size:1.1rem;'>📈 Next-Day High Forecast ({predicted_date})</p>",
                        unsafe_allow_html=True
                    )

                    st.metric(
                        label="-",  # evita espacio extra
                        value=f"${predicted_price:,.2f}",
                        delta=f"{predicted_change:+.2f}%",
                    )

                    st.caption(f"Prediction powered by {model_name}.")

        st.metric(f"💰 Current Price (USD) | {formatted_last_updated}", f"${current_price:,.2f}", border=True)

    # === OHCL Market Performance Section ===
    with ohlc_col:
        st.markdown("**🏦 Market Performance (Last 24h)**")

        if latest_row is None or not isinstance(latest_row, pd.Series):
            high_value = low_value = open_value = close_value = volume_value = market_cap_value = 0.0
        else:
            high_value = latest_row.get("high", 0.0)
            low_value = latest_row.get("low", 0.0)
            open_value = latest_row.get("open", 0.0)
            close_value = latest_row.get("close", 0.0)
            volume_value = volume
            market_cap_value = market_cap

        stats = {
            "24h High": high_value,
            "24h Low": low_value,
            "24h Open": open_value,
            "24h Close": close_value,
            "24h Volume": format_currency_short(volume_value),
            "Market Cap": format_currency_short(market_cap_value),
        }

        cols = st.columns(2)
        for i, (label, value) in enumerate(stats.items()):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(
                        f"<div style='text-align:center; opacity:0.9; padding-bottom:1rem;'>"
                        f"<p style='margin:0; font-size:1rem; color:gray;'>{label}</p>"
                        f"<p style='margin:0; font-weight:600; font-size:1.2rem;'>${value}</p>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
