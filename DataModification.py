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
        data_rates = exchangeRate(currency_a, currency_b, period=period)['Close']
    else:
        # Get data from file
        path = r'/home/wtc/Documents/RepositoryAccounts/Personal_GitHUb/Forecast/EURAUD.ifx.csv'
        data_rates = pd.read_csv(path, sep='\t').dropna()['<CLOSE>']

    data_size = data_rates.size
    sell_rate_ab = data_rates.iloc[-1]
    buy_rate_ba = 1 / (sell_rate_ab + spread)

    rate_a_profit = exchangeRate(currency_a, profit_currency) if external_data else 19.1156
    rate_inv_a = 1/rate_a_profit


    # Forecast of Data
    data_mod = DataMod()
    forecast_range = data_size
    forecast, max_cast, min_cast = data_mod.forecastData(data_rates, from_x=sell_rate_ab)

    sell_threshold = forecast < sell_rate_ab + spread
    buy_threshold = forecast > sell_rate_ab + spread

    if sell_threshold:
        messagebox.showinfo('SELL!!!', f'Sell {trade_units}')
        opening_rate = sell_rate_ab
        closing_rate = 1/(forecast + spread)

    elif buy_threshold:
        messagebox.showinfo('BUY!!!', f'Buy {trade_units}')
        opening_rate = buy_rate_ba
        closing_rate = forecast
    else:
        messagebox.showinfo('VOID', f'Do not Trade trade {trade_units}')
        exit('No potential Trade to execute : Exited Program')

    # region Plot Data 
    plot_data = True
    if plot_data:
            
        plt.figure(figsize=(12, 6))
        plt.title(f'Forcast of {trade_units}', color='black')
        x_plot_range = range(data_size)
        plt.plot(x_plot_range, data_rates, color='blue')

        rnd = 2
        col = 'red'
        h_lines = forecast
        plt.axhline(
            y=forecast,
            label=f'Forecast is {round(forecast, rnd)} ',
            color=col,
            linewidth=0.8,
            linestyle='--',
        )

        # Plot the linear line from the last data point to the forecast
        plt_linear = False
        if plt_linear:
            x_start = data_size - 1  # Last index
            y_start = data_rates[-1]        # Last data point
            x_end = data_size + len(data_rates)  # Next index for forecast + iterations
            y_end = forecast           # Forecast value

            # Create a linear line from (x_start, y_start) to (x_end, y_end)
            x_values = np.linspace(x_start, x_end, num=len(data_rates) + 10)  # More points for a smooth line
            y_values = np.linspace(y_start, y_end, num=len(x_values))   # Linear interpolation

            plt.plot(x_values, y_values, color='green', linestyle='--', linewidth=0.9, label='Forecast Line')

        # region Plot Labels
        empty_plot = []
        col = 'black'
        style = '--'
        width = 0.8
        plt.plot(
            empty_plot,
            label=f'Max of Foracst {round(max_cast, rnd)}',
            linewidth=width,
            color=col,
            linestyle=style,
        )
        plt.plot(
            empty_plot,
            label=f'Min of Forecast  {round(min_cast, rnd)}',
            linewidth=width,
            color=col,
            linestyle=style,
        )
        # endregion

        plt.xlabel('Data Points')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    #endregion