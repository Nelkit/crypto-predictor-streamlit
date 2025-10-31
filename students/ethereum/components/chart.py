from operator import index

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from students.ethereum.components import footer


def render_view(ohlc_df: pd.DataFrame = None):
    st.subheader("📈 Price")

    left_col, right_col = st.columns([1, 1], vertical_alignment="center")

    with left_col:
        period_labels = {
            1: "1D",
            7: "7D",
            30: "1M",
            90: "6M",
            365: "1Y",
        }
        selected_period = st.pills(
            "Time range",
            options=period_labels.keys(),
            format_func=lambda option: period_labels[option],
            selection_mode="single",
            default=st.session_state.get("selected_period", 7)
        )

        if st.session_state.get("selected_period") != selected_period:
            st.session_state["selected_period"] = selected_period
            st.rerun()

    with right_col:
        chart_options = ["Line Chart", "Mountain Chart", "Candlestick Chart"]
        default_value = st.session_state.get("selected_chart_type", chart_options[0])

        selected_chart_type = st.selectbox(
            "Chart type",
            options=chart_options,
            index=chart_options.index(default_value),
        )

        if selected_chart_type != default_value:
            st.session_state["selected_chart_type"] = selected_chart_type
            st.rerun()

    if selected_chart_type == "Mountain Chart":
        render_area_chart(ohlc_df)
    elif selected_chart_type == "Candlestick Chart":
        render_candlestick_chart(ohlc_df)
    elif selected_chart_type == "Line Chart":
        render_line_chart(ohlc_df)

    st.divider()
    footer.render_view("Price chart data provided by CoinGecko API (Public Free Tier).")

def render_area_chart(ohlc_data: pd.DataFrame):
    if ohlc_data is None or ohlc_data.empty:
        st.warning("No data available to display the chart.")
        return

    first_close = ohlc_data["close"].iloc[0]
    last_close = ohlc_data["close"].iloc[-1]

    color = "#00FF7F" if last_close > first_close else "#FF4C4C"

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=ohlc_data["timestamp"],
        y=ohlc_data["close"],
        fill="tozeroy",
        mode="lines",
        line=dict(color=color, width=2),
        fillcolor=f"rgba{tuple(int(color[i:i + 2], 16) for i in (1, 3, 5)) + (0.3,)}",  # versión translúcida
        name="Close Price"
    ))

    fig.update_layout(
        title="Ethereum price (area)",
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        hovermode="x unified",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

def render_candlestick_chart(ohlc_data: pd.DataFrame):
    if ohlc_data is None or ohlc_data.empty:
        st.warning("No data available to display the chart.")
        return

    first_close = ohlc_data["close"].iloc[0]
    last_close = ohlc_data["close"].iloc[-1]
    color = "#00FF7F" if last_close > first_close else "#FF4C4C"

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=ohlc_data["timestamp"],
                open=ohlc_data["open"],
                high=ohlc_data["high"],
                low=ohlc_data["low"],
                close=ohlc_data["close"],
                increasing_line_color="#00FF7F",
                decreasing_line_color="#FF4C4C",
                increasing_fillcolor="rgba(0,255,127,0.5)",
                decreasing_fillcolor="rgba(255,76,76,0.5)",
                name="Candles"
            )
        ]
    )

    fig.add_trace(go.Scatter(
        x=ohlc_data["timestamp"],
        y=ohlc_data["close"].rolling(3).mean(),
        mode="lines",
        line=dict(color=color, width=2),
        name="Trend"
    ))

    fig.update_layout(
        title="Ethereum price (candlestick)",
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
        height=420,
        margin=dict(l=10, r=10, t=40, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

def render_line_chart(ohlc_data: pd.DataFrame):
    if ohlc_data is None or ohlc_data.empty:
        st.warning("No data available to display the chart.")
        return

    first_close = ohlc_data["close"].iloc[0]
    last_close = ohlc_data["close"].iloc[-1]
    color = "#00FF7F" if last_close > first_close else "#FF4C4C"

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=ohlc_data["timestamp"],
        y=ohlc_data["close"],
        mode="lines+markers",
        line=dict(color=color, width=2),
        marker=dict(size=4, color=color, opacity=0.8),
        name="Close Price"
    ))

    fig.add_trace(go.Scatter(
        x=ohlc_data["timestamp"],
        y=ohlc_data["close"].rolling(window=7).mean(),
        mode="lines",
        line=dict(color="rgba(25, 181, 254,0.4)", width=1.5, dash="dot"),
        name="7D Moving Avg"
    ))

    fig.update_layout(
        title="Ethereum price (line)",
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        hovermode="x unified",
        template="plotly_dark",
        height=400,
        margin=dict(l=10, r=10, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)