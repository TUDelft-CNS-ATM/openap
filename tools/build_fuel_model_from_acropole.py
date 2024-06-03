# %%
import warnings
from glob import glob

import click
import matplotlib.pyplot as plt
import numpy as np
import openap
import pandas as pd
from acropole import FuelEstimator
from scipy.optimize import curve_fit
from tqdm.autonotebook import tqdm
from traffic.core import Flight, Traffic

pd.options.display.max_columns = 100

fe = FuelEstimator()


def func(ratio, coef):
    return -coef * (ratio - 1) ** 2 + coef


# %%
acropole_aircraft = pd.read_csv("acropole_aircraft_params.csv")


def gen_fuel_model(typecode, engine_type, wave_drag=False, show_plot=False):

    if typecode.lower() not in openap.prop.available_aircraft():
        warnings.warn(f"{typecode} not in openap")
        return None

    aac = acropole_aircraft.query(f"ACFT_ICAO_TYPE=='{typecode.upper()}'")
    if aac.shape[0] == 0:
        warnings.warn(f"{typecode} not in acropole")
        return None

    engine_type = aac.ENGINE_ICAO.iloc[0]

    print(typecode, engine_type)

    files = np.random.permutation(
        glob("/mnt/md16/data/openap-rebuild/2022/full_flights/*.parquet")
    )

    t_type = None

    for i, f in tqdm(enumerate(files), desc="reading files"):
        t = Traffic.from_file(f)

        if t_type is not None:
            t_type = t.query(f"typecode=='{typecode.lower()}'") + t_type
        else:
            t_type = t.query(f"typecode=='{typecode.lower()}'")

        if t_type is not None and len(t_type.flight_ids) > 500:
            t_type = t_type.sample(500)
            break

        if t_type is None and i > 1:
            break

    if t_type is None:
        warnings.warn(f"{typecode} no flight data available")
        return None

    ac = openap.prop.aircraft(typecode)

    eng = openap.prop.engine(ac["engine"]["default"])

    drag = openap.Drag(typecode, wave_drag=wave_drag, use_synonym=True)
    thrust = openap.Thrust(typecode, use_synonym=True)

    results = []

    for flight in tqdm(t_type):

        mass = np.random.uniform(
            ac["limits"]["MTOW"] * 0.7, ac["limits"]["MTOW"] * 0.95
        )

        df = flight.resample("4s").data.assign(
            typecode=typecode.upper(),
            second=lambda d: (d.timestamp - d.timestamp.iloc[0]).dt.total_seconds(),
            v=lambda d: d.groundspeed * openap.aero.kts,
            trk=lambda d: np.radians(d.track),
            vgx=lambda d: d.v * np.sin(d.trk),
            vgy=lambda d: d.v * np.cos(d.trk),
            vax=lambda d: d.vgx - d.u_component_of_wind,
            vay=lambda d: d.vgy - d.v_component_of_wind,
            tas=lambda d: np.sqrt(d.vax**2 + d.vay**2) / openap.aero.kts,
        )

        df = fe.estimate(
            df,
            timestamp="second",
            airspeed="tas",
        )

        # plt.plot(flight_fuel.second, flight_fuel.fuel_flow)
        # plt.show()

        D = drag.clean(
            mass=mass,
            tas=df.tas,
            alt=df.altitude,
            vs=df.vertical_rate,
        )

        T = D + mass * 9.81 * np.sin(
            np.arctan2(
                df.vertical_rate * openap.aero.fpm,
                df.tas * openap.aero.kts,
            )
        )

        T0 = eng["max_thrust"] * ac["engine"]["number"]

        T_idle = thrust.descent_idle(tas=df.tas, alt=df.altitude)
        T_max = thrust.climb(alt=df.altitude, tas=df.tas, roc=df.vertical_rate)
        T[T < T_idle] = T_idle
        T[T > T_max] = T_max

        thrust_ratio = T / T0

        df = df.assign(thrust_ratio=thrust_ratio).query("0<thrust_ratio<1")

        results.append(df)

    df_all = (
        pd.concat(results, ignore_index=True)
        .query("thrust_ratio<1")
        .round(3)
        .drop_duplicates(subset=["thrust_ratio", "fuel_flow"])
    )

    thrust_ratio = df_all.thrust_ratio
    fuel_flow = df_all.fuel_flow

    popt, pcov = curve_fit(func, thrust_ratio, fuel_flow, bounds=(0, np.inf))
    print(typecode, engine_type, popt)

    if show_plot:
        plt.figure(figsize=(6, 4))
        plt.scatter(thrust_ratio, fuel_flow, alpha=0.1, s=5)
        x = np.linspace(0, 1, 100)
        plt.plot(x, func(x, *popt), "r-", label=f"fit: {popt}")
        plt.suptitle(typecode)
        plt.legend()
        plt.show()

    return typecode, engine_type, popt[0]


# %%

# gen_fuel_model("A320", None, wave_drag=True, show_plot=True)

# %%


@click.command()
@click.option("--typecode", default=None)
def main(typecode):

    if typecode is not None:
        params = gen_fuel_model(typecode, None, show_plot=True)
        print(params)

    else:
        typecodes = acropole_aircraft.ACFT_ICAO_TYPE.unique()

        results = []
        for typecode in typecodes:
            res = gen_fuel_model(typecode, None, show_plot=False)
            if res is not None:
                results.append(res)

        df = pd.DataFrame(results, columns=["typecode", "engine_type", "coef"])
        df.to_csv("fuel_models.csv", index=False)


if __name__ == "__main__":
    main()
