import pandas as pd
import os
import matplotlib.pyplot as plt
os.chdir('C:/Users/Fraser Baird/OneDrive - University of Surrey/Documents/data/SENDAuto')


start = pd.to_datetime('2021-07-26 00:00')
end = pd.to_datetime('2021-08-01 00:00')
roll_period_str = '12H'

data = pd.read_csv('CorrData.dat', parse_dates=[0])
data.set_index('DATE_TIME', inplace=True)
data = data.rolling(roll_period_str).mean()

data.loc[start:end, 'Q_CORR'].plot()
plt.show()