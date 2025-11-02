import streamlit as st
import pandas as pd
from random import random
from students.ethereum.constants import ETH_LOGO
from students.ethereum.controller import fetch_ethereum_forecast


def render_view(latest_row: pd.Series, metadata: dict = None):
    coin_name = metadata.get("name", "Unknown")
    coin_symbol = metadata.get("symbol", "N/A").upper()
    current_price = metadata.get("current_price", 0)
    market_cap = metadata.get("market_cap", 0)
    volume = metadata.get("total_volume", 0)

    # --- Header ---
    st.markdown(
        f"""
        <h1 style='margin-bottom:0.2rem; font-size:1.5rem;'>
            <img src="{ETH_LOGO}" width="40" style="vertical-align:middle; margin-right:4px;"/>
            {coin_name} <small style="color:grey;">({coin_symbol})</small>
        </h1>
        """,
        unsafe_allow_html=True,
    )

    # === Prediction Section ===
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
                    f"<p style='margin-bottom:0rem; font-size:1.1rem;'>📈 Next-Day High Forecast ({predicted_date})</p>",
                    unsafe_allow_html=True
                )

                st.metric(
                    label="-",  # evita espacio extra
                    value=f"${predicted_price:,.2f}",
                    delta=f"{predicted_change:+.2f}%",
                )

                st.caption(f"Prediction powered by {model_name}.")

    st.metric("💰 Current Price (USD)", f"${current_price:,.2f}", border=True)

    # === Market Summary Section ===
    st.markdown("**📊 24h Market Overview**")

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
        "24h Volume": volume_value,
        "Market Cap": market_cap_value,
    }

    cols = st.columns(2)
    for i, (label, value) in enumerate(stats.items()):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(
                    f"<div style='text-align:center; opacity:0.9; padding-bottom:1rem;'>"
                    f"<p style='margin:0; font-size:0.85rem; color:gray;'>{label}</p>"
                    f"<p style='margin:0; font-weight:600; font-size:0.95rem;'>${value:,.2f}</p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
