import pandas as pd
import argparse
import matplotlib.pyplot as plt

# parser = argparse.ArgumentParser()
# parser.add_argument('--jesd', dest="fin_jesd", required=True,
#                     help="Jet Engine Specification Database")
# args = parser.parse_args()
#
# html = pd.read_html(args.fin_jesd)

df = pd.read_csv('input/civtfspec.csv', header=None, thousands=',')
df.columns = df.iloc[0, :] + df.iloc[1, :].fillna('') + df.iloc[2, :].fillna('')
df = df.iloc[4:, :]
df.dropna(subset=['Model'], inplace=True)

df1 = df[pd.notnull(df['Thrust(cruise)[lbf]'])][['Thrust(dry)[lbf]', 'OPR(static)', 'BPR(static)', 'Thrust(cruise)[lbf]']]

df1.columns = ['thr', 'opr', 'bpr', 'thr_cr']

plt.scatter(df1['thr'], df1['thr_cr'])
plt.show()
