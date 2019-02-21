import os
import glob
import yaml
import numpy as np
import pandas as pd

curr_path = os.path.dirname(os.path.realpath(__file__))
dir_aircraft = curr_path + "/data/aircraft/"
db_engine = curr_path + "/data/engine/engines.txt"


def available_aircraft():
    files = sorted(glob.glob(dir_aircraft + '*.yml'))
    acs = [f[-8:-4].upper() for f in files]
    return acs


def aircraft(ac):
    ac = ac.lower()

    files = glob.glob(dir_aircraft + ac + '.yml')

    if len(files) == 0:
        raise RuntimeError('Aircraft data not found.')

    f = files[0]
    acdict = yaml.load(open(f))

    return acdict


def aircraft_engine_options(ac):
    acdict = aircraft(ac)

    if type(acdict['engine']['options']) == dict:
        eng_options = list(acdict['engine']['options'].values())
    elif type(acdict['engine']['options']) == list:
        eng_options = list(acdict['engine']['options'])

    return eng_options


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


def engine(eng):
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
