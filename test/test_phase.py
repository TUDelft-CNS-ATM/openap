import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from openap import FlightPhase

root = os.path.dirname(os.path.realpath(__file__))

df = pd.read_csv(root+'/data/flight_phase_test.csv')

ts0 = df['ts'].values
ts0 = ts0 - ts0[0]
alt0 = df['alt'].values
spd0 = df['spd'].values
roc0 = df['roc'].values

ts = np.arange(0, ts0[-1], 1)
alt = np.interp(ts, ts0, alt0)
spd = np.interp(ts, ts0, spd0)
roc = np.interp(ts, ts0, roc0)


fp = FlightPhase()
fp.set_trajectory(ts, alt, spd, roc)
labels = fp.phaselabel()


def test_segment():

    phasecolors = {
        'GND': 'black',
        'CL': 'green',
        'DE': 'blue',
        'LVL': 'cyan',
        'CR': 'purple',
        'NA': 'red'
    }

    colors = [phasecolors[lbl] for lbl in labels]

    plt.subplot(311)
    plt.scatter(ts, alt, marker='.', c=colors, lw=0)
    plt.ylabel('altitude (ft)')

    plt.subplot(312)
    plt.scatter(ts, spd, marker='.', c=colors, lw=0)
    plt.ylabel('speed (kt)')

    plt.subplot(313)
    plt.scatter(ts, roc, marker='.', c=colors, lw=0)
    plt.ylabel('roc (fpm)')

    plt.show()


def test_phase():
    idx = fp.flight_phase_indices()

    fig = plt.figure()

    ax = fig.add_subplot(111)
    plt.plot(ts, alt, color='gray')
    y0, y1 = ax.get_ylim()
    for k, v in idx.items():
        if v is None:
            continue

        plt.plot([ts[v], ts[v]], [y0, y1], label=k)
        # plt.text(lx, ly, k, ha='center')
    plt.title('altitude')
    plt.legend()

    plt.show()


if __name__ == '__main__':
    test_segment()
    test_phase()
