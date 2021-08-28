import logging
import os
from datetime import datetime

import altair
import pandas as pd
import streamlit as st

from index_analyzer.index_data import IndexDataProvider


def show_index_time_series(result):
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


def index_time_series(data_provider, index_name, **kwargs):
    start_date = kwargs['start_date']
    end_date = kwargs['end_date']

    logging.info("Getting data for index: %s, from %s to %s",
                 index_name, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    result = data_provider.get_index_data(index_name, start_date, end_date)
    show_index_time_series(result)


def index_components(data_provider, index_name, **kwargs):
    summary = data_provider.get_components_overview(index_name)
    if not summary.empty:
        def highlight_change(value):
            value = str(value)
            colour = 'red' if value.startswith('-') else 'green'
            return f"color: {colour}"

        summary = summary.style.applymap(highlight_change, subset=['change', 'change_percentage'])
        st.write(summary)


def index_weightings(data_provider, index_name, **kwargs):
    st.dataframe(data_provider.get_weightings(index_name))


def index_sector_weightings(data_provider, index_name, **kwargs):
    st.dataframe(data_provider.get_sector_weightings(index_name))


def display_index_data(data_provider, index_name, start_date, end_date):
    """Calls the appropriate 'handler function' based on ``view_type``. The handler function implements one of the
    possible views for the different index related datasets, such as

    * time series plot of OHLC values per date
    * Details about each component stock such as prices, percentage change etc.
    * Per component weighting
    * Sector based weighting

    the handler functions fetch the data for the given index using the ``index_provider`` and display the data in the
    most appropriate format.
    """
    handlers = {
        'Time Series': index_time_series,
        'Components': index_components,
        'Weightings': index_weightings,
        'Sector Weightings': index_sector_weightings
    }
    view_type = st.session_state.get('view_type')

    if view_type not in handlers:
        logging.warning('View %s not supported, must be one of %s', view_type, list(handlers.keys()))
        return

    handlers[view_type](data_provider, index_name, start_date=start_date, end_date=end_date)
    st.title(f"{index_name}: {view_type}")


def main(country_code):
    country_code = country_code.upper()
    logging.info("Running for country %s", country_code)
    data_provider = IndexDataProvider(country_code=country_code)
    index_names = data_provider.get_available_indices()

    col1, col2, col3, col4 = st.columns(4)
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

    with col4:
        st.selectbox(
            'View',
            ['Time Series', 'Components', 'Weightings', 'Sector Weightings'],
            key='view_type',
            on_change=display_index_data,
            args=[data_provider, index_name, start_date, end_date],
        )


if __name__ == '__main__':
    country_code = os.environ.get('TARGET_COUNTRY', 'DE')
    logging.basicConfig(level=logging.INFO)
    main(country_code)
