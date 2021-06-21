import pandas as pd
import matplotlib.pyplot as plt
import os
from send_handling.live_data import import_data
import numpy as np
from matplotlib.ticker import MaxNLocator


def pd_nanmean(data2mean):
    nansum = np.nansum(data2mean.values)
    count_non_nan = data2mean.count()
    return nansum / count_non_nan


os.chdir("C:/Users/Fraser Baird/OneDrive - University of Surrey/Documents/data/SEND")
filenames = {'MOD': 'CR1000_CountsMod1S.dat', 'UNMOD': 'CR1000_CountsUnmod1S.dat'}
starts = {'MOD': pd.to_datetime(['2021-05-14 10:37:00', '2021-05-14 10:48:00', '2021-05-14 10:58:00']),
          'UNMOD': pd.to_datetime(['2021-05-14 11:13:00', '2021-05-14 11:23:00', '2021-05-14 11:35:00'])}

stops = {'MOD': pd.to_datetime(['2021-05-14 10:46:00', '2021-05-14 10:57:00', '2021-05-14 11:07:00']),
         'UNMOD': pd.to_datetime(['2021-05-14 11:22:00', '2021-05-14 11:32:00', '2021-05-14 11:44:00'])}

colours = {'MOD': ['#66CDAA', '#3C493F'], 'UNMOD': ['#C09BD8', '#663399']}
length = len(starts['MOD'])


binned_data = {'MOD': np.zeros(length), 'UNMOD': np.zeros(length)}
means = {'MOD': np.zeros(length), 'UNMOD': np.zeros(length)}
normed_means = {'MOD': np.zeros(length), 'UNMOD': np.zeros(length)}
errors = {'MOD': np.zeros(length), 'UNMOD': np.zeros(length)}

position_numbers = {'MOD': [2, 1, 3], 'UNMOD': [3, 2, 1]}
for suffix in ['MOD', 'UNMOD']:

    df_key = 'CTS_%s' % suffix
    data = import_data(filenames[suffix], '1S', suffix)

    data = data.mask(data[df_key] > 120)

    ax = data[df_key].plot(color=colours[suffix][0], marker='.', linestyle='None')
    ax.set_xlabel('Time')
    ax.set_ylabel('Count Rate (s$^{-1}$)')

    for i in range(0, length):
        binned_data[suffix][i] = np.nansum(data.loc[starts[suffix][i]:stops[suffix][i], df_key])
        means[suffix][i] = pd_nanmean(data.loc[starts[suffix][i]:stops[suffix][i], df_key])
        errors[suffix][i] = 1 / np.sqrt(binned_data[suffix][i])
        ax.axvline(starts[suffix][i], color='black', linestyle='--')
        ax.axvline(stops[suffix][i], color='black', linestyle='--')

    plt.show()

    ax = plt.gca()
    ax.errorbar(position_numbers[suffix], means[suffix], yerr=errors[suffix] * means[suffix], fmt='none',
                ecolor=colours[suffix][0], capsize=5)
    ax.scatter(position_numbers[suffix], means[suffix], color=colours[suffix][1], marker='s', zorder=100)
    ax.set_xlabel('Detector Position Number')
    ax.set_ylabel('Mean Counts')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.show()


ax = plt.gca()
for suffix in ['MOD', 'UNMOD']:
    norm_const = np.sum(means[suffix])
    normed_means[suffix] = means[suffix]/norm_const
    ax.errorbar(position_numbers[suffix], normed_means[suffix], yerr=errors[suffix] * normed_means[suffix], fmt='none',
                ecolor=colours[suffix][0], capsize=5)
    ax.scatter(position_numbers[suffix], normed_means[suffix], color=colours[suffix][1], marker='s', zorder=100)
    ax.set_xlabel('Detector Position Number')
    ax.set_ylabel('Normalised Counts')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

plt.show()