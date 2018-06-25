import pandas as pd
import argparse

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

parser = argparse.ArgumentParser()
parser.add_argument('--input', dest="fin", required=True,
                    help="ICAO eimission databank xlsx file")
args = parser.parse_args()

xl = pd.ExcelFile(args.fin)

df0 = xl.parse(sheetname=2)

df0.dropna(subset=['UID'], inplace=True)

df = df0.iloc[1:, [0, 1, 3, 4, 5, 6, 11, 12, 17, 19, 80, 81, 82, 83, 84, 94]]

df.columns = ['uid', 'name', 'type', 'bpr', 'pr', 'thr', 'superseded',
              'superseded_by', 'out_production', 'out_service',
              'ff_to', 'ff_co', 'ff_app', 'ff_idl', 'fuel_lto', 'maker']


df.dropna(subset=['name'], inplace=True)

df.loc[:, 'uid'] = df['uid'].str.strip()
df.loc[:, 'name'] = df['name'].str.strip()
df.loc[:, 'name'] = df['name'].apply(clean_name)

df.loc[:, 'thr'] = (df['thr'] * 1000).astype(int)

df = df[df['superseded']!='x']
df = df[df['uid'] != '']
df = df[df['bpr'] != '-']
df = df[df['ff_to'] != '-']
df = df[df['ff_co'] != '-']
df = df[df['ff_app'] != '-']
df = df[df['ff_idl'] != '-']
df = df[df['fuel_lto'] != '-']

df.drop_duplicates(subset=['name'], keep='last', inplace=True)

df = df.loc[:, ['uid', 'name', 'type', 'maker', 'bpr', 'pr', 'thr',
                  'ff_to', 'ff_co', 'ff_app', 'ff_idl', 'fuel_lto']]


df.to_csv('db/engines.csv', index=False)
print("Engine database created: engines.csv")
