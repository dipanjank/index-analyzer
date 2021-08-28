import functools
import logging
import os

import investpy
import pandas as pd
from pycountry import countries


@functools.lru_cache(maxsize=20)
def get_index_data(index_name):
    """
    Read the data file for the specified index if it exists, otherwise return an empty DataFrame. Cache the result
    so we only read once.
    """
    this_dir = os.path.basename(__file__)
    index_data = os.path.abspath(os.path.join(this_dir, '..', 'data', f"{index_name}.csv"))
    if os.path.isfile(index_data):
        logging.info("Reading %s", index_data)
        return pd.read_csv(index_data)
    else:
        return pd.DataFrame(data=[], columns=["Company", "Sector", "Ticker", "Weighting"])


class IndexDataProvider:

    def __init__(self, country_code):
        country_code = country_code.upper()
        assert country_code in ('NL', 'DE'), f"Country Code must be NL or DE, got {country_code} instead."
        country_name = countries.get(alpha_2=country_code).name.lower()
        self._country = country_name

    def get_available_indices(self):
        """Return the list of available indexes."""
        indices = investpy.get_indices(self._country)
        names = indices.name.sort_index().tolist()
        return names

    def get_index_data(self, name, start_date, end_date):
        """Return the time series of the index values between ``start_date`` and ``end_date``, both inclusive."""
        assert start_date < end_date
        start_date = start_date.strftime('%d/%m/%Y')
        end_date = end_date.strftime('%d/%m/%Y')

        data_df = investpy.get_index_historical_data(
            name, self._country,
            from_date=start_date, to_date=end_date
        )
        data_df.index.name = 'Date'
        if not data_df.index.empty:
            data_df.index = data_df.index.strftime('%Y/%m/%d')
        return data_df

    def preprocess_tickers(self, tickers):
        def remove_suffix(ticker):
            if ticker.endswith('Gn'):
                return ticker[:-2]
            elif ticker.endswith('G'):
                return ticker[:-1]
            else:
                return ticker

        if self._country == 'germany':
            return tickers.map(remove_suffix)
        else:
            return tickers

    def get_components_overview(self, index_name):
        index_data = get_index_data(index_name)
        if index_data.empty:
            logging.warning("No index overview found for %s", index_name)
            return pd.DataFrame()

        tickers = index_data.loc[:, 'Ticker'].tolist()
        overview = investpy.get_stocks_overview(country=self._country)
        overview.loc[:, 'symbol'] = overview.symbol.str.upper()
        overview = overview.loc[overview.symbol.isin(tickers), :].reset_index(drop=True)
        return overview

    def get_weightings(self, index_name):
        """Return the weightings of the individual stocks of the index. This is a DataFrame with two columns,
        ``Company`` and ``Weighting``."""
        index_data = get_index_data(index_name)
        if index_data.empty:
            logging.warning("No index weightings found for %s", index_name)
            return pd.DataFrame(data=[], columns=['Company', 'Weighting'])

        weightings = index_data.loc[:, ['Company', 'Weighting']]
        return weightings

    def get_sector_weightings(self, index_name):
        """Return the weightings of the sectors of the index. This is a DataFrame with two columns,
                ``Sector`` and ``Weighting``."""
        index_data = get_index_data(index_name)
        if index_data.empty:
            logging.warning("No index weightings found for %s", index_name)
            return pd.DataFrame(data=[], columns=['Sector', 'Weighting'])

        weightings = index_data.groupby('Sector')['Weighting'].sum().reset_index()
        return weightings
