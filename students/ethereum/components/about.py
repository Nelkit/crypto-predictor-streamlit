import streamlit as st

from students.ethereum.components import footer


def render_view(coin_metadata: dict = None):
	price_usd = coin_metadata.get("current_price", 0)
	market_cap_usd = coin_metadata.get("market_cap", 0)
	total_volume_usd = coin_metadata.get("total_volume", 0)
	hash_algo = coin_metadata.get("hashing_algorithm", "N/A")
	homepage_url = coin_metadata.get("homepage")
	explorer_url = coin_metadata.get("blockchain_site")
	category_list = coin_metadata.get("categories", [])
	description_text = coin_metadata.get("description", "").replace("\r\n", "\n\n")
	coin_name = coin_metadata.get("name", "Ethereum")

	st.subheader("📊 Market overview")

	col1, col2, col3 = st.columns(3)
	with col1:
		st.metric("Current price", f"${price_usd:,.2f}")
	with col2:
		st.metric("Market cap", f"${market_cap_usd:,.0f}")
	with col3:
		st.metric("24h volume", f"${total_volume_usd:,.0f}")

	st.divider()
	st.subheader(f"🧠 {coin_name} overview")
	st.markdown(description_text)

	st.divider()
	st.subheader("⚙️ Technical details")

	st.markdown(f"**Hashing algorithm:** {hash_algo}")
	if homepage_url:
		st.markdown(f"**Website:** [Visit site]({homepage_url})")
	if explorer_url:
		st.markdown(f"**Explorer:** [View on Etherscan]({explorer_url})")

	st.divider()
	st.subheader("🏷️ Categories")

	if category_list:
		st.write(", ".join(category_list))
	else:
		st.write("No categories available.")

	st.divider()
	footer.render_view("Market data provided by CoinGecko API (Public Free Tier).")
