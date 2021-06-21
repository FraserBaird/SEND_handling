import numpy as np
import matplotlib.pyplot as plt


def get_n(sig, inc, mn):
    n = (sig ** 2) / (mn * ((inc - 1) ** 2))
    return np.ceil(n)


significance = 3

increases = {'70': {'1min': 1.32, '10min': 1.22, '30min': 1.17},
             '69': {'1min': 2.5, '10min': 1.8, '30min': 1.6},
             '66': {'1min': 1.14, '10min': 1.13, '30min': 1.12}}

means = {'MOD': {'1min': 24.53, '10min': 245.3, '30min': 735.9},
         'UNMOD': {'1min': 16.33, '10min': 163.3, '30min': 489.9}}

for gle in increases.keys():
    for model in means.keys():
        for time in increases[gle].keys():
            n_detectors = get_n(significance, increases[gle][time], means[model][time])
            print('GLE %s, %s, %s resolution (solar min): %s detectors' % (gle, model, time, n_detectors))
            n_detectors = get_n(significance, increases[gle][time], 0.9 * means[model][time])
            print('GLE %s, %s, %s resolution (solar max): %s detectors' % (gle, model, time, n_detectors))