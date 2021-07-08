from numpy import *
from casadi import *  # this override the previous

# numpy functions -> casadi functions
where = casadi.if_else
maximum = casadi.fmax
minimum = casadi.fmin
interp = lambda x, y: casadi.interpolant("LUT", "linear", [x], y)
