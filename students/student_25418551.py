import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone

import time
API_URL = "https://bitcoin-high-prediction-latest.onrender.com/predict/BTC"
HEALTH_URL = "https://bitcoin-high-prediction-latest.onrender.com/health/"

import requests

API_URL = "https://bitcoin-high-prediction-latest.onrender.com/predict/BTC"

# --- utils ---
def _format_usd(x: float | int) -> str:
    return f"${x:,.0f}"

def fetch_ohlc(days: int = 90) -> pd.DataFrame:
    """Fetch daily OHLC for BTC/USD from Kraken (UTC candles)."""
    url = "https://api.kraken.com/0/public/OHLC"
    params = {"pair": "BTCUSD", "interval": 1440}  # 1-day candles
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    raw = r.json()["result"]["XXBTZUSD"]  # BTC/USD key
    df = pd.DataFrame(
        raw,
        columns=["time","open","high","low","close","vwap","volume","count"]
    )
    # types + time
    for c in ["open","high","low","close","vwap","volume"]:
        df[c] = df[c].astype(float)
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.sort_values("time").reset_index(drop=True)
    # keep last N days for speed
    return df.tail(days)

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add MA7, MA30, returns and rolling vol (30D, annualized)."""
    df = df.copy()
    df["MA7"] = df["close"].rolling(7).mean()
    df["MA30"] = df["close"].rolling(30).mean()
    # daily simple returns
    df["ret"] = df["close"].pct_change()
    # 30D rolling std of daily returns (crypto trades 365d) -> annualized vol
    df["vol30_annual"] = df["ret"].rolling(30).std() * np.sqrt(365)
    # quick helper metrics
    df["ret_7d"] = df["close"].pct_change(7)
    return df

@st.cache_data(ttl=120)  # cache for 2 minutes to avoid repeated calls
def fetch_prediction_with_retry(max_retries: int = 2):
    # warm the Render app (handles cold starts)
    try:
        requests.get(HEALTH_URL, timeout=5)
    except Exception:
        pass

    last_err = None
    for i in range(max_retries + 1):
        try:
            r = requests.get(API_URL, timeout=20)  # longer timeout for Render cold start
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e
            time.sleep(1 + i)  # small backoff and try again
    raise last_err

def render_tab():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import requests
    import plotly.graph_objects as go
    from datetime import datetime, timedelta, timezone

    def _format_usd(x: float | int) -> str:
        return f"${x:,.0f}"

    def fetch_ohlc(days: int = 90) -> pd.DataFrame:
        """Fetch daily OHLC for BTC/USD from Kraken (UTC candles)."""
        url = "https://api.kraken.com/0/public/OHLC"
        params = {"pair": "BTCUSD", "interval": 1440}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        raw = r.json()["result"]["XXBTZUSD"]
        df = pd.DataFrame(
            raw,
            columns=["time", "open", "high", "low", "close", "vwap", "volume", "count"]
        )
        for c in ["open", "high", "low", "close", "vwap", "volume"]:
            df[c] = df[c].astype(float)
        df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
        df = df.sort_values("time").reset_index(drop=True)
        return df.tail(days)

    def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add MA7, MA30, returns and rolling vol (30D annualized)."""
        df = df.copy()
        df["MA7"] = df["close"].rolling(7).mean()
        df["MA30"] = df["close"].rolling(30).mean()
        df["ret"] = df["close"].pct_change()
        df["vol30_annual"] = df["ret"].rolling(30).std() * np.sqrt(365)
        return df

    # ===== HEADER =====
    st.header("Student 25418551 – My Analysis")

    # ===== Section 1. Current vs Predicted HIGH =====
    st.subheader("Bitcoin Daily HIGH Overview")

    try:
        # Fetch the most recent candle (1-day interval)
        url = "https://api.kraken.com/0/public/OHLC"
        params = {"pair": "BTCUSD", "interval": 1440}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        raw = r.json()["result"]["XXBTZUSD"]
        last_candle = raw[-1]  # latest day
        last_time = datetime.utcfromtimestamp(float(last_candle[0])).date()
        current_high = float(last_candle[2])
    except Exception as e:
        current_high = None
        st.warning(f"Could not fetch current data: {e}")

    c1, c2 = st.columns(2)

    # Left: current HIGH from Kraken
    with c1:
        st.markdown("**Current HIGH (BTC-USD)**")
        if current_high:
            st.metric(label="", value=_format_usd(current_high))
            st.caption(f"As of {last_time} (UTC)")
        else:
            st.metric(label="", value="N/A")
            st.caption("Data unavailable")

    # Right: predicted HIGH placeholder
    with c2:
        st.markdown("**🧠 Next-day HIGH Prediction**")

        try:
            data = fetch_prediction_with_retry()
            predicted = data.get("predicted_high_usd_next_day") or data.get("predicted_high_price")
            source = data.get("data_source", "n/a")
            st.metric("Predicted HIGH for tomorrow (BTC-USD)", _format_usd(predicted))
            st.caption(f"Data source: {source} • cached up to 2 min")
        except Exception as e:
            st.metric("Predicted HIGH for tomorrow (BTC-USD)", "N/A")
            st.caption(f"⚠️ API unavailable: {e}  \nTip: open {API_URL} in a browser once to wake it.")

    st.divider()

    # ===== Section 2. Historical OHLC + Indicators =====
    st.subheader("📈 Historical OHLC + MA7/MA30")
    days = st.radio("Select period (days)", [30, 60, 90, 180, 365], horizontal=True, index=1)

    try:
        df = fetch_ohlc(days)
        df = add_indicators(df)

        # Detect MA crossovers
        df["cross_up"] = (df["MA7"].shift(1) < df["MA30"].shift(1)) & (df["MA7"] >= df["MA30"])
        df["cross_down"] = (df["MA7"].shift(1) > df["MA30"].shift(1)) & (df["MA7"] <= df["MA30"])

        # Candlestick with MAs and cross markers
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df["time"], open=df["open"], high=df["high"],
            low=df["low"], close=df["close"], name="BTC/USD"
        ))
        fig.add_trace(go.Scatter(x=df["time"], y=df["MA7"], mode="lines", name="MA7"))
        fig.add_trace(go.Scatter(x=df["time"], y=df["MA30"], mode="lines", name="MA30"))

        # Cross markers
        fig.add_trace(go.Scatter(
            x=df.loc[df["cross_up"], "time"],
            y=df.loc[df["cross_up"], "MA7"],
            mode="markers",
            marker=dict(symbol="triangle-up", color="lime", size=10),
            name="Golden Cross"
        ))
        fig.add_trace(go.Scatter(
            x=df.loc[df["cross_down"], "time"],
            y=df.loc[df["cross_down"], "MA7"],
            mode="markers",
            marker=dict(symbol="triangle-down", color="red", size=10),
            name="Death Cross"
        ))

        fig.update_layout(
            title=f"Bitcoin (BTC-USD) — Last {days} Days (UTC)",
            xaxis_title="Date (UTC)", yaxis_title="Price (USD)",
            xaxis_rangeslider_visible=False,
            height=520, margin=dict(l=30, r=30, t=50, b=30)
        )

        st.plotly_chart(fig, use_container_width=True)

