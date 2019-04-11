import pandas as pd

df = pd.read_csv('input/civtfspec.csv')

df1 = df.iloc[:, [1,11,12,13,14]]

df1.columns = ['engine', 'cruise_thrust', 'cruise_sfc', 'cruise_mach', 'cruise_alt']

df1 = df1.dropna(subset=(['engine', 'cruise_thrust']))

# sfc: lb / hr / lbf -> kg / s / kN
# 1 -> 0.0283267
df1.cruise_sfc = (df1.cruise_sfc.astype(float) * 0.0283267).round(4)

# lbs -> N, 4.44822
df1.cruise_thrust = (df1.cruise_thrust.astype(float) * 4.44822).astype(int)

df1.loc[df1.engine=='CFM56-5A4', 'cruise_sfc'] = df1.loc[df1.engine=='CFM56-5A3', 'cruise_sfc']
df1.loc[df1.engine=='CFM56-5A5', 'cruise_sfc'] = df1.loc[df1.engine=='CFM56-5A3', 'cruise_sfc']
df1.loc[df1.engine=='CFM56-5B3', 'cruise_sfc'] = df1.loc[df1.engine=='CFM56-5B2', 'cruise_sfc']
df1.loc[df1.engine=='CFM56-7B18', 'cruise_sfc'] = df1.loc[df1.engine=='CFM56-7B20', 'cruise_sfc']
df1.loc[df1.engine=='CFM56-7B22', 'cruise_sfc'] = df1.loc[df1.engine=='CFM56-7B20', 'cruise_sfc']
df1.loc[df1.engine=='CFM56-7B26', 'cruise_sfc'] = df1.loc[df1.engine=='CFM56-7B20', 'cruise_sfc']

df1.to_csv('input/engine_cruise_performance.csv', index=False)
