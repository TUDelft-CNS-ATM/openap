import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from openap import aero

df = pd.read_fwf('db/engines.txt')
df1 = df[~df.cruise_sfc.isnull()].copy()

SFC_TO = []
SFC_CR = []
for i, eng in df1.iterrows():
    x = 1
    ff = eng.fuel_c3*x**3 + eng.fuel_c2*x**2 + eng.fuel_c1*x
    sfc_to = ff / eng.max_thrust * 1000
    SFC_TO.append(sfc_to)
    SFC_CR.append(eng.cruise_sfc)

SFC_TO = np.array(SFC_TO)
SFC_CR = np.array(SFC_CR)

factor = (SFC_CR - SFC_TO) / (df1.cruise_alt * aero.ft)
print('fuel flow altitude correction factor', np.mean(factor))

plt.scatter(SFC_TO, factor)
plt.ylim([factor.min(), factor.max()])
plt.show()
