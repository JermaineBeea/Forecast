import numpy as np


class DataMod:

    def __init__(self, data=None) -> None:

        self.data = data

    def linearise(self, data_arg=None, data_type=float):
        data = self.data if data_arg is None else data_arg

        data = np.array(data)

        min_data = data.min()
        max_data = data.max()

        diff_ = np.diff(data)
        mean_abs_diff = np.mean(np.abs(diff_))

        if mean_abs_diff == 0:
            raise ValueError(
                "The data does not have sufficient variation to compute a meaningful linear form."
            )

        linear_data = np.arange(min_data, max_data, mean_abs_diff)

        linear_data = linear_data.astype(data_type)

        return linear_data

    def deviation(self, set_1, set_2, absolute=False):
        set_1 = np.array(set_1)
        set_2 = np.array(set_2)

        set_1 = set_1.reshape(-1, 1)
        set_2 = set_2.reshape(1, -1)

        deviation_set = np.abs(set_1 - set_2) if absolute else set_1 - set_2

        return deviation_set

    def meanTend(self, data_arg=None):
        data = self.data if data_arg is None else data_arg
        linearise = self.linearise
        deviation = self.deviation

        data = np.array(data)
        linear_data = linearise(data)
        deviat_data = deviation(linear_data, data, True)
        tend_data = np.apply_along_axis(np.sum, axis=0, arr=deviat_data)
        index_tend = np.where(tend_data == tend_data.min())
        tendency = data[index_tend].mean()
        return tendency

    def expectation(self, data_arg, from_x=None, iterations=None):
        data = self.data if data_arg is None else data_arg
        meanTend = self.meanTend

        from_x = data[-1] if from_x is None else from_x
        iterations = len(data) if iterations is None else iterations

        differences = np.diff(data, n=1)
        size_diff = differences.size

        diff_pos = differences[differences >= 0]
        diff_neg = differences[differences < 0]

        size_pos = diff_pos.size
        size_neg = diff_neg.size

        tend_pos = meanTend(diff_pos)
        tend_neg = meanTend(diff_neg)

        prob_pos = size_pos / size_diff
        prob_neg = size_neg / size_diff

        change_excpection = iterations * (prob_pos * tend_pos + prob_neg * tend_neg)
        expectation_data = from_x + change_excpection
        max_expectation = from_x + iterations * tend_pos
        min_expectation = from_x + iterations * tend_neg

        return expectation_data, min_expectation, max_expectation


# Test Functions
if __name__ == "__main__":

    import pandas as pd
    import matplotlib.pyplot as plt

    path = r"/home/wtc/Documents/RepositoryAccounts/Personal_GitHUb/Forecast/EURAUD.ifx.csv"
    data = pd.read_csv(path, sep="\t")["<CLOSE>"].dropna()

    data_size = data.size
    data = data.to_list()

    indx_start = data_size // 4
    indx_end = data_size

    instance = DataMod()
    forecast, min_cast, max_cast = instance.expectation(data)

    # Plot Data
    plt.title("Forcast", color="black")
    x_plot_range = range(data_size)
    plt.plot(x_plot_range, data, color="blue")

    rnd = 2
    col = "red"
    h_lines = forecast
    plt.axhline(
        y=forecast,
        label=f"Forecast is {round(forecast, rnd)} ",
        color=col,
        linewidth=0.8,
        linestyle="--",
    )

    # Plot Labels
    empty_plot = []
    col = "black"
    style = "--"
    width = 0.8
    plt.plot(
        empty_plot,
        label=f"Max of Foracst {round(max_cast, rnd)}",
        linewidth=width,
        color=col,
        linestyle=style,
    )
    plt.plot(
        empty_plot,
        label=f"Min of Forecast  {round(min_cast, rnd)}",
        linewidth=width,
        color=col,
        linestyle=style,
    )

    plt.legend()
    plt.show()
