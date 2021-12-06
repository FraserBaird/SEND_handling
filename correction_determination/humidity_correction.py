import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as ss
import scipy.optimize as so
import coscal.coscal as cc

def cubic(x, a, b, c, d):
    y = a*x**3 + b*x**2 + c*x + d
    return y


filename = 'C:/Users/Fraser Baird/OneDrive - University of Surrey/Documents/data/COSMOS-UK_OLD/CHOBH.csv'

data = pd.read_csv(filename, parse_dates=[0], header=0)
data.set_index('DATE_TIME', inplace=True)
data.mask(data['Q'] > 20, inplace=True)
data[['CTS_MOD', 'Q']].dropna(inplace=True)
data['CTS_MOD_CORR'] = data['CTS_MOD'] * cc.pressure_correction(data['PA'], 2.9, .00701)
min300 = data.rolling('300T').mean()





regress = dict()
regress['MOD_Q_UN'] = ss.linregress(min300['Q'].values, min300['CTS_MOD'].values)
regress['MOD_Q_CORR_EMP'] = ss.linregress(min300['Q'].values, min300['CTS_MOD_CORR'].values)


fig, axes = plt.subplots(1, 2, sharex=True, figsize=(6,3))
axes[0].scatter(min300['Q'], min300['CTS_MOD'], color='blue', marker='.')
axes[1].scatter(min300['Q'], min300['CTS_MOD_CORR'], color='blue', marker='.')

axes[0].plot(min300['Q'], regress['MOD_Q_UN'].slope * min300['Q'] + regress['MOD_Q_UN'].intercept, color='black')
axes[1].plot(min300['Q'], regress['MOD_Q_CORR_EMP'].slope * min300['Q'] + regress['MOD_Q_CORR_EMP'].intercept,
             color='black')


axes[0].set_xlabel('Q')
axes[1].set_xlabel('Q')

axes[0].set_ylabel('MOD detector counts, minute$^{-1}$')
axes[1].set_ylabel('Corrected MOD detector counts, minute$^{-1}$')

plt.tight_layout(True)
plt.savefig('MOD_corr_performance.png', dpi=600)
plt.show()