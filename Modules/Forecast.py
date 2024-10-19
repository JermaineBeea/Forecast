import numpy as np

"""_summary_
"""


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

