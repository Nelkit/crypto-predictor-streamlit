import streamlit as st
from students.ethereum.components import footer

def render_view(title:str="Market overview", coin_metadata: dict = None):
	"""
	Renders the about view for Ethereum.

	This function displays market performance metrics (current price, market cap, volume),
	an overview description, technical details (hashing algorithm, links), and categories.
	Includes a footer with data source attribution.

	Args:
		title (str, optional): The title parameter (not used in rendering). Defaults to "Market overview".
		coin_metadata (dict, optional): Dictionary with coin data such as price, market cap,
			volume, hashing algorithm, homepage, explorer, categories, description. Defaults to None.

	Returns:
		None: This function renders UI elements directly using Streamlit.
	"""
	price_usd = coin_metadata.get("current_price", 0)
	market_cap_usd = coin_metadata.get("market_cap", 0)
	total_volume_usd = coin_metadata.get("total_volume", 0)
	hash_algo = coin_metadata.get("hashing_algorithm", "N/A")
	homepage_url = coin_metadata.get("homepage")
	explorer_url = coin_metadata.get("blockchain_site")
	category_list = coin_metadata.get("categories", [])
	description_text = coin_metadata.get("description", "").replace("\r\n", "\n\n")
	coin_name = coin_metadata.get("name", "Ethereum")

	st.subheader("🏦 Market Performance - 24h Metrics")

	col1, col2, col3 = st.columns(3)
	with col1:
		st.metric("Current Price", f"${price_usd:,.2f}")
	with col2:
		st.metric("Market Cap", f"${market_cap_usd:,.0f}")
	with col3:
		st.metric("24h Volume", f"${total_volume_usd:,.0f}")

	st.divider()
	st.subheader(f"🧠 {coin_name} Overview")
	st.markdown(description_text)

	st.divider()
	st.subheader("⚙️ Technical Details")

	st.markdown(f"**Hashing algorithm:** {hash_algo}")
	if homepage_url:
		st.markdown(f"**Website:** [Visit site]({homepage_url})")
	if explorer_url:
		st.markdown(f"**Explorer:** [View on Etherscan]({explorer_url})")

	st.divider()
	st.subheader("🏷️ Ecosystem & Categories")

	if category_list:
		st.write(", ".join(category_list))
	else:
		st.write("No categories available.")

	st.divider()
	footer.render_view("Market data provided by CoinGecko API (Public Free Tier).")
