import pickle
import numpy as np
import skfuzzy as fuzz
from matplotlib import pyplot as plt
from scipy import stats
from openap.filters import SavitzkyGolay, Spline

# margin of outputs rules determin if a state is a valid state
STATE_DIFF_MARGIN = 0.2

# logic states
alt_range = np.arange(0, 40000, 1)
roc_range = np.arange(-4000, 4000, 0.1)
spd_range = np.arange(0, 600, 1)
states = np.arange(0, 6, 0.01)

alt_gnd = fuzz.zmf(alt_range, 0, 200)
alt_lo = fuzz.gaussmf(alt_range, 10000, 10000)
alt_hi = fuzz.gaussmf(alt_range, 35000, 20000)

roc_zero = fuzz.gaussmf(roc_range, 0, 100)
roc_plus = fuzz.smf(roc_range, 10, 1000)
roc_minus = fuzz.zmf(roc_range, -1000, -10)

spd_hi = fuzz.gaussmf(spd_range, 600, 100)
spd_md = fuzz.gaussmf(spd_range, 300, 100)
spd_lo = fuzz.gaussmf(spd_range, 0, 50)

state_ground = fuzz.gaussmf(states, 1, 0.1)
state_climb = fuzz.gaussmf(states, 2, 0.1)
state_descent = fuzz.gaussmf(states, 3, 0.1)
state_cruise = fuzz.gaussmf(states, 4, 0.1)
state_level = fuzz.gaussmf(states, 5, 0.1)

state_lable_map = {1: 'GND', 2: 'CL', 3: 'DE', 4: 'CR', 5:'LVL'}


# Visualize these universes and membership functions
def plot_logics():
    plt.figure(figsize=(10, 8))

    plt.subplot(411)
    plt.plot(alt_range, alt_gnd, lw=2, label='Ground')
    plt.plot(alt_range, alt_lo, lw=2, label='Low')
    plt.plot(alt_range, alt_hi, lw=2, label='High')
    plt.ylim([-0.05, 1.05])
    plt.ylabel('Altitude (ft)')
    plt.yticks([0, 1])
    plt.legend()

    plt.subplot(412)
    plt.plot(roc_range, roc_zero, lw=2, label='Zero')
    plt.plot(roc_range, roc_plus, lw=2, label='Positive')
    plt.plot(roc_range, roc_minus, lw=2, label='Negative')
    plt.ylim([-0.05, 1.05])
    plt.ylabel('RoC (ft/m)')
    plt.yticks([0, 1])
    plt.legend()

    plt.subplot(413)
    plt.plot(spd_range, spd_hi, lw=2, label='High')
    plt.plot(spd_range, spd_md, lw=2, label='Midium')
    plt.plot(spd_range, spd_lo, lw=2, label='Low')
    plt.ylim([-0.05, 1.05])
    plt.ylabel('Speed (kt)')
    plt.yticks([0, 1])
    plt.legend()

    plt.subplot(414)
    plt.plot(states, state_ground, lw=2, label='ground')
    plt.plot(states, state_climb, lw=2, label='climb')
    plt.plot(states, state_descent, lw=2, label='descent')
    plt.plot(states, state_cruise, lw=2, label='cruise')
    plt.plot(states, state_level, lw=2, label='level flight')
    plt.ylim([-0.05, 1.05])
    plt.ylabel('Flight Phases')
    plt.yticks([0, 1])
    plt.legend(prop={'size': 7})
    plt.show()


