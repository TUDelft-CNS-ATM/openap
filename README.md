Open Aircraft Performance Model (OpenAP) Toolkit
========================================================================

This repository contains all OpenAP databases and a Python implementation which facilitates the data access and aircraft performance computation.

Databases:
---------

  - Aircraft
  - Engines
  - Drag polar
  - Kinematic ([WRAP](https://github.com/junzis/wrap))
  - Navigation

Libraries
---------

  - `prop`: aircraft and engine properties
  - `thrust`: model to compute aircraft thrust
  - `drag`: model to compute aircraft drag
  - `fuel`: model to compute fuel consumption
  - `kinematic`: a utility library to access WRAP data
  - `aero`: common aeronautical conversions
  - `nav`: model to access navigation information
  - `segment`: a utility library to determine climb, cruise, descent, level flight
  - `phase`: a wrapper around `segment`, providing identification of all flight phases

Examples
--------

Get the aircraft and engine data:

```python
from openap import prop

prop.aircraft('A320')
prop.engine('CFM56-5B4')
```

Compute maximum aircraft engine thrust:

```python
from openap import Thrust

thrust = Thrust(ac='A320', eng='CFM56-5B4')

thrust.takeoff(tas=100, alt=0)
thrust.climb(tas=200, alt=20000, roc=1000)
thrust.cruise(tas=230, alt=32000)
```

Compute the aircraft drag:

```python
from openap import Drag

drag = Drag(ac='A320')

drag.clean(mass=60000, tas=200, alt=20000, path_angle=5)
drag.initclimb(mass=60000, tas=150, alt=1000, path_angle=10)
drag.approach(mass=50000, tas=150, alt=1000, path_angle=-10)
```

Compute the fuel flow:

```python
from openap import FuelFlow

ff = FuelFlow(ac='A320', eng='CFM56-5B4')

ff.at_thrust(thr=50000)
ff.takeoff(tas=100, alt=0, throttle=1)
ff.enroute(mass=60000, tas=200, alt=20000, path_angle=3)
ff.enroute(mass=60000, tas=230, alt=32000, path_angle=0)
```

Accessing the WRAP parameters:

```python
from openap import WRAP

wrap = WRAP(ac='A320')

wrap.takeoff_distance()
wrap.takeoff_acceleration()
wrap.initclimb_cas()
wrap.initclimb_vs()
wrap.climb_range()
wrap.climb_vs_pre_const_cas()
wrap.climb_const_cas()
wrap.climb_alt_cross_const_cas()
wrap.climb_vs_const_cas()
wrap.climb_const_mach()
wrap.climb_alt_cross_const_mach()
wrap.climb_vs_const_mach()
wrap.cruise_range()
wrap.cruise_alt()
wrap.cruise_init_alt()
wrap.cruise_mach()
wrap.descent_range()
wrap.descent_const_mach()
wrap.descent_alt_cross_const_mach()
wrap.descent_const_cas()
wrap.descent_alt_cross_const_cas()
wrap.descent_vs_const_cas()
wrap.descent_vs_const_mach()
wrap.descent_vs_post_const_cas()
wrap.finalapp_cas()
wrap.finalapp_vs()
wrap.landing_speed()
wrap.landing_distance()
wrap.landing_acceleration()
```
