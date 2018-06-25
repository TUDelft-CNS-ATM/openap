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
    with open(db_aircraft) as f:
        acs = json.load(f)

    if mdl in acs:
        return acs[mdl]
    else:
        raise RuntimeError('Aircraft data not found')

def get_engine(eng):
    eng = eng.strip().upper()
    allengines = pd.read_csv(db_engine, encoding='utf-8')
    selengine = allengines[allengines['name'].str.startswith(eng)]

    if selengine.shape[0] == 0:
        raise RuntimeError('Engine data not found')

    if selengine.shape[0] > 1:
        warnings.warn('Multiple engines found, first one used')

    return json.loads(selengine.iloc[0, :].to_json())

def get_ac_default_engine(mdl):
    ac = get_aircraft(mdl)
    eng = ac['engines'][0]
    return get_engine(eng)


def interp(ts, data):
    ts = np.asarray(ts)
    data = np.asarray(data)
    mask = np.isfinite(data)

    f = interpolate.interp1d(ts[mask], data[mask], fill_value='extrapolate')
    return f(ts)
