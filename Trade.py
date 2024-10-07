import numpy as np
import pandas as pd

from DataMod import meanTend

path = r'EURAUD.ifx.csv'


data = pd.read_csv(path, sep = '\t')['<CLOSE>'].dropna()
data = data.to_list()

differences = np.diff(data, n = 1)
size_diff = differences.size

diff_pos = differences[differences >= 0]
diff_neg = differences[differences < 0]

size_pos = diff_pos.size
size_neg = diff_neg.size

tend_pos = meanTend(diff_pos)
tend_neg = meanTend(diff_neg)

prob_pos = size_pos/size_diff

excpec = tend_pos


