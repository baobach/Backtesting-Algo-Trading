import yfinance as yf
import pandas as pd
import os

# Define the ticker symbol
ticker = "AAPL"

# Define the start and end dates
start_date = "2020-01-01"
end_date = "2023-12-31"

# Download the historical data
data = yf.download(ticker, start=start_date, end=end_date)

# Ensure the data directory exists
data_dir = "./data/"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Define the file path for saving the CSV file
csv_file = os.path.join(data_dir, f"{ticker}_{start_date}_{end_date}.csv")

# Save the data as a CSV file
data.to_csv(csv_file)

print(f"Data saved successfully as {csv_file}")
