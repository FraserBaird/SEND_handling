import pandas as pd
import os
import smtplib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
# ignore this error - it is compatible with cmd line execution
from coscal import coscal as cc
import time


def open_file(filename):
    file = open(filename, 'r')
    data_text = np.asarray(file.readlines())[4:]
    data_no_return = np.char.strip(data_text, '\n')
    data_nd = np.vstack(np.char.split(data_no_return, ','))
    return data_nd


def read_file(filename, suffix):
    data_ndarray = open_file(filename)
    # TODO modularise this function
    if suffix != 'weather':
        dt = np.asarray(pd.to_datetime(data_ndarray[:, 0], format='"%Y-%m-%d %H:%M:%S"'))
        n = np.asarray(data_ndarray[:, 1])
        cts = np.asarray(data_ndarray[:, 2])
        t_delta = np.asarray(data_ndarray[:, 3])
        temp = np.asarray(data_ndarray[:, 4])
        rh = np.asarray(data_ndarray[:, 5])

        dict_for_df = {'DATE_TIME': dt, 'N_' + suffix: n, 'CTS_' + suffix: cts, 'T_DELTA_' + suffix: t_delta,
                       'TEMP_' + suffix: temp, 'RH_' + suffix: rh}
        ret_df = pd.DataFrame(dict_for_df)
        ret_df.replace({'"NAN"': np.nan}, inplace=True)
        ret_df.iloc[:, 1:] = ret_df.iloc[:, 1:].astype('float')
    else:

        dt = np.asarray(pd.to_datetime(data_ndarray[:, 0], format='"%Y-%m-%d %H:%M:%S"'))
        n = np.asarray(data_ndarray[:, 1])
        temp = np.asarray(data_ndarray[:, 2])
        press = np.asarray(data_ndarray[:, 3])
        rh = np.asarray(data_ndarray[:, 4])

        dict_for_df = {'DATE_TIME': dt, 'N': n, 'TA': temp, 'PA': press, 'RH': rh}
        df = pd.DataFrame(dict_for_df)
        df.replace({'"NAN"': np.nan}, inplace=True)
        df.iloc[:, 1:] = df.iloc[:, 1:].astype('float')
        ret_df = compute_ah(df)

    return ret_df


def compute_ah(the_df):
    df = the_df.copy()
    temp = df['TA'].values
    rh = df['RH'].values

    exponential = np.exp((17.67 * temp) / (temp + 243.5))
    ah = (13.2471 * rh * exponential) / (temp + 273.15)

    df.loc[:, 'Q'] = ah

    return df


def import_data(filename, sample_period_str, suff):
    """
    function to import SEND data, returns data frame with sorted datetime index and any missing timestamps filled with
     nans.
    :param filename: str - filename or path
    :param sample_period_str: sampling period of the data
    :return: pandas date_frame
    """
    date_frame = read_file(filename, suff)
    date_frame.set_index('DATE_TIME', inplace=True)
    date_frame.sort_index(inplace=True)
    date_frame = date_frame.resample(sample_period_str).asfreq()

    return date_frame


def compute_counting_rate(data_frame, suff):
    """
    computes the counting rate of the counts in the dataframe, by dividing the counts by the time_delta
    :param data_frame: dataframe containing the timestamped counts and time_deltas
    :return:
    """
    counting_rate = np.round(data_frame.loc[:, 'CTS_' + suff] / data_frame.loc[:, 'T_DELTA_' + suff], 3)
    new_dataframe = pd.concat([data_frame, pd.DataFrame({'CT_RATE_' + suff: counting_rate})], axis=1)

    return new_dataframe


def get_suffix(mod, weather):
    if weather:
        suffix = 'weather'
    elif mod:
        suffix = 'MOD'
    else:
        suffix = 'UNMOD'
    return suffix


def nan_average(arr):
    """
    function to compute the average of non-nan entries in an array
    :param arr: numpy 1d array
    :return: double
    """
    # compute the nan sum - a sum that counts nan values as zero.
    nan_sum = np.nansum(arr)
    # count how many non_nan entries there are
    n_non_nans = np.count_nonzero(~np.isnan(arr))
    nan_ave = nan_sum / n_non_nans

    return nan_ave


def import_last_ts():
    fname = 'last_ts.dat'

    file = open(fname, 'r')
    ret_val = pd.Timestamp(file.read())
    file.close()
    return ret_val


def send_error_email(final_ts, interim=False):
    message = generate_error_message(final_ts, interim)
    server = get_server()
    server.sendmail("surreyend@outlook.com", "f.baird@surrey.ac.uk", message)
    server.close()
    return


def generate_error_message(final_ts, interim):
    if interim:
        message = "Subject: SEND Failure Notification \n\n SEND failed to upload recent data. Interim data will be " \
                  "processed and uploaded to OneDrive.\n\n Last data recorded: %s. " % final_ts
    else:
        message = "Subject: SEND Failure Notification \n\n SEND failed to upload recent data. There was no interim " \
                  "data. \n\n Last data recorded: %s." % final_ts

    return message


def process_data(data_frame, suffix):
    t_delta_guard = np.logical_and(data_frame['T_DELTA_%s' % suffix] > 66, data_frame['T_DELTA_%s' % suffix] < 1750)
    data_frame.loc[:, 'CTS_%s' % suffix] = data_frame.mask(data_frame['T_DELTA_%s' % suffix] < 50).loc[:, 'CTS_%s' % suffix]
    data_frame.loc[:, 'CTS_%s' % suffix] = data_frame.mask(t_delta_guard).loc[:, 'CTS_%s' % suffix]
    data_frame.loc[:, 'CTS_%s' % suffix] = data_frame.mask(data_frame['T_DELTA_%s' % suffix] > 1850).loc[:, 'CTS_%s' % suffix]

    n_data_frame = compute_counting_rate(data_frame, suffix)

    return n_data_frame


