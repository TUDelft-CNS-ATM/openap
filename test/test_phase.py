import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from openap import FlightPhase

root = os.path.dirname(os.path.realpath(__file__))

df = pd.read_csv(root+'/data/flight_phase_test.csv')

ts = df['ts'].values
ts = ts - ts[0]
alt = df['alt'].values
spd = df['spd'].values
roc = df['roc'].values

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
    print('TOIC:\t', fp.getTOIC())
    print('CL:\t', fp.getCL())
    print('CR:\t', fp.getCR())
    print('DE:\t', fp.getDE())
    print('FALD:\t', fp.getFALD())

    iis = fp.full_phase_idx()
    plabels = ['TO', 'IC', 'CL', 'CR', 'DE', 'FA', 'LD', 'STOP']

    fig = plt.figure()

    ax = fig.add_subplot(111)
    plt.plot(ts, alt, color='gray')
    y0, y1 = ax.get_ylim()
    for i, l in zip(iis, plabels):
        if i is not None:
            plt.plot([ts[i], ts[i]], [y0, y1])
            plt.text(ts[i], 0, l, ha='center')
    plt.title('altitude')

    plt.show()


if __name__ == '__main__':
    test_segment()
    test_phase()
