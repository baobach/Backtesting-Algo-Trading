import os
import pandas as pd
import backtrader as bt

class DataManager:
    def __init__(self):
        """
        Manage the data in the `data` folder. Provides methods to get available tickers and load ticker data.
        - get_available_tickers(): Returns a list of available tickers.
        - load_ticker_data(ticker): Loads the data for a specific ticker.
        - cerebro_add_data(ticker1, ticker2, cerebro): Loads and adds the data for two tickers to the cerebro engine.
        """
        self.data_folder = '../data/raw'

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
        df = df.set_index('date')  # Set the index as the date column
        return df
    
    def cerebro_add_data(self, ticker1, ticker2, cerebro):
        """
        Loads and adds the data for two tickers to the cerebro engine.

        It checks if the ticker data files exist in the data_folder.
        If any of the files do not exist, it raises a ValueError.
        Otherwise, it reads the CSV files using pandas and adds the data to the cerebro engine.

        Parameters:
        - ticker1 (str): The ticker symbol for the first data to load and add.
        - ticker2 (str): The ticker symbol for the second data to load and add.
        - cerebro (backtrader.Cerebro): The cerebro engine to add the data to.
        """
        file_path1 = os.path.join(self.data_folder, f'{ticker1}.csv')
        file_path2 = os.path.join(self.data_folder, f'{ticker2}.csv')
        if not os.path.exists(file_path1):
            raise ValueError(f'Ticker data for {ticker1} does not exist.')
        if not os.path.exists(file_path2):
            raise ValueError(f'Ticker data for {ticker2} does not exist.')
        data1 = bt.feeds.YahooFinanceCSVData(dataname=file_path1)
        data2 = bt.feeds.YahooFinanceCSVData(dataname=file_path2)
        cerebro.adddata(data1, name=ticker1)
        cerebro.adddata(data2, name=ticker2)