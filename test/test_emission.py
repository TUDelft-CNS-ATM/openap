import numpy as np
import matplotlib.pyplot as plt
from openap import Emission, FuelFlow, prop
from mpl_toolkits.mplot3d import Axes3D

ac = "A320"

aircraft = prop.aircraft(ac)
fuelflow = FuelFlow(ac=ac)
emission = Emission(ac=ac)


tas = np.linspace(50, 500, 50)
alt = np.linspace(100, 35000, 50)
tas_, alt_ = np.meshgrid(tas, alt)
mass = aircraft["limits"]["MTOW"] * 0.85


ff = fuelflow.enroute(mass=mass, tas=tas_, alt=alt_, path_angle=0)

co2 = emission.co2(ff)
h2o = emission.h2o(ff)
sox = emission.sox(ff)
nox = emission.nox(ff, tas=tas_, alt=alt_)
co = emission.co(ff, tas=tas_, alt=alt_)
hc = emission.hc(ff, tas=tas_, alt=alt_)

fig = plt.figure()
ax = fig.gca(projection="3d")
surf = ax.plot_surface(tas_, alt_, ff)
plt.title("fuel flow (kg/s)")
plt.xlabel("TAS (kt)")
plt.ylabel("Altitude (ft)")
plt.show()

fig = plt.figure()
ax = fig.gca(projection="3d")
surf = ax.plot_surface(tas_, alt_, h2o)
plt.title("H2O (g/s)")
plt.xlabel("TAS (kt)")
plt.ylabel("Altitude (ft)")
plt.show()

fig = plt.figure()
ax = fig.gca(projection="3d")
surf = ax.plot_surface(tas_, alt_, co2)
plt.title("CO2 (kg/s)")
plt.xlabel("TAS (kt)")
plt.ylabel("Altitude (ft)")
plt.show()

fig = plt.figure()
ax = fig.gca(projection="3d")
surf = ax.plot_surface(tas_, alt_, sox)
plt.title("SOx (g/s)")
plt.xlabel("TAS (kt)")
plt.ylabel("Altitude (ft)")
plt.show()

fig = plt.figure()
ax = fig.gca(projection="3d")
surf = ax.plot_surface(tas_, alt_, nox)
plt.title("NOx (g/s)")
plt.xlabel("TAS (kt)")
plt.ylabel("Altitude (ft)")
plt.show()

fig = plt.figure()
ax = fig.gca(projection="3d")
surf = ax.plot_surface(tas_, alt_, co)
plt.title("CO (g/s)")
plt.xlabel("TAS (kt)")
plt.ylabel("Altitude (ft)")
plt.show()

fig = plt.figure()
ax = fig.gca(projection="3d")
surf = ax.plot_surface(tas_, alt_, hc)
plt.title("HC (g/s)")
plt.xlabel("TAS (kt)")
plt.ylabel("Altitude (ft)")
plt.show()
