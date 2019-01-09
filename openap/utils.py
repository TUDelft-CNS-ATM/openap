import os
import glob
import yaml
import numpy as np
import pandas as pd
from scipy import interpolate
import warnings

curr_path = os.path.dirname(os.path.realpath(__file__))
dir_aircraft = curr_path + "/data/aircraft/"
dir_dragpolar = curr_path + "/data/dragpolar/"
db_airport = curr_path + "/data/nav/airports.csv"
db_engine = curr_path + "/data/engine/engines.txt"


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


def get_aircraft(acmdl):
    acmdl = acmdl.lower()

    files = glob.glob(dir_aircraft + acmdl + '.yml')

    if len(files) == 0:
        raise RuntimeError('Aircraft data not found.')

    f = files[0]
    ac = yaml.load(open(f))

    return ac


def get_dragpolar(acmdl):
    acmdl = acmdl.lower()

    files = glob.glob(dir_dragpolar + acmdl + '.yml')

    if len(files) == 0:
        raise RuntimeError('Dragpolar data not found.')

    f = files[0]
    dragpolar = yaml.load(open(f))

    return dragpolar


def search_engine(eng):
    ENG = eng.strip().upper()
    engines = pd.read_fwf(db_engine)

    selengs = engines[engines['name'].str.upper().str.startswith(ENG)]

    if selengs.shape[0] == 0:
        print('Engine not found.')
        result = None
    else:
        print('Engines found:')
        result = selengs.name.tolist()
        print(result)

    return result


def get_engine(eng):
    ENG = eng.strip().upper()
    engines = pd.read_fwf(db_engine)

    # try to look for the unique engine
    selengs = engines[engines['name'].str.upper() == ENG]
    if selengs.shape[0] == 1:
        selengs.index = selengs.name
        result = selengs.to_dict(orient='records')[0]
    else:
        raise RuntimeError('Engine data not found.')

    return result


def interp(ts, data):
    ts = np.asarray(ts)
    data = np.asarray(data)
    mask = np.isfinite(data)

    f = interpolate.interp1d(ts[mask], data[mask], fill_value='extrapolate')
    return f(ts)
