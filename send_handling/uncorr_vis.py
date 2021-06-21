import pandas as pd
import send_handling.plotting as plot
import numpy as np
import matplotlib.pyplot as plt

filename = 'SENDAuto/data/all_data.dat'

data = pd.read_csv(filename, parse_dates=[0], header=0)
data.set_index('DATE_TIME', inplace=True)

keys = ['CT_RATE_MOD', 'CT_RATE_UNMOD']
colour1 = ['#66CDAA', '#C09BD8', '#F2D591', '#70DEFF', '#FF5C5C']
colour2 = ['#014421', '#663399', '#C99418', '#0081A7', '#660000']
ylabels = ['Moderated Neutron\n Counts, $N_M$ (s$^{-1}$)', 'Unmoderated Neutron\n Counts, $N_M$ (s$^{-1}$)']
plot.vert_subplots_1df(data, keys, colour1, 'report_figs/no_t_guard.png', no_minor=True, ylab=ylabels)


for suffix in ['MOD', 'UNMOD']:
    t_delta_guard = np.logical_and(data['T_DELTA_%s' % suffix] > 60, data['T_DELTA_%s' % suffix] < 1750)
    data.loc[:, 'CT_RATE_%s' % suffix] = data.mask(data['T_DELTA_%s' % suffix] < 50).loc[:, 'CT_RATE_%s' % suffix]
    data.loc[:, 'CT_RATE_%s' % suffix] = data.mask(t_delta_guard).loc[:, 'CT_RATE_%s' % suffix]
    data.loc[:, 'CT_RATE_%s' % suffix] = data.mask(data['T_DELTA_%s' % suffix] > 1850).loc[:, 'CT_RATE_%s' % suffix]

rolled_data = data.rolling('30T', min_periods=15).mean()

fig, axes = plot.vert_subplots_2df(data.reset_index(), rolled_data, keys, colour1, colour2, 'report_figs/t_guard.png',
                       no_minor=True, ylab=ylabels, no_show=True)

axes[0].axvspan(pd.to_datetime('2020-12-26'), pd.to_datetime('2020-12-28'), color=colour1[3], alpha=0.5)
axes[0].axvspan(pd.to_datetime('2021-01-19'), pd.to_datetime('2021-01-23'), color=colour1[3], alpha=0.5)
axes[0].axvspan(pd.to_datetime('2021-02-06'), pd.to_datetime('2021-02-09'), color=colour1[3], alpha=0.5)
plt.savefig('report_figs/t_guard.png')
plt.show()

fig, axes = plt.subplots(1, 2, sharey=True, figsize=(6, 4))
axes[0].hist(rolled_data['CT_RATE_MOD'].values, bins=50, color='#66CDAA', density=True)
axes[1].hist(rolled_data['CT_RATE_UNMOD'].values, bins=50, color='#C09BD8', density=True)
axes[0].set_ylabel('Probability (%)')
axes[0].set_xlabel('Moderated Neutron \n Count Rate (s$^{-1}$)')
axes[1].set_xlabel('Unmoderated Neutron \n Count Rate (s$^{-1}$)')
plt.tight_layout()
plt.savefig('report_figs/uncorr_hist.png')
plt.show()