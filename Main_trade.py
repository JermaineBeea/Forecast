# 1. Import Statements
import os
import json
import pickle
import pandas as pd
import numpy as np
from Modules.Forecast import forecastData
from Modules.Forex import exchangeRate, get_conversion_rate

def format_value(value):
    """Format the given value based on specified rounding and notation settings."""
    if isinstance(value, (int, float)):
        if should_round:
            value = round(value, rounding_precision)
        if use_scientific_notation:
            return f'{value:e}'
    return value

# Configure display options for pandas and numpy
np.set_printoptions(threshold=np.inf)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_seq_items', None)

# 2. Constants and Configurations
sell_currency = 'EUR'
buy_currency = 'USD'
investment_currency = 'ZAR'
profit_currency = 'ZAR'
time_interval = 'hrs'
price_spread = 0.00042
initial_investment = 1000

# Toggles for writing external data
fetch_external_data = True
save_external_data = True
use_binary_format = False 
use_json_format = False

# Toggles for formatting output variables
should_round = True
rounding_precision = 5
use_scientific_notation = False

# Toggles for writing output variables
allow_file_overwrite = True
save_to_json = False

# File paths
local_data_path = r'/home/wtc/Documents/RepositoryAccounts/Personal_GitHUb/Forecast/Trade Data/EURAUD.ifx.csv'
trade_folder_path = f'Trade_of_{sell_currency}_{buy_currency}/'
variable_file_name = f'{trade_folder_path}{sell_currency}{buy_currency}.py'
external_data_file_name = f'{sell_currency}{buy_currency}_data'

# Ensure the trade folder exists
os.makedirs(os.path.dirname(trade_folder_path), exist_ok=True) if os.path.dirname(trade_folder_path) else None

# 3. Data Loading and Setup
if fetch_external_data:
    # Fetch the latest conversion rates for the specified currencies
    raw_data = get_conversion_rate(sell_currency, buy_currency, period='1mo', interval='1h')['Close']

# Save fetched data to specified format
if save_external_data:
    # Determine file format based on user settings
    file_extension = '.json' if use_json_format else '.pkl' if use_binary_format else '.csv'
    file_mode = 'wb' if use_binary_format else 'w'
    with open(f'{trade_folder_path}{external_data_file_name}{file_extension}', mode=file_mode) as file:
        if use_json_format:
            json.dump(raw_data.to_list(), file)
        elif use_binary_format:
            pickle.dump(raw_data, file)
        else:  
            file.write(str(raw_data))
else:
    # Load data from local CSV file if not fetching external data
    raw_data = pd.read_csv(local_data_path, sep='\t')['<CLOSE>'].dropna()

# Convert raw data to a list for further processing
data_list = raw_data.to_list()

# Forecast calculation
forecast_func = forecastData
current_exchange_rate = data_list[-1]
forecast_period = len(data_list)
forecast_distribution = forecast_func(data_list, current_exchange_rate, period=forecast_period)

# Extract forecast values
min_closing_rate, closing_rate, max_closing_rate = forecast_distribution
forecast_distribution = [
    min_closing_rate, 
    float(np.mean([min_closing_rate, closing_rate])), 
    closing_rate, 
    float(np.mean([closing_rate, max_closing_rate])),
    max_closing_rate 
]

# Calculate immediate risk factor
immediate_risk_factor = current_exchange_rate / (current_exchange_rate + price_spread) - 1

# 4. Trade Action Logic
if closing_rate < current_exchange_rate - price_spread:
    trade_action = f'SELL {sell_currency}{buy_currency}'
    active_currency_a = sell_currency
    active_currency_b = buy_currency
    profit_distribution_factors = [
        current_exchange_rate / (closing_rate + price_spread) - 1 for closing_rate in forecast_distribution
    ]
elif closing_rate > current_exchange_rate + price_spread:
    trade_action = f'BUY {buy_currency}{sell_currency}'
    active_currency_a = buy_currency
    active_currency_b = sell_currency
    profit_distribution_factors = [
        closing_rate / (current_exchange_rate + price_spread) - 1 for closing_rate in forecast_distribution
    ]

# 5. Exchange Rate Calculations
investment_rate_a = exchangeRate(investment_currency, active_currency_a)
profit_rate_a = exchangeRate(active_currency_a, profit_currency)

# Sample investment calculations
sample_risk = initial_investment * investment_rate_a * profit_rate_a * immediate_risk_factor
sample_profit_distribution = [
    initial_investment * investment_rate_a * profit_rate_a * profit_factor
    for profit_factor in profit_distribution_factors
]
sample_max_possible_loss = min(sample_profit_distribution)

# 6. Output Preparation
output_variables = {
    'rate_given': f'"{sell_currency}{buy_currency}"',
    'trade_action': f'"{trade_action}"',
    'currency_investment': f'"{investment_currency}"',
    'currency_profit': f'"{profit_currency}"',
    'forecast_function': f'"{forecast_func.__name__}"',
    f'forecast_period_in_{time_interval}': forecast_period,
    'price_spread': price_spread,
    f'{investment_currency}_to_{active_currency_a}': investment_rate_a,
    f'{profit_currency}_to_{active_currency_a}': 1 / profit_rate_a,
    'rate_opening': current_exchange_rate,
    'initial_investment': initial_investment,
    'immediate_risk_factor': immediate_risk_factor,
    'sample_immediate_risk': sample_risk,
    'forecast_closing_rates': forecast_distribution,
    'profit_distribution_factors': profit_distribution_factors,
    'sample_profit_distribution': sample_profit_distribution,
    'expected_closing_rate': closing_rate,
    'expected_sample_profit': sample_profit_distribution[len(sample_profit_distribution) // 2],
    'sample_max_possible_loss': sample_max_possible_loss
}

# Format values for output
formatted_output_variables = {key: [format_value(v) for v in val] if isinstance(val, list) else format_value(val) for key, val in output_variables.items()}

# Check if the variable file exists
file_exists = False
try:
    with open(variable_file_name):
        file_exists = True
except FileNotFoundError:
    pass

# Write to file based on conditions
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
