import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from DataMod import meanTend

def expectation (data, from_x = None , iterations = None):

    from_x = data[-1] if from_x is None else from_x
    iterations = len(data) if iterations is None else iterations

    differences = np.diff(data, n = 1)
    size_diff = differences.size

    diff_pos = differences[differences >= 0]
    diff_neg = differences[differences < 0]

    size_pos = diff_pos.size
    size_neg = diff_neg.size

    tend_pos = meanTend(diff_pos)
    tend_neg = meanTend(diff_neg)

    prob_pos = size_pos/size_diff
    prob_neg = size_neg/size_diff

    change_excpection = iterations*(prob_pos*tend_pos + prob_neg*tend_neg)
    expectation_data = from_x + change_excpection
    max_expectation = from_x + iterations*tend_pos
    min_expectation = from_x - iterations*tend_neg

    return expectation_data, max_expectation, min_expectation

path = r'/home/wtc/Documents/RepositoryAccounts/Personal_GitHUb/Forecast/EURAUD.ifx.csv'
data = pd.read_csv(path, sep = '\t')['<CLOSE>'].dropna()
data_size = data.size
data = data.to_list()

indx_start = data_size//4
indx_end = data_size


# Plot Data
data_plotted = data[indx_start: indx_end]
x_plot_range = range(indx_start, indx_end)

plt.plot(x_plot_range, data_plotted, color = 'red')
plt.show()