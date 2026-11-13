# 1_Home.py
import sys
import os
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# --- HEADER ---
st.title("📈 Cryptocurrency Prediction Dashboard")
st.caption("Developed for 36120 – Advanced Machine Learning Applications (Spring 2025)")

# --- INTRODUCTION ---
st.markdown(
    """
    Welcome to the **Crypto Prediction Dashboard**, an interactive data product developed by **Group 6 – AMLA AT3**.  
    This web app enables users to explore **historical cryptocurrency market data** and analyze **machine learning–based predictions** for next-day price highs.
    """
)

st.divider()

# --- PROJECT OVERVIEW ---
st.markdown(
    """
    ### 🔍 Project Overview  
    This dashboard demonstrates the full lifecycle of a **data-driven product**, from experimentation to deployment.  
    Each team member developed, trained, and deployed a **distinct machine learning model** for one of the major cryptocurrencies, exposing predictions through FastAPI microservices and integrating them into this unified Streamlit interface.
    """
)

# --- CRYPTOCURRENCIES ---
st.markdown(
    """
    ### 💰 Cryptocurrencies Monitored
    - [**<a href='/Ethereum' target='_self'>Ethereum (ETH)</a>**](/Ethereum) – Model by *Nelkit Isael Chavez* *(LSTM Neural Network)*  
    - [**<a href='/Bitcoin' target='_self'>Bitcoin (BTC)</a>**](/Bitcoin) – Model by *Juan David Rodríguez* *(LightGBM)*  
    - [**<a href='/Solana' target='_self'>Solana (SOL)</a>**](/Solana) – Model by *Mario Rubiano* *(Gradient Boosting)*  
    - [**<a href='/XRP' target='_self'>XRP (XRP)</a>**](/XRP) – Model by *Brayam Pineda* *(Random Forest)*  
    """,
    unsafe_allow_html=True,
)

# --- TECHNICAL STACK ---
st.markdown(
    """
        ### ⚙️ Technical Stack
        - **Frontend:** Streamlit  
        - **Backend:** FastAPI  
        - **Deployment:** Docker, Render  
        - **Programming Language:** Python 3.11.4  
        - **Machine Learning Libraries:** scikit-learn, TensorFlow (for LSTM), LightGBM
    """
)

# --- DATA SOURCES ---
with st.expander("📡 Data Sources", expanded=True):
    st.markdown(
        """
        - [CoinDesk API](https://developers.coindesk.com/documentation/data-api/introduction) – Provides historical and live market prices.  
        - [TokenMetrics API](https://developers.tokenmetrics.com/reference/tokens) – Supplies token fundamentals and technical indicators.  
        - [CoinGecko API](https://www.coingecko.com/en/api) – Used for real-time OHLC data visualization.  
        - **Deployed FastAPI Endpoints:** [Ethereum](https://crypto-forecast-api.onrender.com) | [Bitcoin](https://bitcoin-high-prediction.onrender.com) | [Solana](https://at3-36120-25sp-24900627-api.onrender.com) | [XRP](https://xrp-price-api-latest.onrender.com) – ML model predictions for next-day high prices.
        """
    )

# --- MACHINE LEARNING MODELS ---
with st.expander("🤖 Machine Learning Models", expanded=True):
    st.markdown(
        """
        Each student implemented a **unique algorithm** to predict the **next-day HIGH price** of their assigned cryptocurrency.  
        Models were trained and validated using historical OHLCV data to ensure robustness and generalization.  
        The best-performing models were deployed as **FastAPI microservices** on Render and connected to this Streamlit dashboard via REST APIs.
        """
    )

# --- HOW TO USE ---
st.markdown(
    """
    ### 🚀 How to Use This Dashboard
    1. Use the **sidebar menu** to navigate between pages.  
       - 🏠 *Home*: Overview of the project and its objectives.  
       - 💰 *Cryptocurrencies*: Access dedicated pages for Bitcoin, Ethereum, Solana, and XRP.  
    2. On each cryptocurrency page, explore **historical data**, **forecast visualizations**, and **market indicators**.  
    3. Review next-day **price predictions** and recent **crypto news** to support data-driven analysis.  
    4. Compare model performances across algorithms and assess their predictive behavior.  
    """
)

# --- PROJECT REPOSITORIES ---
st.markdown("### 📂 Project Repositories")

with st.container(border=True):
    st.markdown(
        """
        - 🧪 **Experimentation Repository:** [36120-25SP-Group6-AT3-Experiments](https://github.com/Nelkit/36120-25SP-group6-AT3-experimentation)  
          Contains all Jupyter notebooks, model training scripts, and analysis developed using the Cookiecutter Data Science structure.  

        - 🌐 **Streamlit App Repository:** [36120-25SP-Group6-AT3-Streamlit](https://github.com/Nelkit/36120-25SP-Group6-AT3-streamlit)  
          Hosts the deployed Streamlit web application integrating all model endpoints from the group members.  
        """
    )

# --- FOOTER ---
st.divider()
st.caption("© 2025 Group 6 – AMLA AT3 | University of Technology Sydney")
