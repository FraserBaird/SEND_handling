import os
import pandas as pd
from send_handling.live_data import import_data
import numpy as np
import matplotlib.pyplot as plt


def pd_nanmean(data2mean):
    nansum = np.nansum(data2mean.values)
    count_non_nan = data2mean.count()
    return nansum / count_non_nan


def aggregate_runs(the_dfs):
    aggregated_df = make_aggregated_df(the_dfs['LOG'])
    for i in aggregated_df.index:
        sensor = the_dfs['LOG'].loc[i, 'Sensor']
        start = the_dfs['LOG'].loc[i, 'Start']
        stop = the_dfs['LOG'].loc[i, 'Stop']
        aggregated_df.loc[i, 'Agg_counts'] = np.nansum(the_dfs[sensor].loc[start:stop, 'CTS_%s' % sensor])
        aggregated_df.loc[i, 'Agg_mean'] = pd_nanmean(the_dfs[sensor].loc[start:stop, 'CTS_%s' % sensor])
        aggregated_df.loc[i, 'Agg_err'] = 1/np.sqrt(aggregated_df.loc[i, 'Agg_counts'])
    return aggregated_df


def make_aggregated_df(log_df):
    agg_df = log_df.loc[:, ['Sensor', 'Condition', 'Position']]
    agg_df['Agg_counts'] = np.zeros(len(log_df.index))
    agg_df['Agg_mean'] = np.zeros(len(log_df.index))
    agg_df['Agg_err'] = np.zeros(len(log_df.index))
    return agg_df


def plot_results(result_df):
    conds = result_df.loc[:, 'Condition'].unique()
    sens = result_df.loc[:, 'Sensor'].unique()
    n_cols = len(sens)

    fig, axes = plt.subplots(1, n_cols)
    colours = ['#66CDAA', '#3C493F']
    for i in range(n_cols):
        for j in range(len(conds)):
            sensor = sens[i]
            condition = conds[j]

            run_res = result_df.where(np.logical_and((result_df['Condition'] == condition),
                                      (result_df['Sensor'] == sensor))).dropna(axis=0).sort_values(by='Position')

            axes[i].scatter(run_res['Position'].values, run_res['Agg_mean'].values, color=colours[j])
            axes[i].errorbar(run_res['Position'].values, run_res['Agg_mean'].values,
                             yerr=run_res['Agg_mean'].values*run_res['Agg_err'].values, color=colours[j], fmt='none',
                             capsize=5)

    axes[0].set_ylabel('Mean Count Rate (Moderated), s$^{-1}$')
    axes[1].set_ylabel('Mean Count Rate (Unmoderated), s$^{-1}$')
    axes[0].set_xlabel('Position (Source Number)')
    axes[1].set_xlabel('Position (Source Number)')

    plt.tight_layout()
    plt.legend(['Pump In Water', 'Pump Removed'])

    plt.show()


experiment_name = "PumpExp"
os.chdir('C:/Users/Fraser Baird/OneDrive - University of Surrey/Documents/data/SEND/ExperimentalData')
fnames = {'MOD': experiment_name + 'Mod.dat', 'UNMOD': experiment_name + 'Unmod.dat',
          'LOG': 'ExperimentLogs/%s.csv' % experiment_name}

dfs = {'LOG': pd.read_csv(fnames['LOG'], header=0, parse_dates=[1, 2]), 'MOD': import_data(fnames['MOD'], '1S', 'MOD'),
       'UNMOD': import_data(fnames['UNMOD'], '1S', 'UNMOD')}

res_df = aggregate_runs(dfs)
plot_results(res_df)

print('test')
