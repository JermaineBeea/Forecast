import numpy as np

class DataMod:
    """Class for data modification and forecasting."""
    
    def __init__(self, data=[]):
        """Initialize with optional data."""
        self.data = data 

        global linearise, deviation, distribution, expectation
        linearise = self.linearise
        deviation = self.deviation
        distribution = self.distribution
        expectation = self.expectation

    def linearise(self, data_arg=None, data_type=float):
        """
        Linearize the provided data.
        
        Args:
            data_arg (iterable, optional): Data to linearize. Raises an error if not provided.
            data_type (type, optional): Data type for the output array. Defaults to float.

        Raises:
            ValueError: If no data is provided or if the data has insufficient variation.

        Returns:
            np.ndarray: Linearized data as a NumPy array.
        """
        if data_arg is None:
            raise ValueError('No data provided for linearization.')
        
        data = np.array(data_arg)
        min_data, max_data = data.min(), data.max()
        mean_abs_diff = np.mean(np.abs(np.diff(data)))

        if mean_abs_diff == 0:
            raise ValueError('Insufficient variation in data to compute a meaningful linear form.')

        return np.arange(min_data, max_data, mean_abs_diff).astype(data_type)

    def deviation(self, set_1, set_2, standard_deviation=False, absolute=True):
        """
        Calculate the deviation between two sets of data.

        Args:
            set_1 (iterable): First set of data.
            set_2 (iterable): Second set of data.
            standard_deviation (bool, optional): If True, calculate the standard deviation (mean of squared deviations). Defaults to False.
            absolute (bool, optional): If True, calculate absolute deviations. Defaults to True.

        Raises:
            ValueError: If the input sets do not have the same length.

        Returns:
            tuple: 
                - mean_dev (float): The mean deviation or standard deviation.
                - elementwise_mean_deviation (np.ndarray): Mean deviation for each element in set_1.
                - deviations (np.ndarray): Deviations between set_1 and set_2.
        """

        set_1, set_2 = np.array(set_1), np.array(set_2)
        set_1 = set_1.reshape(-1, 1)

        if absolute:
            deviations = np.abs(set_1 - set_2)
        else:
            deviations = set_1 - set_2
        
        if standard_deviation:
            squared_deviations = deviations ** 2
            elementwise_mean_deviation = np.mean(squared_deviations, axis=0)
            mean_dev = np.sqrt(np.mean(elementwise_mean_deviation))  # Standard deviation
        else:
            elementwise_mean_deviation = np.mean(deviations, axis=0)
            mean_dev = np.mean(elementwise_mean_deviation)

        return mean_dev, elementwise_mean_deviation, deviations

    def distribution(self, data_arg, linear=True, absolute_diff=True):
        """
        Calculate the central tendency of the provided data.

        Args:
            data_arg (iterable): Data for calculation.
            linear (bool, optional): If True, linearize the data before calculating tendency. Defaults to True.
            absolute_diff (bool, optional): If True, calculate absolute differences. Defaults to True.

        Returns:
            tuple: 
                - central_tendency (float): The central tendency value.
                - lower_bound (float): Lower bound (central_tendency - mean deviation).
                - upper_bound (float): Upper bound (central_tendency + mean deviation).
        """
        data = np.array(data_arg)
        data_1 = self.linearise(data) if linear else data
        mean_dev, elementwise_dev = self.deviation(data_1, data, absolute=absolute_diff)[ :2]
        index_tend = np.argmin(elementwise_dev)
        central_tendency = data[index_tend]

        return np.sort([central_tendency - mean_dev, central_tendency, central_tendency + mean_dev])
    
    def expectation(self, quantity_events, possible_events, probabilities):
        """
        Calculate the expected value of events.
        
        Args:
            quantity_events (int): Number of events.
            possible_events (iterable): Possible outcomes for the events.
            probabilities (iterable): Corresponding probabilities for each possible outcome.

        Returns:
            float: The expected value of the events.
        """
        return quantity_events * np.sum(np.array(possible_events) * np.array(probabilities))
     
    def forecastData(self, data_arg, func=None, from_x=None, iterations=None):
        """
        Forecast future data based on past trends.
        
        Args:
            data_arg (iterable): Historical data for forecasting.
            func (callable, optional): Function to calculate tendency (defaults to mean tendency).
            from_x (float, optional): Starting point for the forecast. Defaults to the last value of data_arg.
            iterations (int, optional): Number of forecast iterations. Defaults to the length of data_arg.

        Returns:
            tuple:
                - forecasted_value (float): Forecasted data based on expected change.
                - min_estimate (float): Minimum forecast estimate.
                - max_estimate (float): Maximum forecast estimate.
        """
        data = np.array(data_arg)
        func = func or distribution
        from_x = data[-1] if from_x is None else from_x
        iterations = len(data) if iterations is None else iterations

        differences = np.diff(data, n = 1)
        diff_pos, diff_neg = differences[differences >= 0], differences[differences < 0]
        prob_pos, prob_neg = len(diff_pos) / len(differences), len(diff_neg) / len(differences)
        
        distr_pos = distribution(diff_pos)
        distr_neg = distribution(diff_neg)
        min_pos, tend_pos, max_pos = distr_pos
        min_neg, tend_neg, max_neg = distr_neg

        probabilities = prob_pos, prob_neg
        expect = from_x + expectation(iterations, (tend_pos, tend_neg), probabilities)
        min_expect = from_x + expectation(iterations, (min_pos, min_neg), probabilities)
        max_expect = from_x + expectation(iterations, (max_pos, max_neg), probabilities)

        return min_expect, expect, max_expect


# Test Functions
if __name__ == '__main__':

    data_mod = DataMod()
    
    data = (1, 2, 3, 4, 5, 6, 7)

    distr = data_mod.distribution(data).round(2)

    print(distr)