# --- Metric summary (robust for short windows)
        df_metrics = df.dropna(subset=["close", "MA7", "MA30", "vol30_annual"])
        if not df_metrics.empty:
            last = df_metrics.iloc[-1]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Close (last)", _format_usd(last["close"]))
            c2.metric("MA7", _format_usd(last["MA7"]))
            c3.metric("MA30", _format_usd(last["MA30"]))
            c4.metric("30D Vol (annualized)", f"{last['vol30_annual']*100:,.2f}%")
        else:
            st.info("Not enough data to compute indicators for this period. Try 60 or 90 days.")

        # Explanation
        st.markdown("""
        **Interpretation**

        The chart shows Bitcoin’s daily price movements (candlesticks) with two moving averages:
        - **MA7** averages the last 7 daily closes (short-term momentum)  
        - **MA30** averages the last 30 daily closes (medium-term trend)

        When the 7-day line rises above the 30-day line (*green triangle*), it often signals **positive momentum** (“Golden Cross”).  
        When it falls below (*red triangle*), it can indicate **weakening momentum** (“Death Cross”).  
        These help users quickly gauge whether Bitcoin’s short-term direction aligns with or diverges from its longer-term trend.
        """)

        # ===== Section 3. Downloadable Data =====
        st.divider()
        st.subheader("💾 Download Historical Data")

        st.dataframe(
            df[["time", "open", "high", "low", "close", "volume"]].tail(10),
            use_container_width=True,
            hide_index=True
        )

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Full Dataset (CSV)",
            data=csv_data,
            file_name=f"bitcoin_ohlc_{days}d.csv",
            mime="text/csv"
        )

        st.caption(
            "This dataset includes open, high, low, close, and volume data "
            "retrieved from the Kraken API for the selected period."
        )

