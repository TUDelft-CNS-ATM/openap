# %%
import warnings
from glob import glob

import click
from acropole import FuelEstimator
from tqdm.autonotebook import tqdm
from traffic.core import Flight, Traffic

import numpy as np
import openap
import pandas as pd

# %%
acropole_aircraft = pd.read_csv("acropole_aircraft_params.csv")

fe = FuelEstimator()

# %%


def get_flights(typecode, folder, number):
    aac = acropole_aircraft.query(f"ACFT_ICAO_TYPE=='{typecode.upper()}'")
    if aac.shape[0] == 0:
        warnings.warn(f"{typecode} not in acropole")
        return None

    engine_type = aac.ENGINE_ICAO.iloc[0]

    print(typecode, engine_type)

    files = np.random.permutation(glob(f"{folder}/*.parquet"))

    t_extracted = None

    for i, f in tqdm(
        enumerate(files), desc=f"reading parquet files to get {number} flights"
    ):
        t = Traffic.from_file(f)

        if t_extracted is not None:
            t_extracted = t.query(f"typecode=='{typecode.lower()}'") + t_extracted
        else:
            t_extracted = t.query(f"typecode=='{typecode.lower()}'")

        if t_extracted is not None and len(t_extracted.flight_ids) > number:
            # more than enough flights, randomly sample
            t_extracted = t_extracted.sample(number)
            break

        if t_extracted is None and i > 1:
            # type not found in day one
            break

    if t_extracted is None:
        warnings.warn(f"{typecode} no flight data available")
        return None

    results = []

    for flight in tqdm(t_extracted):
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
            second="second",
            airspeed="tas",
        )

        results.append(df)

    return pd.concat(results, ignore_index=True)


@click.command()
@click.option("--typecode", required=True, help="typecode to extract")
@click.option("--folder", required=True, help="path to the input parquet files")
@click.option("--number", required=True, type=int, help="Number of flights to extract")
def main(typecode, folder, number):
    flights = get_flights(typecode, folder, number)
    flights.to_parquet(f"{typecode}_{number}.parquet", index=False)


if __name__ == "__main__":
    main()
