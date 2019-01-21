import os
import pandas as pd

curr_path = os.path.dirname(os.path.realpath(__file__))
dir_wrap = curr_path + "/data/wrap/"

class WRAP(object):
    """
    Compute the drag of aicraft
    """

    def __init__(self, ac):
        super(WRAP, self).__init__()

        self.ac = ac.lower()
        self.df = pd.read_fwf(dir_wrap + self.ac + '.txt')

    def _get_var(self, var):
        r = self.df[self.df['variable']==var]

        if r.shape[0] == 0:
            raise RuntimeError('variable not found')

        v = r.values[0]
        opt = v[3]
        min = v[4]
        max = v[5]
        model = v[6]
        params = v[7].split('|')
        return opt, min, max, model, params


    def takeoff_speed(self):
        return self._get_var('to_v_lof')

    def takeoff_distance(self):
        return self._get_var('to_d_tof')

    def takeoff_acceleration(self):
        return self._get_var('to_acc_tof')

    def initclimb_cas(self):
        return self._get_var('ic_va_avg')

    def initclimb_vs(self):
        return self._get_var('ic_vs_avg')

    def climb_range(self):
        return self._get_var('cl_d_range')

    def climb_vs_pre_const_cas(self):
        return self._get_var('cl_vs_avg_pre_cas')

    def climb_const_cas(self):
        return self._get_var('cl_v_cas_const')

    def climb_alt_cross_const_cas(self):
        return self._get_var('cl_h_cas_const')

    def climb_vs_const_cas(self):
        return self._get_var('cl_vs_avg_cas_const')

    def climb_const_mach(self):
        return self._get_var('cl_v_mach_const')

    def climb_alt_cross_const_mach(self):
        return self._get_var('cl_h_mach_const')

    def climb_vs_const_mach(self):
        return self._get_var('cl_vs_avg_mach_const')

    def cruise_range(self):
        return self._get_var('cr_d_range')

    def cruise_alt(self):
        return self._get_var('cr_h_mean')

    def cruise_init_alt(self):
        return self._get_var('cr_h_init')

    def cruise_mach(self):
        return self._get_var('cr_v_mach_mean')

    def descent_range(self):
        return self._get_var('de_d_range')

    def descent_const_mach(self):
        return self._get_var('de_v_mach_const')

    def descent_alt_cross_const_mach(self):
        return self._get_var('de_h_mach_const')

    def descent_const_cas(self):
        return self._get_var('de_v_cas_const')

    def descent_alt_cross_const_cas(self):
        return self._get_var('de_h_cas_const')

    def descent_vs_const_cas(self):
        return self._get_var('de_vs_avg_cas_const')

    def descent_vs_const_mach(self):
        return self._get_var('de_vs_avg_mach_const')

    def descent_vs_post_const_cas(self):
        return self._get_var('de_vs_avg_after_cas')

    def finalapp_cas(self):
        return self._get_var('fa_va_avg')

    def finalapp_vs(self):
        return self._get_var('fa_vs_avg')

    def landing_speed(self):
        return self._get_var('ld_v_app')

    def landing_distance(self):
        return self._get_var('ld_d_brk')

    def landing_acceleration(self):
        return self._get_var('ld_acc_brk')
