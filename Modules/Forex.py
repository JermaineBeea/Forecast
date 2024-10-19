import yfinance as yf
import requests

# Using Yahho Finance
def exchangeRate_yf(from_x, to_x, period="1d", interval=None, start_date=None, end_date=None):
    """
    Fetch the exchange rate between two currencies.

    Parameters:
        from_x (str): The currency code to convert from (e.g., 'USD').
        to_x (str): The currency code to convert to (e.g., 'ZAR').
        period (str, optional): The period for which to fetch data. 
            Valid options are ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'].
        interval (str, optional): The frequency of the data points.
            Default is None. Other options include ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1wk', '1mo', '3mo'].
        start_date (str, optional): The start date for fetching data in 'YYYY-MM-DD' format.
        end_date (str, optional): The end date for fetching data in 'YYYY-MM-DD' format.

    Returns:
        pandas.DataFrame: A DataFrame containing the exchange rate data.
    """
    currency_pair = f"{from_x}{to_x}=X"
    data = yf.Ticker(currency_pair)

    if start_date and end_date:
        if interval:
            exchange_rate = data.history(start=start_date, end=end_date, interval=interval)
        else: 
            exchange_rate = data.history(start=start_date, end=end_date)
    elif interval:
        exchange_rate = data.history(period=period, interval=interval)
    else: 
        exchange_rate = data.history(period=period)

    if exchange_rate.empty:
        print(f"No data available for {currency_pair} in the specified range.")
    return exchange_rate

def assetPrice_yf(asset_ticker, period="1d", interval=None, start_date=None, end_date=None):
    """
    Fetch the historical price data for a specified asset.

    Parameters:
        asset_ticker (str): The ticker symbol of the asset (e.g., 'AAPL' for Apple Inc.).
        period (str, optional): The period for which to fetch data. 
            Valid options are ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'].
        interval (str, optional): The frequency of the data points.
            Default is None. Other options include ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1wk', '1mo', '3mo'].
        start_date (str, optional): The start date for fetching data in 'YYYY-MM-DD' format.
        end_date (str, optional): The end date for fetching data in 'YYYY-MM-DD' format.

    Returns:
        pandas.DataFrame: A DataFrame containing the asset price data.
    """
    asset_data = yf.Ticker(asset_ticker)

    if start_date and end_date:
        # Fetch data for a specific date range
        price_data = asset_data.history(start=start_date, end=end_date, interval=interval)
    else:
        # Fetch data for the given period (e.g., '1d', '5d')
        price_data = asset_data.history(period=period, interval=interval)

    if price_data.empty:
        print(f"No data available for {asset_ticker} in the specified range.")
    return price_data

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
    source_currency = 'ZAR'       
    target_currency = 'USD'       

    exchange_rate = exchangeRate(source_currency, target_currency)

    print(f"Exchange rate for {target_currency}/{source_currency}: {exchange_rate} .")

    # asset_symbol = 'AAPL'  # Example asset symbol (e.g., Apple Inc.)
    # asset_price = assetPrice(asset_symbol)

    # print(f"The current price of {asset_symbol} is ${asset_price:.2f}.")

