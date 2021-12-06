import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as ss

filename = 'C:/Users/Fraser Baird/OneDrive - University of Surrey/Documents/data/SENDAuto/CorrData.dat'

data = pd.read_csv(filename, parse_dates=[0], header=0)
data.set_index('DATE_TIME', inplace=True)
data.mask(data['CTS_MOD'] > 1000, inplace=True)
data.dropna(inplace=True)

min300 = data.rolling('300T', min_periods=150).mean()
min300.dropna(inplace=True)


regress = dict()
regress['MOD_P_UN'] = ss.linregress(min300['PA'].values, np.log(min300['CTS_MOD'].values))
regress['MOD_P_CORR_EMP'] = ss.linregress(min300['PA'].values, np.log(min300['CTS_MOD_CORR_EMP'].values))


fig, axes = plt.subplots(1, 2, sharex=True, figsize=(6,3))
axes[0].scatter(min300['PA'], np.log(min300['CTS_MOD']), color='blue', marker='.')
axes[1].scatter(min300['PA'], np.log(min300['CTS_MOD_CORR_EMP']), color='blue', marker='.')

axes[0].plot(min300['PA'], regress['MOD_P_UN'].slope * min300['PA'] + regress['MOD_P_UN'].intercept, color='black')
axes[1].plot(min300['PA'], regress['MOD_P_CORR_EMP'].slope * min300['PA'] + regress['MOD_P_CORR_EMP'].intercept,
             color='black')


axes[0].annotate('m=%0.5f c=%0.1f r$^2$=%0.2f' % (regress['MOD_P_UN'].slope, regress['MOD_P_UN'].intercept,
                                                  regress['MOD_P_UN'].rvalue**2), xy=(980, 2.61))
axes[1].annotate('m=%0.5f c=%0.1f r$^2$=%0.2f' % (regress['MOD_P_CORR_EMP'].slope, regress['MOD_P_CORR_EMP'].intercept,
                                                  regress['MOD_P_CORR_EMP'].rvalue**2), xy=(980, 2.65))

axes[0].set_xlabel('p, hPa')
axes[1].set_xlabel('p, hPa')


axes[0].set_ylabel('MOD detector counts, minute$^{-1}$')
axes[1].set_ylabel('Corrected MOD detector counts, minute$^{-1}$')

plt.tight_layout(True)
# plt.savefig('MOD_corr_performance.png', dpi=600)
plt.show()