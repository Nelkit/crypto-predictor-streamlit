# students/solana/view.py
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from datetime import datetime
import time

# =========================
# Config – your FastAPI
# =========================
API_URL    = "https://at3-36120-25sp-24900627-api.onrender.com/predict/sol?source=kraken&days=60"
HEALTH_URL = "https://at3-36120-25sp-24900627-api.onrender.com/health/"

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

def _kraken_ohlc(pair: str = "SOLUSD", interval: int = 1440) -> pd.DataFrame:
    url = "https://api.kraken.com/0/public/OHLC"
    r = requests.get(url, params={"pair": pair, "interval": interval}, timeout=15)
    r.raise_for_status()
    data = r.json()["result"]
    key = next(k for k in data.keys() if k != "last")  # first non-'last' key
    rows = data[key]
    df = pd.DataFrame(rows, columns=["time","open","high","low","close","vwap","volume","count"])
    for c in ["open","high","low","close","vwap","volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df.sort_values("time").reset_index(drop=True)
    return df

def fetch_ohlc(days: int = 180) -> pd.DataFrame:
    return _kraken_ohlc("SOLUSD", 1440).tail(days)

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["MA7"]  = df["close"].rolling(7,  min_periods=3).mean()
    df["MA30"] = df["close"].rolling(30, min_periods=10).mean()
    df["ret"]  = df["close"].pct_change()
    df["vol30_annual"] = df["ret"].rolling(30, min_periods=10).std() * np.sqrt(365)
    return df

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
        if rank >= 0.85:   risk_note = "Volatility is very high – aggressive conditions."
        elif rank >= 0.60: risk_note = "Volatility above average – caution advised."
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
# UI — modern design
# =========================
st.set_page_config(page_title="SOL Dashboard", layout="wide")

# ---- CSS (cards, badges, spacing)
st.markdown("""
<style>
/* cards */
.card {
  border-radius: 14px;
  padding: 16px 18px;
  border: 1px solid var(--secondary-background-color);
  background: var(--background-color);
  box-shadow: 0 0 0 1px rgba(125,125,125,0.06) inset;
}
.metric-lg { font-size: 32px; font-weight: 700; line-height: 1.1; margin-top: 4px; }
.subtle  { color: var(--text-color); opacity: .6; font-size: 12px; }
.badge {
  display:inline-block; padding:4px 8px; border-radius:999px;
  font-size:11px; font-weight:600; border:1px solid rgba(125,125,125,.25)
}
.badge-success{ background:rgba(16,185,129,.12); color:#10b981; border-color:rgba(16,185,129,.35);}
.badge-danger{  background:rgba(239,68,68,.12); color:#ef4444; border-color:rgba(239,68,68,.35);}
hr.hr { border: none; border-top: 1px solid rgba(125,125,125,.2); margin: 12px 0 24px; }
</style>
""", unsafe_allow_html=True)

# ---- SIDEBAR (controles)
with st.sidebar:
    st.markdown("### Controls")
    days = st.slider("Period (days)", 30, 365, 180, step=10)
    source = st.radio("Data source", ["kraken"], horizontal=True, index=0)
    st.caption("Tip: prediction is cached up to 2 minutes.")

# ---- HEADER / HERO
st.markdown("<h2 style='text-align:center; margin-bottom:4px;'>Solana (SOL-USD) — Analytics & Next-Day HIGH</h2>", unsafe_allow_html=True)
st.markdown("<div class='subtle' style='text-align:center;'>Clean, responsive layout with logical grouping</div>", unsafe_allow_html=True)
st.markdown("<hr class='hr'/>", unsafe_allow_html=True)

# Current vs Predicted (cards)
try:
    last = _kraken_ohlc("SOLUSD", 1440).iloc[-1]
    current_high = last["high"]; last_date = last["time"].date()
except Exception:
    current_high, last_date = None, None

c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("**Current HIGH (Kraken)**")
    st.markdown(f"<div class='metric-lg'>{_format_usd(current_high) if current_high else 'N/A'}</div>", unsafe_allow_html=True)
    if last_date: st.markdown(f"<div class='subtle'>As of {last_date} (UTC)</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("**Predicted Next-Day HIGH**")
    try:
        data = fetch_prediction_with_retry()
        predicted = data.get("next_day_high_pred") or data.get("predicted_high_usd_next_day") or data.get("predicted_high_price")
        st.markdown(f"<div class='metric-lg'>{_format_usd(predicted)}</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtle'>Source: API (cached)</div>", unsafe_allow_html=True)
    except Exception as e:
        st.markdown("<div class='metric-lg'>N/A</div>", unsafe_allow_html=True)
        st.caption(f"API unavailable: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr class='hr'/>", unsafe_allow_html=True)

# ---- TABS
tab_overview, tab_strategy, tab_data = st.tabs(["Overview", "Strategy", "Data"])

# ============ OVERVIEW ============
with tab_overview:
    df = add_indicators(fetch_ohlc(days))
    df["cross_up"]   = (df["MA7"].shift(1) < df["MA30"].shift(1)) & (df["MA7"] >= df["MA30"])
    df["cross_down"] = (df["MA7"].shift(1) > df["MA30"].shift(1)) & (df["MA7"] <= df["MA30"])

    # Plotly theme based on Streamlit theme
    use_dark = st.get_option("theme.base") == "dark"
    template = "plotly_dark" if use_dark else "plotly_white"

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df["time"], open=df["open"], high=df["high"],
                                 low=df["low"], close=df["close"], name="SOL/USD"))
    fig.add_trace(go.Scatter(x=df["time"], y=df["MA7"],  mode="lines", name="MA7"))
    fig.add_trace(go.Scatter(x=df["time"], y=df["MA30"], mode="lines", name="MA30"))
    fig.add_trace(go.Scatter(x=df.loc[df["cross_up"], "time"], y=df.loc[df["cross_up"], "MA7"],
                             mode="markers", marker=dict(symbol="triangle-up", color="lime", size=10),
                             name="Golden Cross"))
    fig.add_trace(go.Scatter(x=df.loc[df["cross_down"], "time"], y=df.loc[df["cross_down"], "MA7"],
                             mode="markers", marker=dict(symbol="triangle-down", color="red", size=10),
                             name="Death Cross"))
    fig.update_layout(template=template, xaxis_rangeslider_visible=False,
                      height=520, margin=dict(l=30,r=30,t=30,b=30))
    st.plotly_chart(fig, use_container_width=True)

    # KPIs
    tail = df.dropna(subset=["close","MA7","MA30","vol30_annual"]).tail(1)
    if not tail.empty:
        k1,k2,k3,k4 = st.columns(4)
        last = tail.iloc[-1]
        for col, title, val in [
            (k1, "Close", _format_usd(last["close"])),
            (k2, "MA7", _format_usd(last["MA7"])),
            (k3, "MA30", _format_usd(last["MA30"])),
            (k4, "Vol 30D (ann.)", _safe_pct(last["vol30_annual"]))
        ]:
            with col:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"**{title}**")
                st.markdown(f"<div class='metric-lg'>{val}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Market Signals
    st.subheader("Market Signals")
    sig = compute_signals(df)
    s1, s2, s3 = st.columns([1.2,1.2,2], gap="large")
    with s1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        badge = "badge-success" if sig["trend"]=="Bullish" else "badge-danger"
        st.markdown(f"**Trend**  <span class='badge {badge}'>{sig['trend']}</span>", unsafe_allow_html=True)
        st.markdown("<div class='subtle'>Bullish if MA7 ≥ MA30</div>", unsafe_allow_html=True)
        st.markdown("<hr class='hr'/>", unsafe_allow_html=True)
        st.markdown("**Annualized Volatility (30D)**")
        st.markdown(f"<div class='metric-lg'>{_safe_pct(sig['vol_annual'])}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with s2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("**Last Golden Cross**")
        st.markdown(f"<div class='metric-lg'>{sig['last_golden'].strftime('%Y-%m-%d') if sig['last_golden'] else '—'}</div>", unsafe_allow_html=True)
        st.markdown("<hr class='hr'/>", unsafe_allow_html=True)
        st.markdown("**Last Death Cross**")
        st.markdown(f"<div class='metric-lg'>{sig['last_death'].strftime('%Y-%m-%d') if sig['last_death'] else '—'}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with s3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("**Insight**")
        st.info(sig["risk_note"])
        st.markdown("</div>", unsafe_allow_html=True)

# ============ STRATEGY ============
with tab_strategy:
    st.subheader("MA7 / MA30 — Long-Only Strategy")
    bt = backtest_ma(df)
    if not bt["ok"]:
        st.warning(bt["msg"])
    else:
        m = bt["metrics"]
        m1,m2,m3,m4,m5,m6 = st.columns(6, gap="small")
        for col, title, val, is_pct in [
            (m1,"Strategy CAGR", m["Strategy CAGR"], True),
            (m2,"Buy&Hold CAGR", m["Buy&Hold CAGR"], True),
            (m3,"Strat Max DD",   m["Strategy Max DD"], True),
            (m4,"B&H Max DD",     m["Buy&Hold Max DD"], True),
            (m5,"Strat Sharpe",   m["Strategy Sharpe"], False),
            (m6,"B&H Sharpe",     m["Buy&Hold Sharpe"], False),
        ]:
            with col:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"**{title}**")
                st.markdown(f"<div class='metric-lg'>{_safe_pct(val) if is_pct else f'{val:.2f}'}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        # Curves
        curve_df = pd.DataFrame({
            "time": bt["dfx"]["time"].values,
            "Strategy": bt["strat_curve"].values,
            "Buy & Hold": bt["bh_curve"].values
        })
        fig_bt = go.Figure()
        fig_bt.add_trace(go.Scatter(x=curve_df["time"], y=curve_df["Strategy"], mode="lines", name="Strategy"))
        fig_bt.add_trace(go.Scatter(x=curve_df["time"], y=curve_df["Buy & Hold"], mode="lines", name="Buy & Hold"))
        fig_bt.update_layout(template=template, title="Equity Curves (normalized to 1.0)",
                             height=380, margin=dict(l=30,r=30,t=40,b=30), yaxis_title="Equity")
        st.plotly_chart(fig_bt, use_container_width=True)

# ============ DATA ============
with tab_data:
    st.subheader("Historical Data")
    st.dataframe(df[["time","open","high","low","close","volume"]].tail(20),
                 use_container_width=True, hide_index=True)
    st.download_button("📥 Download CSV",
                       df.to_csv(index=False).encode(),
                       file_name=f"sol_ohlc_{days}d.csv",
                       mime="text/csv")
