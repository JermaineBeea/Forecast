import numpy as np
import itertools as iter

class DataMod:
    """Class for data modification and forecasting."""
    
    def __init__(self, data=[]):
        """Initialize with optional data."""
        self.data = np.array(data)

    def linearise(self, data_arg=None, data_type=float):
        """
        Linearize the provided data.
        """
        if data_arg is None:
            raise ValueError('No data provided for linearization.')
        
        data = np.array(data_arg)
        min_data, max_data = data.min(), data.max()
        mean_abs_diff = np.mean(np.abs(np.diff(data)))

        if mean_abs_diff == 0:
            raise ValueError('Insufficient variation in data to compute a meaningful linear form.')

        return list(np.arange(min_data, max_data, mean_abs_diff).astype(data_type))

    def deviation(self, set_1, set_2, standard_deviation=False, absolute=True):
        """
        Calculate the deviation between two sets of data element-wise.
        """
        set_1, set_2 = np.array(set_1), np.array(set_2)
        set_1 = set_1.reshape(-1, 1)  # Reshape to ensure element-wise difference (broadcasting)

        if absolute:
            deviations = np.abs(set_1 - set_2)
        else:
            deviations = set_1 - set_2

        if standard_deviation:
            squared_deviations = deviations ** 2
            mean_dev = np.sqrt(np.mean(squared_deviations))  # Standard deviation
        else:
            mean_dev = np.mean(deviations)

        return float(mean_dev), list(np.mean(deviations, axis=0)), list(deviations)

    def distribution(self, data_arg, linear=True, absolute_diff=True):
        """
        Calculate the central tendency of the provided data.
        """
        data = self.data if len(data_arg) == 0 else np.array(data_arg)
        data_1 = self.linearise(data) if linear else data

        mean_dev, elementwise_dev = self.deviation(data_1, data, absolute=absolute_diff)[:2]
        index_tend = np.argmin(elementwise_dev)
        central_tendency = data[index_tend]

        return sorted([float(central_tendency - mean_dev), float(central_tendency), float(central_tendency + mean_dev)])
    
    def expectation(self, quantity_events, possible_events, probabilities):
        """
        Calculate the expected value of events.
        """
        expected_value = quantity_events * np.sum(np.array(possible_events) * np.array(probabilities))
        return float(expected_value)
     
    def forecastData(self, data_arg=None, func=None, from_x=None, iterations=None):
        """
        Forecast future data based on past trends.
        """
        data = self.data if data_arg is None else np.array(data_arg)
        from_x = data[-1] if from_x is None else from_x
        iterations = len(data) if iterations is None else iterations

        differences = np.diff(data, n=1)
        diff_pos, diff_neg = differences[differences >= 0], differences[differences < 0]
        prob_pos, prob_neg = len(diff_pos) / len(differences), len(diff_neg) / len(differences)
        
        distr_pos = self.distribution(diff_pos)
        distr_neg = self.distribution(diff_neg)

        distr_pos = [0 if num < 0 else num for num in distr_pos]
        distr_neg = [0 if num > 0 else num for num in distr_neg]
 
        product_map = list(iter.product(distr_neg, distr_pos))
        distr_expectation = []

        probabilities = (prob_neg, prob_pos)
        for event in product_map:
            change_expectation = self.expectation(iterations, event, probabilities)
            distr_expectation.append(float(from_x + change_expectation))

        return sorted(distr_expectation)

# Test Functions
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from scipy.stats import norm
    import pandas as pd

    path = r'/home/wtc/Documents/RepositoryAccounts/Personal_GitHUb/Forecast/Trade Data/EURAUD.ifx.csv'
    data = pd.read_csv(path, sep='\t').dropna()['<CLOSE>'].to_list()

    data_mod = DataMod(data)

    # Test forecast
    distr_forecast = data_mod.forecastData()

    print(distr_forecast)
  

