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

"""CLOSING RATE"""
min_closing_rate, closing_rate, max_closing_rate = forecast_distribution
if asset_trading: initial_investment = initial_investment*closing_rate


forecast_distribution = [
    min_closing_rate,
    float(np.mean([min_closing_rate, closing_rate])),
    closing_rate,
    float(np.mean([closing_rate, max_closing_rate])),
    max_closing_rate
]

# Calculate immediate risk factor
immediate_risk_factor = current_exchange_rate/(current_exchange_rate + price_spread) - 1


# 7. Trade Action Logic: Determine trade action based on forecast
if closing_rate < current_exchange_rate - price_spread:
    trade_action = f'SELL {sell_unit}{buy_unit}'
    active_currency_a = sell_unit
    active_currency_b = buy_unit
    distr_profit_factor = [
        current_exchange_rate / (closing_rate + price_spread) - (1 + borrowing_fee) for closing_rate in forecast_distribution
    ]
elif closing_rate > current_exchange_rate + price_spread:
    trade_action = f'BUY {buy_unit}{sell_unit}'
    active_currency_a = buy_unit
    active_currency_b = sell_unit
    distr_profit_factor = [
        closing_rate / (current_exchange_rate + price_spread) - 1 for closing_rate in forecast_distribution
    ]


# 8. Rate Calculations: Calculate investment and profit rates
if asset_trading:
    investment_rate_a = (
        exchangeRate(currency_investment, buy_unit) / current_exchange_rate
        if trade_action.split()[0] == 'SELL'
        else exchangeRate(currency_investment, buy_unit)
    )
    profit_rate_a = (
        exchangeRate(buy_unit, profit_currency) * current_exchange_rate 
        if trade_action.split()[0] == 'SELL'
        else exchangeRate(buy_unit, profit_currency)
    )
else:
    investment_rate_a = exchangeRate(currency_investment, active_currency_a)
    profit_rate_a = exchangeRate(active_currency_a, profit_currency)


# 9. Sample Calculations: Risk and true profit distributions
sample_risk = initial_investment * investment_rate_a * profit_rate_a * immediate_risk_factor

if trade_action.split()[0] == 'SELL':
    sample_profit_distribution = []
    
    for profit_factor in distr_profit_factor:
        # True Profit calculation based on the formula
        trade_profit = initial_investment * investment_rate_a * profit_factor
        true_profit = trade_profit - initial_investment * borrowing_fee  # Deduct borrowing fee
        
        # Gains calculation if trade profit >= borrowing fee
        if (profit_factor / (profit_factor + price_spread)) >= (1 + borrowing_fee):
            gain = initial_investment * investment_rate_a * profit_rate_a * (profit_factor / (profit_factor + price_spread) - (1 + borrowing_fee))
            sample_profit_distribution.append(gain)
        else:
            # Loss calculation if trade profit < borrowing fee
            loss = (initial_investment * investment_rate_a / profit_rate_a) * (profit_factor / (profit_factor + price_spread) - (1 + borrowing_fee))
            sample_profit_distribution.append(loss)
else:
    # For BUY action, simpler profit calculation (no borrowing fee involved)
    sample_profit_distribution = [
        initial_investment * investment_rate_a * profit_rate_a * profit_factor
        for profit_factor in distr_profit_factor
    ]

# Calculate max possible loss
sample_max_possible_loss = min(sample_profit_distribution)


# 10. Output: Prepare and format output variables
output_variables = {
    'rate_given': f'"{sell_unit}{buy_unit}"',
    'time_of_trade': f"'{current_time}'",
    'trade_action': f'"{trade_action}"',
    'currency_investment': f'"{currency_investment}"',
    'currency_profit': f'"{profit_currency}"',
    'FUNCTION_FORECASTtion': f'"{FUNCTION_FORECAST.__name__}"',
}

for key, val in param_period.items():
    output_variables[key] = f"'{val}'"

output_variables.update(
{
    f'forecast_size': forecast_period,
    'price_spread': price_spread,
    'borrowing_fee': borrowing_fee,
    f'{currency_investment}_to_{active_currency_a}': investment_rate_a,
    f'{profit_currency}_to_{active_currency_a}': 1 / profit_rate_a,
    'initial_investment': initial_investment,
    'immediate_risk_factor': immediate_risk_factor,
    'sample_immediate_risk': sample_risk,
    'forecast_closing_rates': forecast_distribution,
    'distr_profit_factor': distr_profit_factor,
    'sample_profit_distribution': sample_profit_distribution,
    'rate_opening'.upper(): current_exchange_rate,
    'expected_closing_rate'.upper(): closing_rate,
    'expected_sample_profit': sample_profit_distribution[len(sample_profit_distribution) // 2],
    'sample_max_possible_loss': sample_max_possible_loss
}
)

# Format output values for writing
formatted_output_variables = {key: [format_value(v) for v in val] if isinstance(val, list) else format_value(val) for key, val in output_variables.items()}


# 11. File Handling: Write output to file if allowed
file_exists = False
try:
    with open(variable_file_name):
        file_exists = True
except FileNotFoundError:
    pass

if (allow_file_overwrite and file_exists) or not file_exists:
    try:
        if save_to_json:
            with open(variable_file_name, mode='x' if not allow_file_overwrite else 'w') as file:
                json.dump(formatted_output_variables, file, indent=4)
        else:
            with open(variable_file_name, mode='x' if not allow_file_overwrite else 'w') as file:
                for key, val in output_variables.items():
                    if isinstance(val, list):
                        formatted_val = ', '.join(
                            f'{round(v, rounding_precision) if should_round else (f"{v:e}" if use_scientific_notation else v)}'
                            if isinstance(v, (int, float)) else str(v)
                            for v in val)
                        formatted_val = f'[{formatted_val}]'
                    else:
                        formatted_val = (
                            f'{round(val, rounding_precision)}' if should_round and isinstance(val, (int, float)) else
                            (f'{val:e}' if use_scientific_notation and isinstance(val, (int, float)) else str(val))
                        )
                    file.write(f'{key} = {formatted_val}\n')
                    if key in ('currency_profit', 'rate_opening', 'sample_immediate_risk', 'sample_profit_distribution'):
                        file.write('\n')

    except FileExistsError:
        print(f"File '{variable_file_name}' already exists. Set allow_file_overwrite to True if you want to overwrite it.")
