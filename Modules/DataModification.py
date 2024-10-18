import numpy as np
import itertools as iter

class DataMod:
    """Class for data modification and forecasting, providing methods to linearize data, compute deviations, 
    and forecast future values based on past trends."""
    
    def __init__(self, data=[]):
        """
        Initialize the DataMod class with optional data.
        
        Args:
            data (list): List of numeric values to initialize the data attribute.
        """
        self.data = np.array(data)

    def linearise(self, data_arg=None, data_type=float):
        """
        Linearize the provided data by generating evenly spaced values between the min and max of the data.

        Args:
            data_arg (list or array-like): Data to be linearized. Must be provided.
            data_type (type): The type to which the linearized data should be cast (default is float).

        Returns:
            list: A linearized list of values.

        Raises:
            ValueError: If no data is provided or if the data has insufficient variation.
        """
        if data_arg is None:
            raise ValueError('No data provided for linearization.')
        
        data = np.array(data_arg)
        min_data, max_data = data.min(), data.max()
        mean_abs_diff = np.mean(np.abs(np.diff(data)))

        if mean_abs_diff == 0:
            raise ValueError('Insufficient variation in data to compute a meaningful linear form.')

        # Generate linearized data from min to max with steps equal to mean absolute difference
        return list(np.arange(min_data, max_data, mean_abs_diff).astype(data_type))

    def deviation(self, set_1, set_2, standard_deviation=False, absolute=True):
        """
        Calculate the element-wise deviation between two sets of data.

        Args:
            set_1 (list or array-like): First data set.
            set_2 (list or array-like): Second data set.
            standard_deviation (bool): Whether to calculate standard deviation instead of mean deviation (default False).
            absolute (bool): If True, return the absolute deviation (default True).

        Returns:
            tuple: Contains the element of set_1 closest to set_2, mean deviation, element-wise deviations, 
            and list of all deviations.
        """
        set_1, set_2 = np.array(set_1), np.array(set_2)
        set_1 = set_1.reshape(-1, 1)  # Reshape to ensure element-wise broadcasting
        
        # Compute deviations either in absolute terms or not
        if absolute:
            deviations = np.abs(set_1 - set_2)
        else:
            deviations = set_1 - set_2

        # Calculate standard deviation or mean deviation
        if standard_deviation:
            squared_deviations = deviations ** 2
            mean_deviation = np.sqrt(np.mean(squared_deviations))  # Standard deviation
        else:
            mean_deviation = np.mean(deviations)

        # Element-wise deviations and the closest element from set_1 closest to set_2
        element_wise_deviations = list(np.mean(deviations, axis=0))
        index_min_deviation =  np.where(element_wise_deviations == min(element_wise_deviations))
        closest_elements = set_1[index_min_deviation]

        return closest_elements, float(mean_deviation), element_wise_deviations, list(deviations)

    def distribution(self, data_arg, tend_func =  linear=True, absolute_diff=True):
        """
        Calculate the distribution of central tendency for the provided data.

        Args:
            data_arg (list or array-like): Data to analyze.
            linear (bool): Whether to linearize the data before calculating deviation (default True).
            absolute_diff (bool): If True, use absolute deviation for calculations (default True).

        Returns:
            list: A sorted list containing the lower bound, central tendency, and upper bound.
        """
        # Use class data if no argument provided
        data = self.data if len(data_arg) == 0 else np.array(data_arg)
        # Optionally linearize the data
        linear_data = self.linearise(data) if linear else data

        # Compute the deviation and find central tendency
        mean_deviation, element_wise_deviation = self.deviation(linear_data, data, absolute=absolute_diff)[:2]
        index_of_tendency = np.argmin(element_wise_deviation)
        central_tendency = data[index_of_tendency]

        # Return lower bound, central tendency, and upper bound based on mean deviation
        return sorted([float(central_tendency - mean_deviation), float(central_tendency), float(central_tendency + mean_deviation)])
    
    def expectation(self, quantity_events, possible_events, probabilities):
        """
        Calculate the expected value for a set of events.

        Args:
            quantity_events (int): Total quantity of events.
            possible_events (list or array-like): Possible outcomes for each event.
            probabilities (list or array-like): Probabilities associated with each possible event.

        Returns:
            float: The expected value of the events.
        """
        expected_value = quantity_events * np.sum(np.array(possible_events) * np.array(probabilities))
        return float(expected_value)
     
    def forecastData(self, data_arg=None, func=None, from_x=None, iterations=None):
        """
        Forecast future data based on trends in past data.

        Args:
            data_arg (list or array-like): Optional data to be used for forecasting. Defaults to class data.
            func (function): Optional function to modify data trends.
            from_x (numeric): Starting point for the forecast. Defaults to the last value in the data.
            iterations (int): Number of forecast iterations. Defaults to the length of the data.

        Returns:
            list: Sorted forecasted values based on past data trends.
        """
        data = self.data if data_arg is None else np.array(data_arg)
        from_x = data[-1] if from_x is None else from_x
        iterations = len(data) if iterations is None else iterations

        # Calculate differences between consecutive data points
        differences = np.diff(data, n=1)
        positive_diffs, negative_diffs = differences[differences >= 0], differences[differences < 0]
        prob_pos, prob_neg = len(positive_diffs) / len(differences), len(negative_diffs) / len(differences)
        
        # Calculate the distribution for positive and negative changes
        distr_pos = self.distribution(positive_diffs)
        distr_neg = self.distribution(negative_diffs)

        # Ensure positive and negative distributions don't mix incorrectly
        distr_pos = [0 if num < 0 else num for num in distr_pos]
        distr_neg = [0 if num > 0 else num for num in distr_neg]
 
        # Create combinations of negative and positive distributions
        product_combinations = list(iter.product(distr_neg, distr_pos))
        forecasted_values = []

        probabilities = (prob_neg, prob_pos)
        # Compute expected values for each combination
        for event_pair in product_combinations:
            change_expectation = self.expectation(iterations, event_pair, probabilities)
            forecasted_values.append(float(from_x + change_expectation))

        return sorted(forecasted_values)

# Test Functions
if __name__ == '__main__':
    import pandas as pd

    data_mod = DataMod()

    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    dev = data_mod.deviation(data, data)

    for item in dev:
        print(f'{item}\n')