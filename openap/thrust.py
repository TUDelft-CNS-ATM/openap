import numpy as np
from openap import aero


class ThrustRatioTF2S(object):
    """
    Turbonfan two shaft, simplified model
    REF: M. Bartel, T. M. Young, Simplified Thrust and Fuel Consumption Models
         for Modern Two-Shaft Turbonfan Engines

    """
    def __init__(self, bpr):
        super(ThrustRatioTF2S, self).__init__()
        self.bpr = bpr
        self.G0 = 0.0606 * bpr + 0.6337

    def takeoff(self, mach):
        G0 = self.G0
        bpr = self.bpr

        ratio = 1 - 0.377 * (1+bpr) / np.sqrt((1+0.82*bpr)*G0) * mach \
                   + (0.23 + 0.19 * np.sqrt(bpr)) * mach**2

        return ratio

    def inflight(self, mach, pressure):
        G0 = self.G0
        bpr = self.bpr

        M = mach
        P = pressure
        P0 = aero.p0
        PP = P / P0

        A = -0.4327 * PP**2 + 1.3855 * PP + 0.0472
        Z = 0.9106 * PP**3 - 1.7736 * PP**2 + 1.8697 * PP
        X = 0.1377 * PP**3 - 0.4374 * PP**2 + 1.3003 * PP

        ratio = A - 0.377 * (1+bpr) / np.sqrt((1+0.82*bpr)*G0) * Z * M \
              + (0.23 + 0.19 * np.sqrt(bpr)) * X * M**2

        return ratio

    def descent(self, Vtas, H):
        ratio = 0.15 * self.inflight(Vtas, H)
        return ratio


class ThrustRatioVSM(object):
    """
    Very simple model, for sea-level thrust calculation (take-off)
    1. http://home.anadolu.edu.tr/~mcavcar/common/Jetengine.pdf
    2. http://adg.stanford.edu/aa241/AircraftDesign.html
    """

    COEF = {
        'takeoff': (0.640, -1.024, 0.967),
    }

    def __init__(self):
        super(ThrustRatioVSM, self).__init__()

    def takeoff(self, mach):
        c1, c2, c3 = self.COEF['takeoff']

        ratio = c1 * mach**2 + c2 * mach + c3
        return ratio


if __name__ == '__main__':
    Thr0 = 112000 * 2
    thrust_ratio = ThrustRatioTF2S(bpr=5)
    M1 = np.arange(0, 0.3, 0.01)
    thr_ratio1 = thrust_ratio.takeoff(M1)

    M2 = np.arange(0.1, 1.0, 0.01)
    H2 = np.arange(0, 10000, 10)
    X, Y = np.meshgrid(M2, H2)
    thr_ratio2 = thrust_ratio.inflight(X, aero.pressure(Y))

    from matplotlib import pyplot as plt
    from mpl_toolkits.mplot3d.axes3d import Axes3D
    fig = plt.figure(figsize=(18, 6))

    plt.suptitle('A two shaft turbofan thrust model, bpr=5')

    ax = fig.add_subplot(121)
    plt.title('takeoff')
    ax.plot(M1, thr_ratio1, '.-', ms=10)
    ax.set_xlabel('mach')
    ax.set_ylabel('T / T0')
    ax.grid()

    ax = fig.add_subplot(122, projection='3d')
    plt.title('inflight')
    ax.plot_wireframe(X, Y, thr_ratio2, rstride=40, cstride=2)
    ax.set_xlabel('Mach number')
    ax.set_ylabel('altitude (m)')
    ax.set_zlabel('T / T0')
    ax.view_init(20, 40)
    plt.show()
