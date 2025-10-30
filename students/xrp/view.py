import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# API Configuration
API_URL = "https://xrp-price-api-latest.onrender.com/predict/XRP"
HISTORICAL_API_URL = "https://xrp-price-api-latest.onrender.com/data/recent"

def _format_usd(x: float | int) -> str:
    """Format number as USD currency."""
    return f"${x:,.4f}"

def _format_volume(x: float | int) -> str:
    """Format volume numbers."""
    if x >= 1_000_000:
        return f"{x/1_000_000:.2f}M"
    elif x >= 1_000:
        return f"{x/1_000:.2f}K"
    return f"{x:.2f}"

def calculate_rsi(data: pd.Series, periods: int = 14) -> pd.Series:
    """Calculate Relative Strength Index."""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_bollinger_bands(data: pd.Series, window: int = 20, num_std: int = 2):
    """Calculate Bollinger Bands."""
    rolling_mean = data.rolling(window=window).mean()
    rolling_std = data.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return rolling_mean, upper_band, lower_band

@st.cache_data(ttl=120)  # cache for 2 minutes
def fetch_xrp_prediction():
    """Fetch XRP prediction from the API."""
    try:
        response = requests.get(API_URL, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"API Error: {str(e)}")

@st.cache_data(ttl=300)  # cache for 5 minutes
def fetch_xrp_historical(months: int = 3):
    """Fetch historical XRP data from the API."""
    try:
        response = requests.get(f"{HISTORICAL_API_URL}?months={months}", timeout=20)
        response.raise_for_status()
        data = response.json()
        
        # Convert to DataFrame
        df = pd.DataFrame(data.get("data", []))
        if not df.empty:
            df["time"] = pd.to_datetime(df["time"])
            df = df.sort_values("time").reset_index(drop=True)
        
        return df, data
    except Exception as e:
        raise Exception(f"Historical API Error: {str(e)}")

