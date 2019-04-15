import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from openap import aero

df = pd.read_fwf('db/engines.txt')
df1 = df.query('cruise_sfc>0').copy()

df1['sealevel_sfc'] = (df1.fuel_c3 + df1.fuel_c2 + df1.fuel_c1) / (df1.max_thrust / 1000)

df1['fuel_ch'] = (df1.cruise_sfc - df1.sealevel_sfc) / (df1.cruise_alt * aero.ft)

factor = df1.fuel_ch
print(np.mean(factor))
print('fuel flow altitude correction factor', np.mean(factor))

plt.scatter(np.arange(len(factor)), factor)
plt.ylim([factor.min(), factor.max()])
plt.show()
