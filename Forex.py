import yfinance as yf

def exchangeRate (from_x, to_x, period_x = '1d'):
    currency_pair = from_x + to_x + '=' + 'X'
    data = yf.Ticker(currency_pair)
    exchange_rate = data.history(period=period_x)['Close'][0]
    return exchange_rate

def assetPrice (asset_ticker, period_x = '1d'):
    asset_data = yf.Ticker(asset_ticker)
    current_price = asset_data.history(period=period_x)['Close'][0]
    return current_price

if __name__ == '__main__':

    # Specify the asset ticker (e.g., AAPL for Apple Inc.)
    asset_ticker = 'AAPL'
    # Fetch Bitcoin to USD price
    crypto_ticker = 'BTC-USD'

    exch_rate = assetPrice(crypto_ticker)

    print(f'Crypto {exch_rate}')

