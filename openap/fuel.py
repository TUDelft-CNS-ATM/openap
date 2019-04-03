"""OpenAP FuelFlow model."""

import numpy as np
from openap.extra import aero
from openap import prop, Thrust, Drag


class FuelFlow(object):
    """Fuel flow model based on ICAO emmision databank."""

    def __init__(self, ac, eng=None):
        """Initialize FuelFlow object.

        Args:
            ac (string): ICAO aircraft type (for example: A320).
            eng (string): Engine type (for example: CFM56-5A3).
                Leave empty to use the default engine specified
                by in the aircraft database.

        """
        self.ac = ac
        self.aircraft = prop.aircraft(ac)

        if eng is not None:
            self.eng = eng
        else:
            self.eng = ac['engine']['default']

        self.engine = prop.engine(eng)

        self.thrust = Thrust(self.ac, self.eng)
        self.drag = Drag(self.ac)

        c3, c2, c1 = self.engine['fuel_c3'], self.engine['fuel_c2'], self.engine['fuel_c1']
        print(c3,c2,c1)
        self.fuel_flow_model = lambda x: c3*x**3 + c2*x**2 + c1*x

    def at_thrust(self, acthr):
        """Compute the fuel flow at a given total thrust.

        Args:
            acthr (int or ndarray): The total net thrust of the aircraft (unit: kN).

        Returns:
            float: Fuel flow (unit: kg/s).

        """
        ratio = acthr / (self.engine['max_thrust'] * self.aircraft['engine']['number'])
        fuelflow = self.fuel_flow_model(ratio) * self.aircraft['engine']['number']
        return fuelflow

    def takeoff(self, tas, alt=None, throttle=1):
        """Compute the fuel flow at takeoff.

        The net thrust is first estimated based on the maximum thrust model
        and throttle setting. Then FuelFlow.at_thrust() is called to compted
        the thrust.

        Args:
            tas (int or ndarray): Aircraft true airspeed (unit: kt).
            alt (int or ndarray): Altitude of airport (unit: ft). Defaults to sea-level.
            throttle (float or ndarray): The throttle setting, between 0 and 1.
                Defaults to 1, which is at full thrust.

        Returns:
            float: Fuel flow (unit: kg/s).

        """
        Tmax = self.thrust.takeoff(tas=tas, alt=alt)
        fuelflow =  throttle * self.at_thrust(Tmax)
        return fuelflow

    def enroute(self, mass, tas, alt, path_angle=0):
        """Compute the fuel flow during climb, cruise, or descent.

        The net thrust is first estimated based on the dynamic equation.
        Then FuelFlow.at_thrust() is called to compted the thrust.

        Args:
            tas (int or ndarray): Aircraft true airspeed (unit: kt).
            alt (int or ndarray): Altitude of airport, default at sea-level (unit: ft).
            throttle (float or ndarray): The throttle setting, between 0 and 1.

        Returns:
            float: Fuel flow (unit: kg/s).

        """
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

        fuelflow = self.at_thrust(T)

        return fuelflow

    def plot_model(self, plot=True):
        """Plot the engine fuel model, or return the pyplot object.

        Args:
            plot (bool): Display the plot or return an object.

        Returns:
            None or pyplot object.

        """
        import matplotlib.pyplot as plt
        xx = np.linspace(0, 1, 50)
        yy = self.fuel_flow_model(xx)
        # plt.scatter(self.x, self.y, color='k')
        plt.plot(xx, yy, '--', color='gray')
        if plot:
            plt.show()
        else:
            return plt
