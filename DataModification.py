import numpy as np

global forecast_kwargs


class DataMod:

    def __init__(self, data=None) -> None:

        self.data = data
    
        # global_kwargs = {
        # 'data': self.data,
        # 'meanTend' : self.meanTend,
        # 'expectation': self.expectation,
        # 'func' :self.meanTend,
        # 'from_x' : None,
        # 'iterations' : None
        # }

        # self.global_kwargs = global_kwargs
        
    def linearise(self, data_arg=None, data_type=float):
        data = self.data if data_arg is None else data_arg

        data = np.array(data)

        min_data = data.min()
        max_data = data.max()

        diff_ = np.diff(data)
        mean_abs_diff = np.mean(np.abs(diff_))

        if mean_abs_diff == 0:
            raise ValueError(
                'The data does not have sufficient variation to compute a meaningful linear form.'
            )

        data_1 = np.arange(min_data, max_data, mean_abs_diff)

        data_1 = data_1.astype(data_type)

        return data_1

    def deviation(self, set_1, set_2, absolute=False):
        set_1 = np.array(set_1)
        set_2 = np.array(set_2)
        set_1 = set_1.reshape(-1, 1)
        set_2 = set_2.reshape(1, -1)
        deviation_set = np.abs(set_1 - set_2) if absolute else set_1 - set_2

        return deviation_set
    
    def meanTend(self, data_arg=None, linear=True, absolute_diff=True):
        '''
        Calculate the mean tendency of the provided data.

        This method computes the mean central tendency based on the input data. If no data is 
        provided through the `data_arg` parameter, the method will utilize the data 
        specified during the initialization of the class.

        Args:
            data_arg (Default is None):
                The data source for calculating the mean tendency. If None, the method 
                will use the instance data initialized with the class. Default is None.
                    
            linear (bool, optional): 
                If set to True, the method linearizes `data_1` before passing it to 
                the deviation function. Default is True.

            absolute_diff (bool, optional): 
                Indicates whether to compute the absolute difference in the calculation. 
                Default is True.

        Returns:
            float: The mean tendency of the provided data.

        Raises:
            ValueError: If the input data is invalid or incompatible.
        
        Derivation:
        -----------
            1. The mean central tendency is the mean of all elemnts of the data of which have the lowest tendency
                data = [x_0, x_1, .....x_n]
                if x_3 and x_4 have the lowest tendency of data, then mean of central tendency is
                mean_central_tend = mean(x_3, x_4)

            2. The tendency of an elemnet in the data is the mean of the sum of the absolut difference between that elemnt to all other elemnts in the data:
                >>> tendency = mean(SUM[abs(x_0 - x_n)]) for x_n in data, where x_0 is the element in question.
                
        Example:
            >>> mean_tendency = instance.meanTend(data_arg=my_data, linear=False)
        
        **For more info , see link below**:
            `<https://latrobe.libguides.com/maths/measures-of-central-tendency>`
        '''
        data = self.data if data_arg is None else data_arg
        linearise = self.linearise
        deviation = self.deviation

        data = np.array(data)
        data_1 = linearise(data) if linear else data
        deviat_data = deviation(data_1, data, absolute = absolute_diff)
        tend_data = np.apply_along_axis(sum, axis=0, arr=deviat_data)
        index_tend = np.where(tend_data == tend_data.min())
        tendency = data[index_tend].mean()
        return tendency

    def expectation (self, quantity_events, possible_events, probabilities):
        result = quantity_events*sum(event*prob for event, prob in zip(possible_events, probabilities))
        return result
     
    def forecastData(self, data_arg, func = None,  from_x=None, iterations=None, **kwargs):

        data = self.data if data_arg is None else data_arg
        meanTend = self.meanTend
        expectation = self.expectation

        if func == None:
            func = self.meanTend

        from_x = data[-1] if from_x is None else from_x
        iterations = len(data) if iterations is None else iterations

        differences = np.diff(data, n=1)
        size_diff = differences.size

        diff_pos = differences[differences >= 0]
        diff_neg = differences[differences < 0]

        size_pos = diff_pos.size
        size_neg = diff_neg.size

        tend_pos = func(diff_pos)
        tend_neg = func(diff_neg)

        prob_pos = size_pos / size_diff
        prob_neg = size_neg / size_diff

        events = tend_pos, tend_neg
        probs = prob_pos, prob_neg
        num_events = iterations

        change_excpection = expectation(num_events, events, probs)
        expectation_data = from_x + change_excpection
        max_expectation = from_x + iterations * tend_pos
        min_expectation = from_x + iterations * tend_neg

        return expectation_data, min_expectation, max_expectation

# Test Functions
if __name__ == '__main__':

    import pandas as pd
    import matplotlib.pyplot as plt
    from Forex import exchangeRate

    path = r'/home/wtc/Documents/RepositoryAccounts/Personal_GitHUb/Forecast/EURAUD.ifx.csv'
    data = pd.read_csv(path, sep='\t')['<CLOSE>'].dropna()

    data_size = data.size
    data = data.to_list()

    instance = DataMod()
    forecast, min_cast, max_cast = instance.forecastData(data)

    # Buy -> converted to source, then trade on source to converted
    # Sell -> source to converted, then trade on converted to source

    # Rate to buy is inverse of rate given 
    # Rate to sell is rate given

    source = 'AUD'
    converted = 'EUR'
    Trade_units = converted + source

    investment_currency = 'ZAR'
    profit_currency = 'ZAR'

    rate_source_conv = data[-1]

    rate_inv_source = exchangeRate(investment_currency, source)

    print(rate_inv_source)

    # region Plot Data 
    plot_data = False
    if plot_data:
        plt.figure(figsize=(12, 6))
        plt.title(f'Forcast of {Trade_units}', color='black')
        x_plot_range = range(data_size)
        plt.plot(x_plot_range, data, color='blue')

        rnd = 2
        col = 'red'
        h_lines = forecast
        plt.axhline(
            y=forecast,
            label=f'Forecast is {round(forecast, rnd)} ',
            color=col,
            linewidth=0.8,
            linestyle='--',
        )

        # Plot the linear line from the last data point to the forecast
        plt_linear = False
        if plt_linear:
            x_start = data_size - 1  # Last index
            y_start = data[-1]        # Last data point
            x_end = data_size + len(data)  # Next index for forecast + iterations
            y_end = forecast           # Forecast value

            # Create a linear line from (x_start, y_start) to (x_end, y_end)
            x_values = np.linspace(x_start, x_end, num=len(data) + 10)  # More points for a smooth line
            y_values = np.linspace(y_start, y_end, num=len(x_values))   # Linear interpolation

            plt.plot(x_values, y_values, color='green', linestyle='--', linewidth=0.9, label='Forecast Line')

        # region Plot Labels
        empty_plot = []
        col = 'black'
        style = '--'
        width = 0.8
        plt.plot(
            empty_plot,
            label=f'Max of Foracst {round(max_cast, rnd)}',
            linewidth=width,
            color=col,
            linestyle=style,
        )
        plt.plot(
            empty_plot,
            label=f'Min of Forecast  {round(min_cast, rnd)}',
            linewidth=width,
            color=col,
            linestyle=style,
        )
        # endregion

        plt.xlabel('Data Points')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    #endregion