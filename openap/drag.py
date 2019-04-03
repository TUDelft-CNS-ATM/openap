"""OpenAP drag model."""

import os
import glob
import yaml
import numpy as np
from openap import prop
from openap.extra import aero

curr_path = os.path.dirname(os.path.realpath(__file__))
dir_dragpolar = curr_path + "/data/dragpolar/"


class Drag(object):
    """Compute the drag of aicraft."""

    def __init__(self, ac):
        """Initialize Drag object.

        Args:
            ac (string): ICAO aircraft type (for example: A320).

        """
        super(Drag, self).__init__()

        self.ac = ac.lower()
        self.aircraft = prop.aircraft(ac)
        self.polar = self.dragpolar()

    def dragpolar(self):
        """Find and construct the drag polar model.

        Returns:
            dict: drag polar model parameters.

        """
        polar_files = glob.glob(dir_dragpolar + '*.yml')
        ac_polar_avaiable = [s[-8:-4].lower() for s in polar_files]

        if self.ac in ac_polar_avaiable:
            ac = self.ac
        else:
            if self.ac.startswith('a32'):
                ac = 'a320'
            elif self.ac.startswith('a33'):
                ac = 'a332'
            elif self.ac.startswith('a34'):
                ac = 'a333'
            elif self.ac.startswith('a35'):
                ac = 'a359'
            elif self.ac.startswith('a38'):
                ac = 'a388'
            elif self.ac.startswith('b73'):
                ac = 'b738'
            elif self.ac.startswith('b74'):
                ac = 'b744'
            elif self.ac.startswith('b77'):
                ac = 'b777'
            else:
                raise RuntimeError('%s drag polar not avaiable.' % self.ac.upper())

            print("warning: %s drag polar used for %s." % (ac.upper(), self.ac.upper()))

        f = dir_dragpolar + ac + '.yml'
        dragpolar = yaml.load(open(f))
        return dragpolar

    def _calc_drag(self, mass, tas, alt, cd0, k, path_angle):
        v = tas * aero.kts
        h = alt * aero.ft
        gamma = np.radians(path_angle)

        S = self.aircraft['wing']['area']

        rho = aero.density(h)
        qS = 0.5 * rho * v**2 * S
        L = mass * aero.g0 * np.cos(gamma)
        cl = L / qS
        cd = cd0 + k * cl**2
        D = cd * qS

        if isinstance(D, np.ndarray):
            D = D.astype(int)
        else:
            D = int(D)

        return D

    def clean(self, mass, tas, alt, path_angle=0):
        """Compute drag at clean configuration (considering compressibility).

        Args:
            mass (int or ndarray): Mass of the aircraft (unit: kg).
            tas (int or ndarray): True airspeed (unit: kt).
            alt (int or ndarray): Altitude (unit: ft).
            path_angle (float or ndarray): Path angle (unit: degree). Defaults to 0.

        Returns:
            int: Total drag (unit: N).

        """
        cd0 = self.polar['cd0']['clean']
        k = self.polar['k']['clean']

        mach_crit = self.polar['mach_crit']
        mach = aero.tas2mach(tas*aero.kts, alt*aero.ft)

        if isinstance(mach, np.ndarray):
            dCdw = np.where(mach > mach_crit, 20*(mach-mach_crit)**4, 0)
        else:
            dCdw = 20*(mach-mach_crit)**4 if mach > mach_crit else 0

        cd0 = cd0 + dCdw

        D = self._calc_drag(mass, tas, alt, cd0, k, path_angle)
        return D

    def initclimb(self, mass, tas, alt, path_angle=0):
        """Compute drag at initial climb.

        Args:
            mass (int or ndarray): Mass of the aircraft (unit: kg).
            tas (int or ndarray): True airspeed (unit: kt).
            alt (int or ndarray): Altitude (unit: ft).
            path_angle (float or ndarray): Path angle (unit: degree). Defaults to 0.

        Returns:
            int or ndarray: Total drag (unit: N).

        """
        cd0 = self.polar['cd0']['initclimb']
        k = self.polar['k']['initclimb']
        D = self._calc_drag(mass, tas, alt, cd0, k, path_angle)
        return D

    def finalapp(self, mass, tas, alt, path_angle=0):
        """Compute drag at final approach.

        Args:
            mass (int or ndarray): Mass of the aircraft (unit: kg).
            tas (int or ndarray): True airspeed (unit: kt).
            alt (int or ndarray): Altitude (unit: ft).
            path_angle (float or ndarray): Path angle (unit: degree). Defaults to 0.

        Returns:
            int or ndarray: Total drag (unit: N).

        """
        cd0 = self.polar['cd0']['finalapp']
        k = self.polar['k']['finalapp']
        D = self._calc_drag(mass, tas, alt, cd0, k, path_angle)
        return D
