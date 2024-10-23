import yfinance as yf
import requests
import pandas as pd

# Using Yahho Finance

def get_conversion_rate(
    from_currency: str, to_currency: str,
    start_date=None, end_date=None,
    period : str = None, interval: str = None
    ) -> float:
    """
    Fetches the conversion rate between two currencies using Yahoo Finance.
    
    :param period: ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    :param interval:  [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]
    :param from_currency: The base currency code (e.g., 'USD').
    :param to_currency: The target currency code (e.g., 'EUR').
    :return: Conversion rate as a float.
    """
    
    # Create the currency pair symbol, e.g., 'USDEUR=X'
    pair_symbol = f"{from_currency}{to_currency}=X"

    # Fetch the ticker data for the currency pair
    ticker = yf.Ticker(pair_symbol)

    # Get the last price (conversion rate)
    # Get the last price (conversion rate)
    if period and not (start_date and end_date):
        rate = (
            ticker.history(period=period, interval=interval)
            if interval
            else ticker.history(period=period)
        )
    elif start_date and end_date:
        rate = (
            ticker.history(start=start_date, end=end_date, interval=interval)
            if interval
            else ticker.history(start=start_date, end=end_date)
        )
    else:
        rate = ticker.history()

    return rate

def get_asset_price(
    asset: str,
    start_date=None,end_date=None,
    period: str = None, interval: str = None,
    ) -> float:
    """
    Fetches the latest price of a specified asset using Yahoo Finance.

    :param period: ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    :param interval:  [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]
    :param asset: The stock ticker symbol (e.g., 'TSLA').
    :param start_date: Start date for historical data (optional).
    :param end_date: End date for historical data (optional).
    :param period: Period for historical data (optional).
    :param interval: Interval for historical data (optional).
    :return: Latest price as a float.
    """
    # Fetch the ticker data for the asset
    ticker = yf.Ticker(asset)

    # Get the last price
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
    
def get_forex_asset(
    asset: str,
    currency: str,
    ) -> float:
    """
    Converts asset to forex using 'USD' as base
    """

    if currency == 'USD': 
        return yf.Ticker(asset).history()
    
    # Fetch the ticker data for the asset
    rate_usd_currency = get_conversion_rate('USD',currency)['Close'].iloc[-1]
    data_ticker = yf.Ticker(asset).history()
    data_converted = data_ticker * rate_usd_currency

    return data_converted


# Using API

def exchangeRate(currency_a, currency_b, start_date=None, end_date=None, api_url=None):
    # Set the API URL for fetching historical exchange rates
    api_url = f"https://api.exchangerate-api.com/v4/latest/{currency_a}" if api_url is None else api_url
    
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
    # Example usage
 
    asset = 'TSLA'
    currency = 'EUR'

    result = get_forex_asset(asset, currency)
    # result = get_conversion_rate('USD', 'EUR')
    print(result)