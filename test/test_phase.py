import os
import pandas as pd
import matplotlib.pyplot as plt
from openap import phase, aero

pd.set_option('display.max_columns', None)

root = os.path.dirname(os.path.realpath(__file__))
df = pd.read_csv(root+'/data/flight1.csv')

# df['alt_gnss'].plot()
# plt.show()

print('TOIC:\t', phase.getTOIC(df['ts'], df['alt'], df['tas'], df['roc']))
print('CL:\t', phase.getCL(df['ts'], df['alt'], df['tas'], df['roc']))
print('CR:\t', phase.getCR(df['ts'], df['alt'], df['tas'], df['roc']))
print('DE:\t', phase.getDE(df['ts'], df['alt'], df['tas'], df['roc']))
print('FALD:\t', phase.getFALD(df['ts'], df['alt'], df['tas'], df['roc']))

iis = phase.full_phase_idx(df['ts'], df['alt'], df['tas'], df['roc'])

fig = plt.figure()

ax = fig.add_subplot(211)
df['alt_gnss'].plot(color='gray')
y0, y1 = ax.get_ylim()
for i in iis:
    plt.plot([i, i], [y0, y1])
plt.title('altitude')

ax = fig.add_subplot(212)
df['tas'].plot(color='gray')
y0, y1 = ax.get_ylim()
for i in iis:
    plt.plot([i, i], [y0, y1])
plt.title('speed')

plt.show()
