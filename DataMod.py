import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random 

data = np.random.uniform(1, 10, size = 10)

def linearise (data, data_type = float):
    """
    Converts a given ordered set of data into a linear form.

    The linear form is expressed as A_n = A_0 + k*n, where `k` represents the constant change 
    and `A_0` is the starting value of the linear sequence.

    Args:
        data (set, list, or np.ndarray): A collection of numerical data to be sorted and linearized.
        data_type (type): The desired data type of the output. Defaults to float.

    Returns:
        np.ndarray: A numpy array representing the linearized data in the form A_0 + k*n, 
                    with the specified `data_type`.

    Examples:
        >>> linearise([4, 13, 2, 9, 8, 18, 12, 5, 11])
        array([ 2.,  4.,  6.,  8., 10., 12., 14., 16., 18.])
      
        >>> linearise([4, 13, 2, 9, 8, 18, 12, 5, 11], int)
        array([ 2,  4,  6,  8, 10, 12, 14, 16, 18])
    
      For more information about linearization, see:
      `Linearization <https://en.wikipedia.org/wiki/Linearization>`_

  """
    # Convert data to a numpy array if it is not already
    data = np.asarray(data)
    
    # Sort data from lowest to highest
    min_data = data[0]
    max_data = data[-1]

    # Calculate differences and the mean absolute difference
    diff_ = np.diff(data)
    mean_abs_diff = np.mean(np.abs(diff_)) 
    
    # Determine the step size (k) for the range
    if mean_abs_diff == 0:
        raise ValueError("The data does not have sufficient variation to compute a meaningful linear form.")

    # Generate the linear data
    linear_data = np.arange(min_data, max_data + mean_abs_diff, mean_abs_diff)

    # Convert to the specified data type
    linear_data = linear_data.astype(data_type)

    return linear_data

def deviation (set_1, set_2, absolute = False):
    """
    Calculates the differences between each element in `set_1` and all elements in `set_2`.
    The result is a 2D array where each row represents the differences between an element in `set_1`
    and all elements in `set_2`.

    Args:
        set_1 (set, list, or np.ndarray): A set of numerical values OR a variable.
        set_2 (set, list, or np.ndarray): Another set of numerical values OR a variable.
        absolute (bool): If True, calculates the absolute differences; otherwise, calculates regular differences.
                         Defaults to False.

    Returns:
        np.ndarray: A 2D array where each row represents the differences (absolute or regular) between an element in `set_1`
        and all elements in `set_2`.

    Example:
        >>> deviation([1, 2, 3], [4, 5])
        array([[-3, -4],
               [-2, -3],
               [-1, -2]])

        >>> deviation([1, 2, 3], [4, 5], absolute=True)
        array([[3, 4],
               [2, 3],
               [1, 2]])
    
      For more information about Deviation, see:
      `Linearization <https://en.wikipedia.org/wiki/Linearization>`_

    """

    set_1 = np.array(set_1)
    set_2 = np.array(set_2)

    set_1 = set_1.reshape(-1, 1)
    set_2 = set_2.reshape(1, -1)

    # Calculate differences
    deviation_set = np.abs(set_1 - set_2) if absolute else set_1 - set_2

    return deviation_set

# Test Functions
run_main = False
if __name__ == '__main__' and run_main is True:

  val = deviation(1 , [1,2], True)
  print(val)


# Tendency of data set

data = np.random.uniform(1, 20, size = 10)

