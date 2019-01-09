import yaml
import numpy as np
from openap import aero, utils, thrust

class FuelFlow(object):
    """Fuel flow model based on ICAO emmision databank"""

    def __init__(self, acmdl, engtype):
        self.acmdl = acmdl
        self.engtype = engtype
        self.ac = utils.get_aircraft(acmdl)
        self.eng = utils.get_engine(engtype)


        coef = [self.eng['fuel_c2'], self.eng['fuel_c1'], self.eng['fuel_c0']]
        self.flow = np.poly1d(coef)


    def from_thrust(self, thr):
        """compute the fuel flow at given thrust ratio"""
        ratio = thr / (self.eng['max_thrust'] * self.ac['engine']['number'])
        fuelflow = self.flow(ratio)
        return fuelflow


    def enroute(self, mass, tas, alt):
        """compute the fuel flow during the steady cruise"""
        rho = aero.density(alt * aero.ft)
        v = tas * aero.kts

        S = self.ac['dimensions']['wing_area']
        dragpolar = utils.get_dragpolar(self.acmdl)
        cd0 = dragpolar['cd0']['clean']
        k = dragpolar['k']

        q = 0.5 * rho * v**2 * S
        thr = q * cd0 + k * (mass * aero.g0)**2 / q
        fuelflow =  self.at_thrust(thr)

        return fuelflow


    def at_takeoff(self, tas, alt=None):
        """compute the fuel flow at takeoff"""
        Thrust = thrust.Thrust(self.acmdl, self.engtype)
        thr = Thrust.takeoff(tas, alt)
        fuelflow =  self.at_thrust(thr)
        return fuelflow


    def at_max_thrust_climb(self, tas, alt, roc):
        """compute the fuel flow based on the maximum thrust profile"""
        Thrust = thrust.Thrust(self.acmdl, self.engtype)
        thr = Thrust.inflight(tas, alt, roc)
        fuelflow =  self.at_thrust(thr)
        return fuelflow


    def plot_engine_fuel_flow(self, plot=True):
        """plot the interpolation model, or return the plot"""
        import matplotlib.pyplot as plt
        xx = np.linspace(0, 1, 50)
        yy = self.flow(xx)
        # plt.scatter(self.x, self.y, color='k')
        plt.plot(xx, yy, '--', color='gray')
        if plot:
            plt.show()
        else:
            return plt
