# main.py
import streamlit as st

# Define pages using native st.Page
home_page = st.Page("pages/1_Home.py", title="Home")
eth_page = st.Page("pages/2_Ethereum.py", title="Ethereum")
btc_page = st.Page("pages/3_Bitcoin.py", title="Bitcoin")
sol_page = st.Page("pages/4_Solana.py", title="Solana")
xrp_page = st.Page("pages/5_XRP.py", title="XRP")

# Build navigation with hidden position
pg = st.navigation([home_page, eth_page, btc_page, sol_page, xrp_page], position="hidden")

# Set page config
st.set_page_config(
    page_title="Crypto Prediction Dashboard - Group 6",
    page_icon="💹",
    layout="wide"
)

# Custom CSS styles
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            width: 300px !important;
        }
        button[aria-label="Fullscreen"] {display: none;}
        img {
            pointer-events: none;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Custom sidebar content
st.sidebar.image("app/images/crypto-currency-logo.png", width="stretch")
st.sidebar.markdown("""
    <div width="100%" style="text-align: center;"> 
        <h1 style="font-weight:bold; margin:0; padding:0">CRYPTOCURRENCY</h1>
        <h2 style="margin-top:10px; padding:0">Prediction Dashboard</h2>
    </div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Page links
pages = [
    ("app/images/home-page.png", home_page, "Home"),
    ("app/images/ethereum-eth-logo.png", eth_page, "Ethereum"),
    ("app/images/bitcoin-btc-logo.png", btc_page, "Bitcoin"),
    ("app/images/solana-sol-logo.png", sol_page, "Solana"),
    ("app/images/xrp-xrp-logo.png", xrp_page, "XRP"),
]

for img_path, page, label in pages:
    col1, col2 = st.sidebar.columns([1, 8])
    with col1:
        st.image(img_path, width=40)
    with col2:
        st.page_link(page, label=label)

# Run the selected page
pg.run()