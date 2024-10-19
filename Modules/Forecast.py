import numpy as np
from DataModification import DataMod


def forecastData(data, from_x=None, size_forecast=None):
    
    data_mod  = DataMod()

    from_x = data[-1] if from_x is None else from_x
    size_forecast = len(data) if size_forecast is None else size_forecast

    #Get the first oder difference of data
    diff = np.dif(data, n = 1)
    disr_details = data_mod.distribution(diff)
    distr = disr_details[1]
    relative_prob = disr_details[-1]



    

