import os
import pandas as pd
from Modules.Forecast import forecastData
from Modules.Forex import exchangeRate

"""
The sell rate is the current rate given
The buy_rate at any given point in time  = 1/(sell_rate + spread)
"""
file_path = r'/home/wtc/Documents/RepositoryAccounts/Personal_GitHUb/Forecast/Trade Data/EURAUD.ifx.csv'
raw_data = pd.read_csv(file_path, sep = '\t')['<CLOSE>'].dropna()
data = raw_data.to_list()
forecast_function = forecastData

currency_sell = 'EUR'
currency_buy = 'AUD'
currency_investment = 'ZAR'
currency_profit = 'ZAR'
interval = 'hrs'
spread = 0.00042

# Opening and closing rate
current_rate = data[-1]
period = len(data)
distr_forecast = forecast_function(data, current_rate, period=period)
min_closing_rate, closing_rate, max_closing_rate = distr_forecast

# Fcators of trade
distr_profit_factor = 0
factor_immediate_risk = current_rate/(current_rate + spread) - 1

if closing_rate < current_rate - spread: 

    trade_action = f'SELL {currency_sell}/{currency_buy}'
    currency_a = currency_sell
    currency_b = currency_buy
    distr_profit_factor = [current_rate/(closing_rate + spread) - 1 for closing_rate in distr_forecast]

elif closing_rate > current_rate + spread: 

    trade_action = f'BUY {currency_buy}/{currency_sell}'
    currency_a = currency_buy
    currency_b = currency_sell
    distr_profit_factor = [closing_rate/(current_rate + spread) - 1 for closing_rate in distr_forecast]


rate_inv_a = exchangeRate(currency_investment, currency_a)
rate_a_profit = exchangeRate(currency_a, currency_profit)

sample_investment = 10000
sample_risk = sample_investment*rate_inv_a*rate_a_profit*factor_immediate_risk
sample_profit_distr = [sample_investment*rate_inv_a*rate_a_profit*profit_factor for profit_factor in distr_profit_factor]
sample_max_potential_loss = min(sample_profit_distr)

# Variables to write to file

variables = {
    'rate_given': f'"{currency_sell}/{currency_buy}"',
    'trade_action': f'"{trade_action}"',
    'currency_investment': f'"{currency_investment}"',
    'currency_profit': f'"{currency_profit}"',
    'forecast_function': f'"{forecast_function.__name__}"',
    f'forecast_period_in_{interval}': period,
    'spread': spread,
    'rate_opening': current_rate,
    'sample_investment'.upper(): sample_investment,
    'factor_immediate_risk': factor_immediate_risk,
    'sample_immediate_risk': sample_risk,
    'distr_closing_rate': distr_forecast,
    'distr_profit_factor': distr_profit_factor,
    'sample_profit_distr': sample_profit_distr,
    'sample_max_potential_loss': sample_max_potential_loss
}

# Construct the file path
write_to_file = f'Trade of {currency_sell}{currency_buy}/{currency_sell}{currency_buy}.py'

over_write_file = True
file_found = False

# Ensure that the directory exists
os.makedirs(os.path.dirname(write_to_file), exist_ok=True)

# Check if the file exists
try:
    with open(write_to_file):
        file_found = True
except FileNotFoundError:
    pass

# Determine whether to write to the file based on overwrite flag and file existence
if (over_write_file and file_found) or not file_found:
    try:
        with open(write_to_file, mode='x' if not over_write_file else 'w') as file:
            for key, val in variables.items():
                file.write(f'{key} = {val}\n')
                if key in ('currency_profit', 'rate_opening', 'sample_immediate_risk'): file.write(f'\n')
    except FileExistsError:
        print(f"File '{write_to_file}' already exists. Set over_write_file to True if you want to overwrite it.")
    













    







    

