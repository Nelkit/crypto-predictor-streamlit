# main.py
import streamlit as st

# Define pages using native st.Page
home_page = st.Page("pages/1_Home.py", title="Home")
eth_page = st.Page("pages/2_Ethereum.py", title="Ethereum")
btc_page = st.Page("pages/3_Bitcoin.py", title="Bitcoin")
sol_page = st.Page("pages/4_Solana.py", title="Solana")
xrp_page = st.Page("pages/5_XRP.py", title="XRP")

# Create navigation with hidden position to allow custom sidebar
pg = st.navigation([home_page, eth_page, btc_page, sol_page, xrp_page], position="hidden")

st.set_page_config(
    page_title="Crypto Prediction Dashboard - Group 6",
    page_icon="💹",
    layout="wide"
)
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            width: 300px; /* Ancho fijo */
        }
    </style>
    """,
    unsafe_allow_html=True
)
# Build custom sidebar navigation
st.sidebar.image("app/images/crypto-currency-logo.png", width="stretch")
st.sidebar.markdown("""
    <div width="100%" style="text-align: center;"> 
        <h1 style="font-weight:bold; margin:0; padding:0">CRYPTOCURRENCY</h1>
        <h2 style="margin-top:10px; padding:0">Prediction Dashboard</h2>
    </div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Home
# Ethereum
col1, col2 = st.sidebar.columns([1, 8])
with col1:
    st.image("app/images/home-page.png", width=40)
with col2:
    st.page_link(home_page, label="Home")

# Ethereum
col3, col4 = st.sidebar.columns([1, 8])
with col3:
    st.image("app/images/ethereum-eth-logo.png", width=40)
with col4:
    st.page_link(eth_page, label="Ethereum")

# Bitcoin
col5, col6 = st.sidebar.columns([1, 8])
with col5:
    st.image("app/images/bitcoin-btc-logo.png", width=40)
with col6:
    st.page_link(btc_page, label="Bitcoin")

# Solana
col7, col8 = st.sidebar.columns([1, 8])
with col7:
    st.image("app/images/solana-sol-logo.png", width=40)
with col8:
    st.page_link(sol_page, label="Solana")

# XRP
col9, col10 = st.sidebar.columns([1, 8])
with col9:
    st.image("app/images/xrp-xrp-logo.png", width=40)
with col10:
    st.page_link(xrp_page, label="XRP")

# Run the selected page
pg.run()
