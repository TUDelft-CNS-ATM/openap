import os
import json
import numpy as np
import pandas as pd
from scipy import interpolate
import warnings

curr_path = os.path.dirname(os.path.realpath(__file__))
db_airport = curr_path + "/data/5_navigation/airports.csv"
db_aircraft = curr_path + "/data/1_aircraft_and_engines/aircraft.json"
db_engine = curr_path + "/data/1_aircraft_and_engines/engines.csv"
db_engine_cr_perf = curr_path + "/data/1_aircraft_and_engines/engine_cruise_performance.csv"

with open(db_aircraft) as f:
    ACS = json.load(f)

ENGINES = pd.read_csv(db_engine, encoding='utf-8')
ENGINES_CR_PERF = pd.read_csv(db_engine_cr_perf)

def get_airport_data(name):
    df = pd.read_csv(db_airport)
    df = df[(df['icao']==name) | (df['iata']==name)]
    if df.shape[0] == 0:
        return None
    else:
        return df.iloc[0, :].to_dict()


def get_closest_airport(lat, lon, type='icao'):
    df = pd.read_csv(db_airport)
    df = df[df['lat'].between(lat-2, lat+2) & df['lon'].between(lon-2, lon+2)]

    if df.shape[0] == 0:
        return None

    coords = np.array(df[['lat', 'lon']])
    dist2 = np.sum((coords - [lat, lon])**2, axis=1)
    idx = np.argmin(dist2)

    ap = df.iloc[idx, :]

    if type.lower() == 'icao':
        return ap.icao
    if type.lower() == 'iata':
        return ap.iata


def get_aircraft(mdl):
    mdl = mdl.upper()

    if mdl not in ACS:
        raise RuntimeError('Aircraft data not found')

    ac = ACS[mdl].copy()
    eng_options = ac['engine']['options']
    ac['engines'] = {}

    for eng in eng_options:
        ac['engines'].update(get_engines(eng))

    return ac


def get_engines(eng):
    eng = eng.strip().upper()
    selengs = ENGINES[ENGINES['name'].str.upper().str.startswith(eng)]
    selengs = selengs.merge(ENGINES_CR_PERF, left_on='name', right_on='engine', how='left')
    selengs = selengs.drop('engine', axis=1)

    if selengs.shape[0] == 0:
        engines = {}

    if selengs.shape[0] > 0:
        selengs.index = selengs.uid
        engines = selengs.to_dict(orient='index')

    return engines

def interp(ts, data):
    ts = np.asarray(ts)
    data = np.asarray(data)
    mask = np.isfinite(data)

    f = interpolate.interp1d(ts[mask], data[mask], fill_value='extrapolate')
    return f(ts)
