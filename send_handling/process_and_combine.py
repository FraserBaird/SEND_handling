import pandas as pd

all_mod_only_unproc = pd.read_csv('SENDAuto/data/AllModOnly.dat', header=0)
all_mod_only_unproc['CT_RATE_MOD'] = all_mod_only_unproc['CTS_MOD']/all_mod_only_unproc['T_DELTA_MOD']
all_mod_only_unproc.to_csv('SENDAuto/data/all_mod_ct_rate.dat', index=False)

rest = pd.read_csv('SENDAuto/CorrData.dat', header=0)
all_data = pd.concat((all_mod_only_unproc, rest))
print('oooh')
all_data.to_csv('SENDAuto/data/all_data.dat', index=False)