import os
import glob
import yaml
import numpy as np
import pandas as pd
from openap import prop, aero

curr_path = os.path.dirname(os.path.realpath(__file__))
dir_dragpolar = curr_path + "/data/dragpolar/"


class Drag(object):
    """
    Compute the drag of aicraft
    """

    def __init__(self, ac):
        super(Drag, self).__init__()

        self.ac = ac.lower()
        self.aircraft = prop.aircraft(ac)
        self.polar = self.dragpolar()


    def dragpolar(self):
        files = glob.glob(dir_dragpolar + self.ac + '.yml')

        if len(files) == 0:
            raise RuntimeError('Dragpolar data not found.')

        f = files[0]
        dragpolar = yaml.load(open(f))

        return dragpolar


    def _calc_drag(self, mass, tas, alt, cd0):
        v = tas * aero.kts
        h = alt * aero.ft

        k = self.polar['k']
        S = self.aircraft['wing']['area']

        rho = aero.density(h)
        q = 0.5 * rho * v**2
        L = mass * aero.g0
        cl = L / (q * S)
        cd = cd0 + k * cl**2
        D = q * S * cd
        return D


    def clean(self, mass, tas, alt, path_angle=0):
        cd0 = self.polar['cd0']['clean']
        D = self._calc_drag(mass, tas, alt, path_angle, cd0)
        return D

    def initclimb(self, mass, tas, alt, path_angle):
        cd0 = self.polar['cd0']['initclimb']
        D = self._calc_drag(mass, tas, alt, path_angle, cd0)
        return D

    def approach(self, mass, tas, alt, path_angle):
        cd0 = self.polar['cd0']['approach']
        D = self._calc_drag(mass, tas, alt, path_angle, cd0)
        return D
