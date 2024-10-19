import numpy as np
import unittest
from collections import Counter

# Toggle to enable unit test execution
# Toggle to print logs from the binData function
RUN_UNIT_TESTING = False 
DISPLAY_LOG_binData = False

class DataMod:
    """
    A class for performing various data modifications, including binning, 
    computing element-wise deviations, linearization, and forecasting based on data trends.
    """

    def __init__(self, data=[], **kwargs):
        """
        Initialize the DataMod class with optional data.
        
        Args:
            data (list): List of numeric values to initialize the data attribute. Defaults to an empty list.
            **kwargs: Keyword arguments to configure options like standard deviation and absolute difference.
        """
        self.data = np.array(data)
        self.STANDARD_DEVIATION = kwargs.get('std_dev', False)
        self.ABSOLUTE_DIFFERENCE = kwargs.get('abs_diff', True)


    def numRange(self, num, data):
        """
        Purpose
        --------
        Find the range in a sorted list where the given number lies.

        Args:
            num (int or float): The number to search for.
            data (array-like): Sorted array of data to search through.

        Returns:
            tuple: Index of the lower bound and a tuple of the two bounding values.
                  Returns None if the number is outside the range.
        """
        data = sorted(data)
        min_data = data[0]
        max_data = data[-1]

        # If the number is out of bounds, return None
        if num < min_data or num > max_data:
            return None
        
        # Special case: if the number equals the minimum or maximum data
        if num == min_data:
            idx = 0
            value_range = min_data, data[1]
        elif num == max_data:
            idx = len(data) - 2
            value_range = data[-2], max_data
        else:
            idx = int(np.searchsorted(data, num)) - 1
            value_range = int(data[idx]), int(data[idx + 1])

        return idx, value_range


    def binData(self, bin_ranges, data, rnd=None):
        """_summary_

        Args:
            bin_ranges (_type_): _description_
            data (_type_): _description_
            rnd (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        data = np.array(data) if not isinstance(data, np.ndarray) else data
        size_bin_ranges = len(bin_ranges) - 1  # Number of bins is one less than number of ranges
        size_data = len(data)
        size_data_in_range = int(sum((data >= data.min()) & (data <= data.max())))

        # Initialize bin statistics lists
        bins_count = [0] * size_bin_ranges
        bins_abs_factor = [0] * size_bin_ranges
        bins_rel_factor = [0] * size_bin_ranges

        for indx, (range) in enumerate(zip(bin_ranges[: -1], bin_ranges[1:])):
            count = 0
            for num in data:
                if num >= range[0] and num <= range[1]:
                    count += 1
                    bins_count[indx] = count
                    bins_abs_factor[indx] = count/size_data
                    bins_rel_factor[indx] = count/size_data_in_range
                else: continue
            
        return bins_count, bins_abs_factor, bins_rel_factor


    def linearise(self, data_arg=None, data_type=float):
        """
        Purpose
        --------
        Generate a linearized form of the input data.

        Args:
            data_arg (array-like): Data to be linearized.
            data_type (type, optional): Data type for linearized data. Defaults to float.

        Returns:
            list: Linearized sequence of data based on the mean absolute difference.
        
        Raises:
            ValueError: If no data is provided or if data has insufficient variation.
        """
        if data_arg is None:
            raise ValueError('No data provided for linearization.')
        
        data = np.array(data_arg)
        min_data, max_data = data.min(), data.max()
        mean_abs_diff = np.mean(np.abs(np.diff(data)))

        if mean_abs_diff == 0:
            print(f'From {self.linearise.__name__}\nMean of absolute difference is 0, returned original data as linearised data\n')
            return data
            

        return list(np.arange(min_data, max_data, mean_abs_diff).astype(data_type))


    def deviation(self, set_1, set_2, std_dev=None, abs_diff=None):
        """
        Purpose
        --------
        Compute the element-wise deviations between two datasets.

        Args:
            set_1 (array-like): First dataset.
            set_2 (array-like): Second dataset to compare with set_1.
            std_dev (bool, optional): If True, compute standard deviation. Defaults to False.
            abs_diff (bool, optional): If True, return absolute element-wise deviations. Defaults to True.

        Returns:
            tuple: 
                - central_tendency (array): Elements in set_1 with the smallest deviation to set_2.
                - mean_element_wise_deviations (float): Mean deviation between the datasets.
                - element_wise_deviations (list): All element-wise deviations between corresponding elements.
        """
        std_dev = self.STANDARD_DEVIATION if std_dev is None else std_dev
        abs_diff = self.ABSOLUTE_DIFFERENCE if abs_diff is None else abs_diff

        set_1, set_2 = np.array(set_1), np.array(set_2)
        set_1 = set_1.reshape(-1, 1) if len(set_1) > 1 else set_1

        # Compute deviations: absolute or normal
        if abs_diff:
            element_wise_deviations = np.abs(set_1 - set_2)
        else:
            element_wise_deviations = set_1 - set_2

        # Compute mean or standard deviation of deviations
        if std_dev:
            squared_element_wise_deviations = element_wise_deviations ** 2
            mean_element_wise_deviations = np.sqrt(np.mean(squared_element_wise_deviations))
        else:
            mean_element_wise_deviations = np.mean(element_wise_deviations)

        # Find the element with the minimum deviation from the central tendency
        if len(set_1) > 1:
            mean_element_deviations = list(np.mean(element_wise_deviations, axis=0))  
            index_min_deviation = np.where(mean_element_deviations == min(mean_element_deviations))
            central_tendency = set_1[:, 0][index_min_deviation]
        else:
            central_tendency = set_1[0]

        return central_tendency, float(mean_element_wise_deviations), list(element_wise_deviations)


    def distribution(self, data_arg, tend_func=None, linear=True, std_dev=None, abs_diff=None):
        """
        Purpose
        --------
        
            Calculate the central tendency and distribution of the input data and compute probabilities based on deviation.

        Args:
            data_arg (array-like or None): The data on which to compute the distribution. If None, uses self.data.
            tend_func (function, optional): A custom function for calculating the central tendency. 
                                            Defaults to `self.deviation` if not provided.
            linear (bool, optional): If True, the data is linearized before processing. Defaults to True.
            std_dev (bool, optional): If True, the standard deviation is used for calculating deviations. 
                                    If not provided, uses the class attribute `STANDARD_DEVIATION`.
            abs_diff (bool, optional): If True, absolute deviations are used instead of regular deviations. 
                                    Defaults to the class attribute `ABSOLUTE_DIFFERENCE`.

        Returns:
            tuple:
                mean_central_dev (float): The mean deviation from the central tendency.
                distribution (list): A list containing the central tendency and deviations 
                                    (central tendency ± mean deviation).
                absolute_probabilities (list): Absolute probabilities calculated for each bin in the distribution.
                relative_probabilities (list): Relative probabilities calculated for each bin in the distribution.
        """

        tend_func = self.deviation if tend_func is None else tend_func
        std_dev = self.STANDARD_DEVIATION if std_dev is None else std_dev
        abs_diff = self.ABSOLUTE_DIFFERENCE if abs_diff is None else abs_diff

        data = self.data if data_arg is None else np.array(data_arg)
        data_1 = self.linearise(data) if linear else data

        if tend_func.__name__ != self.deviation.__name__:
            central_tendency = tend_func(data)
        else:
            central_tendency = self.deviation(data_1, data, abs_diff=abs_diff)[0][0]

        central_tendency = float(central_tendency) 
        mean_central_dev = self.deviation([central_tendency], data, std_dev=std_dev)[1]

        distribution = sorted([central_tendency - mean_central_dev, central_tendency, central_tendency + mean_central_dev])

        absolute_probabilities, relative_probabilities = self.binData(distribution, data)[1:]

        return mean_central_dev, distribution, absolute_probabilities, relative_probabilities


    def expectation(self, quantity_events, possible_events, probabilities):
        """
        Purpose
        --------
        Compute the expected value of a set of events.

        Args:
            quantity_events (int): Number of times the events occur.
            possible_events (array-like): Possible outcomes of the events.
            probabilities (array-like): Probabilities of each outcome.

        Returns:
            float: Expected value of the events.
        """
        expected_value = quantity_events * np.sum(np.array(possible_events) * np.array(probabilities))
        return float(expected_value)


class TestDataMod(unittest.TestCase):

    def setUp(self):
        """Set up an instance of DataMod with sample data for testing."""
        self.data_mod = DataMod()  

    def test_binData(self):
        """Test the binData method."""
        args = [1, 2, 3, 4], [1, 1, 2, 2, 3, 3, 4, 4]
        result = self.data_mod.binData(*args)
        expected_result = ([2]*4, [0.5]*4, [3]*4, [4]*4) 

        self.assertEqual(result, expected_result)


# Main Execution: Unit test and function calls
if __name__ == '__main__':

    if RUN_UNIT_TESTING:
        unittest.main()

    data_mod = DataMod()

    data = [1, 1, 1, 1, 1]
    bins = [1, 2, 3]

    range = data_mod.binData(bins, data)

    print(data)
    print(range)


