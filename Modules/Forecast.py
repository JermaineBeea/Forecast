import numpy as np
from DataModification import DataMod


def forecastData(data, from_x=None, size_forecast=None, rel_prob = True):
    
    data_mod  = DataMod()

    from_x = data[-1] if from_x is None else from_x
    size_forecast = len(data) if size_forecast is None else size_forecast

    #Get the first oder difference of data
    diff = np.diff(data, n = 1)
    #Genrate distribution details ->  mean_central_dev, distribution, absolute_probabilities, relative_probabilities
    distr_details = data_mod.distribution(diff)
    distr = distr_details[1]
    absolute_prob = distr_details[2]
    relative_prob = distr_details[-1]

    probabilities = relative_prob if rel_prob else absolute_prob

    mean_lower_bound = np.mean((distr[0], distr[1]))
    mean_upper_bound = np.mean((distr[1], distr[2]))

    prob_lower_bound = probabilities[0]
    prob_upper_bound =  1 - prob_lower_bound


    # Compute expectation 
    expectation = data_mod.expectation(size_forecast, [mean_lower_bound, mean_upper_bound], [prob_lower_bound, prob_upper_bound])
    print(expectation)


forecastData([1, 2, 3, 4, 5, 6, 7])


    


  




    

