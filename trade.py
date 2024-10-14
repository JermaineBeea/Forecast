import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from tkinter import messagebox
from Modules.DataModification import DataMod
from Modules.Forex import exchangeRate, exchangeRate_yf

# Set up non-truncated output display for NumPy and Pandas
np.set_printoptions(threshold=np.inf)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_seq_items', 1000)

currency_a, currency_b = 'EUR', 'AUD'  # Define currencies
trade_units = currency_a + currency_b
spread = 0
investment_currency = 'ZAR'
profit_currency = 'ZAR'

# Condition to get data from API or file
external_data = True

# Get data from API or file
if external_data:
    period = '1d'
    data_rates = exchangeRate_yf(currency_a, currency_b, period=period)['Close']
else:
    path = r'/home/wtc/Documents/RepositoryAccounts/Personal_GitHUb/Forecast/Trade Data/EURAUD.ifx.csv'
    data_rates = pd.read_csv(path, sep='\t').dropna()['<CLOSE>']

external_data = True
# Parameters of data
sell_rate_ab = data_rates.iloc[-1]
buy_rate_ba = 1 / (sell_rate_ab + spread)
rate_a_profit = exchangeRate(currency_a, profit_currency) if external_data else 19.1156
rate_inv_a =  exchangeRate(investment_currency, currency_a) if external_data else 1/19.1156
print(f'Exchange rate from {currency_a} to {profit_currency} is {rate_a_profit}')
print(f'Exchange rate from {investment_currency} to {currency_a} is {rate_inv_a}')

# Forecast of Data
data_mod = DataMod()
min_cast, forecast, max_cast = data_mod.forecastData(data_rates, from_x=sell_rate_ab)

# Calculate profit factors
sell_profit_factor = sell_rate_ab / (forecast + spread) - 1
buy_profit_factor = forecast * buy_rate_ba - 1
profit_factor = sell_profit_factor if sell_profit_factor > 0 else buy_profit_factor if buy_profit_factor > 0 else 0

# Prepare message for trading decision
test_profit = 1000 * rate_inv_a * rate_a_profit * profit_factor
str = 'sell' if sell_profit_factor > 0 else 'buy' if buy_profit_factor > 0 else ''
message_box_message = (
    f'{str.upper()}!', f'Sell {trade_units} with Profit factor {profit_factor:e}\nTest investement: {investment_currency} 1000 yields {profit_currency} {test_profit}')

# Show trading message
messagebox.showinfo(message_box_message[0], message_box_message[1])

# Calculate profit from trade
investment = 40000  # Investment amount in investment currency
profit = investment * rate_inv_a * rate_a_profit * profit_factor

print(f'Profit from {message_box_message[1]} is {investment_currency} {profit}')

# Plot Data
plot_data = True  
if plot_data:
    plt.figure(figsize=(12, 6))
    plt.title(f'Forecast of {trade_units}\n {message_box_message[1]}', color='black')
    plt.plot(range(data_rates.size), data_rates, color='blue')

    # Plot forecast line
    plt.axhline(y=forecast, label=f'Forecast is {round(forecast, 2)}', color='red', linewidth=0.8, linestyle='--')

    # # Plot max and min Labels
    # empty_plt = []
    # empty_plt = []
    plt.plot([], label=f'Max of Forecast {round(max_cast, 2)}', color='black', linestyle='--', linewidth=0.8)
    plt.plot([], label=f'Min of Forecast {round(min_cast, 2)}', color='black', linestyle='--', linewidth=0.8)

    plt.xlabel('Data Points')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
