import yaml
import numpy as np
from openap import aero, utils

class Thrust(object):
    """
    Turbonfan two shaft, simplified model

    REF 1: M. Bartel, T. M. Young, Simplified Thrust and Fuel Consumption
        Models for Modern Two-Shaft Turbonfan Engines

    REF 2: C. Svoboda, Turbofan engine database as a preliminary desgin (cruise thrust)

    Note: top of climb from REF1 is altered to FL350, to be consistant with
        the model derived from REF2
    """

    def __init__(self, acmdl, engtype):
        super(Thrust, self).__init__()

        ac = utils.get_aircraft(acmdl)
        eng = utils.get_engine(engtype)

        if type(ac['engine']['options']) == dict:
            eng_options = list(ac['engine']['options'].values())
        elif type(ac['engine']['options']) == list:
            eng_options = list(ac['engine']['options'])
        if eng['name'] not in eng_options:
            raise RuntimeError('Engine and aircraft mismatch. Avaiable engines are %s' % eng_options)


        self.eng_bpr = eng['bpr']
        self.eng_max_thrust = eng['max_thrust']
        self.eng_number = ac['engine']['number']

        if eng['cruise_mach']:
            self.cruise_mach = eng['cruise_mach']
            self.eng_cruise_thrust = eng['cruise_thrust']
        else:
            self.cruise_mach = ac['cruise']['mach']
            self.eng_cruise_thrust = 0.2 * self.eng_max_thrust + 890


    def dfunc(self, mratio):
        d = -0.4204 * mratio + 1.0824
        return d


    def nfunc(self, roc):
        n = np.where(roc<1500, 0.89, np.where(roc<2500, 0.93, 0.97))
        return n


    def mfunc(self, vratio, roc):
        m = -1.2043e-1 * vratio - 8.8889e-9 * roc**2 + 2.4444e-5 * roc + 4.7379e-1
        return m


    def takeoff(self, tas, alt=None):
        tas = np.asarray(tas)
        alt = np.asarray(alt) if alt is not None else None

        mach = aero.tas2mach(tas*aero.kts, 0)

        eng_bpr = self.eng_bpr
        G0 = 0.0606 * self.eng_bpr + 0.6337

        if alt is None:
            # at sea level
            ratio = 1 - 0.377 * (1+eng_bpr) / np.sqrt((1+0.82*eng_bpr)*G0) * mach \
                       + (0.23 + 0.19 * np.sqrt(eng_bpr)) * mach**2

        else:
            # at certain altitude
            p = aero.pressure(alt * aero.ft)
            pp = p / aero.p0

            A = -0.4327 * pp**2 + 1.3855 * pp + 0.0472
            Z = 0.9106 * pp**3 - 1.7736 * pp**2 + 1.8697 * pp
            X = 0.1377 * pp**3 - 0.4374 * pp**2 + 1.3003 * pp

            ratio = A - 0.377 * (1+eng_bpr) / np.sqrt((1+0.82*eng_bpr)*G0) * Z * mach \
                  + (0.23 + 0.19 * np.sqrt(eng_bpr)) * X * mach**2

        F = ratio * self.eng_max_thrust * self.eng_number
        return F


    def inflight(self, tas, alt, roc):
        tas = np.asarray(tas)
        alt = np.asarray(alt)
        roc = np.abs(np.asarray(roc))

        h  = alt * aero.ft
        tas = np.where(tas < 10, 10, tas)

        mach = aero.tas2mach(tas*aero.kts, h)
        vcas = aero.tas2cas(tas*aero.kts, h)

        p = aero.pressure(h)
        p10 = aero.pressure(10000*aero.ft)
        p30 = aero.pressure(30000*aero.ft)

        # approximate thrust at top of climb (REF 2)
        F30 = self.eng_cruise_thrust * self.eng_number
        vcas_ref = aero.mach2cas(self.cruise_mach, 30000*aero.ft)

        # segment 3: alt > 30000:
        d = self.dfunc(mach/self.cruise_mach)
        b = (mach / self.cruise_mach) ** (-0.11)
        ratio_seg3 = d * np.log(p/p30) + b

        # segment 2: 10000 < alt <= 30000:
        a = (vcas / vcas_ref) ** (-0.1)
        n = self.nfunc(roc)
        ratio_seg2 = a * (p/p30) ** (-0.355 * (vcas/vcas_ref) + n)

        # segment 1: alt <= 10000:
        F10 = F30 * a * (p10/p30) ** (-0.355 * (vcas/vcas_ref) + n)
        m = self.mfunc(vcas/vcas_ref, roc)
        ratio_seg1 = m * (p/p30) + (F10/F30 - m * (p10/p30))

        ratio = np.where(alt>30000, ratio_seg3, np.where(alt>10000, ratio_seg2, ratio_seg1))

        F = ratio * F30
        return F


    def descent(self, tas, alt, roc):
        F = 0.15 * self.inflight(tas, alt, roc)
        return F
