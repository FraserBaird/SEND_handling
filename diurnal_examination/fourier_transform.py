import scipy.fftpack as fft
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def import_send():
    filename = 'C:/Users/Fraser Baird/OneDrive - University of Surrey/Documents/data/SENDAuto/CorrData.dat'
    start = pd.to_datetime('2021-10-01 00:00')
    end = pd.to_datetime('2021-11-05 00:00')
    data = pd.read_csv(filename, parse_dates=[0], header=0)
    data.set_index('DATE_TIME', inplace=True)
    data = data[start:end].resample('1T').asfreq()
    data.mask(data['CTS_MOD'] > 1000, inplace=True)
    data = data.rolling('12H').mean()
    data.interpolate(inplace=True)
    return data


sbnm = import_send()
ax = sbnm['CTS_MOD_CORR_EMP'].plot()


mean = np.nanmean(sbnm['CTS_MOD_CORR_EMP'].values)
poiss = np.sqrt(mean)
size = len(sbnm.index)
noise = np.random.normal(mean, poiss, size)
ax.axhline(mean, zorder=100, color='black')

plt.show()

plt.plot(sbnm.index, noise, color='red', zorder=150)
plt.show()

mod_counts_fft = fft.fft(sbnm['CTS_MOD_CORR_EMP'].values)
mod_counts_power = np.abs(mod_counts_fft)

noise_fft = fft.fft(noise)
noise_power = np.abs(noise_fft)

frequencies = fft.fftfreq(size, d=60)
periods = 1 / frequencies
periods_in_days = periods/(23*60*60 + 56*60 + 4)
plt.semilogx(periods_in_days[frequencies > 0], mod_counts_power[frequencies > 0])
plt.axvline(1)
plt.show()

plt.semilogx(periods_in_days[frequencies > 0], noise_power[frequencies > 0], color='red')
plt.show()