# 1. Import Statements
import os
import json
import pickle
import pandas as pd
import numpy as np
from Modules.Forecast import forecastData
from Modules.Forex import exchangeRate, get_conversion_rate

def format_value(val):
    if isinstance(val, (int, float)):
        if round_num:
            val = round(val, rnd)
        if scientific_notation:
            return f'{val:e}'
    return val

np.set_printoptions(threshold=np.inf)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_seq_items', None)

# 2. Constants and Configurations
currency_sell = 'EUR'
currency_buy = 'USD'
currency_investment = 'ZAR'
currency_profit = 'ZAR'
interval = 'hrs'
spread = 0.00042
sample_investment = 1000

# Toggles concernign writing external data
use_external_date = True
write_external_data = True
binary_format = False 
json_format = False

# Toggles to format variables
round_num = True
rnd = 5
scientific_notation = False

# Toggles for writing variables
over_write_file = True
write_to_json = True

path_local_data = r'/home/wtc/Documents/RepositoryAccounts/Personal_GitHUb/Forecast/Trade Data/EURAUD.ifx.csv'
path_trade_folder = f'Trade_of_{currency_sell}_{currency_buy}/'
name_variable_file = f'{path_trade_folder}{currency_sell}{currency_buy}.py'
name_external_data = f'{currency_sell}{currency_buy}_data'

# Ensure directory exists
os.makedirs(os.path.dirname(path_trade_folder), exist_ok=True) if os.path.dirname(path_trade_folder) else None

# 3. Data Loading and Setup
if use_external_date:
    raw_data = get_conversion_rate(currency_sell, currency_buy, period='1mo', interval='1h')['Close']
    data = raw_data.to_list()

if write_external_data:
    # Open the file in binary mode if using pickle
    prefix = '.json' if json_format else '.pkl' if binary_format else '.csv'
    mode = 'wb' if binary_format else 'w'
    with open(f'{path_trade_folder}{name_external_data}{prefix}', mode=mode) as file:
        if json_format:
            json.dump(data, file)
        elif binary_format:
            pickle.dump(data, file)
        else:  
            file.write(str(raw_data))
else:
    raw_data = pd.read_csv(path_local_data, sep='\t')['<CLOSE>'].dropna()
    data = raw_data.to_list()


# Forecast calculation
forecast_function = forecastData
current_rate = data[-1]
period = len(data)
distr_forecast = forecast_function(data, current_rate, period=period)
min_closing_rate, closing_rate, max_closing_rate = distr_forecast
distr_forecast = [
    min_closing_rate, 
    float(np.mean([min_closing_rate, closing_rate])), 
    closing_rate, 
    float(np.mean([closing_rate, max_closing_rate])),
    max_closing_rate 
]

# Immediate risk factor
factor_immediate_risk = current_rate / (current_rate + spread) - 1

# 4. Trade Action Logic
if closing_rate < current_rate - spread:
    trade_action = f'SELL {currency_sell}{currency_buy}'
    currency_a = currency_sell
    currency_b = currency_buy
    distr_profit_factor = [
        current_rate / (closing_rate + spread) - 1 for closing_rate in distr_forecast
    ]
elif closing_rate > current_rate + spread:
    trade_action = f'BUY {currency_buy}{currency_sell}'
    currency_a = currency_buy
    currency_b = currency_sell
    distr_profit_factor = [
        closing_rate / (current_rate + spread) - 1 for closing_rate in distr_forecast
    ]

# 5. Exchange Rate Calculations
rate_inv_a = exchangeRate(currency_investment, currency_a)
rate_a_profit = exchangeRate(currency_a, currency_profit)

# Sample investment calculations
sample_risk = sample_investment * rate_inv_a * rate_a_profit * factor_immediate_risk
sample_profit_distr = [
    sample_investment * rate_inv_a * rate_a_profit * profit_factor
    for profit_factor in distr_profit_factor
]
sample_max_potential_loss = min(sample_profit_distr)

# 6. Output Preparation
variables = {
    'rate_given': f'"{currency_sell}{currency_buy}"',
    'trade_action': f'"{trade_action}"',
    'currency_investment': f'"{currency_investment}"',
    'currency_profit': f'"{currency_profit}"',
    'forecast_function': f'"{forecast_function.__name__}"',
    f'forecast_period_in_{interval}': period,
    'spread': spread,
    f'{currency_investment}_to_{currency_a}': rate_inv_a,
    f'{currency_profit}_to_{currency_a}': 1 / rate_a_profit,
    'rate_opening': current_rate,
    'SAMPLE_INVESTMENT': sample_investment,
    'factor_immediate_risk': factor_immediate_risk,
    'sample_immediate_risk': sample_risk,
    'distr_closing_rate': distr_forecast,
    'distr_profit_factor': distr_profit_factor,
    'sample_profit_distr': sample_profit_distr,
    'expectation_closing_rate': closing_rate,
    'expectation_sample_profit': sample_profit_distr[len(sample_profit_distr)//2],
    'sample_max_potential_loss': sample_max_potential_loss
}

# Format values for output
formatted_variables = {key: [format_value(v) for v in val] if isinstance(val, list) else format_value(val) for key, val in variables.items()}

# Check if file exists
file_found = False
try:
    with open(name_variable_file):
        file_found = True
except FileNotFoundError:
    pass

# Write to file based on conditions
if (over_write_file and file_found) or not file_found:
    try:
        if write_to_json:
            with open(name_variable_file, mode='x' if not over_write_file else 'w') as file:
                json.dump(formatted_variables, file, indent=4)
        else:
            with open(name_variable_file, mode='x' if not over_write_file else 'w') as file:
                for key, val in variables.items():
                    if isinstance(val, list):
                        formatted_val = ', '.join(
                            f'{round(v, rnd) if round_num else (f"{v:e}" if scientific_notation else v)}'
                            if isinstance(v, (int, float)) else str(v)
                            for v in val)
                        formatted_val = f'[{formatted_val}]'
                    else:
                        formatted_val = (
                            f'{round(val, rnd)}' if round_num and isinstance(val, (int, float)) else
                            (f'{val:e}' if scientific_notation and isinstance(val, (int, float)) else str(val))
                        )
                    file.write(f'{key} = {formatted_val}\n')
                    if key in ('currency_profit', 'rate_opening', 'sample_immediate_risk', 'sample_profit_distr'):
                        file.write('\n')

    except FileExistsError:
        print(f"File '{name_variable_file}' already exists. Set over_write_file to True if you want to overwrite it.")
