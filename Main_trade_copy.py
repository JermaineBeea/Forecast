# 1. Import necessary modules and functions
import os
import time
import json
import pickle
from functools import partial
import pandas as pd
import numpy as np
from Modules.Forecast import forecastData
from Modules.Forex import get_conversion_rate, get_asset_price, get_forex_asset


# Set display options for pandas and numpy
np.set_printoptions(threshold=np.inf)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_seq_items', None)


# 3. Constants: Trading settings
current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
currency_sell = 'USD'
currency_buy = 'NZD' 
currency_investment = 'ZAR'
profit_currency = currency_investment
spread = 0.0008
borrowing_fee = 0

param_period = {
    'start_date': None, 'end_date': None, 
    'period': '1d', 'interval': '1m'
}

# Fetch data for ptocessing
data = get_conversion_rate(currency_sell, currency_buy, **param_period)['Close'].dropna() 
data = data.to_list()

# Function to be used
FORECAST_FUNCTION = forecastData

###__FORECAST DISTRIBUTION__###

current_rate = data[-1]
size_forecast = len(data)
distr_forecast = FORECAST_FUNCTION(data, current_rate,size_forecast)
min_forecast, forecast, max_forecast = distr_forecast
print(f'SIZE FORECAST {size_forecast}\nCURRENT RATE {current_rate}\nFORECAST IS {forecast}\n')

###____TRADE LOGIC______###

# Condition to Sell
if forecast < current_rate - spread:
    action = 'sell'
    unit_a = currency_sell
    distr_profit_factor = [current_rate / (n + spread) - (1 + borrowing_fee) for n in distr_forecast]
# end

# Condition to Buy
elif forecast > current_rate + spread:
    action = 'buy'
    unit_a = currency_buy
    distr_profit_factor = [n / (current_rate + spread) - 1 for n in distr_forecast]
# end 

# Toggle to determine if trade amount is in sell units
amount_in_sell_units = True
trade_amount_a = 1000
trade_amount_b = trade_amount_a * (current_rate + spread)
investment_amount = trade_amount_a 

rate_inv_unit_a = get_conversion_rate(currency_investment, unit_a)
rate_unit_a_sell = 1 if action == 'sell' else 1/(current_rate + spread)

if amount_in_sell_units:
    investment_amount = trade_amount_a / (rate_inv_unit_a * rate_unit_a_sell)
else:
    trade_amount_a = investment_amount * rate_inv_unit_a * rate_unit_a_sell
    trade_amount_b = trade_amount_a * (current_rate + spread)
