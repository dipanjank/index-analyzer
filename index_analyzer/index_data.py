import investpy
from index_analyzer.components import index_components


class IndexDataProvider:

    def __init__(self, country):
        assert country in ('netherlands', 'germany')
        self._country = country

    def get_available_indices(self):
        indices = investpy.get_indices(self._country)
        names = indices.name.sort_index().tolist()
        return names

    def get_index_data(self, name, start_date, end_date):
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

    def get_components_overview(self, name):
        tickers = index_components['AEX']
        overview = investpy.get_stocks_overview(country=self._country)
        overview.loc[:, 'symbol'] = overview.symbol.str.upper()
        overview = overview.loc[overview.symbol.isin(tickers), :]
        return overview
