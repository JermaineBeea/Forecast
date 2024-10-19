import numpy as np
import pandas as pd
from DataModification import DataMod

data_mod  = DataMod()

def forecastData(data, from_value=None, size_forecast=None, rel_prob = True):
    
    from_value = data[-1] if from_value is None else from_value
    size_forecast = len(data) if size_forecast is None else size_forecast

    # Get the first oder difference of data
    diff = np.diff(data, n = 1)
    # distribution ouput ->  mean_central_dev, distribution, absolute_probabilities, relative_probabilities
    distr, absolute_prob, relative_prob= data_mod.distribution(diff)[1:]
    probabilities = relative_prob if rel_prob else absolute_prob

    mean_lower_bound = np.mean((distr[0], distr[1]))
    mean_upper_bound = np.mean((distr[1], distr[2]))

    prob_lower_bound = probabilities[0]
    prob_upper_bound =  1 - prob_lower_bound

    # Compute diff expectation 
    diff_expectation = data_mod.expectation(size_forecast, [mean_lower_bound, mean_upper_bound], [prob_lower_bound, prob_upper_bound])
    forecast = from_value + diff_expectation

    return forecast


if __name__ == '__main__':

    file_path = r'/home/wtc/Documents/RepositoryAccounts/Personal_GitHUb/Forecast/Trade Data/EURAUD.ifx.csv'
    raw_data = pd.read_csv(file_path, sep = '\t')['<CLOSE>'].dropna()
    data = raw_data.to_list()

    forecast = forecastData(data)





    


  




    

