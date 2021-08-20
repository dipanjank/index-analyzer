import logging
from datetime import datetime

import altair
import pandas as pd
import streamlit as st

from index_analyzer.index_data import IndexDataProvider


def show_index_price_chart(result):
    if result.empty:
        st.write('No data found.')
        return

    result = pd.melt(
        result,
        value_vars=['Open', 'High', 'Low', 'Close'],
        var_name='PriceType',
        value_name='Price',
        ignore_index=False
    )
    result = result.reset_index()

    hist_chart = altair.Chart(result).mark_line().encode(
        x=altair.X('Date:T', axis=altair.Axis(tickCount=20)),
        y='Price',
        color='PriceType'
    )
    st.altair_chart(hist_chart, use_container_width=True)


def display_index_data(data_provider, index_name, start_date, end_date):
    logging.info("Getting data for index: %s, from %s to %s",
                 index_name, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    result = data_provider.get_index_data(index_name, start_date, end_date)
    show_index_price_chart(result)
    summary = data_provider.get_components_overview(index_name)

    if not summary.empty:
        def highlight_change(value):
            value = str(value)
            colour = 'red' if value.startswith('-') else 'green'
            return f"color: {colour}"

        summary = summary.style.applymap(highlight_change, subset=['change', 'change_percentage'])
        st.write(summary)

    st.title(index_name)


def main():
    data_provider = IndexDataProvider(country='netherlands')
    index_names = data_provider.get_available_indices()

    col1, col2, col3 = st.columns(3)
    with col1:
        index_name = st.selectbox("Select index", index_names)
    with col2:
        start_date = st.date_input(
            "From",
            min_value=datetime(2021, 1, 1),
            value=datetime(2021, 8, 1),
        )
    with col3:
        end_date = st.date_input(
            "To",
            min_value=datetime(2021, 1, 2),
            value=datetime.utcnow()
        )

    st.button(
        label='Get Details',
        on_click=display_index_data,
        args=[data_provider, index_name, start_date, end_date]
    )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
