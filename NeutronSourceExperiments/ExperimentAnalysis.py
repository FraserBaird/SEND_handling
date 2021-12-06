import os
import pandas as pd
from send_handling.live_data import import_data
import numpy as np
import matplotlib.pyplot as plt


def pd_nanmean_count_rate(data2mean, integration_time_int):
    nansum = np.nansum(data2mean.values)
    count_non_nan = data2mean.count()
    naive_cr = nansum / ((count_non_nan - 1) * integration_time_int)
    tau_corr_cr = dead_time_corr(naive_cr)
    return tau_corr_cr[0]


def dead_time_corr(raw_cr):
    true_rates = np.arange(0, 300, 0.01)
    output_rates = takacs_model(true_rates, theta=0.1707, tau=0.000687)
    closest_output_rates_ind = get_closest_inds(raw_cr, output_rates)

    return true_rates[closest_output_rates_ind]


def get_closest_inds(raw, calc_output):

    abs_difference = np.abs(raw - calc_output)
    index = np.where(abs_difference == np.min(abs_difference))

    return index


def takacs_model(true, theta, tau):
    return (true * theta) / (np.exp(true * theta * tau) + theta - 1)


def aggregate_runs(the_dfs):
    aggregated_df = make_aggregated_df(the_dfs['LOG'])
    for i in aggregated_df.index:
        sensor = the_dfs['LOG'].loc[i, 'Sensor']
        start = the_dfs['LOG'].loc[i, 'Start']
        stop = the_dfs['LOG'].loc[i, 'Stop']
        aggregated_df.loc[i, 'Agg_counts'] = np.nansum(the_dfs[sensor].loc[start:stop, 'CTS_%s' % sensor])
        aggregated_df.loc[i, 'Agg_mean'] = pd_nanmean_count_rate(the_dfs[sensor].loc[start:stop, 'CTS_%s' % sensor], 15)
        aggregated_df.loc[i, 'Agg_err'] = 1/np.sqrt(aggregated_df.loc[i, 'Agg_counts'])
    return aggregated_df


def make_aggregated_df(log_df):
    agg_df = log_df.loc[:, ['Sensor', 'Condition', 'Position']]
    agg_df['Agg_counts'] = np.zeros(len(log_df.index))
    agg_df['Agg_mean'] = np.zeros(len(log_df.index))
    agg_df['Agg_err'] = np.zeros(len(log_df.index))
    return agg_df


def plot_results(result_df):
    positions = result_df.loc[:, 'Position'].unique()
    sens = result_df.loc[:, 'Sensor'].unique()
    n_cols = len(sens)

    fig, axes = plt.subplots(1, n_cols)
    # colours = ['#3C493F', '#66CC76', '#66CDAA']
    for i in range(n_cols):
        for j in range(len(positions)):
            sensor = sens[i]
            pos = positions[j]

            run_res = result_df.where(np.logical_and((result_df['Position'] == pos),
                                      (result_df['Sensor'] == sensor))).dropna(axis=0).sort_values(by='Position')

            axes[i].scatter(run_res['Condition'].values, run_res['Agg_mean'].values / 15, marker='.')
            axes[i].errorbar(run_res['Condition'].values, run_res['Agg_mean'].values / 15,
                             yerr=run_res['Agg_mean'].values*run_res['Agg_err'].values / 15, fmt='none',
                             capsize=5)

    axes[0].set_ylabel('Mean Count Rate (Moderated), s$^{-1}$')
    axes[1].set_ylabel('Mean Count Rate (Unmoderated), s$^{-1}$')
    axes[0].set_xlabel('Water Depth (cm)')
    axes[1].set_xlabel('Water Depth (cm)')
    axes[0].legend(['Position 1', 'Position 2', 'Position 3'])
    axes[1].legend(['Position 1', 'Position 2', 'Position 3'])

    plt.tight_layout()
    # plt.legend(result_df['Position'].unique())
    plt.savefig('depth.png', dpi=600)
    plt.show()

    return


experiment_name = "ThermalDepth"
os.chdir('C:/Users/Fraser Baird/OneDrive - University of Surrey/Documents/data/SEND/ExperimentalData')
fnames = {'MOD': experiment_name + 'Mod.dat', 'UNMOD': experiment_name + 'Unmod.dat',
          'LOG': 'ExperimentLogs/%s.csv' % experiment_name}

dfs = {'LOG': pd.read_csv(fnames['LOG'], header=0, parse_dates=[1, 2]), 'MOD': import_data(fnames['MOD'], '1S', 'MOD'),
       'UNMOD': import_data(fnames['UNMOD'], '1S', 'UNMOD')}

res_df = aggregate_runs(dfs)
# plot_results(res_df)
# res_df.to_csv('%s_analysed.csv' % experiment_name, index=False)
print('test')