def render_tab():
    # Professional Header with XRP branding
    st.markdown("""
        <div style='background: linear-gradient(135deg, #23292F 0%, #3C4449 100%); 
                    padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h1 style='color: #FFFFFF; text-align: center; margin: 0; font-size: 2.5rem;'>
                🌊 XRP Trading Intelligence
            </h1>
            <p style='color: #B8BDC1; text-align: center; margin-top: 0.5rem; font-size: 1.1rem;'>
                Advanced Analytics & ML Predictions | Powered by Random Forest
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # === SECTION 1: ML PREDICTION SHOWCASE ===
    with st.spinner("🔮 Fetching AI prediction..."):
        try:
            data = fetch_xrp_prediction()
            prediction = data.get("prediction", {})
            latest_data = data.get("latest_data", {})
            
            current_high = latest_data.get("high", 0)
            predicted_high = prediction.get("next_day_high", 0)
            change_percent = prediction.get("expected_change_percent", 0)
            change_direction = prediction.get("expected_change_direction", "neutral")
            
            # Hero metrics with gradient cards
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%); 
                                padding: 1.5rem; border-radius: 10px; color: white;'>
                        <p style='margin:0; opacity:0.9; font-size:0.9rem;'>CURRENT HIGH</p>
                        <h2 style='margin:0.5rem 0; font-size: 2rem;'>{_format_usd(current_high)}</h2>
                        <p style='margin:0; opacity:0.8; font-size:0.85rem;'>📅 {latest_data.get('date', 'N/A')}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #F093FB 0%, #F5576C 100%); 
                                padding: 1.5rem; border-radius: 10px; color: white;'>
                        <p style='margin:0; opacity:0.9; font-size:0.9rem;'>AI PREDICTED HIGH</p>
                        <h2 style='margin:0.5rem 0; font-size: 2rem;'>{_format_usd(predicted_high)}</h2>
                        <p style='margin:0; opacity:0.8; font-size:0.85rem;'>🎯 {prediction.get('predicted_date', 'N/A')}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                color = "#10B981" if change_direction == "up" else "#EF4444" if change_direction == "down" else "#6B7280"
                arrow = "↗" if change_direction == "up" else "↘" if change_direction == "down" else "→"
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {color}22 0%, {color}44 100%); 
                                padding: 1.5rem; border-radius: 10px; border-left: 4px solid {color};'>
                        <p style='margin:0; opacity:0.8; font-size:0.9rem; color: #333;'>EXPECTED MOVEMENT</p>
                        <h2 style='margin:0.5rem 0; font-size: 2rem; color: {color};'>{arrow} {change_percent}%</h2>
                        <p style='margin:0; opacity:0.7; font-size:0.85rem; color: #555;'>🤖 Random Forest Model</p>
                    </div>
                """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"⚠️ Prediction API Error: {str(e)}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === SECTION 2: PROFESSIONAL TRADING ANALYTICS ===
    period_options = {"1 Week": (3, 7), "1 Month": (3, 30), "3 Months": (3, 90)}
    
    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.markdown("### 📊 Technical Analysis Dashboard")
    with col_b:
        selected_period = st.selectbox("Period", list(period_options.keys()), index=2)
    
    months_to_fetch, days_to_display = period_options[selected_period]
    
    with st.spinner("📈 Loading market data..."):
        try:
            df_historical, metadata = fetch_xrp_historical(months=months_to_fetch)
            
            if df_historical.empty:
                st.warning("No data available")
                return
            
            df = df_historical.tail(days_to_display).copy()
            
            # Calculate technical indicators
            df['RSI'] = calculate_rsi(df['close'])
            df['BB_middle'], df['BB_upper'], df['BB_lower'] = calculate_bollinger_bands(df['close'])
            df['returns'] = df['close'].pct_change() * 100
            df['volatility'] = df['returns'].rolling(window=7).std()
            
            # === CHART 1: Price Action with Bollinger Bands (Unique!) ===
            st.markdown("#### 🎯 Price Action & Volatility Bands")
            
            fig1 = go.Figure()
            
            # Bollinger Bands fill
            fig1.add_trace(go.Scatter(
                x=df['time'], y=df['BB_upper'],
                line=dict(width=0), showlegend=False, hoverinfo='skip'
            ))
            fig1.add_trace(go.Scatter(
                x=df['time'], y=df['BB_lower'],
                fill='tonexty', fillcolor='rgba(147, 112, 219, 0.1)',
                line=dict(width=0), showlegend=False, hoverinfo='skip'
            ))
            
            # Price line with gradient effect
            fig1.add_trace(go.Scatter(
                x=df['time'], y=df['close'],
                name='Close Price',
                line=dict(color='#8B5CF6', width=3),
                mode='lines'
            ))
            
            # Bollinger Band lines
            fig1.add_trace(go.Scatter(
                x=df['time'], y=df['BB_upper'],
                name='Upper Band',
                line=dict(color='rgba(255, 99, 132, 0.5)', width=1, dash='dash')
            ))
            fig1.add_trace(go.Scatter(
                x=df['time'], y=df['BB_lower'],
                name='Lower Band',
                line=dict(color='rgba(54, 162, 235, 0.5)', width=1, dash='dash')
            ))
            
            # MA7 and MA30
            if 'close_MA7' in df.columns:
                fig1.add_trace(go.Scatter(
                    x=df['time'], y=df['close_MA7'],
                    name='MA7', line=dict(color='#FFA500', width=2, dash='dot')
                ))
            
            fig1.update_layout(
                height=450,
                template='plotly_dark',
                hovermode='x unified',
                xaxis_title='Date',
                yaxis_title='Price (USD)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=10, r=10, t=40, b=10)
            )
            
            st.plotly_chart(fig1, use_container_width=True)
            
            with st.expander("💡 Trading Insight: Bollinger Bands"):
                st.markdown("""
                **What you're seeing:** Bollinger Bands measure market volatility and potential reversal points.
                - **Purple zone**: Normal trading range (95% of price action)
                - **Price touches upper band**: Potentially overbought (consider selling)
                - **Price touches lower band**: Potentially oversold (buying opportunity)
                - **Bands squeeze**: Low volatility, breakout likely imminent
                - **Bands expand**: High volatility, strong trend in motion
                """)
            
            # === CHART 2: RSI Momentum Indicator (Professional) ===
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### ⚡ RSI Momentum Oscillator")
                
                fig2 = go.Figure()
                
                # RSI line with color gradient
                colors = ['#EF4444' if x > 70 else '#10B981' if x < 30 else '#3B82F6' 
                         for x in df['RSI'].dropna()]
                
                fig2.add_trace(go.Scatter(
                    x=df['time'], y=df['RSI'],
                    name='RSI',
                    line=dict(color='#3B82F6', width=3),
                    fill='tozeroy',
                    fillcolor='rgba(59, 130, 246, 0.1)'
                ))
                
                # Overbought/Oversold zones
                fig2.add_hline(y=70, line_dash="dash", line_color="red", 
                              annotation_text="Overbought (70)", annotation_position="right")
                fig2.add_hline(y=30, line_dash="dash", line_color="green", 
                              annotation_text="Oversold (30)", annotation_position="right")
                fig2.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.5)
                
                # Highlight zones
                fig2.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1, line_width=0)
                fig2.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1, line_width=0)
                
                fig2.update_layout(
                    height=300,
                    template='plotly_white',
                    yaxis_title='RSI',
                    xaxis_title='Date',
                    yaxis=dict(range=[0, 100]),
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                st.markdown("#### 🎲 RSI Signal")
                current_rsi = df['RSI'].iloc[-1]
                
                if current_rsi > 70:
                    signal = "OVERBOUGHT"
                    color = "#EF4444"
                    emoji = "🔴"
                    advice = "Consider taking profits"
                elif current_rsi < 30:
                    signal = "OVERSOLD"
                    color = "#10B981"
                    emoji = "🟢"
                    advice = "Potential buying opportunity"
                else:
                    signal = "NEUTRAL"
                    color = "#3B82F6"
                    emoji = "🔵"
                    advice = "Market in equilibrium"
                
                st.markdown(f"""
                    <div style='background: {color}22; padding: 2rem; border-radius: 10px; 
                                border-left: 5px solid {color}; margin-top: 2rem;'>
                        <h3 style='color: {color}; margin: 0;'>{emoji} {signal}</h3>
                        <h1 style='color: {color}; margin: 0.5rem 0;'>{current_rsi:.1f}</h1>
                        <p style='margin: 0; color: #666;'>{advice}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.info("""
                **RSI Range:**
                - 0-30: Oversold
                - 30-70: Normal
                - 70-100: Overbought
                """)
            
            # === CHART 3: Volume Profile Analysis ===
            st.markdown("#### 📊 Volume & Price Distribution Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Volume bars with color coding
                fig3 = go.Figure()
                
                colors_vol = ['#10B981' if df.iloc[i]['close'] > df.iloc[i]['open'] 
                             else '#EF4444' for i in range(len(df))]
                
                fig3.add_trace(go.Bar(
                    x=df['time'], y=df['volume'],
                    name='Volume',
                    marker_color=colors_vol,
                    opacity=0.7
                ))
                
                # Add MA7 volume
                if 'volume_MA7' in df.columns:
                    fig3.add_trace(go.Scatter(
                        x=df['time'], y=df['volume_MA7'],
                        name='Volume MA7',
                        line=dict(color='#FFA500', width=2)
                    ))
                
                fig3.update_layout(
                    height=300,
                    template='plotly_white',
                    yaxis_title='Volume',
                    xaxis_title='Date',
                    showlegend=True,
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                
                st.plotly_chart(fig3, use_container_width=True)
            
            with col2:
                # Price distribution histogram
                fig4 = go.Figure()
                
                fig4.add_trace(go.Histogram(
                    y=df['close'],
                    nbinsy=30,
                    name='Price Distribution',
                    marker_color='#8B5CF6',
                    opacity=0.75
                ))
                
                # Add current price line
                current_price = df['close'].iloc[-1]
                fig4.add_hline(y=current_price, line_dash="dash", line_color="red",
                              annotation_text=f"Current: {_format_usd(current_price)}",
                              annotation_position="right")
                
                fig4.update_layout(
                    height=300,
                    template='plotly_white',
                    xaxis_title='Frequency',
                    yaxis_title='Price (USD)',
                    showlegend=False,
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                
                st.plotly_chart(fig4, use_container_width=True)
            
            st.markdown("""
            <div style='background: #F3F4F6; padding: 1rem; border-radius: 8px; border-left: 4px solid #3B82F6;'>
                <strong>📍 Volume Profile Insight:</strong> High volume at specific price levels indicates strong support/resistance. 
                The histogram shows where most trading occurred – these levels often act as price magnets.
            </div>
            """, unsafe_allow_html=True)
            
            # === ADVANCED METRICS DASHBOARD ===
            st.markdown("#### 🎯 Advanced Trading Metrics")
            
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            # Calculate advanced metrics
            volatility_7d = df['returns'].tail(7).std()
            avg_volume = df['volume'].mean()
            price_change_period = ((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0] * 100)
            max_gain = df['returns'].max()
            max_loss = df['returns'].min()
            sharpe_ratio = (df['returns'].mean() / df['returns'].std()) * np.sqrt(252) if df['returns'].std() > 0 else 0
            
            with col1:
                st.metric("7D Volatility", f"{volatility_7d:.2f}%", 
                         help="Standard deviation of daily returns")
            with col2:
                st.metric("Avg Volume", _format_volume(avg_volume),
                         help="Average daily trading volume")
            with col3:
                st.metric("Period Return", f"{price_change_period:+.2f}%",
                         delta=f"{price_change_period:.2f}%")
            with col4:
                st.metric("Max Daily Gain", f"{max_gain:.2f}%",
                         delta="Best day", delta_color="normal")
            with col5:
                st.metric("Max Daily Loss", f"{max_loss:.2f}%",
                         delta="Worst day", delta_color="inverse")
            with col6:
                st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}",
                         help="Risk-adjusted return metric")
            
            # === DATA DOWNLOAD ===
            with st.expander("💾 Download Data & API Response"):
                tab1, tab2 = st.tabs(["📊 Historical Data", "🤖 ML Prediction"])
                
                with tab1:
                    st.dataframe(df[['time', 'open', 'high', 'low', 'close', 'volume']].tail(20),
                                use_container_width=True, hide_index=True)
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Download CSV",
                        data=csv_data,
                        file_name=f"xrp_data_{selected_period.replace(' ', '_')}.csv",
                        mime="text/csv"
                    )
                
                with tab2:
                    try:
                        pred_data = fetch_xrp_prediction()
                        st.json(pred_data)
                    except:
                        st.error("Could not fetch prediction data")
                        
        except Exception as e:
            st.error(f"⚠️ Error loading market data: {str(e)}")