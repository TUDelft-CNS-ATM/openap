import os
import pandas as pd
import numpy as np
from openap import aero

fixes = None

curr_path = os.path.dirname(os.path.realpath(__file__))
db_airport = curr_path + "/data/nav/airports.csv"


def airport(name):
    df = pd.read_csv(db_airport)
    df = df[(df['icao']==name) | (df['iata']==name)]
    if df.shape[0] == 0:
        return None
    else:
        return df.iloc[0, :].to_dict()


def closest_airport(lat, lon, type='icao'):
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



def cloest_fix(lat, lon):
    global fixes

    if not isinstance(fixes, pd.DataFrame):
        fixes = pd.read_csv(curr_path + '/data/5_navigation/fix.dat', skiprows=3,
                            skipfooter=1, engine='python',
                            sep=r'\s*', names=('lat', 'lon', 'fix'))

    mask = (fixes['lat'].between(lat-1, lat+1)) & (fixes['lon'].between(lon-1, lon+1))
    chunk = fixes[mask]

    lats = np.asarray(chunk['lat'])
    lons = np.asarray(chunk['lon'])

    distances = aero.distance(lat, lon, lats, lons)
    idx = distances.argmin()

    fix = chunk.iloc[idx].tolist()
    dist = distances[idx]

    return fix, int(dist)
