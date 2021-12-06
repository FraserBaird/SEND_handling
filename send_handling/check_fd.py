import pandas as pd

from live_data import get_corrected_data
import os
import matplotlib.pyplot as plt


if __name__ == "__main__":
    os.chdir("C:/Users/Fraser Baird/OneDrive - University of Surrey/Documents/data/SEND/ExperimentalData/MonitorStuff")
    nm_data = pd.read_table('DRBS.dat', sep=';', parse_dates=[0])
    nm_data.set_index('DATE_TIME', inplace=True)
    nm_data = nm_data.resample('60S').asfreq()
    nm_data = nm_data.rolling('12H', min_periods=6*60).mean()
    data = get_corrected_data()
    data = data.resample('60S').asfreq()
    data = data.rolling('12H', min_periods=6 * 60).mean()/60
    colour = '#002768'
    fig, ax = plt.subplots(3, 1, sharex=True)
    data['CTS_MOD_CORR'].plot(ax=ax[0], color=colour, label='Moderated 12 Hour Rolling Mean')
    data['CTS_UNMOD_CORR'].plot(ax=ax[1], color=colour, label='Unmoderated 12 Hour Rolling Mean')
    nm_data['CTS'].plot(ax=ax[2], color=colour, label='Dourbes NM 12 Hour Rolling Mean')
    for axis in ax:
        axis.legend()
        axis.axvline('2021-11-03 19:57', color='black', linestyle=':')
        axis.axvline('2021-10-31 09:00', color='black', linestyle='-.')
        axis.axvline('2021-10-28 16:00', color='black', linestyle='--')
        axis.set_ylabel('Counts, s$^{-1}$')
        axis.set_xlabel('Time')
    plt.tight_layout()
    # plt.savefig('fd.png', dpi=600)
    plt.show()
