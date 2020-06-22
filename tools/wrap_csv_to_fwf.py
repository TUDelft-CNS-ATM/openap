import os
import glob
import yaml
import numpy as np
import pandas as pd


from tabulate import tabulate
def to_fwf(df, fname):
    content = tabulate(df.values.tolist(), list(df.columns), tablefmt="plain", numalign="left", stralign="left")
    open(fname, "w").write(content)
pd.DataFrame.to_fwf = to_fwf

root = os.path.dirname(os.path.realpath(__file__))

phases = {
    'TO': 'takeoff',
    'IC': 'initial_climb',
    'CL': 'climb',
    'CR': 'cruise',
    'DE': 'descent',
    'FA': 'final_approach',
    'LD': 'landing',
}

prop = {
    'to_v_lof':               'Liftoff speed'                               ,
    'to_d_tof':               'Takeoff distance'                            ,
    'to_acc_tof':             'Mean takeoff accelaration'                   ,
    'ic_va_avg':              'Mean airspeed'                               ,
    'ic_vs_avg':              'Mean vertical rate'                          ,
    'ic_va_std':              'Standard deviation of airspeed'              ,
    'ic_vs_std':              'Standard deviation of vertical rate '        ,
    'cl_d_range':             'Climb range'                                 ,
    'cl_v_cas_const':         'Constant CAS'                                ,
    'cl_v_mach_const':        'Constant Mach'                               ,
    'cl_h_cas_const':         'Constant CAS crossover altitude'             ,
    'cl_h_mach_const':        'Constant Mach crossover altitude'            ,
    'cl_vs_avg_pre_cas':      'Mean climb rate, pre-constant-CAS'           ,
    'cl_vs_avg_cas_const':    'Mean climb rate, constant-CAS'               ,
    'cl_vs_avg_mach_const':   'Mean climb rate, constant-Mach'              ,
    'cr_d_range':             'Cruise range'                                ,
    'cr_v_cas_mean':          'Mean cruise CAS'                             ,
    'cr_v_cas_max':           'Maximum cruise CAS'                          ,
    'cr_v_mach_mean':         'Mean cruise Mach'                            ,
    'cr_v_mach_max':          'Maximum cruise Mach'                         ,
    'cr_h_init':              'Initial cruise altitude'                     ,
    'cr_h_mean':              'Mean cruise altitude'                        ,
    'cr_h_max':               'Maximum cruise altitude'                     ,
    'de_d_range':             'Descent range'                               ,
    'de_v_mach_const':        'Constant Mach'                               ,
    'de_v_cas_const':         'Constant CAS'                                ,
    'de_h_cas_const':         'Constant CAS crossover altitude'             ,
    'de_h_mach_const':        'Constant Mach crossover altitude'            ,
    'de_vs_avg_cas_const':    'Mean descent rate, constant-CAS'             ,
    'de_vs_avg_mach_const':   'Mean descent rate, constant-Mach'            ,
    'de_vs_avg_after_cas':    'Mean descent rate, after-constant-CAS'       ,
    'fa_va_avg':              'Mean airspeed'                               ,
    'fa_vs_avg':              'Mean vertical rate'                          ,
    'fa_va_std':              'Standard deviation of airspeed'              ,
    'fa_vs_std':              'Standard deviation of vertical rate'         ,
    'fa_agl':                 'Approach angle'                              ,
    'ld_v_app':               'Touchdown speed'                             ,
    'ld_d_brk':               'Braking distance'                            ,
    'ld_acc_brk':             'Mean braking acceleration'                   ,
}


files = sorted(glob.glob('input/wrap/*.csv'))

for f in files:
    mdl = f[-8:-4]
    print(mdl)
    df = pd.read_csv(f)

    for i, r in df.iterrows():
        df.loc[i, 'phase'] = phases[r.phase]
        df.loc[i, 'note'] = prop[r.param]

    df = df[['param', 'phase', 'note', 'opt', 'min', 'max', 'model', 'pm']]
    df.columns = ['variable', 'flight phase', 'name', 'opt', 'min', 'max', 'model', 'parameters']

    df.to_fwf(root+'/../openap/data/wrap/%s.txt' % mdl)
