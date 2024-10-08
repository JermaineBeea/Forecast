import numpy as np

class DataMod ():
   
    def __init__(self, data = None) -> None:
        
        self.data = data

    def linearise (self, data_arg = None, data_type = float):
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
        data = self.data if data_arg is None else data_arg

        data = np.array(data)
        
        min_data = data.min()
        max_data = data.max()

        diff_ = np.diff(data)
        mean_abs_diff = np.mean(np.abs(diff_)) 
        
        if mean_abs_diff == 0:
            raise ValueError("The data does not have sufficient variation to compute a meaningful linear form.")

        # Generate the linear data
        linear_data = np.arange(min_data, max_data + mean_abs_diff, mean_abs_diff)

        # Convert to the specified data type
        linear_data = linear_data.astype(data_type)

        return linear_data

# Test Functions
if __name__ == '__main__':


    data_n = [1, 2, 3, 4, 5, 6, 7, 9, 11, 13, 15, 17, 19, 22, 25, 28]

    instance = DataMod()
    res = instance.linearise(data_n)

    print(res)



