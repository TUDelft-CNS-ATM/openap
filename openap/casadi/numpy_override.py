from numpy import *
from casadi import *  # this override the previous

# numpy functions -> casadi functions
abs = casadi.fabs
where = casadi.if_else
maximum = casadi.fmax
minimum = casadi.fmin
interp = lambda x, xp, yp: casadi.interpolant("LUT", "linear", [xp], yp)(x)
