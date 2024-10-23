# 1. Import necessary modules and functions
import os
import time
import json
import pickle
import pandas as pd
import numpy as np
from Modules.Forecast import forecastData
from Modules.Forex import get_conversion_rate, exchangeRate
from Modules.ReadWrite import write_output_to_file


# 2. Set display options for pandas and numpy
np.set_printoptions(threshold=np.inf)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_seq_items', None)


# 3. Constants & Trading settings
current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
sell_unit = 'USD'
buy_unit = 'NOK'
currency_investment = 'ZAR'
profit_currency = currency_investment
spread = 0.0047
borrowing_fee = 0
investment_amount = 1000

# Period valid - ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
# Interval valid - [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]

param_period = {
    'start_date': None,
    'end_date': None,
    'period': '1d',
    'interval': '1m'
}

# 4. Data Loading: Fetch or load data
fetch_external_data = True
save_external_data = True
over_write_save = True

write_variables = True
allow_file_overwrite = True
use_binary_format = False
save_to_json = True
use_csv_format = True

# Trade folder path
trade_folder_path = f'Trade_of_{sell_unit}_{buy_unit}/'
external_file_name = f'{trade_folder_path}{sell_unit}_{buy_unit}'
write_file = f'{trade_folder_path}{sell_unit}_{buy_unit}'

# Ensure trade folder exists
os.makedirs(os.path.dirname(trade_folder_path), exist_ok=True) if os.path.dirname(trade_folder_path) else None

if fetch_external_data:
    raw_data = get_conversion_rate(sell_unit, buy_unit, **param_period).dropna()
else:
    local_data_path = r'/path/to/local/file.csv'
    raw_data = pd.read_csv(local_data_path)

# Save external data
if save_external_data: 
    file_extension = '.csv'
    with open(f'{external_file_name}{file_extension}', 'w') as file:
        file.write(str(raw_data))

data = raw_data['Close'].to_list()


###____TRADE SECTION____###

current_rate = data[-1]
size_forecast = len(data)

# 1. Forecast Calculation
FORECAST_FUNCTION = forecastData
distr_forecast = FORECAST_FUNCTION(data, current_rate, size_forecast)
min_forecast, forecast, max_forecast = distr_forecast

print(f'SIZE FORECAST {size_forecast}\nCURRENT RATE {current_rate}\nFORECAST IS {forecast}\n')


# 2. Trade Logic
if forecast < current_rate - spread:
    action = 'sell'
    unit_a = sell_unit
    distr_profit_factor = [current_rate / (n + spread) - (1 + borrowing_fee) for n in distr_forecast]
elif forecast > current_rate + spread:
    action = 'buy'
    unit_a = buy_unit
    distr_profit_factor = [n / (current_rate + spread) - 1 for n in distr_forecast]
else:
    action = 'hold'
    distr_profit_factor = []

# Toggle to determine if trade amount is in sell units
amount_in_sell_units = True
trade_amount_a = 1000
trade_amount_b = trade_amount_a * (current_rate + spread)
investment_amount = trade_amount_a

rate_inv_unit_a = (
    1 if currency_investment == unit_a else 
    get_conversion_rate(currency_investment, unit_a)['Close'].iloc[-1]
    )
rate_unit_a_sell = 1 if action == 'sell' else 1 / (current_rate + spread)

if amount_in_sell_units:
    investment_amount = trade_amount_a / (rate_inv_unit_a * rate_unit_a_sell)
else:
    trade_amount_a = investment_amount * rate_inv_unit_a * rate_unit_a_sell
    trade_amount_b = trade_amount_a * (current_rate + spread)


# 3. Profit Calculation
investment_rate_a = exchangeRate(currency_investment, unit_a)
immediate_loss = investment_amount * (current_rate / (current_rate + spread) - 1)

distr_profit = [
    investment_amount * profit_factor
    for profit_factor in distr_profit_factor
]

max_possible_loss = min(distr_profit)


###____SAVED VARIABLES____###

output_variables = {
    'rate_given': f'"{sell_unit}{buy_unit}"',
    'time_of_trade': f"'{current_time}'",
    'trade_action': f'"{action}"',
    'currency_investment': f'"{currency_investment}"',
    'Forecast_Function': f'"{FORECAST_FUNCTION.__name__}"',
}

for key, val in param_period.items():    
    output_variables[key] = f"'{val}'"

output_variables.update({
    'forecast_size': size_forecast,
    'price_spread': spread,
    'borrowing_fee': borrowing_fee,
    'amount_in_sell_units' : amount_in_sell_units,
    'trade_amount_a' : trade_amount_a,
    'trade_amount_b' : trade_amount_b if action == 'buy' else None,
    'investment_amount': investment_amount,
    'immediate_loss': immediate_loss,
    'forecast_closing_rates': distr_forecast,
    'distr_profit_factor': distr_profit_factor,
    'distr_profit': distr_profit,
    'rate_opening'.upper(): current_rate,
    'expected_closing_rate'.upper(): forecast,
    'expected_profit': distr_profit[1],
    'sample_max_possible_loss': max_possible_loss
}
)

write_output_to_file(
    write_file, output_variables, 
    allow_file_overwrite=allow_file_overwrite, 
    save_to_json=save_to_json
)
