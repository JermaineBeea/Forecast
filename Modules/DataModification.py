import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import messagebox
from Modules.Forex import exchangeRate  # Assuming this is a valid module

class DataMod:
    """Class for data modification and forecasting."""
    
    def __init__(self, data=None) -> None:
        """Initialize with optional data."""
        self.data = data

    def linearise(self, data_arg=None, data_type=float):
        """
        Linearize the provided data.

        Args:
            data_arg: Optional data to linearize.
            data_type: Data type for the output array.

        Returns:
            Linearized data as a NumPy array.
        """
        # Use the provided data or instance data if not specified
        data = np.array(self.data if data_arg is None else data_arg)
        
        # Find the minimum and maximum values of the data
        min_data, max_data = data.min(), data.max()
        
        # Calculate the mean absolute difference between consecutive data points
        mean_abs_diff = np.mean(np.abs(np.diff(data)))

        # Raise an error if there is no variation in the data
        if mean_abs_diff == 0:
            raise ValueError('Insufficient variation in data to compute a meaningful linear form.')

        # Generate linearized data based on the calculated mean absolute difference
        return np.arange(min_data, max_data, mean_abs_diff).astype(data_type)

    def deviation(self, set_1, set_2, absolute=False):
        """
        Calculate the deviation between two sets of data.

        Args:
            set_1: First set of data.
            set_2: Second set of data.
            absolute: If True, calculate absolute deviations.

        Returns:
            Deviations as a 2D NumPy array.
        """
        # Convert inputs to NumPy arrays
        set_1, set_2 = np.array(set_1), np.array(set_2)
        
        # Reshape the arrays to compute pairwise deviations
        deviation_set = (
            np.abs(set_1[:, np.newaxis] - set_2[np.newaxis, :]) 
            if absolute 
            else set_1[:, np.newaxis] - set_2[np.newaxis, :]
        )
        return deviation_set
    
    def meanTend(self, data_arg=None, linear=True, absolute_diff=True):
        """
        Calculate the mean tendency of the provided data.

        Args:
            data_arg: Optional data for calculation.
            linear: If True, linearize the data before calculating tendency.
            absolute_diff: If True, calculate absolute differences.

        Returns:
            Mean tendency value.
        """
        # Use the provided data or instance data if not specified
        data = np.array(self.data if data_arg is None else data_arg)
        
        # Linearize the data if required
        data_1 = self.linearise(data) if linear else data
        
        # Calculate deviations from the linearized data
        deviat_data = self.deviation(data_1, data, absolute=absolute_diff)
        
        # Sum the deviations across columns to find tendency
        tend_data = np.sum(deviat_data, axis=0)
        
        # Find the index of the minimum tendency value
        index_tend = np.argmin(tend_data)
        
        # Return the mean of the data at the index with minimum tendency
        return data[index_tend].mean()

    def expectation(self, quantity_events, possible_events, probabilities):
        """
        Calculate the expected value of events.

        Args:
            quantity_events: Number of events.
            possible_events: Possible outcomes.
            probabilities: Probabilities of outcomes.

        Returns:
            Expected value.
        """
        # Calculate expected value using the formula for expectation
        return quantity_events * np.sum(np.array(possible_events) * np.array(probabilities))
     
    def forecastData(self, data_arg, func=None, from_x=None, iterations=None):
        """
        Forecast future data based on past trends.

        Args:
            data_arg: Historical data for forecasting.
            func: Function to calculate tendency (mean tendency by default).
            from_x: Starting point for the forecast.
            iterations: Number of forecast iterations.

        Returns:
            Forecasted data, minimum, and maximum estimates.
        """
        # Use the provided data or instance data if not specified
        data = self.data if data_arg is None else data_arg
        
        # Use the specified function or default to mean tendency
        func = func or self.meanTend
        
        # Determine the starting point for forecasting
        from_x = data[-1] if from_x is None else from_x
        iterations = len(data) if iterations is None else iterations

        # Calculate the differences between consecutive data points
        differences = np.diff(data)
        
        # Separate positive and negative differences
        diff_pos, diff_neg = differences[differences >= 0], differences[differences < 0]

        # Calculate probabilities of positive and negative trends
        prob_pos, prob_neg = len(diff_pos) / len(differences), len(diff_neg) / len(differences)
        
        # Get tendencies for positive and negative trends
        events = (func(diff_pos), func(diff_neg))

        # Calculate the expected change based on tendencies and probabilities
        change_excpection = self.expectation(iterations, events, (prob_pos, prob_neg))
        
        # Forecast future data based on the last known value and expected change
        expectation_data = from_x + change_excpection

        # Calculate maximum and minimum forecasts
        return expectation_data, from_x + iterations * events[1], from_x + iterations * events[0]


# Test Functions
if __name__ == '__main__':
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
    external_data = False

    # Get data from API or file
    if external_data:
        period = '1d'
        data_rates = exchangeRate(currency_a, currency_b, period=period)['Close']
    else:
        path = r'/home/wtc/Documents/RepositoryAccounts/Personal_GitHUb/Forecast/EURAUD.ifx.csv'
        data_rates = pd.read_csv(path, sep='\t').dropna()['<CLOSE>']

    # Parameters of data
    sell_rate_ab = data_rates.iloc[-1]
    buy_rate_ba = 1 / (sell_rate_ab + spread)
    rate_a_profit = exchangeRate(currency_a, profit_currency) if external_data else 19.1156
    rate_inv_a = 1 / rate_a_profit

    # Forecast of Data
    data_mod = DataMod()
    forecast, max_cast, min_cast = data_mod.forecastData(data_rates, from_x=sell_rate_ab)

    # Calculate profit factors
    sell_profit_factor = sell_rate_ab / (forecast + spread) - 1
    buy_profit_factor = forecast * buy_rate_ba - 1

    # Prepare message for trading decision
    message_box_message = (
        ('SELL!', f'Sell {trade_units}') if sell_profit_factor > 0 else 
        ('BUY!', f'Buy {trade_units}') if buy_profit_factor > 0 else 
        ('VOID', f'Do not trade {trade_units}')
    )
    profit_factor = sell_profit_factor if sell_profit_factor > 0 else buy_profit_factor if buy_profit_factor > 0 else 0

    # Show trading message
    messagebox.showinfo(message_box_message[0], message_box_message[1])

    # Calculate profit from trade
    investment = 40000  # Investment amount in investment currency
    profit = investment * rate_inv_a * rate_a_profit * profit_factor

    print(f'Profit from {message_box_message[1]} is {investment_currency} {profit}')

    # Plot Data
    plot_data = False  
    if plot_data:
        plt.figure(figsize=(12, 6))
        plt.title(f'Forecast of {trade_units}', color='black')
        plt.plot(range(data_rates.size), data_rates, color='blue')

        # Plot forecast line
        plt.axhline(y=forecast, label=f'Forecast is {round(forecast, 2)}', color='red', linewidth=0.8, linestyle='--')

        # Plot max and min forecasts
        plt.axhline(y=max_cast, label=f'Max of Forecast {round(max_cast, 2)}', color='black', linestyle='--', linewidth=0.8)
        plt.axhline(y=min_cast, label=f'Min of Forecast {round(min_cast, 2)}', color='black', linestyle='--', linewidth=0.8)

        plt.xlabel('Data Points')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
