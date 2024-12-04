# OpenAP: Open Aircraft Performance Model and Toolkit

This repository contains the OpenAP model data and Python packages for aircraft performance and emission calculations.

## 🕮 User Guide

The OpenAP handbook is available at [openap.dev](https://openap.dev/).

## Installation

Install the latest stable release from PyPI:

```sh
pip install --upgrade openap
```

Install the development branch from GitHub (may not be stable):

```sh
pip install --upgrade git+https://github.com/junzis/openap
```

## Content

### Model Data

Data in this repository includes:

- Aircraft data: Collected from open literature.
- Engine data: Primarily from the ICAO emission data-bank, including fuel flow and emissions.
- Drag polar model data: Exclusively derived from open data ([reference](https://research.tudelft.nl/files/71038050/published_OpenAP_drag_polar.pdf)).
- Fuel model data: Polynomial models derived from the [acropole model](https://github.com/DGAC/Acropole) by [@JarryGabriel](https://github.com/JarryGabriel).
- Kinematic data: The kinematic model describes speed, altitude, and vertical rate ([reference](https://github.com/junzis/wrap)).
- Navigation data: Airport and waypoints obtained from [X-Plane](https://developer.x-plane.com/docs/data-development-documentation/).

### Python Packages

The OpenAP Python library includes the following packages:

- `prop`: Module for accessing aircraft and engine properties.
- `aero`: Module for common aeronautical conversions.
- `nav`: Module for accessing navigation information.
- `thrust`: Module provides `Thrust()` class for computing aircraft thrust.
- `drag`: Module provides `Drag()` class for computing aircraft drag.
- `fuel`: Module provides `FuelFlow()` class for computing fuel consumption.
- `emission`: Module provides `Emission()` class for computing aircraft emissions.
- `kinematic`: Module provides `WRAP()` class for accessing kinematic performance data.
- `phase`: Module provides `FlightPhase()` class for determining flight phases.
- `gen`: Module provides `FlightGenerator()` class for trajectory generation.

Examples:

```python
import openap

openap.prop.aircraft("A320")
fuelflow = openap.FuelFlow("A320")
fuelflow.enroute(mass, tas, alt) # -> kg/s
```

The input parameters can be scalar, list, or ndarray. Most of the OpenAP methods' parameters are in aeronautical units, such as knots, feet, feet/min. The mass is always in SI units, i.e., kilograms.

### Add-ons

The OpenAP library can also be used to interact with BADA performance models if you have access to the BADA data from EUROCONTROL. You can use the following code:

```python
from openap.addon import bada4

fuelflow = bada4.FuelFlow()
```

The methods and attributes of `openap.addon.bada4.FuelFlow()` are the same as those of `openap.FuelFlow()`.

## Symbolic Implementation for CasADi

The OpenAP model can also be used with the CasADi library for symbolic computations. The symbolic model is available in the `openap.casadi` package. For example, you can use the following code to create a symbolic model for fuel flow:

```python
from openap.casadi import FuelFlow

fuelflow = FuelFlow()
```

All the methods of `openap.casadi.FuelFlow()` are the same as those of `openap.FuelFlow()`, and they are now symbolic functions that can be used to compute fuel flow for given flight conditions in CasADi `DM`, `SX`, or `MX` types.

How did we implement this? When the `casadi` module is initiated, a metaclass is used to replace the `sci` function from `numpy`, which overrides all the `numpy` functions with `casadi` functions. For more details, check the `openap/casadi/__init__.py` code.

## Citing OpenAP

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
