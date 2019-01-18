import os
import numpy as np
from scipy import interpolate

curr_path = os.path.dirname(os.path.realpath(__file__))

def interp(ts, data):
    ts = np.asarray(ts)
    data = np.asarray(data)
    mask = np.isfinite(data)

    f = interpolate.interp1d(ts[mask], data[mask], fill_value='extrapolate')
    return f(ts)
