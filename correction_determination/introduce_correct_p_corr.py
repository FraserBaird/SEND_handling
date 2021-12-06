import pandas as pd
import coscal.coscal as cc

filename = 'C:/Users/Fraser Baird/OneDrive - University of Surrey/Documents/data/SENDAuto/CorrData.dat'

data = pd.read_csv(filename, parse_dates=[0], header=0)
beta = {'MOD': 0.00701, 'UNMOD': 0.00718}

for detector in ['MOD', 'UNMOD']:
    p_corr = cc.pressure_correction(data['PA'].values, 2.8, beta['%s' % detector])
    data['P_CORR_%s' % detector] = p_corr
    data['CTS_%s_CORR_EMP' % detector] = data['CTS_%s' % detector] * data['P_CORR_%s' % detector]

data.to_csv(filename, index=False)
