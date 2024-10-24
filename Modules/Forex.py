import yfinance as yf
import requests
import pandas as pd


# Using Yahho Finance
"""
KEY VALUES FOR FOREX
---------------------
'bid': The current bid price (0.9253).
'ask': The current ask price (0.9258).
'previousClose': The previous close price (0.9271).
'open': The opening price for the current day (0.9272).
'regularMarketDayHigh' and 'regularMarketDayLow': The highest and lowest prices for the current trading day (0.9282 and 0.9251, respectively).
"""

def forexRate(from_currency: str, to_currency: str) -> tuple:
    """
    Fetches the latest conversion rate between two currencies using Yahoo Finance.

    :param from_currency: The base currency code (e.g., 'USD').
    :param to_currency: The target currency code (e.g., 'EUR').
    :return: Latest sell rate, buy rate, and spread as a tuple.
    """
    pair_symbol = f"{from_currency}{to_currency}=X"
    ticker = yf.Ticker(pair_symbol)

    latest_sell_rate = ticker.info['bid']  # Sell price
    latest_buy_rate = ticker.info['ask']    # Buy price
    spread = float(latest_buy_rate - latest_sell_rate)

    return latest_sell_rate, latest_buy_rate, spread

def assetRate(asset: str) -> tuple:
    """
    Fetches the latest bid and ask prices of a specified asset using Yahoo Finance.

    :param asset: The stock ticker symbol (e.g., 'TSLA').
    :return: Latest bid price and ask price as a tuple.
    """
    ticker = yf.Ticker(asset)
    latest_bid = ticker.info['bid']  # Bid price
    latest_ask = ticker.info['ask']    # Ask price

    return latest_bid, latest_ask

def hist_forex(from_currency: str, to_currency: str, start_date: str, end_date: str, period: str = None, interval: str = None):
    """
    Fetches historical forex rates between two currencies.

    :param from_currency: The base currency code (e.g., 'USD').
    :param to_currency: The target currency code (e.g., 'EUR').
    :param start_date: Start date for historical data.
    :param end_date: End date for historical data.
    :param period: Period for historical data (optional).
    :param interval: Interval for historical data (optional).
    :return: Historical forex data as a DataFrame.
    """
    pair_symbol = f"{from_currency}{to_currency}=X"
    ticker = yf.Ticker(pair_symbol)

    # Get historical data
    if period and not (start_date and end_date):
        price_data = (
            ticker.history(period=period, interval=interval)
            if interval
            else ticker.history(period=period)
        )
    elif start_date and end_date:
        price_data = (
            ticker.history(start=start_date, end=end_date, interval=interval)
            if interval
            else ticker.history(start=start_date, end=end_date)
        )
    else:
        price_data = ticker.history()

    return price_data

def hist_asset(asset: str, start_date: str, end_date: str, period: str = None, interval: str = None):
    """
    Fetches historical prices of a specified asset.

    :param asset: The stock ticker symbol (e.g., 'TSLA').
    :param start_date: Start date for historical data.
    :param end_date: End date for historical data.
    :param period: Period for historical data (optional).
    :param interval: Interval for historical data (optional).
    :return: Historical asset data as a DataFrame.
    """
    ticker = yf.Ticker(asset)

    # Get historical data
    if period and not (start_date and end_date):
        price_data = (
            ticker.history(period=period, interval=interval)
            if interval
            else ticker.history(period=period)
        )
    elif start_date and end_date:
        price_data = (
            ticker.history(start=start_date, end=end_date, interval=interval)
            if interval
            else ticker.history(start=start_date, end=end_date)
        )
    else:
        price_data = ticker.history()

    return price_data


# Using API

def blitzRate(currency_a, currency_b, start_date=None, end_date=None, api_url=None):
    # Set the API URL for fetching historical exchange rates
    api_url = f"https://api.blitzRate-api.com/v4/latest/{currency_a}" if api_url is None else api_url
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        
        # Extract the exchange rates for the specified currency
        if currency_b in data['rates']:
            exchange_rate = data['rates'][currency_b]
            # print(f"Current exchange rate for {currency_b} to {currency_a}: {exchange_rate}")
            return exchange_rate  # Just returning the current rate for demonstration
        else:
            print(f"Error: {currency_b} is not available in the exchange rates.")
            return None
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return None

def assetPrice(asset_symbol, api_url=None):
    # Set the API URL for fetching asset prices
    # This example uses a mock URL. Replace it with the actual endpoint for the asset price API you're using.
    api_url = f"https://api.example.com/v1/price/{asset_symbol}" if api_url is None else api_url

    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        
        # Extract the price of the asset
        asset_price = data.get('price')  # Change this based on the API's response structure
        
        if asset_price is not None:
            return asset_price
        else:
            # print(f"Error: Price information for {asset_symbol} is not available.")
            return None
    except Exception as e:
        print(f"Error fetching asset price: {e}")
        return None

if __name__== '__main__':
 
    unit_a = 'EUR'
    unit_b = 'GBP'

