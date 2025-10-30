import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go

# API Configuration
API_URL = "https://xrp-price-api-latest.onrender.com/predict/XRP"
HISTORICAL_API_URL = "https://xrp-price-api-latest.onrender.com/data/recent"

def _format_usd(x: float | int) -> str:
    """Format number as USD currency."""
    return f"${x:,.4f}"

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
    # Header
    st.markdown(
        """
        <hr style="border: none; border-top: 2px solid #ccc; margin-top: 0.5em; margin-bottom: 0.5em;">
        <h2 style='text-align:center; color:#333333;'>XRP Analysis & Prediction</h2>
        <p style='text-align:center; color:#666666;'>Student: Brayam</p>
        <hr style="border: none; border-top: 2px solid #ccc; margin-top: 0.5em; margin-bottom: 1em;">
        """,
        unsafe_allow_html=True
    )
    
    # Fetch prediction data
    st.subheader("🔮 Next-Day HIGH Price Prediction")
    
    with st.spinner("Fetching prediction from API..."):
        try:
            data = fetch_xrp_prediction()
            
            # Extract data
            prediction = data.get("prediction", {})
            latest_data = data.get("latest_data", {})
            
            current_high = latest_data.get("high", 0)
            predicted_high = prediction.get("next_day_high", 0)
            current_date = latest_data.get("date", "N/A")
            predicted_date = prediction.get("predicted_date", "N/A")
            model_name = data.get("model", "Unknown")
            change_percent = prediction.get("expected_change_percent", 0)
            change_direction = prediction.get("expected_change_direction", "neutral")
            
            # Display metrics in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(
                    "<h4 style='color:#002fa7; font-weight:600;'>Current HIGH (XRP-USD)</h4>",
                    unsafe_allow_html=True
                )
                st.metric("Current Price", _format_usd(current_high))
                st.caption(f"As of {current_date}")
            
            with col2:
                st.markdown(
                    "<h4 style='color:#FF4B4B; font-weight:600;'>Predicted HIGH (XRP-USD)</h4>",
                    unsafe_allow_html=True
                )
                st.metric("Next-Day Prediction", _format_usd(predicted_high))
                st.caption(f"For {predicted_date}")
            
            with col3:
                st.markdown(
                    "<h4 style='color:#28a745; font-weight:600;'>Expected Change</h4>",
                    unsafe_allow_html=True
                )
                delta_symbol = "📈" if change_direction == "up" else "📉" if change_direction == "down" else "➡️"
                st.metric("Change", f"{change_percent}%", delta=f"{delta_symbol} {change_direction}")
                st.caption(f"Model: {model_name}")
            
            st.divider()
            
            # Current Market Data
            st.subheader("📊 Current Market Data")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Open", _format_usd(latest_data.get("open", 0)))
            with col2:
                st.metric("High", _format_usd(latest_data.get("high", 0)))
            with col3:
                st.metric("Low", _format_usd(latest_data.get("low", 0)))
            with col4:
                st.metric("Close", _format_usd(latest_data.get("close", 0)))
            with col5:
                volume = latest_data.get("volume", 0)
                st.metric("Volume", f"{volume:,.0f}")
            
            st.divider()
            
            # Model Information
            st.subheader("🤖 Model Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"""
                **Model Used:** {model_name}
                
                **Prediction Date:** {predicted_date}
                
                **Timestamp:** {data.get('timestamp', 'N/A')}
                """)
            
            with col2:
                st.warning(f"""
                **Disclaimer:**
                
                {data.get('disclaimer', 'This prediction is for informational purposes only.')}
                """)
            
            # Show raw API response (optional, for debugging)
            with st.expander("🔍 View Full API Response"):
                st.json(data)
                
        except Exception as e:
            st.error(f"⚠️ Could not fetch prediction: {str(e)}")
            st.info(f"""
            **Troubleshooting:**
            - The API might be experiencing cold start delays
            - Try refreshing the page in a few seconds
            - API URL: {API_URL}
            """)
    
    st.divider()
    
    # Historical Data Section
    st.subheader("📈 Historical Price Data & Analysis")
    
    # Period selection
    period_options = {
        "Last Week": (3, 7),  # fetch 3 months, display last 7 days
        "Last Month": (3, 30),  # fetch 3 months, display last 30 days
        "Last 3 Months": (3, 90)  # fetch 3 months, display all
    }
    
    selected_period = st.radio(
        "Select time period:",
        options=list(period_options.keys()),
        horizontal=True,
        index=2  # Default to 3 months
    )
    
    months_to_fetch, days_to_display = period_options[selected_period]
    
    with st.spinner(f"Loading {selected_period.lower()} data..."):
        try:
            df_historical, metadata = fetch_xrp_historical(months=months_to_fetch)
            
            if df_historical.empty:
                st.warning("No historical data available.")
            else:
                # Filter to display period
                df_display = df_historical.tail(days_to_display).copy()
                
                # Create interactive candlestick chart with moving averages
                fig = go.Figure()
                
                # Add candlestick
                fig.add_trace(go.Candlestick(
                    x=df_display["time"],
                    open=df_display["open"],
                    high=df_display["high"],
                    low=df_display["low"],
                    close=df_display["close"],
                    name="XRP/USDT",
                    increasing_line_color='#26a69a',
                    decreasing_line_color='#ef5350'
                ))
                
                # Add Moving Averages (if available)
                if "close_MA7" in df_display.columns:
                    fig.add_trace(go.Scatter(
                        x=df_display["time"],
                        y=df_display["close_MA7"],
                        mode="lines",
                        name="MA7",
                        line=dict(color='#FFA726', width=2)
                    ))
                
                if "close_MA30" in df_display.columns and selected_period != "Last Week":
                    fig.add_trace(go.Scatter(
                        x=df_display["time"],
                        y=df_display["close_MA30"],
                        mode="lines",
                        name="MA30",
                        line=dict(color='#42A5F5', width=2)
                    ))
                
                # Update layout
                fig.update_layout(
                    title=f"XRP/USDT Price Chart - {selected_period}",
                    xaxis_title="Date",
                    yaxis_title="Price (USD)",
                    xaxis_rangeslider_visible=False,
                    height=600,
                    hovermode='x unified',
                    template="plotly_white",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display key statistics
                st.markdown("#### 📊 Period Statistics")
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    period_high = df_display["high"].max()
                    st.metric("Period High", _format_usd(period_high))
                
                with col2:
                    period_low = df_display["low"].min()
                    st.metric("Period Low", _format_usd(period_low))
                
                with col3:
                    avg_price = df_display["close"].mean()
                    st.metric("Average Close", _format_usd(avg_price))
                
                with col4:
                    total_volume = df_display["volume"].sum()
                    st.metric("Total Volume", f"{total_volume:,.0f}")
                
                with col5:
                    # Calculate price change
                    price_change = ((df_display.iloc[-1]["close"] - df_display.iloc[0]["close"]) / 
                                   df_display.iloc[0]["close"] * 100)
                    st.metric("Period Change", f"{price_change:+.2f}%")
                
                # Data info
                st.caption(f"""
                📅 **Data Range:** {df_display['time'].min().strftime('%Y-%m-%d')} to {df_display['time'].max().strftime('%Y-%m-%d')}  
                📊 **Records:** {len(df_display)} days  
                🔄 **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """)
                
                # Downloadable data
                with st.expander("💾 Download Historical Data"):
                    st.dataframe(
                        df_display[["time", "open", "high", "low", "close", "volume"]].tail(10),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    csv_data = df_display.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Download Full Dataset (CSV)",
                        data=csv_data,
                        file_name=f"xrp_historical_{selected_period.replace(' ', '_').lower()}.csv",
                        mime="text/csv"
                    )
                
        except Exception as e:
            st.error(f"⚠️ Could not fetch historical data: {str(e)}")
            st.info("The API might be experiencing issues. Please try again later.")