import streamlit as st

def render_tab():
	st.header("📊 Project Overview")

	with st.container():
		st.markdown(
			"""
			### 🔍 Overview  
			This dashboard presents a **machine learning–based cryptocurrency prediction system**  
			developed as part of the **AMLA AT3 – Group 6** project.
	
			### 💰 Cryptocurrencies  
			- **Bitcoin (BTC)**  
			- **Ethereum (ETH)**  
			- **XRP (XRP)**  
			- **Solana (SOL)**  
	
			### 🧩 Data Sources  
			- [TokenMetrics API](https://developers.tokenmetrics.com/reference/tokens)  
			- [CoinDesk API](https://developers.coindesk.com/documentation/data-api/introduction)
	
			### 🤖 Machine Learning Models  
			- Each student designed, trained, and deployed a distinct ML model.  
			- The models predict the **next-day HIGH price** of the selected cryptocurrency.
	
			### 🚀 Explore the App  
			Use the tabs above to view predictions, insights, and historical data  
			for each cryptocurrency model.
			"""
		)