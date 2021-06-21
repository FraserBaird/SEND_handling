import pandas as pd
import send_handling.plotting as plot
import matplotlib.pyplot as plt
import numpy as np
filename = 'SENDAuto/data/all_data.dat'

data = pd.read_csv(filename, parse_dates=[0], header=0)
data.set_index('DATE_TIME', inplace=True)
data.mask(data['CTS_MOD'] > 1000, inplace=True)

for suffix in ['MOD', 'UNMOD']:
    t_delta_guard = np.logical_and(data['T_DELTA_%s' % suffix] > 66, data['T_DELTA_%s' % suffix] < 1750)
    data.loc[:, 'CT_RATE_%s' % suffix] = data.mask(data['T_DELTA_%s' % suffix] < 50).loc[:, 'CT_RATE_%s' % suffix]
    data.loc[:, 'CT_RATE_%s' % suffix] = data.mask(t_delta_guard).loc[:, 'CT_RATE_%s' % suffix]
    data.loc[:, 'CT_RATE_%s' % suffix] = data.mask(data['T_DELTA_%s' % suffix] > 1850).loc[:, 'CT_RATE_%s' % suffix]
    data.loc[:, 'CT_RATE_%s_CORR' % suffix] = data.mask(data['T_DELTA_%s' % suffix] < 50).loc[:, 'CT_RATE_%s_CORR' % suffix]
    data.loc[:, 'CT_RATE_%s_CORR' % suffix] = data.mask(t_delta_guard).loc[:, 'CT_RATE_%s_CORR' % suffix]
    data.loc[:, 'CT_RATE_%s_CORR' % suffix] = data.mask(data['T_DELTA_%s' % suffix] > 1850).loc[:, 'CT_RATE_%s_CORR' % suffix]


scatter = data.reset_index()
rolled = data.rolling('30T', min_periods=15).mean()

colour1 = ['#66CDAA', '#C09BD8', '#F2D591', '#70DEFF', '#FF5C5C']
colour2 = ['#014421', '#663399', '#C99418', '#0081A7', '#660000']

keys = ['CT_RATE_MOD', 'CT_RATE_UNMOD', 'PA', 'TA', 'RH']
ylabels = ['Moderated Neutron\n Counts, $N_M$', 'Unmoderated Neutron\n Counts, $N_M$', 'Barometric\n Pressure, $P$ ('
                                                                                       'hPa)',
           'Temperature,\n $T$ ($^\circ$C)', 'Relative Humidity,\n $h_R$ (%)']
plot.vert_subplots_2df(scatter, rolled, keys, colour1, colour2, 'report_figs/weather.png', trim=True, ylab=ylabels)

keys = ['Q', 'P_CORR', 'Q_CORR']
ylabels = ['Absolute Humidity,\n $Q$ (g cm$^{-3}$)', 'Pressure\n Correction, $F_p$', 'Humidity\n Correction, $F_Q$']
plot.vert_subplots_2df(scatter, rolled, keys, colour1, colour2, 'report_figs/corrs.png', trim=True, ylab=ylabels)

keys = ['CT_RATE_MOD_CORR', 'CT_RATE_UNMOD_CORR']
ylabels = ['Mod. Neutron\n Counts, $N_M$', 'Unmod. Neutron\n Counts, $N_M$']
plot.vert_subplots_2df(scatter, rolled, keys, colour1, colour2, 'report_figs/corrected.png', trim=True, ylab=ylabels)

colour3 = ['#014421', '#C99418']
colour4 = ['#663399', '#0081A7']
plot.vert_subplots_1df_compare(rolled, ['CT_RATE_MOD', 'CT_RATE_UNMOD'], ['CT_RATE_MOD_CORR', 'CT_RATE_UNMOD_CORR'],
                               colour1, colour2, 'report_figs/compare_corr_uncorr.png', trim=True, ylab=ylabels)

fig, axes = plt.subplots(1, 2, sharey=True, figsize=(6, 4))
axes[0].hist(rolled['CTS_MOD_CORR'].values, bins=51, color='#66CDAA', density=True)
axes[1].hist(rolled['CTS_UNMOD_CORR'].values, bins=51, color='#C09BD8', density=True)
axes[0].set_ylabel('Probability (%)')
axes[0].set_xlabel('Moderated Neutron \n Counts)')
axes[1].set_xlabel('Unmoderated Neutron \n Counts$)')
plt.tight_layout()
plt.savefig('report_figs/corr_hist.png')
plt.show()
