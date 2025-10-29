import streamlit as st
import pandas as pd
import students.ethereum.components.footer as footer

def render_view(news_df: pd.DataFrame=None):
    """Render cryptocurrency news in a clean, modern Streamlit interface."""

    st.subheader("📰 Latest News")

    st.divider()

    if news_df is None or news_df.empty:
        st.info("No news articles available at the moment.")
        return

    for _, row in news_df.iterrows():
        # Safely extract fields
        title = row.get("title") or "Untitled"
        url = row.get("url") or "#"
        source = row.get("source") or "Unknown"
        body = row.get("body") or "..."
        published_on = row.get("published_on")

        # Format date
        if isinstance(published_on, (int, float)):
            published_str = pd.to_datetime(published_on, unit="s").strftime("%b %d, %Y %H:%M")
        elif isinstance(published_on, pd.Timestamp):
            published_str = published_on.strftime("%b %d, %Y %H:%M")
        else:
            published_str = "Unknown date"

        # === Card style ===
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
