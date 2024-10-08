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
    min_expectation = from_x + iterations*tend_neg

    return expectation_data, min_expectation, max_expectation

path = r'/home/wtc/Documents/RepositoryAccounts/Personal_GitHUb/Forecast/EURAUD.ifx.csv'
data = pd.read_csv(path, sep = '\t')['<CLOSE>'].dropna()

data_size = data.size
data = data.to_list()

indx_start = data_size//4
indx_end = data_size
forecast, min_cast, max_cast = expectation(data)


# Plot Data
plt.title('Forcast', color = 'black')
x_plot_range = range(data_size)
plt.plot(x_plot_range, data, color = 'blue')

rnd = 2
col = 'red'
h_lines = forecast
plt.axhline(y = forecast, label = f'Forecast is {round(forecast, rnd)} ', color = col, linewidth = 0.8, linestyle = '--')

# Plot Labels
empty_plot = []
col = 'black'; style = '--'; width = 0.8
plt.plot(empty_plot,  label = f'Max of Foracst {round(max_cast, rnd)}', linewidth = width, color = col, linestyle = style)
plt.plot(empty_plot, label = f'Min of Forecast  {round(min_cast, rnd)}', linewidth = width, color = col, linestyle  = style)

plt.legend()
plt.show()
