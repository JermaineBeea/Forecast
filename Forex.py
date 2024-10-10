import yfinance as yf

def exchangeRate(from_x, to_x, period="1d", interval='1d', start_date=None, end_date=None):
    """
    Fetch the exchange rate between two currencies.

    Parameters:
        from_x (str): The currency code to convert from (e.g., 'USD').
        to_x (str): The currency code to convert to (e.g., 'ZAR').
        period (str, optional): The period for which to fetch data. 
            Valid options are ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'].
        interval (str, optional): The frequency of the data points.
            Default is '1d'. Other options include ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1wk', '1mo', '3mo'].
        start_date (str, optional): The start date for fetching data in 'YYYY-MM-DD' format.
        end_date (str, optional): The end date for fetching data in 'YYYY-MM-DD' format.

    Returns:
        pandas.DataFrame: A DataFrame containing the exchange rate data.
    """
    currency_pair = from_x + to_x + "=X"
    data = yf.Ticker(currency_pair)

    if start_date and end_date:
        # Fetch data for a specific date range
        exchange_rate = data.history(start=start_date, end=end_date, interval=interval)
    else:
        # Fetch data for the given period (e.g., '1d', '5d')
        exchange_rate = data.history(period=period, interval=interval)

    return exchange_rate


def assetPrice(asset_ticker, period="1d", interval='1d', start_date=None, end_date=None):
    """
    Fetch the historical price data for a specified asset.

    Parameters:
        asset_ticker (str): The ticker symbol of the asset (e.g., 'AAPL' for Apple Inc.).
        period (str, optional): The period for which to fetch data. 
            Valid options are ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'].
        interval (str, optional): The frequency of the data points.
            Default is '1d'. Other options include ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1wk', '1mo', '3mo'].
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

    return price_data


if __name__ == "__main__":
    # Specify the asset ticker (e.g., AAPL for Apple Inc.)
    asset_ticker = "AAPL"

    # Fetch Bitcoin to USD price
    crypto_ticker = "BTC-USD"

    exch_rate = exchangeRate('USD', 'ZAR', start_date="2023-01-01", end_date="2024-08-30")
    print(f"Rate is {exch_rate}")
