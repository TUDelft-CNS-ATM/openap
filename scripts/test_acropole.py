# %%

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from acropole import FuelEstimator
from scipy.optimize import curve_fit
from tqdm.autonotebook import tqdm

import numpy as np
import openap
import pandas as pd

pd.options.display.max_columns = 100

# matplotlib.use("WebAgg")

# %%
fe = FuelEstimator()

# %%
typecode = "A320"

alt = np.arange(1000, 40000, 500)
tas = np.arange(0, 500, 10)
vs = np.arange(-3000, 3000, 500)

altitude, speed, vertical_rate = np.meshgrid(alt, tas, vs)

flight = pd.DataFrame(
    {
        "groundspeed": speed.flatten(),
        "altitude": altitude.flatten(),
        "vertical_rate": vertical_rate.flatten(),
    }
).assign(typecode="A320")

# %%
flight_fuel = fe.estimate(flight)


# %%
# sns.lineplot(
#     data=flight_fuel.query("vertical_rate == 0"),
#     x="groundspeed",
#     y="fuel_flow",
#     hue="altitude",
# )
# %%

flight_ = flight_fuel.query("vertical_rate == 0")
speed_, altitude_ = np.meshgrid(tas, alt)
fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))
surf = ax.plot_surface(
    altitude_,
    speed_,
    flight_.fuel_flow.values.reshape(len(alt), len(tas)),
    cmap="viridis",
)
plt.show()


# %%

ac = openap.prop.aircraft("A320")
ac

eng = openap.prop.engine(ac["engine"]["default"])
eng

# %%

alt = np.arange(1000, 40000, 100)
tas = np.arange(0, 500, 10)

altitude, speed = np.meshgrid(alt, tas)

mass = 70000

drag = openap.Drag("A320")
thrust = openap.Thrust("A320")
D = drag.clean(mass=mass, tas=speed, alt=altitude, vs=0)
T = D
thrust_max = thrust.takeoff(tas=speed, alt=altitude)

CL = (
    mass
    * 9.81
    / (
        0.5
        * openap.aero.density(altitude * openap.aero.ft)
        * (speed * openap.aero.kts) ** 2
        * ac["wing"]["area"]
    )
)

flight = pd.DataFrame(
    {
        "groundspeed": speed.flatten(),
        "altitude": altitude.flatten(),
        "drag": D.flatten(),
        "CL": CL.flatten(),
        "thrust": T.flatten(),
        "thrust_max": thrust_max.flatten(),
    }
).assign(typecode="A320", vertical_rate=0)

flight = flight.query("thrust<thrust_max*2 and CL<1.3")

flight

# %%
flight_fuel = fe.estimate(flight).query("fuel_flow==fuel_flow")
flight_fuel
# %%

flight = pd.read_csv("../test/data/flight_a320.csv").query("ALTI_STD_FT>500")
flight.head()

# %%
mass = flight.MASS_KG
speed = flight.TRUE_AIR_SPD_KT
altitude = flight.ALTI_STD_FT
vertical_rate = flight.VERT_SPD_FTMN
fuelflow = flight.FUEL_FLOW_KGH * 2 / 3600

drag = openap.Drag("A320")
thrust = openap.Thrust("A320")
ff = openap.FuelFlow("A320")

D = drag.clean(mass=mass, tas=speed, alt=altitude, vs=vertical_rate)
T = D + mass * 9.81 * np.sin(
    np.arctan2(vertical_rate * openap.aero.fpm, speed * openap.aero.kts)
)

T_idle = thrust.descent_idle(tas=speed, alt=altitude)
T[T < T_idle] = T_idle

thrust_max = thrust.takeoff(tas=speed, alt=altitude)
ff_estimate = ff.enroute(mass=mass, tas=speed, alt=altitude, vs=vertical_rate)

plt.plot(
    flight.FLIGHT_TIME,
    flight.FUEL_FLOW_KGH * 2,
    lw=1,
    label="actual (kg/h)",
)
plt.plot(
    flight.FLIGHT_TIME,
    ff_estimate * 3600,
    alpha=0.8,
    lw=1,
    label="estimate (kg/h)",
)
plt.legend()

# %%


def func(ratio, a, b):
    return -a * (ratio - b) ** 2 + a * b**2


ratio = T / (eng["max_thrust"] * ac["engine"]["number"])

popt, pcov = curve_fit(func, ratio, fuelflow, bounds=((0, 1), (np.inf, np.inf)))
print(popt)

plt.plot(ratio, fuelflow, "b.")

x = np.linspace(0, 1, 100)
plt.plot(x, func(x, *popt), "r-")

ff2 = eng["fuel_c3"] * x**3 + eng["fuel_c2"] * x**2 + eng["fuel_c1"] * x
plt.plot(x, ff2, "g-")

plt.show()

# %%


plt.plot(
    flight.FLIGHT_TIME,
    flight.FUEL_FLOW_KGH * 2,
    lw=1,
    label="actual (kg/h)",
)
plt.plot(
    flight.FLIGHT_TIME,
    func(ratio, *popt) * 3600,
    alpha=0.8,
    lw=1,
    label="estimate (kg/h)",
)
plt.legend()
plt.show()
