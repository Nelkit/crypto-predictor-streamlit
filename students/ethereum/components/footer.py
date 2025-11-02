import streamlit as st

def render_view(message: str = "Data provided by CoinGecko API (Public Free Tier)."):
	"""
	Renders a footer with data source attribution.

	This function displays a centered paragraph with the provided message,
	typically used to attribute data sources in the application.

	Args:
		message (str, optional): The message to display in the footer.
			Defaults to "Data provided by CoinGecko API (Public Free Tier)".

	Returns:
		None: This function renders UI elements directly using Streamlit.
	"""
	with st.container():
		st.markdown(
			f"<p style='text-align:center; color:gray;'>{message}</p>",
			unsafe_allow_html=True,
		)