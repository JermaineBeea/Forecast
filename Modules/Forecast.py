import os
import numpy as np
import pandas as pd
from Modules.DataModification import DataMod
from Modules.Forex import exchangeRate

def forecastData(data, from_value=None, size_forecast=None, use_relative_frequency=False, **kwargs):
    """
    Forecast data based on the given input series.

    Args:
        data (list or np.array): Time series data for which forecast is generated.
        from_value (float, optional): Starting point for forecast. Defaults to the last value in data.
        size_forecast (int, optional): Number of steps to forecast. Defaults to the length of the data.
        use_relative_frequency (bool, optional): Whether to use relative frequencies in the forecast. Defaults to True.
        **kwargs: Additional arguments to be passed to the DataMod class.

    Returns:
        list: A list containing the forecasted lower bound, expected value, and upper bound.
    """
    data_mod  = DataMod(**kwargs)

    # Default to the last value of the data for 'from_value' and data length for 'size_forecast'
    from_value = data[-1] if from_value is None else from_value
    size_forecast = len(data) if size_forecast is None else size_forecast

    # Get the first order difference of data
    diff = np.diff(data, n=1)

    # distribution output -> mean_central_dev, distribution, absolute_frequency, relative_frequency
    distr_values, _, _, absolute_frequency, relative_frequency = data_mod.distribution(diff)
    
    # Select the probability based on the 'use_relative_frequency' flag
    probability = relative_frequency if use_relative_frequency else absolute_frequency

    # Compute the mean and probabilities for the lower and upper bounds
    mean_lower_bound = np.mean(distr_values[0])
    mean_upper_bound = np.mean(distr_values[1])

    prob_lower_bound = probability[0]
    prob_upper_bound = probability[1]

    # Compute the expected difference based on the distribution
    diff_expectation = data_mod.expectation(size_forecast, [mean_lower_bound, mean_upper_bound], [prob_lower_bound, prob_upper_bound])
    
    # Calculate the min and max expectations
    min_diff_expectation = float(mean_lower_bound * size_forecast)
    max_diff_expectation = float(mean_upper_bound * size_forecast)

    # Compute the forecast distribution
    forecast_distr = [from_value + min_diff_expectation, from_value + diff_expectation, from_value + max_diff_expectation]

    return forecast_distr


if __name__ == '__main__':
    
    data = [1, 2, 3, 4, 5, 3, 4, 2, 1, 2, 3, 4, 3, 2, 1]
    diff = np.diff(data, n=1)

    print(diff)
