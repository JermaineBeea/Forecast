import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from Forecast.Data_Modification import meanTend, expectation

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
