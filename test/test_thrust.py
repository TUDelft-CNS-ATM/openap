import pandas as pd
import numpy as np
from openap import Thrust
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes3D


thrust = Thrust(ac='A320', eng='CFM56-5B4')

print('-'*70)

T = thrust.takeoff(tas=100, alt=0)
print("thrust.takeoff(tas=100, alt=0)")
print(T)
print('-'*70)

T = thrust.climb(tas=200, alt=20000, roc=1000)
print("thrust.climb(tas=200, alt=20000, roc=1000)")
print(T)
print('-'*70)

T = thrust.cruise(tas=230, alt=32000)
print("thrust.cruise(tas=230, alt=32000)")
print(T)
print('-'*70)

T = thrust.climb(tas=[200], alt=[20000], roc=[1000])
print("thrust.climb(tas=[200], alt=[20000], roc=[1000])")
print(T)
print('-'*70)


def plot():
    # Thrust = Thrust('A320', 'CFM56-5B4')
    thrust = Thrust('A320', 'V2500-A1')

    fig = plt.figure(figsize=(10,8))

    ax = fig.add_subplot(111, projection='3d')

    tas = np.arange(0, 500, 20)
    alt = np.arange(0, 35000, 2000)
    x, y = np.meshgrid(tas, alt)

    thr_to = thrust.takeoff(x, y)
    thr_cl = thrust.climb(x, y, 2000)

    c1, c2, c3 = .14231E+06, .51680E+05, .56809E-10
    thr_bada = c1 * (1 - y / c2 + c3 * y**2)

    plt.title('inflight')
    ax.plot_wireframe(x, y, thr_to, color='r', label='OpenAP-Thrust-TO')
    ax.plot_wireframe(x, y, thr_cl, color='g', label='Open-Thrust-CL')
    ax.plot_wireframe(x, y, thr_bada, color='b', label='BADA3')
    ax.set_xlabel('tas (kts)')
    ax.set_ylabel('alt (ft)')
    ax.set_zlabel('thr (N)')
    # ax.view_init(20, 40)
    ax.legend()
    plt.tight_layout()
    plt.show()
