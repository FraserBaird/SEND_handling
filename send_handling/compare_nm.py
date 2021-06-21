import pandas as pd

from coscal import coscal as cc
import numpy as np
import matplotlib as mpl
import send_handling.plotting as plot


def import_nm_data(count_fname, pressure_fname):
    nmcnts = pd.read_table(count_fname, sep=';', header=0, parse_dates=[0])
    nmp = pd.read_table(pressure_fname, sep=';', header=0, parse_dates=[0])

    nmcnts.replace({'   null': np.nan}, inplace=True)
    nmp.replace({'   null': np.nan}, inplace=True)

    nmcnts.set_index('DATE_TIME', inplace=True)
    nmp.set_index('DATE_TIME', inplace=True)
    nmcnts = pd.concat((nmcnts, nmp), axis=1)

    nmcnts = nmcnts.astype('float')
    nmcnts = nmcnts.resample('1T').asfreq()
    stations = ['DRBS', 'NEWK']

    rigidity = [3.18, 2.4]

    for i in range(len(stations)):
        corr = cc.get_corr_factors(nmcnts, {'p_corr': stations[i] + '_PRESS', 'h_corr': None}, rigidity[i])
        nmcnts[stations[i] + '_CORR'] = nmcnts[stations[i]] * corr['p_corr']

    return nmcnts


mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=['#C09BD8', '#FF5C5C', '#70DEFF', '#F2D591', ])

nm_counts = import_nm_data('SENDAuto/drbs-newk.txt', 'SENDAuto/drbs-newk-press.txt')

sand = pd.read_csv('SENDAuto/CorrData.dat', parse_dates=[0], header=0)
sand.set_index('DATE_TIME', inplace=True)
sand.mask(sand['CTS_MOD'] > 1000, inplace=True)

for suffix in ['MOD', 'UNMOD']:
    t_delta_guard = np.logical_and(sand['T_DELTA_%s' % suffix] > 60, sand['T_DELTA_%s' % suffix] < 1750)
    sand.loc[:, 'CT_RATE_%s' % suffix] = sand.mask(sand['T_DELTA_%s' % suffix] < 50).loc[:, 'CT_RATE_%s' % suffix]
    sand.loc[:, 'CT_RATE_%s' % suffix] = sand.mask(t_delta_guard).loc[:, 'CT_RATE_%s' % suffix]
    sand.loc[:, 'CT_RATE_%s' % suffix] = sand.mask(sand['T_DELTA_%s' % suffix] > 1850).loc[:, 'CT_RATE_%s' % suffix]
    sand.loc[:, 'CT_RATE_%s_CORR' % suffix] = sand.mask(sand['T_DELTA_%s' % suffix] < 50).loc[:, 'CT_RATE_%s_CORR' % suffix]
    sand.loc[:, 'CT_RATE_%s_CORR' % suffix] = sand.mask(t_delta_guard).loc[:, 'CT_RATE_%s_CORR' % suffix]
    sand.loc[:, 'CT_RATE_%s_CORR' % suffix] = sand.mask(sand['T_DELTA_%s' % suffix] > 1850).loc[:, 'CT_RATE_%s_CORR' % suffix]


sand = sand.rolling('180T').mean()
nm = nm_counts.rolling('180T').mean()

print('NEWK (180 Min) Mean: %s' % nm['NEWK_CORR'].mean())
print('DRBS (180 Min) Mean: %s' % nm['DRBS_CORR'].mean())
print('CRNS Mod (180 Min) Mean: %s' % sand['CT_RATE_MOD_CORR'].mean())
print('NEWK (180 Min) Mean: %s' % sand['CT_RATE_UNMOD_CORR'].mean())

plot.one_plot_2_dfs(nm, sand, ['DRBS_CORR', 'NEWK_CORR'], ['CT_RATE_MOD_CORR', 'CT_RATE_UNMOD_CORR'], True,
               ['Counts (s$^{-1}$)', 'Date'], [[pd.to_datetime("2021-03-11 16:35:00"), sand.index[-1]], [0.1, 1000]],
               'report_figs/nmcomp.png')


sand['MOD_NORM'] = sand['CT_RATE_MOD_CORR'] / sand['CT_RATE_MOD_CORR'].mean()
sand['UNMOD_NORM'] = sand['CT_RATE_UNMOD_CORR'] / sand['CT_RATE_UNMOD_CORR'].mean()
nm['DRBS_NORM'] = nm['DRBS_CORR'] / nm['DRBS_CORR'].mean()
nm['NEWK_NORM'] = nm['NEWK_CORR'] / nm['NEWK_CORR'].mean()

plot.one_plot_2_dfs(nm, sand, ['DRBS_NORM', 'NEWK_NORM'], ['MOD_NORM', 'UNMOD_NORM'], False,
               ['Normalised Counts (arb. units)', 'Date'], [[pd.to_datetime("2021-03-11 16:35:00"), sand.index[-1]], [0.9, 1.1]],
               'report_figs/nmnormcomp.png')



