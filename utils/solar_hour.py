#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import salem
import numpy as np
import xarray as xr
import pandas as pd

import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from context import data_dir, root_dir


# Functions to calculate B, E, and declination (delta)
def B(n):
    return (n - 1) * 360 / 365


def E(n):
    B_rad = np.radians(B(n))
    return 229.2 * (
        0.000075
        + 0.001868 * np.cos(B_rad)
        - 0.032077 * np.sin(B_rad)
        + 0.014615 * np.cos(2 * B_rad)
        - 0.04089 * np.sin(2 * B_rad)
    )


def delta(n):
    return 23.45 * np.sin(np.radians(360 * (284 + n) / 365))


def solve_solar_hour(datetime_utc, longitudes):
    # Compute day of the year for the given datetime
    date_of_interest = datetime_utc.astype("datetime64[D]")
    year_start = np.datetime64(f'{date_of_interest.astype("datetime64[Y]")}-01-01')
    day_of_year = (date_of_interest - year_start).astype(int) + 1

    # declination = delta(day_of_year)
    equation_of_time = E(day_of_year)

    # Calculate solar time for the whole array at once
    time_correction = 4 * longitudes + equation_of_time  # Time correction in minutes
    true_solar_times = datetime_utc + np.array(
        np.round(time_correction), dtype="timedelta64[m]"
    )  # Add correction

    # Extract hours and minutes to calculate solar hour as a decimal
    return (
        true_solar_times.astype("datetime64[h]").astype(int) % 24
        + (
            true_solar_times.astype("datetime64[m]")
            - true_solar_times.astype("datetime64[h]")
        ).astype(int)
        / 60.0
    )


def get_solar_hours(fire_ds):
    times = fire_ds["time"].values
    try:
        longitudes = fire_ds["XLONG"].values
        fire_ds["solar_hour"] = (
            ("time", "south_north", "west_east"),
            np.stack([solve_solar_hour(t, longitudes) for t in times]),
        )
    except:
        longitudes = fire_ds.salem.grid.ll_coordinates[0]
        fire_ds["solar_hour"] = (
            ("time", "y", "x"),
            np.stack([solve_solar_hour(t, longitudes) for t in times]),
        )
    return fire_ds
