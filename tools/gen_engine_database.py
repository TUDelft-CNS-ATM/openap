import pandas as pd
import numpy as np
import argparse
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def clean_name(name):
    if "SelectOne" in name:
        name =  name.split(" ")[0].strip()
    elif "Build Spec" in name:
        name =  name.split(" ")[0].strip()
    elif "Block" in name:
        name =  name.split(" ")[0].strip()
    elif "series" in name:
        name =  name.split(" ")[0].strip()
    elif "(" in name:
        name =  name.split("(")[0].strip()
    return name

def clean_bpr(bpr):
    try:
        bpr = float(bpr)
    except:
        bpr = '-'
    return bpr

def func_fuel(x, c3, c2, c1):
    return c3 * x**3 + c2 * x**2 + c1 * x

parser = argparse.ArgumentParser()
parser.add_argument('--input', dest="fin", required=True,
                    help="ICAO eimission databank xlsx file")
args = parser.parse_args()

xl = pd.ExcelFile(args.fin)

df0 = xl.parse(sheet_name=2)

df0.dropna(subset=['UID'], inplace=True)

df = df0.iloc[1:, [0, 1, 3, 4, 5, 6, 11, 12, 17, 19, 80, 81, 82, 83, 84, 94]]

df.columns = ['uid', 'name', 'type', 'bpr', 'pr', 'max_thrust', 'superseded',
              'superseded_by', 'out_production', 'out_service',
              'ff_to', 'ff_co', 'ff_app', 'ff_idl', 'fuel_lto', 'manufacturer']


df.dropna(subset=['name'], inplace=True)

df.loc[:, 'uid'] = df['uid'].str.strip()
df.loc[:, 'name'] = df['name'].str.strip()
df.loc[:, 'name'] = df['name'].apply(clean_name)

df.loc[:, 'bpr'] = df['bpr'].apply(clean_bpr)

df.loc[:, 'max_thrust'] = (df['max_thrust'] * 1000).astype(int)

df = df[df['superseded']!='x']
df = df[df['uid'] != '']
df = df[df['bpr'] != '-']
df = df[df['ff_to'] != '-']
df = df[df['ff_co'] != '-']
df = df[df['ff_app'] != '-']
df = df[df['ff_idl'] != '-']
df = df[df['fuel_lto'] != '-']

df.drop_duplicates(subset=['name'], keep='last', inplace=True)

df = df.loc[:, ['uid', 'name', 'type', 'manufacturer', 'bpr', 'pr', 'max_thrust',
                  'ff_to', 'ff_co', 'ff_app', 'ff_idl', 'fuel_lto']]


# compute fuel flow coefficient
x = [0, 0.07, 0.3, 0.85, 1.0]
for i, r in df.iterrows():
    y = [0, r['ff_idl'], r['ff_app'], r['ff_co'], r['ff_to']]

    # coef = np.polyfit(x, y, 2)
    # df.loc[i, 'fuel_c2'] = coef[0]
    # df.loc[i, 'fuel_c1'] = coef[1]
    # df.loc[i, 'fuel_c0'] = coef[2]

    coef, cov = curve_fit(func_fuel, x, y)
    df.loc[i, 'fuel_c3'] = coef[0]
    df.loc[i, 'fuel_c2'] = coef[1]
    df.loc[i, 'fuel_c1'] = coef[2]

    # print(r['name'], coef)
    # xx = np.linspace(0, 1, 100)
    # plt.plot(xx, func_fuel(xx, *coef))
    # plt.scatter(x, y)
    # plt.draw()
    # plt.waitforbuttonpress(-1)
    # plt.clf()

df = df.drop(['ff_to', 'ff_co', 'ff_app', 'ff_idl', 'fuel_lto'], axis=1)

dfcr = pd.read_csv('input/engine_cruise_performance.csv')
df = df.merge(dfcr, how='left', left_on='name', right_on='engine')
df = df.drop('engine', axis=1)


from tabulate import tabulate
def to_fwf(df, fname):
    content = tabulate(df.values.tolist(), list(df.columns), tablefmt="plain", numalign="left", stralign="left")
    open(fname, "w").write(content)
pd.DataFrame.to_fwf = to_fwf


df.to_csv('db/engines.csv', index=False)
print("CSV engine database created: engines.csv")

df = df.fillna('')
df.to_fwf('db/engines.txt')
print("Fix width engine database created: engines.txt")
