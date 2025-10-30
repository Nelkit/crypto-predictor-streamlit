# students/solana/view.py
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time

# =========================
# Config – your FastAPI
# =========================
API_URL    = "https://at3-36120-25sp-24900627-api.onrender.com/predict/sol?source=kraken&days=60"
HEALTH_URL = "https://at3-36120-25sp-24900627-api.onrender.com/health/"
PAIR       = "SOLUSD"
INTERVAL   = 1440  # 1D candles (UTC)

# =========================
# Helpers
# =========================
def _format_usd(x) -> str:
    try:
        return f"${float(x):,.0f}"
    except Exception:
        return "N/A"

def _safe_pct(x) -> str:
    try:
        return f"{100*float(x):,.2f}%"
    except Exception:
        return "—"

def _kraken_ohlc(pair: str = PAIR, interval: int = INTERVAL) -> pd.DataFrame:
    url = "https://api.kraken.com/0/public/OHLC"
    r = requests.get(url, params={"pair": pair, "interval": interval}, timeout=15)
    r.raise_for_status()
    data = r.json()["result"]
    key = next(k for k in data.keys() if k != "last")
    rows = data[key]
    df = pd.DataFrame(rows, columns=["time","open","high","low","close","vwap","volume","count"])
    for c in ["open","high","low","close","vwap","volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.sort_values("time").reset_index(drop=True)
    return df

def fetch_ohlc(days: int = 180) -> pd.DataFrame:
    return _kraken_ohlc(PAIR, INTERVAL).tail(days)

def add_core_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["MA7"]  = df["close"].rolling(7,  min_periods=3).mean()
    df["MA30"] = df["close"].rolling(30, min_periods=10).mean()
    df["ret"]  = df["close"].pct_change()
    df["vol30_annual"] = df["ret"].rolling(30, min_periods=10).std() * np.sqrt(365)
    # Bollinger 20,2
    mid = df["close"].rolling(20, min_periods=15).mean()
    std = df["close"].rolling(20, min_periods=15).std()
    df["BB_mid"] = mid
    df["BB_up"]  = mid + 2*std
    df["BB_dn"]  = mid - 2*std
    return df

def add_rsi(df: pd.DataFrame, n: int = 14) -> pd.Series:
    close = df["close"].astype(float)
    delta = close.diff()
    up = np.where(delta > 0, delta, 0.0)
    dn = np.where(delta < 0, -delta, 0.0)
    roll_up = pd.Series(up, index=df.index).ewm(alpha=1/n, adjust=False).mean()
    roll_dn = pd.Series(dn, index=df.index).ewm(alpha=1/n, adjust=False).mean()
    rs = roll_up / (roll_dn + 1e-12)
    return 100 - (100 / (1 + rs))

def add_macd(df: pd.DataFrame, fast=12, slow=26, signal=9):
    close = df["close"].astype(float)
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    sig  = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - sig
    return macd, sig, hist

@st.cache_data(ttl=120)
def fetch_prediction_with_retry(max_retries: int = 2):
    try:
        requests.get(HEALTH_URL, timeout=5)  # warm Render
    except Exception:
        pass
    last_err = None
    for i in range(max_retries + 1):
        try:
            r = requests.get(API_URL, timeout=25)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e
            time.sleep(1 + i)
    raise last_err

# ============== signals & backtest ==============
def compute_signals(df: pd.DataFrame) -> dict:
    dfx = df.dropna(subset=["MA7","MA30","ret"]).copy()
    if dfx.empty:
        return {"trend":"N/A","last_golden":None,"last_death":None,"vol_annual":None,"risk_note":"Not enough data."}
    trend = "Bullish" if dfx.iloc[-1]["MA7"] >= dfx.iloc[-1]["MA30"] else "Bearish"
    dfx["cross_up"] = (dfx["MA7"].shift(1) < dfx["MA30"].shift(1)) & (dfx["MA7"] >= dfx["MA30"])
    dfx["cross_dn"] = (dfx["MA7"].shift(1) > dfx["MA30"].shift(1)) & (dfx["MA7"] <= dfx["MA30"])
    last_golden = dfx.loc[dfx["cross_up"], "time"].max() if dfx["cross_up"].any() else None
    last_death  = dfx.loc[dfx["cross_dn"], "time"].max() if dfx["cross_dn"].any() else None
    vol_series = dfx["ret"].rolling(30, min_periods=10).std() * np.sqrt(365)
    current_vol = vol_series.iloc[-1] if not vol_series.dropna().empty else np.nan
    if np.isnan(current_vol):
        risk_note = "Volatility unavailable."
    else:
        rank = (vol_series.rank(pct=True).iloc[-1]) if vol_series.dropna().shape[0] > 10 else 0.5
        if rank >= 0.85:   risk_note = "Volatility is very high — aggressive conditions."
        elif rank >= 0.60: risk_note = "Volatility above average — caution advised."
        else:              risk_note = "Volatility moderate/low vs. recent history."
    return {"trend":trend,"last_golden":last_golden,"last_death":last_death,"vol_annual":current_vol,"risk_note":risk_note}

def _max_drawdown(curve: pd.Series) -> float:
    peak = curve.cummax()
    return (curve/peak - 1.0).min()

def backtest_ma(df: pd.DataFrame) -> dict:
    dfx = df.dropna(subset=["MA7","MA30","ret"]).copy()
    if dfx.shape[0] < 40:
        return {"ok": False, "msg": "Not enough data for backtest."}
    dfx["position"] = (dfx["MA7"] >= dfx["MA30"]).astype(int)
    strat_ret = dfx["ret"] * dfx["position"].shift(1).fillna(0)
    bh_ret    = dfx["ret"]
    strat_curve = (1 + strat_ret).cumprod()
    bh_curve    = (1 + bh_ret).cumprod()
    n = dfx.shape[0]; ann = 365.0
    m = {
        "Strategy CAGR": strat_curve.iloc[-1]**(ann/n) - 1,
        "Buy&Hold CAGR": bh_curve.iloc[-1]**(ann/n) - 1,
        "Strategy Max DD": _max_drawdown(strat_curve),
        "Buy&Hold Max DD": _max_drawdown(bh_curve),
        "Strategy Sharpe": np.sqrt(ann)*strat_ret.mean()/(strat_ret.std()+1e-9),
        "Buy&Hold Sharpe": np.sqrt(ann)*bh_ret.mean()/(bh_ret.std()+1e-9),
    }
    return {"ok": True, "dfx": dfx, "strat_curve": strat_curve, "bh_curve": bh_curve, "metrics": m}

# =========================
# UI – Trading dashboard
# =========================
def render_tab():
    st.set_page_config(page_title="SOL Trading Dashboard", layout="wide")

    # ---- CSS
    st.markdown("""
    <style>
    .card {border-radius:14px; padding:14px 16px; border:1px solid rgba(125,125,125,.22);}
    .metric-lg{font-size:32px;font-weight:700;line-height:1.1;margin-top:4px}
    .subtle{opacity:.7;font-size:12px}
    .badge{display:inline-block;padding:4px 8px;border-radius:999px;font-size:11px;font-weight:600;border:1px solid rgba(125,125,125,.25)}
    .badge-success{background:rgba(16,185,129,.12);color:#10b981;border-color:rgba(16,185,129,.35)}
    .badge-danger{background:rgba(239,68,68,.12);color:#ef4444;border-color:rgba(239,68,68,.35)}
    .hr{border:none;border-top:1px solid rgba(125,125,125,.25);margin:8px 0 18px}
    </style>
    """, unsafe_allow_html=True)

    # ---- HEADER
    st.markdown(
        """
        <h2 style="margin-bottom:6px">Solana (SOL-USD) — Trading Dashboard</h2>
        <div class="subtle">
          High-throughput chain (PoH + PoS). Popular for DeFi, memecoins and real-time apps. 
          <a href="https://solana.com" target="_blank">Learn more</a>.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<hr class='hr'/>", unsafe_allow_html=True)

    # ---- CONTROLS (top)
    left, right = st.columns([4,3], gap="large")
    with left:
        days = st.slider("Period (days)", 30, 365, 180, step=10)
    with right:
        st.caption("Overlays")
        col_ov1, col_ov2, col_ov3 = st.columns(3)
        with col_ov1:
            show_ma = st.toggle("MA7 / MA30", value=True)
        with col_ov2:
            show_bb = st.toggle("Bollinger 20/2", value=True)
        with col_ov3:
            show_vol = st.toggle("Volume", value=True)

    # ---- DATA + INDICATORS
    df = add_core_indicators(fetch_ohlc(days))
    use_dark = st.get_option("theme.base") == "dark"
    template = "plotly_dark" if use_dark else "plotly_white"

    # RSI / MACD options
    col_i1, col_i2, col_i3 = st.columns([2,2,3])
    with col_i1:
        show_rsi = st.toggle("RSI(14)", value=False)
    with col_i2:
        show_macd = st.toggle("MACD(12,26,9)", value=False)
    with col_i3:
        st.write("")  # spacer

    # ---- MAIN LAYOUT: chart + right panel
    main, side = st.columns([4.5, 2], gap="large")

    with main:
        # Subplots: Price+BB+MAs (row1) + Volumen (row2)
        specs = [[{"secondary_y": False}], [{"secondary_y": False}]]
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.78, 0.22],
            shared_xaxes=True,
            vertical_spacing=0.04,
            specs=specs
        )

        # Candles
        fig.add_trace(go.Candlestick(
            x=df["time"], open=df["open"], high=df["high"], low=df["low"], close=df["close"],
            name="SOL/USD",
            increasing_line_color="#16a34a", decreasing_line_color="#ef4444",
            increasing_fillcolor="#16a34a", decreasing_fillcolor="#ef4444",
            showlegend=True
        ), row=1, col=1)

        # MAs
        if show_ma:
            fig.add_trace(go.Scatter(x=df["time"], y=df["MA7"],  mode="lines", name="MA7",
                                     line=dict(width=2.2, color="#60a5fa")), row=1, col=1)
            fig.add_trace(go.Scatter(x=df["time"], y=df["MA30"], mode="lines", name="MA30",
                                     line=dict(width=2.2, color="#f59e0b")), row=1, col=1)

        # Bollinger
        if show_bb:
            fig.add_trace(go.Scatter(x=df["time"], y=df["BB_up"], mode="lines", name="BB Upper",
                                     line=dict(width=1.2, color="rgba(96,165,250,.7)")), row=1, col=1)
            fig.add_trace(go.Scatter(x=df["time"], y=df["BB_mid"], mode="lines", name="BB Mid",
                                     line=dict(width=1.0, color="rgba(148,163,184,.8)", dash="dot")), row=1, col=1)
            fig.add_trace(go.Scatter(x=df["time"], y=df["BB_dn"], mode="lines", name="BB Lower",
                                     line=dict(width=1.2, color="rgba(96,165,250,.7)")), row=1, col=1)

        # Volume (row 2)
        if show_vol:
            fig.add_trace(go.Bar(
                x=df["time"], y=df["volume"], name="Volume",
                marker=dict(color="rgba(148,163,184,.45)"),
                hovertemplate="%{x|%Y-%m-%d}<br>Vol: %{y:,.0f}<extra></extra>"
            ), row=2, col=1)

        fig.update_layout(
            template=template,
            height=620,
            margin=dict(l=12, r=12, t=30, b=12),
            legend=dict(orientation="h", y=1.02, x=0.0),
            hovermode="x unified",
            xaxis=dict(title="", showgrid=False),
            xaxis2=dict(title="Date (UTC)"),
            yaxis=dict(title="Price (USD)", zeroline=False),
            yaxis2=dict(title="Volume", zeroline=False),
        )
        st.plotly_chart(fig, use_container_width=True)

        # RSI / MACD mini-charts
        if show_rsi:
            rsi = add_rsi(df)
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=df["time"], y=rsi, mode="lines", name="RSI(14)",
                                         line=dict(color="#8b5cf6", width=2)))
            fig_rsi.add_hline(y=70, line_dash="dot", line_color="gray")
            fig_rsi.add_hline(y=30, line_dash="dot", line_color="gray")
            fig_rsi.update_layout(template=template, height=180, margin=dict(l=12,r=12,t=10,b=0),
                                  yaxis=dict(title="RSI", range=[0,100]))
            st.plotly_chart(fig_rsi, use_container_width=True)

        if show_macd:
            macd, sig, hist = add_macd(df)
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Bar(x=df["time"], y=hist, name="Hist", marker=dict(color="rgba(139,92,246,.35)")))
            fig_macd.add_trace(go.Scatter(x=df["time"], y=macd, name="MACD", mode="lines", line=dict(color="#22c55e")))
            fig_macd.add_trace(go.Scatter(x=df["time"], y=sig,  name="Signal", mode="lines", line=dict(color="#ef4444")))
            fig_macd.update_layout(template=template, height=200, margin=dict(l=12,r=12,t=10,b=0),
                                   yaxis=dict(title="MACD"))
            st.plotly_chart(fig_macd, use_container_width=True)

    with side:
        # === LIVE PRICE (para comparar con la predicción) ===
        try:
            live_row  = _kraken_ohlc(PAIR, 1).iloc[-1]  # 1-min candles
            live_price = float(live_row["close"])
            live_time  = live_row["time"].strftime("%Y-%m-%d %H:%M UTC")
        except Exception:
            live_price, live_time = None, None

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("**Live Price (SOL-USD)**")
        st.markdown(f"<div class='metric-lg'>{_format_usd(live_price)}</div>", unsafe_allow_html=True)
        if live_time:
            st.caption(f"Last update: {live_time}")
        st.markdown("</div>", unsafe_allow_html=True)

        # === Predicción con precio actual al lado (delta USD y %) ===
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("**Predicted Next-Day HIGH**")
        try:
            data = fetch_prediction_with_retry()
            predicted = data.get("next_day_high_pred") or data.get("predicted_high_usd_next_day") or data.get("predicted_high_price")
            if predicted is not None and live_price:
                predicted = float(predicted)
                delta_usd = predicted - live_price
                delta_pct = (predicted / live_price - 1.0) * 100.0
                # Muestra el valor y el delta vs live, incluyendo el live en el texto
                st.metric(
                    label="",
                    value=_format_usd(predicted),
                    delta=f"{delta_usd:+,.2f} ({delta_pct:+.2f}%)  vs live {_format_usd(live_price)}",
                )
            else:
                st.markdown(f"<div class='metric-lg'>{_format_usd(predicted)}</div>", unsafe_allow_html=True)
            st.markdown("<div class='subtle'>Source: API (cached)</div>", unsafe_allow_html=True)
        except Exception as e:
            st.markdown("<div class='metric-lg'>N/A</div>", unsafe_allow_html=True)
            st.caption(f"API unavailable: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

        # === Señales de mercado ===
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("**Market Signals**")
        sig = compute_signals(df)
        badge = "badge-success" if sig["trend"]=="Bullish" else "badge-danger"
        st.markdown(f"Trend  <span class='badge {badge}'>{sig['trend']}</span>", unsafe_allow_html=True)
        st.caption("Bullish if MA7 ≥ MA30")
        st.markdown("<hr class='hr'/>", unsafe_allow_html=True)
        st.caption("Annualized Volatility (30D)")
        st.markdown(f"<div class='metric-lg'>{_safe_pct(sig['vol_annual'])}</div>", unsafe_allow_html=True)
        st.markdown("<hr class='hr'/>", unsafe_allow_html=True)
        st.caption("Last Golden Cross")
        st.write(sig["last_golden"].strftime("%Y-%m-%d") if sig["last_golden"] else "—")
        st.caption("Last Death Cross")
        st.write(sig["last_death"].strftime("%Y-%m-%d") if sig["last_death"] else "—")
        st.info(sig["risk_note"])
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr class='hr'/>", unsafe_allow_html=True)

    # ===== Strategy Tab =====
    tab_strategy, = st.tabs(["Strategy"])
    with tab_strategy:
        st.subheader("MA7/MA30 Long-Only — Quick Backtest")
        bt = backtest_ma(df)
        if not bt["ok"]:
            st.warning(bt["msg"])
        else:
            m = bt["metrics"]
            c1,c2,c3,c4,c5,c6 = st.columns(6, gap="small")
            for col, title, val, pct in [
                (c1,"Strategy CAGR", m["Strategy CAGR"], True),
                (c2,"Buy&Hold CAGR", m["Buy&Hold CAGR"], True),
                (c3,"Strat Max DD",   m["Strategy Max DD"], True),
                (c4,"B&H Max DD",     m["Buy&Hold Max DD"], True),
                (c5,"Strat Sharpe",   m["Strategy Sharpe"], False),
                (c6,"B&H Sharpe",     m["Buy&Hold Sharpe"], False),
            ]:
                with col:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown(f"**{title}**")
                    st.markdown(f"<div class='metric-lg'>{_safe_pct(val) if pct else f'{val:.2f}'}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            curve_df = pd.DataFrame({
                "time": bt["dfx"]["time"].values,
                "Strategy": bt["strat_curve"].values,
                "Buy & Hold": bt["bh_curve"].values
            })
            fig_bt = go.Figure()
            fig_bt.add_trace(go.Scatter(x=curve_df["time"], y=curve_df["Strategy"], mode="lines", name="Strategy"))
            fig_bt.add_trace(go.Scatter(x=curve_df["time"], y=curve_df["Buy & Hold"], mode="lines", name="Buy & Hold"))
            fig_bt.update_layout(template=template, title="Equity Curves (normalized to 1.0)",
                                 height=360, margin=dict(l=12,r=12,t=40,b=12), yaxis_title="Equity")
            st.plotly_chart(fig_bt, use_container_width=True)

    # ===== Footer: single download button =====
    csv = df[["time","open","high","low","close","volume"]].to_csv(index=False).encode()
    st.download_button(
        "📥 Download Historical (CSV)",
        csv,
        file_name=f"sol_ohlc_{days}d.csv",
        mime="text/csv",
        use_container_width=True,
        type="primary"
    )
