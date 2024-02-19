# %%
import numpy as np
from scipy import optimize

# %%
gas_constant_water_vapor = 461.51
gas_constant_dry_air = 287.05
temperature_steam = 372.15
pressure_steam = 101325
temperature_ice_point = 273.16
pressure_ice_point = 611.73

ei_water = 1.2232
spec_air_heat_capacity = 1004
ratio_mass_water_vapor_air = 0.622
spec_combustion_heat = 43e6
propulsion_efficiency = 0.4  # variable


def saturation_pressure_over_water(temperature):
    # Murphy and Koop 2005
    return np.exp(
        54.842763
        - 6763.22 / temperature
        - 4.210 * np.log(temperature)
        + 0.000367 * temperature
        + np.tanh(0.0415 * (temperature - 218.8))
        * (
            53.878
            - 1331.22 / temperature
            - 9.44523 * np.log(temperature)
            + 0.014025 * temperature
        )
    )


def saturation_pressure_over_ice(temperature):
    # Murphy and Koop 2005
    return np.exp(
        9.550426
        - 5723.265 / temperature
        + 3.53068 * np.log(temperature)
        - 0.00728332 * temperature
    )


def relative_humidity(specific_humidity, pressure, temperature, to="ice"):
    assert to in ("ice", "water")

    if to == "ice":
        saturation_pressure = saturation_pressure_over_ice(temperature)
    else:
        saturation_pressure = saturation_pressure_over_water(temperature)

    return (
        specific_humidity
        * pressure
        * (gas_constant_water_vapor / gas_constant_dry_air)
        / saturation_pressure
    )


def critical_temperature_water(pressure):
    isobaric_mixing_slope = (
        ei_water
        * spec_air_heat_capacity
        * pressure
        / (
            ratio_mass_water_vapor_air
            * spec_combustion_heat
            * (1 - propulsion_efficiency)
        )
    )

    crit_temp_water = (
        -46.46
        + 9.43 * np.log(isobaric_mixing_slope - 0.053)
        + 0.72 * (np.log(isobaric_mixing_slope - 0.053)) ** 2
        + 273.15
    )

    return crit_temp_water


def critical_temperature_water_and_ice(pressure):
    def func(temp_critical, crit_temp_water, isobaric_mixing_slope):
        return (
            saturation_pressure_over_water(crit_temp_water)
            - saturation_pressure_over_ice(temp_critical)
            - (crit_temp_water - temp_critical) * isobaric_mixing_slope
        )

    isobaric_mixing_slope = (
        ei_water
        * spec_air_heat_capacity
        * pressure
        / (
            ratio_mass_water_vapor_air
            * spec_combustion_heat
            * (1 - propulsion_efficiency)
        )
    )

    crit_temp_water = (
        -46.46
        + 9.43 * np.log(isobaric_mixing_slope - 0.053)
        + 0.72 * (np.log(isobaric_mixing_slope - 0.053)) ** 2
        + 273.15
    )

    sol = optimize.root_scalar(
        func,
        args=(crit_temp_water, isobaric_mixing_slope),
        bracket=[100, crit_temp_water],
        method="brentq",
    )
    # print(sol.root, sol.iterations, sol.function_calls)
    crit_temp_ice = sol.root

    return crit_temp_water, crit_temp_ice
