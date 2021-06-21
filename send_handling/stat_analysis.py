import pandas as pd
import numpy as np
import send_handling.plotting as plot


def import_sand(filename):
    df = pd.read_csv(filename, parse_dates=[0], header=0)
    df.set_index('DATE_TIME', inplace=True)
    df = t_delta_gd(df)

    return df


def t_delta_gd(df):
    for suffix in ['MOD', 'UNMOD']:
        t_delta_guard = np.logical_and(df['T_DELTA_%s' % suffix] > 66, df['T_DELTA_%s' % suffix] < 1620)
        for key in ['CT_RATE_%s' % suffix, 'CTS_%s_CORR' % suffix, 'CT_RATE_%s_CORR' % suffix,  'CTS_%s' % suffix]:
            df.loc[:, key] = df.mask(df['T_DELTA_%s' % suffix] < 54).loc[:, key]
            df.loc[:, key] = df.mask(t_delta_guard).loc[:, key]
            df.loc[:, key] = df.mask(df['T_DELTA_%s' % suffix] > 1980).loc[:, key]

    return df


filename = 'SENDAuto/data/all_data.dat'

sand = import_sand(filename)

plot.hist(sand, ['CTS_MOD', 'CTS_UNMOD'], ['Moderated CRNS \n Counts', 'Unmoderated CRNS \n Counts'],
          'report_figs/uncorr_hist.png')
plot.hist(sand, ['CTS_MOD_CORR', 'CTS_UNMOD_CORR'], ['Moderated CRNS \n Corrected Counts', 'Unmoderated CRNS \n Corrected Counts'],
          'report_figs/corr_hist.png')

print('mean(moderated corrected counts) = %s' % sand['CTS_MOD_CORR'].mean())
print('mean(unmoderated corrected counts) = %s' % sand['CTS_UNMOD_CORR'].mean())