# ===== Section 4. Extra Visuals (independent period) =====
        st.divider()
        st.subheader("Extra Analytics")
        viz_days = st.radio("Select period for analytics (days)", [30, 60, 90, 180, 365],
                            horizontal=True, index=2)

        df_viz = fetch_ohlc(viz_days)
        # Recompute indicators with min_periods to avoid empty tails
        df_viz = df_viz.sort_values("time").reset_index(drop=True).copy()
        df_viz["ret"] = df_viz["close"].pct_change()
        df_viz["vol30_annual"] = df_viz["ret"].rolling(30, min_periods=10).std() * np.sqrt(365)

        # ---------- A) Daily % Change ----------
        st.divider()
        st.subheader("📊 Daily % Change")
        ret_df = df_viz[["time", "ret"]].dropna()
        if ret_df.empty:
            st.info("Not enough data for returns. Increase the analytics period.")
        else:
            fig_ret = go.Figure(go.Bar(x=ret_df["time"], y=ret_df["ret"]*100, name="Daily % change"))
            fig_ret.update_layout(yaxis_title="% change", height=300, margin=dict(l=30, r=30, t=40, b=30))
            st.plotly_chart(fig_ret, use_container_width=True)

            st.markdown("""
            This chart shows Bitcoin’s **day-to-day price variation**, helping you spot periods of high or low market activity.  
            **How it’s calculated:**  
            The percentage change between each day’s closing price and the previous day’s close.
            """)

        # ---------- B) Rolling 30-Day Volatility + Price Range ----------
        st.subheader("📛 Rolling 30-Day Volatility (annualized) + Price Range (%)")
        vol_df = df_viz[["time", "high", "low", "vol30_annual"]].copy()
        # Safe rolling with min_periods
        hi30 = vol_df["high"].rolling(30, min_periods=10).max()
        lo30 = vol_df["low"].rolling(30, min_periods=10).min()
        vol_df["range_pct"] = ((hi30 - lo30) / lo30) * 100
        vol_df = vol_df.dropna(subset=["vol30_annual", "range_pct"])

        if vol_df.empty:
            st.info("Not enough data for 30-day analytics. Try 60 or 90 days.")
        else:
            fig_vol = go.Figure()

            # Blue line – volatility
            fig_vol.add_trace(go.Scatter(
                x=vol_df["time"],
                y=vol_df["vol30_annual"]*100,
                mode="lines",
                name="Volatility (annualized)",
                line=dict(color="royalblue", width=2)
            ))

            # Orange line – 30-day price range
            fig_vol.add_trace(go.Scatter(
                x=vol_df["time"],
                y=vol_df["range_pct"],
                mode="lines",
                name="30-Day Price Range (%)",
                line=dict(color="darkorange", width=2)
            ))

            fig_vol.update_layout(
                yaxis_title="%",
                height=350,
                margin=dict(l=30, r=30, t=40, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
            )

            st.plotly_chart(fig_vol, use_container_width=True)
            st.caption("Blue = risk intensity (annualized volatility). Orange = 30-day swing amplitude (hi/lo range).")

            st.markdown("""
            These lines reveal Bitcoin’s **risk dynamics** when volatility (blue) or price range (orange) expand, markets are more turbulent.  
            **How it’s calculated:**  
            Volatility = standard deviation of daily returns (annualized).  
            Price range = % difference between the 30-day high and 30-day low.
            """)

        # ---------- C) Cumulative Return from period start ----------
        st.subheader("📉Cumulative Return (from period start)")
        cum_df = df_viz[["time", "ret"]].dropna()
        if cum_df.empty:
            st.info("Not enough data for cumulative return. Increase the analytics period.")
        else:
            cum_df["cum_ret"] = (1 + cum_df["ret"]).cumprod() - 1

            fig_cum = go.Figure()

            # Green cumulative return line
            fig_cum.add_trace(go.Scatter(
                x=cum_df["time"],
                y=cum_df["cum_ret"] * 100,
                mode="lines",
                name="Cumulative Return (%)",
                line=dict(color="mediumseagreen", width=3)
            ))

            # Add baseline (0%)
            fig_cum.add_hline(
                y=0,
                line_width=1,
                line_dash="dot",
                line_color="gray",
                annotation_text="Baseline (0%)",
                annotation_position="bottom left"
            )

            fig_cum.update_layout(
                yaxis_title="Cumulative return (%)",
                height=320,
                margin=dict(l=30, r=30, t=40, b=30),
                legend=dict(
                    orientation="h",
                    yanchor="bottom", y=1.02,
                    xanchor="center", x=0.5
                )
            )

            st.plotly_chart(fig_cum, use_container_width=True)
            st.caption("Green line shows cumulative return since the start of the selected period. Dashed gray line = baseline (no change).")
            st.markdown("""
            Shows the **total percentage gain or loss** since the beginning of the selected period a quick snapshot of overall performance.  
            **How it’s calculated:**  
            The compounded sum of daily returns relative to the first day’s price.
            """)

        # ---------- D) Rolling Max Drawdown ----------
        st.subheader("📈 Rolling Max Drawdown (%)")

        dd_df = df_viz[["time", "close"]].dropna().copy()
        if dd_df.empty:
            st.info("Not enough data for drawdown.")
        else:
            dd_df["rolling_peak"] = dd_df["close"].cummax()
            dd_df["drawdown"] = (dd_df["close"] / dd_df["rolling_peak"] - 1.0) * 100

            fig_dd = go.Figure()
            fig_dd.add_trace(go.Scatter(
                x=dd_df["time"], y=dd_df["drawdown"],
                mode="lines", name="Drawdown",
                line=dict(color="crimson"),
                fill="tozeroy", fillcolor="rgba(220,20,60,0.15)"
            ))
            fig_dd.add_hline(y=0, line_width=1, line_dash="dot", line_color="gray")
            fig_dd.update_layout(
                yaxis_title="Drawdown (%)",
                height=320, margin=dict(l=30, r=30, t=40, b=30)
            )
            st.plotly_chart(fig_dd, use_container_width=True)
            st.caption("Drawdown measures losses from the most recent peak. Deeper/longer dips indicate tougher recovery periods.")
            st.markdown("""
            Drawdown highlights **how deep recent losses** have been from the last price peak a key measure of downside risk.  
            **How it’s calculated:**  
            The percentage decline from the most recent rolling maximum closing price.
            """)


            # ---------- E) Risk-Adjusted Return (30D Sharpe proxy) ----------
        st.subheader("🟣 Risk-Adjusted Return (30-Day Sharpe Proxy)")

        sh_df = df_viz[["time", "ret"]].dropna().copy()
        if sh_df.empty:
            st.info("Not enough data for risk-adjusted return.")
        else:
            mean30 = sh_df["ret"].rolling(30, min_periods=10).mean()
            std30  = sh_df["ret"].rolling(30, min_periods=10).std()
            # Annualize using √365
            sh_df["sharpe30"] = (mean30 / std30) * np.sqrt(365)

            sh_df = sh_df.dropna(subset=["sharpe30"])
            if sh_df.empty:
                st.info("Not enough data for 30-day Sharpe proxy. Increase the analytics period.")
            else:
                fig_sh = go.Figure(go.Scatter(
                    x=sh_df["time"], y=sh_df["sharpe30"],
                    mode="lines", name="Sharpe(30D)",
                    line=dict(color="mediumorchid")
                ))
                fig_sh.add_hline(y=0, line_width=1, line_dash="dot", line_color="gray")
                fig_sh.update_layout(
                    yaxis_title="Sharpe (annualized)",
                    height=320, margin=dict(l=30, r=30, t=40, b=30)
                )
                st.plotly_chart(fig_sh, use_container_width=True)
                st.caption("Higher values indicate better return per unit of risk over the last 30 days (annualized).")
                st.markdown("""
                Evaluates the **quality of returns** how much return Bitcoin generated per unit of risk.  
                **How it’s calculated:**  
                Average 30-day return divided by 30-day return volatility, annualized with √365 (a simplified Sharpe ratio).
                """)

    except Exception as e:
        st.error(f"Error fetching or plotting data: {e}")