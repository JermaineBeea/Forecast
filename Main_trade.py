# 1. Import necessary modules and functions
import os
import time
import json
import pickle
from functools import partial
import pandas as pd
import numpy as np
from Modules.Forecast import forecastData
from Modules.Forex import exchangeRate, get_conversion_rate, get_asset_price

def format_value(value):
    """Formats the value based on rounding and scientific notation settings."""
    if isinstance(value, (int, float)):
        if should_round:
            value = round(value, rounding_precision)
        if use_scientific_notation:
            return f'{value:e}'
    return value

# Set display options for pandas and numpy
np.set_printoptions(threshold=np.inf)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_seq_items', None)

# 2. Configuration: Data handling and formatting options
fetch_external_data = True
save_external_data = True
use_binary_format = False 
use_json_format = False
use_csv_format = True

# Configuration for data formatting
should_round = True
rounding_precision = 5
use_scientific_notation = False

# Configuration for writing variables
allow_file_overwrite = True
save_to_json = False

# Determine if trading an asset or a forex currency
asset_trading = True


# 3. Constants: Trading settings
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
sell_unit = 'IBIT'
buy_unit = 'USD' if not asset_trading else 'USD'
currency_investment = 'USD' if not asset_trading else 'IBIT'
profit_currency = 'ZAR'
price_spread = 0.05
borrowing_fee = 0
initial_investment = 1000 

# 4. File paths and parameters
local_data_path = r'/home/wtc/Documents/RepositoryAccounts/Personal_GitHUb/Forecast/Trade Data/EURAUD.ifx.csv'
trade_folder_path = f'Trade_of_{sell_unit}_{buy_unit}/'
variable_file_name = f'{trade_folder_path}{sell_unit}{buy_unit}.py'
external_data_file_name = f'{sell_unit}{buy_unit}_data'

param_period = {
'start_date': None,
'end_date': None,
'period': '1d',
'interval': '1m'
}
field = 'Close'

# Function to be used to get the forecats of data
FUNCTION_FORECAST = forecastData

# Ensure trade folder exists
os.makedirs(os.path.dirname(trade_folder_path), exist_ok=True) if os.path.dirname(trade_folder_path) else None


# 5. Data Loading: Fetch or load data for trading
if fetch_external_data:
    # Fetch asset or conversion rate data

    raw_data = (
        partial(get_asset_price,ticker_symbol = sell_unit, **param_period)()
        if asset_trading else 
        partial(get_conversion_rate, sell_unit, buy_unit, **param_period)()
    )
else:
    # Load from local file if not fetching data
    raw_data = pd.read_csv(local_data_path, sep='\t')

# Drop empty fields
raw_data = raw_data.dropna()

# Save fetched data to specified format
if save_external_data:
    # Determine file format based on user settings
    file_extension = '.json' if use_json_format else '.pkl' if use_binary_format else '.csv' if use_csv_format else '.txt'
    file_mode = 'wb' if use_binary_format else 'w'
    with open(f'{trade_folder_path}{external_data_file_name}{file_extension}', mode=file_mode) as file:
        if use_binary_format:
            pickle.dump(raw_data, file)
        elif use_json_format:
            raw_data_json = raw_data.to_json()
            json.dump(raw_data_json, file)
        elif use_csv_format:  
            file.write(str(raw_data))
        else:
            raw_data = pd.DataFrame(raw_data)
            file.write(str(raw_data))
                   
data_list = raw_data[field].dropna().to_list()

# 6. Forecasting: Calculate forecast distribution and risk
current_exchange_rate = data_list[-1]
forecast_period = len(data_list)/3
forecast_distribution = FUNCTION_FORECAST(data_list, current_exchange_rate, period=forecast_period)
