import os
import numpy as np
import pandas as pd
from Modules.DataModification import DataMod
from Modules.Forex import exchangeRate

def forecastData(data, from_value=None, size_forecast=None, rel_prob = True, **kwargs):
    """_summary_

    Args:
        data (_type_): _description_
        from_value (_type_, optional): _description_. Defaults to None.
        size_forecast (_type_, optional): _description_. Defaults to None.
        rel_prob (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
    data_mod  = DataMod(**kwargs)

    #**Kwargs are arguments to be passed to distribution function

    from_value = data[-1] if from_value is None else from_value
    size_forecast = len(data) if size_forecast is None else size_forecast

    # Get the first oder difference of data
    diff = np.diff(data, n = 1)
    # distribution ouput ->  mean_central_dev, distribution, absolute_probabilities, relative_probabilities
    distr_values, placeholder_1, placeholder_2, absolute_prob, relative_prob= data_mod.distribution(diff)
    probability = relative_prob if rel_prob else absolute_prob

    mean_lower_bound = np.mean(distr_values[0])
    mean_upper_bound = np.mean(distr_values[1])

    prob_lower_bound = probability[0]
    prob_upper_bound =  probability[1]

    # Compute diff expectation 
    diff_expectation = data_mod.expectation(size_forecast, [mean_lower_bound, mean_upper_bound], [prob_lower_bound, prob_upper_bound])
    min_diff_expectation = float(mean_lower_bound*size_forecast)
    max_diff_expectation = float(mean_upper_bound*size_forecast)

    forecast_distr = [from_value + min_diff_expectation, from_value + diff_expectation, from_value + max_diff_expectation]

    return forecast_distr


if __name__ == '__main__':
    
    data = [1, 2, 3, 4, 5, 3, 4, 2, 1, 2, 3, 4, 3, 2, 1]
    diff = np.diff(data, n = 1)

    print(diff)








        


    




        

