import numpy as np
import matplotlib.pyplot as plt
from openap.emission import Emission, FuelFlow
from mpl_toolkits.mplot3d import Axes3D

ac = "A320"

fuel = FuelFlow(ac=ac)

tas = np.linspace(50, 500, 50)
alt = np.linspace(100, 35000, 50)
tas_, alt_ = np.meshgrid(tas, alt)


ff = fuel.enroute(mass=60000, tas=tas_, alt=alt_, path_angle=0)

em = Emission(ac=ac)

co2 = em.co2(ff)
h2o = em.h2o(ff)

fig = plt.figure()
ax = fig.gca(projection="3d")
surf = ax.plot_surface(tas_, alt_, ff)
plt.show()


nox = em.nox(ff, tas=tas_, alt=alt_)
fig = plt.figure()
ax = fig.gca(projection="3d")
surf = ax.plot_surface(tas_, alt_, nox)
plt.show()

co = em.co(ff, tas=tas_, alt=alt_)
fig = plt.figure()
ax = fig.gca(projection="3d")
surf = ax.plot_surface(tas_, alt_, co)
plt.show()

hc = em.hc(ff, tas=tas_, alt=alt_)
fig = plt.figure()
ax = fig.gca(projection="3d")
surf = ax.plot_surface(tas_, alt_, hc)
plt.show()
