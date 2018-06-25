import numpy as np
from openap import utils

class FuelFlow(object):
    """Fuel flow model based on ICAO emmision databank"""

    def __init__(self, engine):
        eng = utils.get_engine(engine)

        # fuel flow model
        self.y = [eng['ff_idl'], eng['ff_app'], eng['ff_co'], eng['ff_to']]
        self.x = [0.07, 0.3, 0.85, 1.0]
        coef = np.polyfit(self.x, self.y, 2)

        self.flow = np.poly1d(coef)      # fuel flow model f(T/T0)

    def at_thrust_ratio(self, ratio):
        """compute the fuel flow at given thrust ratio"""
        return self.flow(ratio)

    def plot_engine_fuel_flow(self, plot=True):
        """plot the interpolation model, or return the plot"""
        import matplotlib.pyplot as plt
        xx = np.linspace(0, 1, 50)
        yy = self.flow(xx)
        plt.scatter(self.x, self.y, color='k')
        plt.plot(xx, yy, '--', color='gray')
        if plot:
            plt.show()
        else:
            return plt
