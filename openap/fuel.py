import yaml
import numpy as np
from openap import aero, prop, Thrust, Drag

class FuelFlow(object):
    """Fuel flow model based on ICAO emmision databank"""

    def __init__(self, ac, eng):
        self.ac = ac
        self.eng = eng
        self.aircraft = prop.aircraft(ac)
        self.engine = prop.engine(eng)

        self.thrust = Thrust(self.ac, self.eng)
        self.drag = Drag(self.ac)

        coef = [self.engine['fuel_c2'], self.engine['fuel_c1'], self.engine['fuel_c0']]
        self.fuel_flow_model = np.poly1d(coef)


    def at_thrust(self, thr):
        """compute the fuel flow at given thrust ratio"""
        ratio = thr / (self.engine['max_thrust'] * self.aircraft['engine']['number'])
        fuelflow = self.fuel_flow_model(ratio)
        return fuelflow


    def takeoff(self, tas, alt=None, throttle=1):
        """compute the fuel flow at takeoff"""
        Tmax = self.thrust.takeoff(tas=tas, alt=alt)
        fuelflow =  throttle * self.at_thrust(Tmax)
        return fuelflow


    def enroute(self, mass, tas, alt, path_angle=0):
        """compute the fuel flow during the steady cruise"""
        rho = aero.density(alt * aero.ft)
        v = tas * aero.kts
        gamma = np.radians(path_angle)

        S = self.aircraft['wing']['area']
        dragpolar = self.drag.dragpolar()
        cd0 = dragpolar['cd0']['clean']
        k = dragpolar['k']

        q = 0.5 * rho * v**2
        L = mass * aero.g0 * np.cos(gamma)
        cl = L / (q * S)
        cd = cd0 + k * (cl)**2
        D = q * S * cd
        T = D + mass * aero.g0 * np.sin(gamma)

        fuelflow =  self.at_thrust(T)

        return fuelflow


    def plot_model(self, plot=True):
        """plot the interpolation model, or return the plot"""
        import matplotlib.pyplot as plt
        xx = np.linspace(0, 1, 50)
        yy = self.fuel_flow_model(xx)
        # plt.scatter(self.x, self.y, color='k')
        plt.plot(xx, yy, '--', color='gray')
        if plot:
            plt.show()
        else:
            return plt
