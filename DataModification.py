import numpy as np

global forecast_kwargs

class DataMod:

    def __init__(self, data=None) -> None:
        self.data = data

    def linearise(self, data_arg=None, data_type=float):
        data = self.data if data_arg is None else data_arg
        data = np.array(data)

        min_data = data.min()
        max_data = data.max()

        diff_ = np.diff(data)
        mean_abs_diff = np.mean(np.abs(diff_))

        if mean_abs_diff == 0:
            raise ValueError('The data does not have sufficient variation to compute a meaningful linear form.')

        data_1 = np.arange(min_data, max_data, mean_abs_diff)
        data_1 = data_1.astype(data_type)

        return data_1

    def deviation(self, set_1, set_2, absolute=False):
        set_1 = np.array(set_1)
        set_2 = np.array(set_2)
        set_1 = set_1.reshape(-1, 1)
        set_2 = set_2.reshape(1, -1)
        deviation_set = np.abs(set_1 - set_2) if absolute else set_1 - set_2

        return deviation_set
    
    def meanTend(self, data_arg=None, linear=True, absolute_diff=True):
        '''
        Calculate the mean tendency of the provided data.
        '''
        data = self.data if data_arg is None else data_arg
        linearise = self.linearise
        deviation = self.deviation

        data = np.array(data)
        data_1 = linearise(data) if linear else data
        deviat_data = deviation(data_1, data, absolute=absolute_diff)
        tend_data = np.apply_along_axis(sum, axis=0, arr=deviat_data)
        index_tend = np.where(tend_data == tend_data.min())
        tendency = data[index_tend].mean()
        return tendency

    def expectation(self, quantity_events, possible_events, probabilities):
        result = quantity_events * sum(event * prob for event, prob in zip(possible_events, probabilities))
        return result
     
    def forecastData(self, data_arg, func=None, from_x=None, iterations=None):
        data = self.data if data_arg is None else data_arg
        meanTend = self.meanTend
        expectation = self.expectation

        if func is None:
            func = self.meanTend

        from_x = data[-1] if from_x is None else from_x
        iterations = len(data) if iterations is None else iterations

        differences = np.diff(data, n=1)
        size_diff = differences.size

        diff_pos = differences[differences >= 0]
        diff_neg = differences[differences < 0]

        size_pos = diff_pos.size
        size_neg = diff_neg.size

        tend_pos = func(diff_pos)
        tend_neg = func(diff_neg)

        prob_pos = size_pos / size_diff
        prob_neg = size_neg / size_diff

        events = tend_pos, tend_neg
        probs = prob_pos, prob_neg
        num_events = iterations

        change_excpection = expectation(num_events, events, probs)
        expectation_data = from_x + change_excpection
        max_expectation = from_x + iterations * tend_pos
        min_expectation = from_x + iterations * tend_neg

        return expectation_data, min_expectation, max_expectation


# Test Functions
if __name__ == '__main__':

    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from tkinter import messagebox
    from Forex import exchangeRate
    from DataModification import DataMod
    
    # region Display non truncated output
    np.set_printoptions(threshold=np.inf)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_seq_items', 1000)
    # endregion

    """
    Buy -> currency_b to currency_a, then trade on currency_a to currency_b
    Sell -> currency_a to currency_b, then trade on currency_b to currency_a
    Rate to buy is inverse of rate given 
    Rate to sell is rate given
    Sell Profit (currency P) = N(Fna')(Fap")[Fab'/(Fab" + Spread) - 1]
    Buy Profit (currency P) = N(Fna')(Fap')[Fab"/(Fab' + Spread) - 1]
    Sell_threshold = Fab" < Fab' - Spread
    Buy_threshold =  Fab" > Fab' + Spread
    """
    
    currency_a = 'EUR'
    currency_b = 'AUD'
    trade_units = currency_a + currency_b
    spread = 0

    investment_currency = 'ZAR'
    profit_currency = 'ZAR'

    # Condition to get data from API, or cloud data.
    external_data = False

    if external_data:
        # Get data from Yahoo Finance
        period = '1d'
        interval = '60m'
        data_rates = exchangeRate(currency_a, currency_b, period=period, interval=interval)
    else:
        # Get data from file
        path = r'/home/wtc/Documents/RepositoryAccounts/Personal_GitHUb/Forecast/EURAUD.ifx.csv'
        data_rates = pd.read_csv(path, sep='\t').dropna()['<CLOSE>']

    data_size = data_rates.size
    sell_rate_ab = data_rates.iloc[-1]
    buy_rate_ba = 1 / (sell_rate_ab + spread)

    rate_inv_a = 0.0520
    rate_a_profit = 19.2445

    # Forecast of Data
    data_mod = DataMod()
    forecast_range = data_size
    forecast, max_cast, min_cast = data_mod.forecastData(data_rates, from_x=sell_rate_ab)

    sell_threshold = forecast < sell_rate_ab + spread
    buy_threshold = forecast > sell_rate_ab + spread

    if sell_threshold:
        messagebox.showinfo('SELL!!!', f'Sell {trade_units}')
    elif buy_threshold:
        messagebox.showinfo('BUY!!!', f'Buy {trade_units}')
    else:
        messagebox.showinfo('VOID', f'Don’t trade {trade_units}')

    # region Plot Data
    plot_data = False
    # Plot functionality goes here if needed
