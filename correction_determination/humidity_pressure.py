import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as ss
import scipy.optimize as so

filename = 'C:/Users/Fraser Baird/OneDrive - University of Surrey/Documents/data/COSMOS-UK_OLD/CorrData.dat'

data = pd.read_csv(filename, parse_dates=[0], header=0)
data.set_index('DATE_TIME', inplace=True)
data.mask(data['CTS_MOD'] > 1000, inplace=True)
data.dropna(inplace=True)

min300 = data.rolling('300T', min_periods=150).mean()
min300.dropna(inplace=True)


regress = dict()
regress['Q_PA'] = ss.linregress(min300['Q'].values, min300['PA'].values)
# regress['MOD_Q_CORR_EMP'] = ss.linregress(min300['Q'].values, min300['PA'].values)


fig, axes = plt.subplots(1, 1, sharex=True, figsize=(6,3))
axes.scatter(min300['Q'], min300['PA'], color='blue', marker='.')


axes.plot(min300['Q'], regress['Q_PA'].slope * min300['Q'] + regress['Q_PA'].intercept, color='black')

axes.set_xlabel('Q')

axes.set_ylabel('PA')

plt.tight_layout(True)
# plt.savefig('MOD_corr_performance.png', dpi=600)
plt.show()