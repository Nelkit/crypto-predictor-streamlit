import streamlit as st
import pandas as pd

from students.ethereum.constants import ETH_LOGO


def render_view(latest_row: pd.Series, metadata: dict = None, forecast_data: dict = None):
    coin_name = metadata.get("name", "Unknown")
    coin_symbol = metadata.get("symbol", "N/A").upper()
    current_price = metadata.get("current_price", 0)
    predicted_price = float(forecast_data.get("next_day_high_predicted", 0))
    predicted_date = forecast_data.get("next_day_high_date", "N/A")

    if current_price > 0:
        predicted_change = ((predicted_price - current_price) / current_price) * 100
    else:
        predicted_change = 0.0

    st.markdown(
        f"""
        <h1 style='margin-bottom:0.2rem; font-size:1.5rem;'>
            <img src="{ETH_LOGO}"
                 width="40" style="vertical-align:middle; margin-right:4px;"/>
            {coin_name} <small style="color:grey;">({coin_symbol})</small>
        </h1>
        """,
        unsafe_allow_html=True,
    )

    # --- Featured metrics ---
    st.metric("💰 Current Price", f"${current_price:,.2f}", border=True)
    with st.container(border=True):
        st.metric(
            f"📈 Predicted High Next Day ({predicted_date})",
            f"${predicted_price:,.2f}",
            f"{predicted_change:+.2f}%",
        )

    st.markdown("**📊 24h Market Summary**")

    if latest_row is None or not isinstance(latest_row, pd.Series):
        high_value = low_value = open_value = close_value = volume_value = market_cap_value = 0.0
    else:
        high_value = latest_row.get("high", 0.0) or 0.0
        low_value = latest_row.get("low", 0.0) or 0.0
        open_value = latest_row.get("open", 0.0) or 0.0
        close_value = latest_row.get("close", 0.0) or 0.0
        volume_value = latest_row.get("volume", 0.0) or 0.0
        market_cap_value = latest_row.get("market_cap", 0.0) or 0.0

    stats = {
        "24h High": high_value,
        "24h Low": low_value,
        "24h Open": open_value,
        "24h Close": close_value,
        "Volume": volume_value,
        "Market Cap": market_cap_value,
    }

    cols = st.columns(2)
    keys = list(stats.keys())

    for i, key in enumerate(keys):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(
                    f"<div style='text-align:center; opacity:0.9; padding-bottom:1rem;'>"
                    f"<p style='margin:0; font-size:0.85rem; color:gray;'>{key}</p>"
                    f"<p style='margin:0; font-weight:600; font-size:0.95rem;'>${stats[key]:,.2f}</p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
