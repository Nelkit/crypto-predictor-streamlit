import streamlit as st
import pandas as pd
import students.ethereum.components.chart as chart
import students.ethereum.components.news as news
import students.ethereum.components.about as about
import students.ethereum.components.historical_data as historical_data

from importlib import reload
reload(chart)
reload(news)
reload(about)
reload(historical_data)

def render_view(coin_metadata: dict = None, ohlc_df: pd.DataFrame = None, news_df: pd.DataFrame = None):
    with st.container(horizontal_alignment="center"):
        view_options = {
            0: "Chart",
            1: "Historical Data",
            2: "News",
            3: "About",
        }
        selected_view = st.segmented_control(
            "Select View",
            options=view_options.keys(),
            format_func=lambda option: view_options[option],
            selection_mode="single",
            label_visibility="hidden",
            default=0
        )
    with st.container(border=True):
        if selected_view == 0:
            chart.render_view(ohlc_df)
        elif selected_view == 1:
            historical_data.render_view(ohlc_df)
        elif selected_view == 2:
            news.render_view(news_df)
        elif selected_view == 3:
            about.render_view(coin_metadata)