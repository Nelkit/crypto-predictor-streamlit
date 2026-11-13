import streamlit as st
import students.ethereum.components.footer as footer
from students.ethereum.controller import (
    fetch_ethereum_related_news,
)
from students.ethereum.utils.helpers import format_datetime

def render_view(title: str = "📰 Market News"):
    """
    Renders the news view for Ethereum.

    This function displays a subheader, fetches Ethereum-related news, and renders
    each news article in a card-style layout with title, source, publication date,
    and a truncated body. Includes a footer with data source attribution.

    Args:
        title (str, optional): The title to display as subheader. Defaults to "📰 Market News".

    Returns:
        None: This function renders UI elements directly using Streamlit.
    """

    st.subheader(title)
    st.divider()

    # Fetch Ethereum-related news
    news_df = fetch_ethereum_related_news(limit=10)

    if news_df is None or news_df.empty:
        st.info("No news available right now.")
        return

    for _, row in news_df.iterrows():
        title = row.get("title") or "Untitled"
        url = row.get("url") or "#"
        source = row.get("source") or "Unknown"
        body = row.get("body") or "..."
        published_on = row.get("published_on")

        # Format publication date
        published_str = format_datetime(published_on)

        # Render news card
        st.markdown(
            f"""
            <div style="
                background-color: var(--background-color);
                padding: 0rem 1.5rem;
            ">
                <h4>
                    <a href="{url}" target="_blank" style="text-decoration: none; color: #0073e6;">
                        {title}
                    </a>
                </h4>
                <p style="color: gray; font-size: 0.9rem; margin-bottom: 0.6rem;">
                    Source: <b>{source}</b> &nbsp;|&nbsp; {published_str}
                </p>
                <p style="font-size: 0.95rem; color: var(--secondary-text-color); line-height: 1.5;">
                    {body[:400]}{'...' if len(body) > 400 else ''}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

    footer.render_view("News data provided by CryptoNews API by NewsData (Public Free Tier)")
