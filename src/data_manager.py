import os
import pandas as pd

class DataManager:
    def __init__(self):
        """
        Initializes a DataManager object.

        The data_folder attribute is set to the relative path '../data'.
        """
        self.data_folder = '../data'

    def get_available_tickers(self):
        """
        Returns a list of available tickers.

        It iterates through the files in the data_folder and extracts the ticker names from the file names.
        Only files with the '.csv' extension are considered.
        """
        tickers = []
        for file_name in os.listdir(self.data_folder):
            if file_name.endswith('.csv'):
                ticker = os.path.splitext(file_name)[0]
                tickers.append(ticker)
        return tickers

    def load_ticker_data(self, ticker):
        """
        Loads the data for a specific ticker.

        It checks if the ticker data file exists in the data_folder.
        If the file does not exist, it raises a ValueError.
        Otherwise, it reads the CSV file using pandas and returns the DataFrame.
        
        Parameters:
        - ticker (str): The ticker symbol for which to load the data.

        Returns:
        - df (pandas.DataFrame): The loaded ticker data as a DataFrame.
        """
        file_path = os.path.join(self.data_folder, f'{ticker}.csv')
        if not os.path.exists(file_path):
            raise ValueError(f'Ticker data for {ticker} does not exist.')
        df = pd.read_csv(file_path)
        return df