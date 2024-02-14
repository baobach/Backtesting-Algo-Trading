import pandas as pd
from openbb import obb
from config import get_api_key

class DataWrangler:
    """
    A class for downloading historical data for a given ticker.

    Attributes:
        pat (str): The personal access token for authentication.
        start_date (str): The start date for the historical data.
        end_date (str): The end date for the historical data.

    Methods:
        download_data(ticker): Downloads historical data for the given ticker.

    """

    def __init__(self):
        self.pat = get_api_key()
        obb.account.login(pat=self.pat)
        self.start_date = '2020-01-01'
        self.end_date = '2023-01-01'

    def download_data(self, ticker, start_date, end_date):
        """
        Downloads historical data for the given ticker.

        Args:
            ticker (str): The ticker symbol for the desired stock.
            start_date (str): The start date for the historical data.
            end_date (str): The end date for the historical data.

        Returns:
            pandas.DataFrame: The historical data for the given ticker.

        """
        historical_data = obb.equity.price.historical(ticker, interval='1d', start_date=start_date, end_date=end_date).to_df()
        return historical_data