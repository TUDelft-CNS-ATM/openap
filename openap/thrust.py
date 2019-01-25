import yaml
import numpy as np
from openap import aero, prop

class Thrust(object):
    """
    Turbonfan two shaft, simplified model

    REF 1: M. Bartel, T. M. Young, Simplified Thrust and Fuel Consumption
        Models for Modern Two-Shaft Turbonfan Engines

    REF 2: C. Svoboda, Turbofan engine database as a preliminary desgin (cruise thrust)

    Note: top of climb from REF1 is altered to FL350, to be consistant with
        the model derived from REF2
    """

    def __init__(self, ac, eng):
        super(Thrust, self).__init__()

        aircraft = prop.aircraft(ac)
        engine = prop.engine(eng)

        if type(aircraft['engine']['options']) == dict:
            eng_options = list(aircraft['engine']['options'].values())
        elif type(aircraft['engine']['options']) == list:
            eng_options = list(aircraft['engine']['options'])
        if engine['name'] not in eng_options:
            raise RuntimeError('Engine and aircraft mismatch. Avaiable engines are %s' % eng_options)


        self.cruise_alt = aircraft['cruise']['height'] / aero.ft
        # self.cruise_alt = 30000
        self.eng_bpr = engine['bpr']
        self.eng_max_thrust = engine['max_thrust']
        self.eng_number = aircraft['engine']['number']

        if engine['cruise_mach'] > 0:
            self.cruise_mach = engine['cruise_mach']
            self.eng_cruise_thrust = engine['cruise_thrust']
        else:
            self.cruise_mach = aircraft['cruise']['mach']
            self.eng_cruise_thrust = 0.2 * self.eng_max_thrust + 890


    def dfunc(self, mratio):
        d = -0.4204 * mratio + 1.0824
        return d


    def nfunc(self, roc):
        # n = np.where(roc<1500, 0.89, np.where(roc<2500, 0.93, 0.97))
        n = 2.667e-05 * roc + 0.8633
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
            P = aero.pressure(alt * aero.ft)
            dP = P / aero.p0

            A = -0.4327 * dP**2 + 1.3855 * dP + 0.0472
            Z = 0.9106 * dP**3 - 1.7736 * dP**2 + 1.8697 * dP
            X = 0.1377 * dP**3 - 0.4374 * dP**2 + 1.3003 * dP

            ratio = A - 0.377 * (1+eng_bpr) / np.sqrt((1+0.82*eng_bpr)*G0) * Z * mach \
                  + (0.23 + 0.19 * np.sqrt(eng_bpr)) * X * mach**2

        F = ratio * self.eng_max_thrust * self.eng_number
        return F


    def cruise(self, tas, alt):
        return self.climb(tas, alt, roc=0)


    def climb(self, tas, alt, roc):
        tas = np.asarray(tas)
        alt = np.asarray(alt)
        roc = np.abs(np.asarray(roc))

        h  = alt * aero.ft
        tas = np.where(tas < 10, 10, tas)

        mach = aero.tas2mach(tas*aero.kts, h)
        vcas = aero.tas2cas(tas*aero.kts, h)

        P = aero.pressure(h)
        P10 = aero.pressure(10000*aero.ft)
        Pcr = aero.pressure(self.cruise_alt*aero.ft)

        # approximate thrust at top of climb (REF 2)
        Fcr = self.eng_cruise_thrust * self.eng_number
        vcas_ref = aero.mach2cas(self.cruise_mach, self.cruise_alt*aero.ft)

        # segment 3: alt > 30000:
        d = self.dfunc(mach/self.cruise_mach)
        b = (mach / self.cruise_mach) ** (-0.11)
        ratio_seg3 = d * np.log(P/Pcr) + b

        # segment 2: 10000 < alt <= 30000:
        a = (vcas / vcas_ref) ** (-0.1)
        n = self.nfunc(roc)
        ratio_seg2 = a * (P/Pcr) ** (-0.355 * (vcas/vcas_ref) + n)

        # segment 1: alt <= 10000:
        F10 = Fcr * a * (P10/Pcr) ** (-0.355 * (vcas/vcas_ref) + n)
        m = self.mfunc(vcas/vcas_ref, roc)
        ratio_seg1 = m * (P/Pcr) + (F10/Fcr - m * (P10/Pcr))

        ratio = np.where(alt>30000, ratio_seg3, np.where(alt>10000, ratio_seg2, ratio_seg1))

        F = ratio * Fcr
        return F


    def descent(self, tas, alt, roc):
        F = 0.15 * self.inflight(tas, alt, roc)
        return F
