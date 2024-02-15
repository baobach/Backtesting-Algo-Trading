import sys
sys.path.append("/Users/baobach/Backtesting-Algo-Trading")
import os
import sys
import pandas as pd
from openbb import obb
from src.config import get_api_key
from src.utils import DataWrangler

# Load equities list
pat = get_api_key()
obb.account.login(pat=pat)
tickers = obb.index.constituents("dowjones").to_df()['symbol']

# Create an instance of the datawrangler class
start_date = '2020-01-01'
end_date = '2023-01-01'
dw = DataWrangler()

# Download data for each ticker in the list
for ticker in tickers:
    df = dw.download_data(ticker = ticker, start_date = start_date, end_date = end_date)
    df.to_csv(f'./data/raw/{ticker}.csv')


