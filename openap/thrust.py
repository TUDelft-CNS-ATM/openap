import numpy as np
from openap import aero


class TF2S(object):
    """
    Turbonfan two shaft, simplified model

    REF 1: M. Bartel, T. M. Young, Simplified Thrust and Fuel Consumption
        Models for Modern Two-Shaft Turbonfan Engines

    REF 2: C. Svoboda, Turbofan engine database as a preliminary desgin (cruise thrust)

    Note: top of climb from REF1 is altered to FL350, to be consistant with
        the model derived from REF2
    """

    def __init__(self, thr0, bpr):
        super(TF2S, self).__init__()
        self.bpr = bpr
        self.thr0 = thr0


    def takeoff(self, tas, alt=None):
        tas = np.asarray(tas)
        alt = np.asarray(alt) if alt is not None else None

        mach = aero.tas2mach(tas*aero.kts, 0)

        bpr = self.bpr
        G0 = 0.0606 * self.bpr + 0.6337

        if alt is None:
            # at sea level
            ratio = 1 - 0.377 * (1+bpr) / np.sqrt((1+0.82*bpr)*G0) * mach \
                       + (0.23 + 0.19 * np.sqrt(bpr)) * mach**2

        else:
            # at certain altitude
            p = aero.pressure(alt * aero.ft)
            pp = p / aero.p0

            A = -0.4327 * pp**2 + 1.3855 * pp + 0.0472
            Z = 0.9106 * pp**3 - 1.7736 * pp**2 + 1.8697 * pp
            X = 0.1377 * pp**3 - 0.4374 * pp**2 + 1.3003 * pp

            ratio = A - 0.377 * (1+bpr) / np.sqrt((1+0.82*bpr)*G0) * Z * mach \
                  + (0.23 + 0.19 * np.sqrt(bpr)) * X * mach**2

        F = ratio * self.thr0
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
        p35 = aero.pressure(35000*aero.ft)

        # approximate thrust at top of climb (REF 2)
        F35 = (200 + 0.2 * self.thr0/4.448) * 4.448
        mach_ref = 0.8
        vcas_ref = aero.mach2cas(mach_ref, 35000*aero.ft)

        # segment 3: alt > 35000:
        d = self.dfunc(mach/mach_ref)
        b = (mach / mach_ref) ** (-0.11)
        ratio_seg3 = d * np.log(p/p35) + b

        # segment 2: 10000 < alt <= 35000:
        a = (vcas / vcas_ref) ** (-0.1)
        n = self.nfunc(roc)
        ratio_seg2 = a * (p/p35) ** (-0.355 * (vcas/vcas_ref) + n)

        # segment 1: alt <= 10000:
        F10 = F35 * a * (p10/p35) ** (-0.355 * (vcas/vcas_ref) + n)
        m = self.mfunc(vcas/vcas_ref, roc)
        ratio_seg1 = m * (p/p35) + (F10/F35 - m * (p10/p35))

        ratio = np.where(alt>35000, ratio_seg3, np.where(alt>10000, ratio_seg2, ratio_seg1))

        F = ratio * F35
        return F


    def descent(self, tas, alt, roc):
        F = 0.15 * self.inflight(tas, alt, roc)
        return F


    def dfunc(self, mratio):
        d = np.where(
            mratio<0.85, 0.73, np.where(
                mratio<0.92, 0.73+(0.69-0.73)/(0.92-0.85)*(mratio-0.85), np.where(
                    mratio<1.08, 0.66+(0.63-0.66)/(1.08-1.00)*(mratio-1.00), np.where(
                        mratio<1.15, 0.63+(0.60-0.63)/(1.15-1.08)*(mratio-1.08), 0.60
                    )
                )
            )
        )
        return d


    def nfunc(self, roc):
        n = np.where(roc<1500, 0.89, np.where(roc<2500, 0.93, 0.97))
        return n


    def mfunc(self, vratio, roc):
        m = np.where(
            vratio<0.67, 0.4, np.where(
                vratio<0.75, 0.39, np.where(
                    vratio<0.83, 0.38, np.where(
                        vratio<0.92, 0.37, 0.36
                    )
                )
            )
        )
        m = np.where(
            roc<1500, m-0.06, np.where(
                roc<2500, m-0.01, m
            )
        )
        return m



class VSM(object):
    """
    Very simple model, for sea-level thrust calculation (take-off)
    1. http://home.anadolu.edu.tr/~mcavcar/common/Jetengine.pdf
    2. http://adg.stanford.edu/aa241/AircraftDesign.html
    """

    COEF = {
        'takeoff': (0.640, -1.024, 0.967),
    }

    def __init__(self):
        super(VSM, self).__init__()

    def takeoff(self, tas):
        c1, c2, c3 = self.COEF['takeoff']
        mach = aero.tas2mach(tas*aero.ft, 0)
        ratio = c1 * mach**2 + c2 * mach + c3
        return ratio
