# Open Aircraft Performance Model (OpenAP) and Toolkit

This repository contains the OpenAP model data and Python packages for aircraft performance and emission calculations.

More information on the user guide and related articles at: [OpenAP.dev](https://openap.dev/)

## Install

Install the latest stable release from pypi:

```sh
pip install --upgrade openap
```

Install the latest stable release on conda-forge:

```sh
conda install openap
```

Install the development branch from GitHub (may not be stable):

```sh
pip install --upgrade git+https://github.com/junzis/openap
```

## Content

### Model data

Data in this repository includes:

- Aircraft data: Collected from open literature.
- Engines data: Primarily from the ICAO emission data-bank, including fuel flow and emissions.
- Drag polar model data: Exclusively derived from open data ([reference](https://research.tudelft.nl/files/71038050/published_OpenAP_drag_polar.pdf)).
- Fuel mode data: Polynomial models derived from the [acropole model](https://github.com/DGAC/Acropole) by [@JarryGabriel](https://github.com/JarryGabriel).
- Kinematic data: The kinematic model describes speed, altitude, and vertical rate ([reference](https://github.com/junzis/wrap)).
- Navigation data: Airport and waypoints obtained from [X-Plane](https://developer.x-plane.com/docs/data-development-documentation/).

### Python packages

The OpenAP Python library includes the following packages:

- `prop`: module for accessing aircraft and engine properties
- `thrust`: module for computing aircraft thrust
- `drag`: module for computing aircraft drag
- `fuel`: module for computing fuel consumption
- `emission`: module for computing aircraft emissions
- `kinematic`: module for accessing WRAP data
- `aero`: module for common aeronautical conversions
- `nav`: module for accessing navigation information
- `segment`: module for determining climb, cruise, descent, level flight
- `phase`: module providing identification of all flight phases
- `traj`: module contains a set of tools for trajectory generation

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
