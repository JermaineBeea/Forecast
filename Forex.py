import yfinance as yf

def exchangeRate(from_x, to_x, period="1d", interval=None, start_date=None, end_date=None):
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

def assetPrice(asset_ticker, period="1d", interval=None, start_date=None, end_date=None):
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

if __name__ == "__main__":
    # Specify the asset ticker (e.g., AAPL for Apple Inc.)
    asset_ticker = "AAPL"

    # Fetch exchange rate from USD to ZAR
    exch_rate = exchangeRate('USD', 'ZAR')
    print(f"Exchange rate from USD to ZAR:\n{exch_rate}\n")

    # Fetch asset price for Apple Inc.
    price_data = assetPrice(asset_ticker)
    print(f"Price data for {asset_ticker}:\n{price_data}")
