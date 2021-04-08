# Open Aircraft Performance Model (OpenAP) and Toolkit

This repository contains all OpenAP databases and a Python toolkit that facilitates data access and performance computation.

[OpenAP](https://github.com/junzis/openap) is a project actively maintained by [Junzi Sun](https://junzis.com/) from TU Delft. 

It is the continuation of his [PhD thesis work (between 2015 and 2019)](https://doi.org/10.4233/uuid:af94d535-1853-4a6c-8b3f-77c98a52346a). You can read more about OpenAP in [this article](https://www.mdpi.com/2226-4310/7/8/104).

Use the [discussion board](https://github.com/junzis/openap/discussions) to give your feedback/suggestions, and use [issue board](https://github.com/junzis/openap/issues) to report bugs.


## Install

To install latest version of OpenAP from the GitHub:

```sh
pip install --upgrade git+https://github.com/junzis/openap
```


## Databases:

  - Aircraft
  - Engines
  - Drag polar
  - Kinematic ([WRAP model](https://github.com/junzis/wrap))
  - Navigation


## Libraries

  - `prop`: aircraft and engine properties
  - `thrust`: model to compute aircraft thrust
  - `drag`: model to compute aircraft drag
  - `fuel`: model to compute fuel consumption
  - `kinematic`: a utility library to access WRAP data
  - `aero`: common aeronautical conversions
  - `nav`: model to access navigation information
  - `segment`: a utility library to determine climb, cruise, descent, level flight
  - `phase`: a wrapper around `segment`, providing identification of all flight phases
  - `traj`: package contains a set of tools related with trajectory generation


## Examples

### Get the aircraft and engine data

```python
from openap import prop

aircraft = prop.aircraft('A320')
engine = prop.engine('CFM56-5B4')
```

### Compute maximum aircraft engine thrust

```python
from openap import Thrust

thrust = Thrust(ac='A320', eng='CFM56-5B4')

T = thrust.takeoff(tas=100, alt=0)
T = thrust.climb(tas=200, alt=20000, roc=1000)
T = thrust.cruise(tas=230, alt=32000)
```

### Compute the aircraft drag

```python
from openap import Drag

drag = Drag(ac='A320')

D = drag.clean(mass=60000, tas=200, alt=20000, path_angle=5)
D = drag.nonclean(mass=60000, tas=150, alt=100, flap_angle=20,
                  path_angle=10, landing_gear=True)
```

### Compute aircraft fuel flow:

```python
from openap import FuelFlow

fuelflow = FuelFlow(ac='A320', eng='CFM56-5B4')

FF = fuelflow.at_thrust(acthr=50000, alt=30000)
FF = fuelflow.takeoff(tas=100, alt=0, throttle=1)
FF = fuelflow.enroute(mass=60000, tas=200, alt=20000, path_angle=3)
FF = fuelflow.enroute(mass=60000, tas=230, alt=32000, path_angle=0)
```

### Compute aircraft emissions:

```python
from openap import FuelFlow, Emission

fuelflow = FuelFlow(ac='A320', eng='CFM56-5B4')
emission = Emission(ac='A320', eng='CFM56-5B4')

TAS = 350
ALT = 30000

fuelflow = fuelflow.enroute(mass=60000, tas=TAS, alt=ALT)   # kg/s

CO2 = emission.co2(fuelflow)                    # g/s
H2O = emission.h2o(fuelflow)                    # g/s
NOx = emission.nox(fuelflow, tas=TAS, alt=ALT)  # g/s
CO = emission.co(fuelflow, tas=TAS, alt=ALT)    # g/s
HC = emission.hc(fuelflow, tas=TAS, alt=ALT)    # g/s
```


### Access WRAP (kinematic model) parameter:

```python
from openap import WRAP

wrap = WRAP(ac='A320')

param = wrap.takeoff_speed()
param = wrap.takeoff_distance()
param = wrap.takeoff_acceleration()
param = wrap.initclimb_vcas()
param = wrap.initclimb_vs()
param = wrap.climb_range()
param = wrap.climb_const_vcas()
param = wrap.climb_const_mach()
param = wrap.climb_cross_alt_concas()
param = wrap.climb_cross_alt_conmach()
param = wrap.climb_vs_pre_concas()
param = wrap.climb_vs_concas()
param = wrap.climb_vs_conmach()
param = wrap.cruise_range()
param = wrap.cruise_alt()
param = wrap.cruise_init_alt()
param = wrap.cruise_mach()
param = wrap.descent_range()
param = wrap.descent_const_mach()
param = wrap.descent_const_vcas()
param = wrap.descent_cross_alt_conmach()
param = wrap.descent_cross_alt_concas()
param = wrap.descent_vs_conmach()
param = wrap.descent_vs_concas()
param = wrap.descent_vs_post_concas()
param = wrap.finalapp_vcas()
param = wrap.finalapp_vs()
param = wrap.landing_speed()
param = wrap.landing_distance()
param = wrap.landing_acceleration()
```

### Generating trajectories


```python
from openap.traj import Generator

trajgen = Generator(ac='a320')

trajgen.enable_noise()   # enable Gaussian noise in trajectory data

data_cl = trajgen.climb(dt=10, random=True)  # using random paramerters
data_cl = trajgen.climb(dt=10, cas_const_cl=280, mach_const_cl=0.78, alt_cr=35000)

data_de = trajgen.descent(dt=10, random=True)
data_de = trajgen.descent(dt=10, cas_const_de=280, mach_const_de=0.78, alt_cr=35000)

data_cr = trajgen.cruise(dt=60, random=True)
data_cr = trajgen.cruise(dt=60, range_cr=2000, alt_cr=35000, m_cr=0.78)

data_all = trajgen.complete(dt=10, random=True)
data_all = trajgen.complete(dt=10, alt_cr=35000, m_cr=0.78,
                            cas_const_cl=260, cas_const_de=260)
```

### Identify flight phases

```python
import pandas as pd
from openap import FlightPhase

df = pd.read_csv('data/trajectory.csv')

ts = df['ts'].values    # timestamp, int, second
alt = df['alt'].values  # altitude, int, ft
spd = df['spd'].values  # speed, int, kts
roc = df['roc'].values  # vertical rate, int, ft/min

fp = FlightPhase()

fp.set_trajectory(ts, alt, spd, roc)

labels = fp.phaselabel()
```

# Citing OpenAP

```
@article{sun2020openap,
  title={OpenAP: An open-source aircraft performance model for air transportation studies and simulations},
  author={Sun, Junzi and Hoekstra, Jacco M and Ellerbroek, Joost},
  journal={Aerospace},
  volume={7},
  number={8},
  pages={104},
  year={2020},
  publisher={Multidisciplinary Digital Publishing Institute}
}
```
