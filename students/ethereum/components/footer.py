import streamlit as st

def render_view(message: str = "Data provided by CoinGecko API (Public Free Tier)."):
	"""Render footer with data source attribution."""
	with st.container():
		st.markdown(
			f"<p style='text-align:center; color:gray;'>{message}</p>",
			unsafe_allow_html=True,
		)