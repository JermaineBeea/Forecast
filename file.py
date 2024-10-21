import yfinance as yf


def get_conversion_rate(
    from_currency: str, to_currency: str,
    from_date=None, end_date=None,
    period: str = None, interval: str = None,
    ) -> float:
    """
    Fetches the conversion rate between two currencies using Yahoo Finance.

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
    if period and not (from_date and end_date):
        rate = (
            ticker.history(period=period, interval=interval)
            if interval
            else ticker.history(period=period)
        )
    elif from_date and end_date:
        rate = (
            ticker.history(start=from_date, end=end_date, interval=interval)
            if interval
            else ticker.history(start=from_date, end=end_date)
        )
    else:
        rate = ticker.history()

    return rate

def get_asset_price(
    ticker_symbol: str,
    from_date=None,end_date=None,
    period: str = None, interval: str = None,
    ) -> float:
    """
    Fetches the latest price of a specified asset using Yahoo Finance.

    :param ticker_symbol: The stock ticker symbol (e.g., 'TSLA').
    :param from_date: Start date for historical data (optional).
    :param end_date: End date for historical data (optional).
    :param period: Period for historical data (optional).
    :param interval: Interval for historical data (optional).
    :return: Latest price as a float.
    """
    # Fetch the ticker data for the asset
    ticker = yf.Ticker(ticker_symbol)

    # Get the last price
    if period and not (from_date and end_date):
        price_data = (
            ticker.history(period=period, interval=interval)
            if interval
            else ticker.history(period=period)
        )
    elif from_date and end_date:
        price_data = (
            ticker.history(start=from_date, end=end_date, interval=interval)
            if interval
            else ticker.history(start=from_date, end=end_date)
        )
    else:
        price_data = ticker.history()

    return price_data


# Example usage:
ticker_symbol = "TSLA"
price = get_asset_price(ticker_symbol, period="1mo")['Close'].iloc[-1]
print(f"Latest price for {ticker_symbol}: {price}")

# Example usage:
from_currency = "USD"
to_currency = "EUR"
rate = get_conversion_rate(from_currency, to_currency, period="1mo")['Close'].iloc[-1]
print(f"Conversion rate from {from_currency} to {to_currency}: {rate}")
