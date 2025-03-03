import numpy as np

from . import prop


def from_range(typecode, distance, load_factor=0.8, fraction=False, **kwargs):
    """Compute aircraft mass based on range, load factor, and fraction settings.

    This function calculates the aircraft mass considering fuel and payload weights
    based on the given flight distance and load factor.

    Args:
        typecode (str): ICAO aircraft type code (e.g. A320, B738)
        distance (float): Flight distance in nautical miles
        load_factor (float): Load factor between 0 and 1, default 0.8
        fraction (bool): If True, return mass fraction of MTOW, default False

    Returns:
        float: Aircraft mass in kg, or mass fraction if fraction=True

    """
    ac = prop.aircraft(typecode, **kwargs)

    range_fraction = distance / ac["cruise"]["range"]
    range_fraction = np.clip(range_fraction, 0.2, 1)

    max_fuel_weight = ac["mfc"] * 0.8025  # L->kg
    fuel_weight = range_fraction * max_fuel_weight

    payload_weight = (ac["mtow"] - max_fuel_weight - ac["oew"]) * load_factor

    mass = ac["oew"] + fuel_weight + payload_weight

    if fraction:
        return mass / ac["mtow"]
    else:
        return mass
