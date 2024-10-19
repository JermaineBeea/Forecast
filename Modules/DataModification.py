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


    def numRange(self, num, data):
        """
        Determines the range in a sorted array where a given number lies.

        This function returns the two elements in `data` such that `num` lies between them.
        If `num` is smaller than the smallest element in `data`, it returns (None, smallest element).
        If `num` is larger than the largest element in `data`, it returns (largest element, None).
        
        Args:
            num (int or float): The number to locate within the range of `data`.
            data (array-like): A sorted array of data_2 to search through.

        Returns:
            tuple: A tuple of two data_2 where `num` lies between them. If `num` is outside the bounds
                of `data`, one of the tuple elements will be `None`.
        """
     
        data = sorted(data) 
        min_data = data[0]
        max_data = data[-1]

        if num < min_data or num > max_data:
            return None
        
        # num is the smallest element
        if num == min_data:
            idx = 0
            value_range = min_data, data[1]

        # num is the largest element
        elif num == max_data:
            idx = len(data) - 2
            value_range = data[-2], max_data  

        else:
            idx = int(np.searchsorted(data, num)) - 1
            value_range = int(data[idx]), int(data[idx + 1])

        return idx , value_range


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

    #TODO GET DISTRIBUTION PROBABILITIES
    def distribution(self, data_arg, tend_func = None,  linear=True, absolute_diff=True):
        """
        Calculate the distribution of central tendency for the provided data.

        Args:
            data_arg (list or array-like): Data to analyze.
            linear (bool): Whether to linearize the data before calculating deviation (default True).
            absolute_diff (bool): If True, use absolute deviation for calculations (default True).

        Returns:
            list: A sorted list containing the lower bound, central tendency, and upper bound.
        """
        tend_func = self.deviation if tend_func is None else tend_func

        # Use class data if no argument provided
        data = self.data if len(data_arg) == 0 else np.array(data_arg)
        # Optionally linearize the data
        linear_data = self.linearise(data) if linear else data

        # Compute the deviation and find central tendency
        central_tendency, mean_deviation = self.deviation(linear_data, data, absolute=absolute_diff)[1]

        central_tendency = central_tendency if tend_func.__name__ == self.deviation.__name__ else tend_func(data)

        # Return lower bound, central tendency, and upper bound based on mean deviation
        return sorted([float(central_tendency - mean_deviation), float(central_tendency), float(central_tendency + mean_deviation)])
    

    def distrProb(self, data, distribution):
            ...

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


# Test Functions
if __name__ == '__main__':
    import numpy as np
    from collections import Counter

    data_mod = DataMod()

def bin_data(bin_ranges, data, rnd=2):
    """
    Bins the input data based on defined bin ranges and calculates bin statistics.

    Args:
        bin_ranges (list of int): The list of bin boundaries.
        data (array-like): Input data to be binned.
        rnd (int, optional): The rounding precision for calculations. Defaults to 2.

    Returns:
        tuple: 
            - bins_count (list of int): The count of items in each bin.
            - bins_abs_factor (list of float): The absolute bin frequency factors.
            - bins_rel_factor (list of float): The relative bin frequency factors.
    """
    # Set predefined bin ranges
    bin_count = len(bin_ranges)

    # Input dataset
    size_data = len(data)

    # Initialize bin statistics lists
    bins_count = [0] * (bin_count - 1)  # Count of elements per bin
    bins_abs_factor = [0] * (bin_count - 1)  # Absolute frequency factor per bin
    bins_rel_factor = [0] * (bin_count - 1)  # Relative frequency factor per bin

    # Total number of data points within the bin range
    num_in_bin_range = sum((data >= min(bin_ranges)) & (data <= max(bin_ranges)))

    # Count occurrences of each element in the dataset
    element_counts = Counter(data)

    # Loop through each unique element in the data
    for value in np.unique(data):
        # Determine the bin range for the current value
        bin_index = data_mod.numRange(value, bin_ranges)
        
        if bin_index is not None:  # If the value falls within a bin range
            count = element_counts[value]  # Number of occurrences of the value
            index = bin_index[0]  # Get the bin index

            # Update bin statistics
            bins_count[index] += count
            bins_abs_factor[index] += round(bins_count[index] / size_data, rnd)
            bins_rel_factor[index] += round(count / num_in_bin_range, rnd)
    
    # Return the bin statistics
    return bins_count, bins_abs_factor, bins_rel_factor
