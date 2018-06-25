import os
import pandas as pd
import numpy as np
from openap import aero

fixes = None

curr_path = os.path.dirname(os.path.realpath(__file__))

def get_cloest_fix(lat, lon):
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
