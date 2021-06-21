import pandas as pd
import numpy as np


def read_weather_file(filename):

    file = open(filename, 'r')
    data_text = np.asarray(file.readlines())[4:]
    data_no_return = np.char.strip(data_text, '\n')
    data_ndarray = np.vstack(np.char.split(data_no_return, ','))

    dt = np.asarray(pd.to_datetime(data_ndarray[:, 0], format='"%Y-%m-%d %H:%M:%S"'))
    n = np.asarray(data_ndarray[:, 1])
    temp = np.asarray(data_ndarray[:, 2])
    press = np.asarray(data_ndarray[:, 3])
    rh = np.asarray(data_ndarray[:, 4])

    dict_for_df = {'DATE_TIME': dt, 'N': n, 'TA': temp, 'PA': press, 'RH': rh}
    df = pd.DataFrame(dict_for_df)
    df.replace({'"NAN"': np.nan}, inplace=True)
    df.iloc[:, 1:] = df.iloc[:, 1:].astype('float')

    return df


def compute_ah(the_df):
    df = the_df.copy()
    temp = df['TA'].values
    rh = df['RH'].values

    exponential = np.exp((17.67 * temp)/(temp + 243.5))
    ah = (13.2471 * rh * exponential) / (temp + 273.15)

    df.loc[:, 'Q'] = ah

    return df


data = read_weather_file('SENDAuto/data/CR1000_Weather.dat')
test = compute_ah(data)
print('weee')