def plot_data(data_frame, key):
    average = nan_average(data_frame[key].values)
    std_dev = np.nanstd(data_frame[key].values)
    ax = data_frame.rolling('30T', min_periods=15).mean().plot(kind='line', y=key, zorder=200, color='red', linewidth=1)
    data_frame.reset_index().plot(ax=ax, kind='scatter', x="DATE_TIME", y=key, color='black', zorder=100, marker='.')
    ax.axhline(average, color='purple')
    ax.axhspan(average - std_dev, average + std_dev, color='green', alpha=0.5)
    plt.savefig('recent_data_figures/%s.png' % key, dpi=600)
    return


def plot_corrected_data(data_frame, key):
    corr_key = key + '_CORR'

    ax = data_frame.rolling('30T', min_periods=15).mean().plot(kind='line', y=key, zorder=200, color='#663399',
                                                               linewidth=1)
    data_frame.reset_index().plot(ax=ax, kind='scatter', x="DATE_TIME", y=key, color='#C09BD8', zorder=150, marker='.')
    data_frame.rolling('30T', min_periods=15).mean().plot(ax=ax, kind='line', y=corr_key, zorder=250, color='#3C493F',
                                                          linewidth=1)
    data_frame.reset_index().plot(ax=ax, kind='scatter', x="DATE_TIME", y=corr_key, color='#66CDAA', zorder=100,
                                  marker='.')

    plt.savefig('recent_data_figures/%s.png' % key, dpi=600)

    return


def upload_ts(time_stamp):
    file = open('last_ts.dat', 'w')
    file.write(str(time_stamp))
    file.close()
    return


def get_server():
    the_server = smtplib.SMTP('smtp.outlook.com', port=587)
    the_server.starttls()
    the_server.login("surreyend@outlook.com", "H45yr!kg!^4@")
    return the_server


def get_locator_formatter():
    locator = dates.AutoDateLocator(minticks=5, maxticks=10)
    formatter = dates.ConciseDateFormatter(locator)

    return locator, formatter


def upload_proc_data(dataframe):
    dataframe.to_csv('CorrData.dat', mode='a', header=None)
    return


def import_df(mod, weather, first):
    if weather:
        filename = 'CR1000_Weather.dat'
    elif mod:
        filename = 'CR1000_CountsMod.dat'
    else:
        filename = 'CR1000_CountsUnmod.dat'

    suff = get_suffix(mod, weather)

    send_df = import_data(filename, '1T', suff)

    last_ts = check_for_recent_data(send_df)

    send_df = send_df.loc[last_ts + pd.Timedelta('1T'):, :]

    if not weather:
        send_df = process_data(send_df, suff)

    return send_df


def check_for_recent_data(df):
    # get timestamp for current day at 08:55
    today = pd.Timestamp.today().floor('1D')

    last_ts_proc = import_last_ts()

    # data logger is always in UTC, this handles the laptop changing time zone when it collects the data
    if time.localtime().tm_isdst:
        recent_ts = today + pd.Timedelta('07:55:00')
    else:
        recent_ts = today + pd.Timedelta('08:55:00')
    # check if last data is within five minutes of the upload time
    if df.index[-1] < recent_ts:
        # if not check if there is data since the last data was uploaded
        if df.index[-1] > last_ts_proc:
            # send the appropriate error email
            send_error_email(df.index[-1], True)

        else:
            # if no unprocessed data send the appropriate error email
            send_error_email(df.index[-1])
            # kill the program
            exit(-1)

    return last_ts_proc


def correct_data(the_df):
    df = the_df.copy()
    corr_keys = cc.set_corr_keys('COSMOS-UK')
    correction_factors = cc.get_corr_factors(df, corr_keys, 2.774)
    df['P_CORR'] = correction_factors['p_corr']
    df['Q_CORR'] = correction_factors['h_corr']
    df['CTS_MOD_CORR'] = df['CTS_MOD'] * df['P_CORR'] * df['Q_CORR']
    df['CTS_UNMOD_CORR'] = df['CTS_UNMOD'] * df['P_CORR'] * df['Q_CORR']
    df['CT_RATE_MOD_CORR'] = df['CT_RATE_MOD'] * df['P_CORR'] * df['Q_CORR']
    df['CT_RATE_UNMOD_CORR'] = df['CT_RATE_UNMOD'] * df['P_CORR'] * df['Q_CORR']
    return df


def main():
    filepath = 'C:/Users/Fraser Baird/OneDrive - University of Surrey/Documents/data/SENDAuto'
    os.chdir(filepath)
    mod_df = import_df(mod=True, weather=False, first=True)
    unmod_df = import_df(mod=False, weather=False, first=False)
    weather_df = import_df(mod=False, weather=True, first=False)
    raw_df = pd.concat((mod_df, unmod_df, weather_df), axis=1)
    corrected_df = correct_data(raw_df)
    plot_keys = ['PA', 'TA', 'Q']

    for key in plot_keys:
        plot_data(corrected_df, key)

    # plot uncorrected and corrected values
    plot_keys = ['CTS_MOD', 'CTS_UNMOD']
    for key in plot_keys:
        plot_corrected_data(corrected_df, key)

    upload_proc_data(corrected_df)
    upload_ts(corrected_df.index[-1])

    return


if '__main__' == __name__:
    main()
    exit(0)