def fuzzylabels(ts, alts, spds, rocs, twindow=60):
    '''
    Fuzzy logic to determine the segments of the flight data
    segments are: ground [GND], climb [CL], descent [DE], cruise [CR].

    Default time window is 60 second.
    '''

    if len(set([len(ts), len(alts), len(spds), len(rocs)])) > 1:
        raise RuntimeError('input ts and alts must have same length')

    n = len(ts)

    ts = np.array(ts).astype(int)
    ts = ts - ts[0]
    idxs = np.arange(0, n)

    # fltr = SavitzkyGolay()
    fltr = Spline(k=2)
    _, alts = fltr.filter(ts, alts)
    _, spds = fltr.filter(ts, spds)
    _, rocs = fltr.filter(ts, rocs)

    labels = ['NA'] * n

    twindows = ts // twindow

    for tw in range(0, max(twindows)):
        if tw  not in twindows:
            continue

        mask = (twindows == tw)

        idxchk = idxs[mask]
        tchk = ts[mask]
        altchk = alts[mask]
        spdchk = spds[mask]
        rocchk = rocs[mask]

        # mean value or extream value as range
        alt = max(min(np.mean(altchk), alt_range[-1]), alt_range[0])
        spd = max(min(np.mean(spdchk), spd_range[-1]), spd_range[0])
        roc = max(min(np.mean(rocchk), roc_range[-1]), roc_range[0])

    # for i, (alt, spd, roc) in enumerate(zip(alts, spds, rocs)):

        # make sure values are within the boundaries
        alt = max(min(alt, alt_range[-1]), alt_range[0])
        spd = max(min(spd, spd_range[-1]), spd_range[0])
        roc = max(min(roc, roc_range[-1]), roc_range[0])

        alt_level_gnd = fuzz.interp_membership(alt_range, alt_gnd, alt)
        alt_level_lo = fuzz.interp_membership(alt_range, alt_lo, alt)
        alt_level_hi = fuzz.interp_membership(alt_range, alt_hi, alt)

        spd_level_hi = fuzz.interp_membership(spd_range, spd_hi, spd)
        spd_level_md = fuzz.interp_membership(spd_range, spd_md, spd)
        spd_level_lo = fuzz.interp_membership(spd_range, spd_lo, spd)

        roc_level_zero = fuzz.interp_membership(roc_range, roc_zero, roc)
        roc_level_plus = fuzz.interp_membership(roc_range, roc_plus, roc)
        roc_level_minus = fuzz.interp_membership(roc_range, roc_minus, roc)

        # print alt_level_gnd, alt_level_lo, alt_level_hi
        # print roc_level_zero, roc_level_plus, roc_level_minus
        # print spd_level_hi, spd_level_md, spd_level_lo

        rule_ground = min(alt_level_gnd, roc_level_zero, spd_level_lo)
        state_activate_ground = np.fmin(rule_ground, state_ground)

        rule_climb = min(alt_level_lo, roc_level_plus, spd_level_md)
        state_activate_climb = np.fmin(rule_climb, state_climb)

        rule_descent = min(alt_level_lo, roc_level_minus, spd_level_md)
        state_activate_descent = np.fmin(rule_descent, state_descent)

        rule_cruise = min(alt_level_hi, roc_level_zero, spd_level_hi)
        state_activate_cruise = np.fmin(rule_cruise, state_cruise)

        rule_level = min(alt_level_lo, roc_level_zero, spd_level_md)
        state_activate_level = np.fmin(rule_level, state_level)

        aggregated = np.max(
            np.vstack([
                state_activate_ground,
                state_activate_climb,
                state_activate_descent,
                state_activate_cruise,
                state_activate_level,
            ]), axis=0
        )

        state_raw = fuzz.defuzz(states, aggregated, 'lom')
        state = int(round(state_raw))
        if state > 6:
            state = 6
        if state < 1:
            state = 1
        label = state_lable_map[state]
        labels[idxchk[0]:idxchk[-1]] = [label] * len(idxchk)
        # labels[i] = label

    return labels


def test_run():
    import os
    print("Runing Fuzzy Segmenting rocess on test data.")

    # get a sample data
    datadir = os.path.dirname(os.path.realpath(__file__))
    f = datadir+'/../test/data/test_segment.pkl'
    dataset = pickle.load(open(f, 'rb'))

    for data in dataset:
        times = np.array(data['ts'])
        times = times - times[0]
        alts = np.array(data['H']) / 0.3048
        vgx = np.array(data['vgx'])
        vgy = np.array(data['vgy'])
        spds = np.sqrt(vgx**2 + vgy**2) / 0.514444
        rocs = np.array(data['vh']) / 0.00508

        labels = fuzzylabels(times, alts, spds, rocs)

        phasecolors = {
            'GND': 'black',
            'CL': 'green',
            'DE': 'blue',
            'LVL': 'purple',
            'CR': 'yellow',
            'NA': 'red'
        }

        colors = [phasecolors[lbl] for lbl in labels]

        fltr = Spline(k=2)
        _, altspl = fltr.filter(times, alts)
        _, spdspl = fltr.filter(times, spds)
        _, rocspl = fltr.filter(times, rocs)

        plt.subplot(311)
        plt.plot(times, altspl, '-', color='k', alpha=0.5)
        plt.scatter(times, alts, marker='.', c=colors, lw=0)
        plt.ylabel('altitude (ft)')

        plt.subplot(312)
        plt.plot(times, spdspl, '-', color='k', alpha=0.5)
        plt.scatter(times, spds, marker='.', c=colors, lw=0)
        plt.ylabel('speed (kt)')

        plt.subplot(313)
        plt.plot(times, rocspl, '-', color='k', alpha=0.5)
        plt.scatter(times, rocs, marker='.', c=colors, lw=0)
        plt.ylabel('roc (fpm)')

        plt.draw()
        plt.waitforbuttonpress(-1)
        plt.clf()

if __name__ == '__main__':
    plot_logics()
    test_run()
