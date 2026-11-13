import streamlit as st
import pandas as pd

from students.ethereum.components import footer


def render_view(title:str = "", ohlc_df: pd.DataFrame = None):
    """
    Renders the historical data view for Ethereum.

    This function displays a subheader, description, time range selector, download button,
    dataframe with OHLC data, summary statistics in an expander, and footer.

    Args:
        title (str, optional): The title to display as subheader. Defaults to "".
        ohlc_df (pd.DataFrame, optional): DataFrame containing historical OHLC data.
            Defaults to None.

    Returns:
        None: This function renders UI elements directly using Streamlit.
    """
    st.subheader(title)
    st.write(f"Historical market data overview for Ethereum (ETH), based on CoinGecko OHLC data.")

    left_col, right_col = st.columns([1, 1], vertical_alignment="center")

    with left_col:
        period_labels = {1: "1D", 7: "7D", 30: "1M", 90: "6M", 365: "1Y"}
        selected_period = st.pills(
            "⏱️ Time Range",
            options=period_labels.keys(),
            format_func=lambda option: period_labels[option],
            selection_mode="single",
            default=st.session_state.get("selected_period", 7),
            key="historical_data_period_selector",
        )

        if st.session_state.get("selected_period") != selected_period:
            st.session_state["selected_period"] = selected_period
            st.rerun()

    with right_col:
        with st.container(horizontal_alignment="right"):
            csv = ohlc_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Data (CSV)", data=csv, file_name="ethereum_historical.csv", mime="text/csv")

    if ohlc_df is None or ohlc_df.empty:
        st.warning("No historical data available.")
        return

    st.dataframe(ohlc_df, use_container_width=True)
    st.caption(f"Showing {len(ohlc_df)} rows.")

    with st.expander("Summary statistics"):
        st.dataframe(ohlc_df.describe().T)

    st.divider()
    footer.render_view("Historical data provided by CoinGecko API (Public Free Tier).")