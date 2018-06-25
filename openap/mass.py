
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.interpolate import UnivariateSpline

from openap import aero, phase, utils
from openap.thrust import ThrustRatioTF2S
from openap.fuel import FuelFlow

from openap import segment


def scale(oldval, xxx_todo_changeme5, xxx_todo_changeme6):
    """scale bias, belief to actual mass value"""
    (oldmin, oldmax) = xxx_todo_changeme5
    (newmin, newmax) = xxx_todo_changeme6
    oldrange = (oldmax - oldmin)
    newrange = (newmax - newmin)
    newval = (((oldval - oldmin) * newrange) / oldrange) + newmin
    return newval


class Estimator(object):
    """Bayesian solver for estimatin aircraft mass"""

    def __init__(self, mdl, coef, vstall):
        """initialize estimator

        Args:
            mdl (string):  aircraft model
            coef (dict):  drag polar
            vstall (list):  stall speeds [ref_mass, v_stall_TO, v_stall_LD]
        """
        self.ac = utils.get_aircraft(mdl)
        self.engtype = self.ac['engines'][0]
        self.eng = utils.get_engine(self.engtype)

        self.tr = ThrustRatioTF2S(bpr=self.eng['bpr'])

        self.mmin = self.ac['oew']
        self.mmax = self.ac['mtow']

        self.mbound = [0, 2 * self.mmax]

        self.bounds_to = ((self.mbound[0], 0.8), (self.mbound[1], 1.0))
        self.bounds_cl = ((self.mbound[0], 0.8), (self.mbound[1], 1.0))
        self.bounds_de = (self.mbound[0], self.mbound[1])

        self.coef = coef
        self.vstall = vstall

        self.data = dict()
        self.idx = dict()
        self.fuelflow = None

        self.mu1 = 0.02

    def set_data(self, *args, **kwargs):
        """set the flight data, and related parameters

        Args:
            ts (:obj:`list` of :obj:`float`):  timestamp (seconds)
            lat (:obj:`list` of :obj:`float`):  latitude
            lon (:obj:`list` of :obj:`float`):  longitude
            alt (:obj:`list` of :obj:`float`):  altitude (feet)
            spd (:obj:`list` of :obj:`float`):  speed (knots)
            roc (:obj:`list` of :obj:`float`):  vertical rate (feet/minute)

        Keyword Args:
            phase_idx (:obj:`list` of :obj:`ind`) : indices where each
                phase starts [iTO, iIC, iCL, iCR, iDE, iFA, iLD, iED]
        """
        if len(args) not in [6, 8]:
            raise "Incorrect number of arguments"

        self.data['ts'] = np.array(args[0]) - args[0][0]
        self.data['lat'] = np.array(args[1])
        self.data['lon'] = np.array(args[2])
        self.data['H'] = np.array(args[3]) * aero.ft
        self.data['v'] = np.array(args[4]) * aero.kts
        self.data['vh'] = np.array(args[5]) * aero.fpm

        if len(args) == 8:
            self.data['mach'] = np.array(args[6])
            self.data['pa'] = np.array(args[7])
        else:
            self.data['mach'] = aero.tas2mach(self.data['v'], self.data['H'])
            self.data['mach'] = aero.pressure(self.data['H'])


        if kwargs.get('phase_idx'):
            phase_idx = kwargs.get('phase_idx')
        else:
            phase_idx = phase.full_phase_idx(self.data['ts'],
                                             self.data['H'] / aero.ft,
                                             self.data['v'] / aero.kts,
                                             self.data['vh'] / aero.fpm)

        self.idx['ito'] = phase_idx[0]
        self.idx['iic'] = phase_idx[1]
        self.idx['icl'] = phase_idx[2]
        self.idx['icr'] = phase_idx[3]
        self.idx['ide'] = phase_idx[4]
        self.idx['ifa'] = phase_idx[5]
        self.idx['ild'] = phase_idx[6]
        self.idx['ied'] = phase_idx[7]

        self.fuelflow = self.compute_fuelburn()


    def compute_fuelburn(self, debug=False):
        icl = self.idx['icl']
        ide = self.idx['ide']

        thrust_ratio = np.zeros(len(self.data['ts']))

        thrust_ratio[0:icl] = self.tr.takeoff(self.data['mach'][0:icl])
        thrust_ratio[icl:ide] = self.tr.inflight(self.data['mach'][icl:ide],
                                                 self.data['pa'][icl:ide])

        thrust_ratio[ide:] = self.tr.descent(self.data['mach'][ide:],
                                             self.data['pa'][ide:])
        engfuel = FuelFlow(self.engtype)
        ffts = engfuel.at_thrust_ratio(thrust_ratio)
        fuel = UnivariateSpline(self.data['ts'], ffts, k=2, s=0.1)

        if debug:
            plt.title('Fuel flow')
            xx = np.linspace(self.data['ts'][0], self.data['ts'][-1], 1000)
            yy = fuel(xx)
            plt.scatter(self.data['ts'], ffts)
            plt.plot(xx, yy)
            plt.show()

        return fuel


    def mass_liftoff(self, debug=False):
        ito = self.idx['ito']
        iic = self.idx['iic']
        # icl = self.idx['icl']

        coef = np.polyfit(self.data['ts'][ito:iic], self.data['v'][ito:iic], 2)
        fv = np.poly1d(coef)

        if self.data['vh'][iic] > 0:
            t_lof = max(self.data['ts'][iic-1], self.data['ts'][iic] - \
                            int(self.data['H'][iic] / self.data['vh'][iic]))
        else:
            t_lof = self.data['ts'][iic-1]

        v_lof = fv(t_lof)

        # print v_lof, self.data['v'][iic]

        m_ref = self.vstall[0]
        vs_lof = self.vstall[1] * aero.kts
        m = m_ref / (1.2**2 * vs_lof**2) * v_lof**2
        return int(m)


    def mass_approaching(self, debug=False):
        ifa = self.idx['ifa']
        ild = self.idx['ild']

        # using only last 10 points of the final approach
        v_app = np.average(self.data['v'][ild-10:ild])

        m_ref = self.vstall[0]
        vs_app = self.vstall[2] * aero.kts
        m = m_ref / (1.3**2 * vs_app**2) * v_app**2

        total_fuel = self.fuelflow.integral(self.data['ts'][0], self.data['ts'][-1])

        return int(m + total_fuel)


    def mass_taking_off(self, debug=False):
        ito = self.idx['ito']
        iic = self.idx['iic']

        rho = aero.rho0
        g = aero.g0
        S = self.ac['wa']
        CD0 = self.coef['TO']['CD0']
        K = self.coef['TO']['K']

        def func_v(t, k1, k2, k3):
            return k1 * t**2 + k2 * t + k3

        def func_a(t, k1, k2, k3):
            return 2 * k1 * t + k2

        def func_to(xxx_todo_changeme, m, eta):
            (T, v, acc) = xxx_todo_changeme
            k1 = T
            k2 = - (self.mu1*g + acc)
            k3 = - 0.5*rho*S*v**2 * (CD0 - self.mu1**2/(4*K))
            err = (k1 * eta + k2 * m + k3)**2
            return err

        def jac_to(xxx_todo_changeme1, m, eta):
            (T, v, acc) = xxx_todo_changeme1
            J = np.empty((T.size, 2))

            k1 = T
            k2 = - (self.mu1*g + acc)
            k3 = - 0.5*rho*S*v**2 * (CD0 - self.mu1**2/(4*K))

            J[:, 0] = 2 * (k1 * eta + k2 * m + k3) * k2
            J[:, 1] = 2 * (k1 * eta + k2 * m + k3) * k1
            return J

        vopt, vcov = curve_fit(
            func_v, self.data['ts'][ito:iic], self.data['v'][ito:iic],
            bounds=([-np.inf, -np.inf, -np.inf], [0, np.inf, np.inf])
        )

        tt = np.linspace(self.data['ts'][ito], self.data['ts'][iic-1], 15)

        vv = func_v(tt, *vopt)
        aa = func_a(tt, *vopt)

        thr = self.tr.takeoff(aero.tas2mach(vv, 0)) \
                * self.ac['n_engines'] * self.eng['thr']

        err = np.zeros(thr.shape)
        me_opt, me_cov = curve_fit(
            func_to, (thr, vv, aa), err, jac=jac_to, bounds=self.bounds_to
        )
        m, eta = me_opt

        if debug:
            err = np.sqrt(np.diag(me_cov))
            print(int(m), round(eta, 2), round(err[0]), round(err[1], 2))
            mm = (thr - 0.5*rho*S*vv**2 * (CD0 - self.mu1**2/(4*K))) / (self.mu1*g + aa)
            print(np.mean(mm))

            plt.subplot(211)
            plt.scatter(self.data['ts'][ito:iic], self.data['v'][ito:iic], alpha=0.5)
            plt.plot(tt, func_v(tt, *vopt), lw=2, color='g')

            plt.subplot(212)
            plt.plot(tt, mm)
            plt.show()

        return int(m)


    def mass_climb(self, debug=False):
        iic = self.idx['iic']
        icr = self.idx['icr']

        # extract continous climb segments, ignore level flight
        labels = segment.fuzzylabels(
            self.data['ts'][iic:icr],
            self.data['H'][iic:icr] / aero.ft,
            self.data['v'][iic:icr] / aero.kts,
            self.data['vh'][iic:icr] / aero.fpm,
        )

        segments_idx = []
        i_tmp = 0
        for i, lb in enumerate(labels):
            if lb != 'CL':
                if self.data['ts'][iic+i] - self.data['ts'][iic+i_tmp] > 60:
                    segments_idx.append((iic+i_tmp, iic+i))
                i_tmp = i

        # # create more segments in climb
        # extend_segments_idx = []
        # for i0, i1 in segments_idx:
        #     nchunks = (i1 - i0) / 100
        #     for j in range(nchunks):
        #         start_end = (i0+j*100, i0+(j+1)*100)
        #         extend_segments_idx.append(start_end)

        g = aero.g0
        S = self.ac['wa']
        CD0 = self.coef['CR']['CD0']
        K = self.coef['CR']['K']

        def func(xxx_todo_changeme2, m, eta):
            (T, v, acc, vh, gamma, rho, mfuel) = xxx_todo_changeme2
            k1 = 2 * K * g**2 * np.cos(gamma)**2 / (rho * v**2 * S)
            k2 = acc + g * vh / v
            k3 = 0.5 * CD0 * rho * v**2 * S
            k4 = -T
            err = (k1 * (m + mfuel)**2 + k2 * (m + mfuel) + k3 + k4 * eta)**2
            return err

        def jac(xxx_todo_changeme3, m, eta):
            (T, v, acc, vh, gamma, rho, mfuel) = xxx_todo_changeme3
            J = np.empty((T.size, 2))

            k1 = 2 * K * g**2 * np.cos(gamma)**2 / (rho * v**2 * S)
            k2 = acc + g * vh / v
            k3 = 0.5 * CD0 * rho * v**2 * S
            k4 = -T

            J[:, 0] = 2 * (k1 * (m+mfuel)**2 + k2 * (m+mfuel) + k3 + k4 * eta) * (2 * k1 * (m+mfuel) + k2)
            J[:, 1] = 2 * (k1 * (m+mfuel)**2 + k2 * (m+mfuel) + k3 + k4 * eta) * k4
            return J

        dd = aero.distance(
            self.data['lat'][iic:icr], self.data['lon'][iic:icr],
            self.data['lat'][iic+1:icr+1], self.data['lon'][iic+1:icr+1],
            self.data['H'][iic:icr]
        )

        dh = self.data['H'][iic+1:icr+1] - self.data['H'][iic:icr]

        spl_H = UnivariateSpline(self.data['ts'][iic:icr], self.data['H'][iic:icr], k=1, s=5000)
        spl_v = UnivariateSpline(self.data['ts'][iic:icr], self.data['v'][iic:icr], k=2, s=5000)
        spl_vh = UnivariateSpline(self.data['ts'][iic:icr], self.data['vh'][iic:icr], k=2, s=5000)
        spl_gamma = UnivariateSpline(self.data['ts'][iic:icr], np.arctan2(dh, dd), k=2, s=5)

        ms = []

        for sidx in segments_idx:

            i0 = sidx[0]
            i1 = sidx[1]

            t_cl = np.linspace(self.data['ts'][i0], self.data['ts'][i1], 200)

            v_cl = spl_v(t_cl)

            # a_cl = np.polyder(spl_v)(t_cl)
            a_cl = spl_v.derivative()(t_cl)
            vh_cl = spl_vh(t_cl)
            H_cl = spl_H(t_cl)
            gamma_cl = spl_gamma(t_cl)
            rho_cl = aero.density(H_cl)

            mfuel_cl = np.zeros(len(t_cl))
            for idx in range(len(t_cl)):
                mfuel_cl[idx] = self.fuelflow.integral(self.data['ts'][0], t_cl[idx])

            thr = self.tr.inflight(aero.tas2mach(v_cl, H_cl), aero.pressure(H_cl)) \
                    * self.ac['n_engines'] * self.eng['thr']


            err = np.zeros(thr.shape)
            try:
                me_opt, me_cov = curve_fit(
                    func, (thr, v_cl, a_cl, vh_cl, gamma_cl, rho_cl, mfuel_cl), err,
                    jac=jac, bounds=self.bounds_cl)

                m, eta = me_opt
                ms.append(int(m))
            except:
                ms.append(np.nan)

        if debug:
            err = np.sqrt(np.diag(me_cov))
            print(int(m), round(eta, 2), round(err[0]), round(err[1], 2))

            xx = np.linspace(self.data['ts'][iic], self.data['ts'][icr], 500)

            plt.subplot(221)
            plt.plot(xx, spl_H(xx), lw=2, color='r')
            plt.scatter(self.data['ts'][iic:icr], self.data['H'][iic:icr],
                        alpha=0.3, color='k', lw=0)

            plt.subplot(222)
            plt.plot(xx, spl_v(xx), lw=2, color='r')
            plt.scatter(self.data['ts'][iic:icr], self.data['v'][iic:icr],
                        alpha=0.3, color='k', lw=0)

            plt.subplot(223)
            plt.plot(xx, spl_vh(xx), lw=2, color='r')
            plt.scatter(self.data['ts'][iic:icr], self.data['vh'][iic:icr],
                        alpha=0.3, color='k', lw=0)

            plt.subplot(224)
            plt.plot(xx, spl_gamma(xx), lw=2, color='r')
            plt.scatter(self.data['ts'][iic:icr], np.arctan2(dh, dd),
                        alpha=0.3, color='k', lw=0)

            plt.show()

        return ms


    def mass_descent(self, debug=False):
        ide = self.idx['ide']
        ifa = self.idx['ifa']

        # extract the continous descent segments, exculed level flight
        labels = segment.fuzzylabels(
            self.data['ts'][ide:ifa],
            self.data['H'][ide:ifa] / aero.ft,
            self.data['v'][ide:ifa] / aero.kts,
            self.data['vh'][ide:ifa] / aero.fpm
        )

        segments_idx = []
        i_tmp = 0
        for i, lb in enumerate(labels):
            if lb != 'DE':
                if self.data['ts'][ide+i] - self.data['ts'][ide+i_tmp] > 120:
                    segments_idx.append((ide+i_tmp, ide+i))
                i_tmp = i

        # # create more segments in climb
        # extend_segments_idx = []
        # for i0, i1 in segments_idx:
        #     nchunks = (i1 - i0) / 100
        #     for j in range(nchunks):
        #         start_end = (i0+j*100, i0+(j+1)*100)
        #         extend_segments_idx.append(start_end)

        g = aero.g0
        S = self.ac['wa']
        CD0 = self.coef['CR']['CD0']
        K = self.coef['CR']['K']

        # too much uncertainty in descent, simplify descent equation

        def func(xxx_todo_changeme4, m):
            (T, v, vh, gamma, rho, mfuel) = xxx_todo_changeme4
            k1 = 2 * K * g**2 * gamma**2 / (rho * v**2 * S)
            k2 = g * vh / v
            k3 = 0.5 * CD0 * rho * v**2 * S
            err = (k1 * (m + mfuel)**2 + k2 * (m + mfuel) + k3)**2
            return err

        # def func((T, v, acc, vh, gamma, rho, mfuel), m, eta):
        #     k1 = 2 * K * g**2 * np.cos(gamma)**2 / (rho * v**2 * S)
        #     k2 = acc + g * vh / v
        #     k3 = 0.5 * CD0 * rho * v**2 * S
        #     k4 = -T
        #     # k4 = 0
        #     err = (k1 * (m + mfuel)**2 + k2 * (m + mfuel) + k3 + k4 * eta)**2
        #     return err

        ms = []

        for sidx in segments_idx:

            i0 = sidx[0]
            i1 = sidx[1]

            dh = self.data['H'][i1] - self.data['H'][i0]

            dd = 0
            for i in range(i0, i1-1):
                dd += aero.distance(
                    self.data['lat'][i], self.data['lon'][i],
                    self.data['lat'][i+1], self.data['lon'][i+1])

            gamma = np.arctan2(dh, dd)

            # spl_H = UnivariateSpline(self.data['ts'][i0:i1], self.data['H'][i0:i1], k=1, s=5000)
            # spl_v = UnivariateSpline(self.data['ts'][i0:i1], self.data['v'][i0:i1], k=2, s=5000)
            # spl_vh = UnivariateSpline(self.data['ts'][i0:i1], self.data['vh'][i0:i1], k=2, s=500)

            # t_de = np.linspace(self.data['ts'][i0], self.data['ts'][i1], 300)
            # v_de = spl_v(t_de)
            # a_de = spl_v.derivative()(t_de)
            # vh_de = spl_vh(t_de)
            # H_de = spl_H(t_de)
            # rho_de = aero.density(H_de)

            t_de = self.data['ts'][i0:i1]
            vh_de = self.data['vh'][i0:i1]
            H_de = self.data['H'][i0:i1]
            v_de = self.data['v'][i0:i1]

            rho_de = aero.density(H_de)

            mfuel_de = np.zeros(len(t_de))
            for idx in range(len(t_de)):
                mfuel_de[idx] = self.fuelflow.integral(self.data['ts'][0], t_de[idx])

            thr = self.tr.descent(aero.tas2mach(v_de, H_de), aero.pressure(H_de)) \
                    * self.ac['n_engines'] * self.eng['thr']

            err = np.zeros(v_de.shape)

            try:
                me_opt, me_cov = curve_fit(
                    func, (thr, v_de, vh_de, gamma, rho_de, mfuel_de), err,
                    p0=(self.mmin+self.mmax)/2,
                    bounds=self.bounds_de)

                ms.append(int(me_opt))
            except:
                ms.append(np.nan)

        if debug:
            err = np.sqrt(np.diag(me_cov))
            print(int(m), round(eta, 2), round(err[0]), round(err[1], 2))

            xx = np.linspace(self.data['ts'][ide], self.data['ts'][ifa], 1000)
            plt.subplot(221)
            plt.plot(xx, spl_H(xx), lw=2, color='r')
            plt.scatter(self.data['ts'][ide:ifa], self.data['H'][ide:ifa],
                        alpha=0.3, color='k', lw=0)

            plt.subplot(222)
            plt.plot(xx, spl_v(xx), lw=2, color='r')
            plt.scatter(self.data['ts'][ide:ifa], self.data['v'][ide:ifa],
                        alpha=0.3, color='k', lw=0)

            plt.subplot(223)
            # plt.plot(xx, spl_vh(xx), lw=2, color='r')
            plt.scatter(self.data['ts'][ide:ifa], self.data['vh'][ide:ifa],
                        alpha=0.3, color='k', lw=0)

            # plt.subplot(224)
            # plt.plot(xx, spl_gamma(xx), lw=2, color='r')
            # plt.scatter(self.data['ts'][ide:ifa], np.arctan2(dh, dd),
            #             alpha=0.3, color='k', lw=0)

            plt.show()

        return ms

    def bayes(self, bias=0, belief=0.4, sigma=None, debug=False):
        """Bayesian maximum likelihood estimation

        Args:
            bias (float): level of bias in prior, range in [-1, 1]
            belief (float): level if belief, range in [0, 1]
            sigma (float or None): Fixed sigma of the normal likelihood

        Returns:
            int: mass in kg
        """
        try:
            m_to = self.mass_taking_off()
        except:
            m_to = np.nan

        try:
            m_lof = self.mass_liftoff()
        except:
            m_lof = np.nan

        try:
            m_cl = self.mass_climb()
        except:
            m_cl = [np.nan]

        try:
            m_de = self.mass_descent()
        except:
            m_de = [np.nan]

        try:
            m_app = self.mass_approaching()
        except:
            m_app = np.nan

        ms = np.array([m_to, m_lof, m_app] + m_cl + m_de).flatten()
        ms = ms[np.isfinite(ms)]

        # Bayesian discard inpossible occurance, regardless of evidence
        # Note: those are also values lsq can't converge
        ms = ms[ms > self.mmin * 0.2]
        ms = ms[ms < self.mbound[1] * 0.8]

        # bias range = [M_OEW, M_MTOW]
        mu0 = scale(bias, (-1, 1), (self.mmin, self.mmax))
        # belief range = (M_MTOW - M_OEW) * [1/2, 1/16]
        delta_m = self.mmax - self.mmin
        sigma0 = scale(belief, (0, 1), (delta_m/2.0, delta_m/16.0))

        mbar = np.mean(ms)

        if sigma is None:
            # estimate the sigma, using the std of measurement
            sigma = np.std(ms)
        else:
            sigma = (self.mmax - self.mmin) * sigma

        n = len(ms)

        mu_post = (n * sigma0**2 * mbar + sigma**2 * mu0) / (sigma**2 + n * sigma0**2)

        sigma_post = np.sqrt(sigma**2 * sigma0**2 / (sigma**2 + n * sigma0**2))

        if debug:
            from scipy import stats
            xmax = max(self.mmax+self.mmin, max(ms))
            xx = np.linspace(-0.1*xmax, 1.1*xmax, 500)

            plt.figure(figsize=(8, 5))

            yy = stats.norm.pdf(xx, mu0, sigma0)
            plt.plot(xx, yy, color='b', lw=2, label='Prior')

            yy = stats.norm.pdf(xx, mbar, sigma)
            plt.plot(xx, yy, color='g', ls='--', lw=2)

            for m in ms:
                y = stats.norm.pdf(m, mbar, sigma)
                plt.plot([m, m], [0, y], color='g', lw=2)

            # just for the label
            plt.plot([0, 1e-9], [0, 1e-9], color='g', lw=2, label='Observations')

            yy = stats.norm.pdf(xx, mu_post, sigma_post)
            plt.plot(xx, yy, color='purple', lw=2, label='Posterior')
            plt.plot([mu_post, mu_post], [0, max(yy)], '-', color='purple')

            plt.xlabel('Aircraft initial mass (t)')
            plt.xlim([min(xx), max(xx)])
            plt.ylim([0, max(yy)*1.2])
            plt.ylabel('Density (-)')

            plt.grid()
            plt.legend(loc='best')
            plt.show()

        return int(mu_post), int(sigma_post), (ms, mbar, sigma, mu0, sigma0)
