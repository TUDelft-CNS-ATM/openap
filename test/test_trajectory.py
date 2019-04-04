import matplotlib.pyplot as plt
from openap import aero
from openap.traj import Generator

if __name__ == '__main__':
    trajgen = Generator(ac='a320')
    trajgen.enable_noise()

    fig, ax = plt.subplots(2, 2, figsize=(12, 6))
    plt.suptitle('Climb trajectories')
    for i in range(5):
        data = trajgen.climb(dt=10, random=True)
        ax[0][0].plot(data['t'], data['h']/aero.ft, label='%d/%.2f' % (data['cas_const_cl'], data['mach_const_cl']))
        ax[0][0].set_ylabel('Altitude (ft)')
        ax[0][1].plot(data['t'], data['s']/1000);
        ax[0][1].set_ylabel('Distanse (km)')
        ax[1][0].plot(data['t'], data['v']/aero.kts);
        ax[1][0].set_ylabel('True airspeed (kt)')
        ax[1][1].plot(data['t'], data['vs']/aero.fpm);
        ax[1][1].set_ylabel('Vertical rate (ft/min)')
        ax[0][0].legend()
    plt.show()

    fig, ax = plt.subplots(2, 2, figsize=(12, 6))
    plt.suptitle('Descent trajectories')
    for i in range(5):
        data = trajgen.descent(dt=10, random=True)
        ax[0][0].plot(data['t'], data['h']/aero.ft, label='%d/%.2f' % (data['cas_const_de'], data['mach_const_de']))
        ax[0][0].set_ylabel('Altitude (ft)')
        ax[0][1].plot(data['t'], data['s']/1000);
        ax[0][1].set_ylabel('Distanse (km)')
        ax[1][0].plot(data['t'], data['v']/aero.kts);
        ax[1][0].set_ylabel('True airspeed (kt)')
        ax[1][1].plot(data['t'], data['vs']/aero.fpm);
        ax[1][1].set_ylabel('Vertical rate (ft/min)')
        ax[0][0].legend()
    plt.show()

    fig, ax = plt.subplots(2, 2, figsize=(12, 6))
    plt.suptitle('Cruise trajectories')
    for i in range(5):
        data = trajgen.cruise(dt=60, random=True)
        ax[0][0].plot(data['t'], data['h']/aero.ft, label='%d' % data['h_cr'])
        ax[0][0].set_ylabel('Altitude (ft)')
        ax[0][1].plot(data['t'], data['s']/1000);
        ax[0][1].set_ylabel('Distanse (km)')
        ax[1][0].plot(data['t'], data['v']/aero.kts);
        ax[1][0].set_ylabel('True airspeed (kt)')
        ax[1][1].plot(data['t'], data['vs']/aero.fpm);
        ax[1][1].set_ylabel('Vertical rate (ft/min)')
        ax[0][0].legend()
    plt.show()

    fig, ax = plt.subplots(2, 2, figsize=(12, 6))
    plt.suptitle('Complete trajectories')
    for i in range(5):
        data = trajgen.complete(dt=10, random=True)
        ax[0][0].plot(data['t'], data['h']/aero.ft)
        ax[0][0].set_ylabel('Altitude (ft)')
        ax[0][1].plot(data['t'], data['s']/1000);
        ax[0][1].set_ylabel('Distanse (km)')
        ax[1][0].plot(data['t'], data['v']/aero.kts);
        ax[1][0].set_ylabel('True airspeed (kt)')
        ax[1][1].plot(data['t'], data['vs']/aero.fpm);
        ax[1][1].set_ylabel('Vertical rate (ft/min)')
    plt.show()
