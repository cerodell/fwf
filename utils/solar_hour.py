#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import salem
import numpy as np
import xarray as xr
import pandas as pd

import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from utils.fwx import FWX


from context import data_dir, root_dir


# startFWX  = datetime.now()
# trail = "obs"
# neurons = '16-8-adam-relu'
# keep_vars = ["FWI", "FFMC", "HFI", "LAI", "NDVI", "HGT", "GS", "dayofyear"]

# # Configuration dictionary for the RAVE and FWX models
# config = dict(
#     model="wrf",
#     trail_name="01",
#     method="hourly",
#     date_range=pd.date_range("2023-06-06", "2023-06-06", freq="h"),
#     domain="d02",
# )

# fwx = FWX(config=config)
# fwx_roi = fwx.open_fwx(var_list=["S", "F", "HFI"])
# static_roi = salem.open_xr_dataset(
#     str(data_dir) + f'/static/static-vars-wrf-{config["domain"]}.nc'
# ).expand_dims("time")

# shape = fwx_roi["F"].shape
# times = fwx_roi["time"].values


# # Example usage
# longitudes = fwx_roi['XLONG'].values
# datetime_utc = times[21]


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
        domain_dims = ("time", "south_north", "west_east")
        fire_ds["solar_hour"] = (
            domain_dims,
            np.stack([solve_solar_hour(t, longitudes) for t in times]),
        )
    except:
        longitudes = fire_ds.salem.grid.ll_coordinates[0]
        domain_dims = ("time", "y", "x")
        fire_ds["solar_hour"] = (
            domain_dims,
            np.stack([solve_solar_hour(t, longitudes) for t in times]),
        )

    shape = longitudes.shape

    df_curve = pd.read_csv(str(data_dir) + "/frp/FRP_diurnal_climatology.csv")
    df_curve.columns = [
        "Land Cover",
        "Ecoregion",
        "hh00",
        "hh01",
        "hh02",
        "hh03",
        "hh04",
        "hh05",
        "hh06",
        "hh07",
        "hh08",
        "hh09",
        "hh10",
        "hh11",
        "hh12",
        "hh13",
        "hh14",
        "hh15",
        "hh16",
        "hh17",
        "hh18",
        "hh19",
        "hh20",
        "hh21",
        "hh22",
        "hh23",
    ]
    df_curve = (
        df_curve.drop(0)
        .drop(columns=["Land Cover", "Ecoregion"])
        .dropna()
        .reset_index(drop=True)
        .astype(float)
    )
    df_curve = df_curve.mean()
    curve_array = df_curve.values
    curve_values = []
    for i in range(len(fire_ds.time)):
        curve_values.append(
            curve_array[fire_ds["solar_hour"].isel(time=i).values.astype(int) - 1]
        )
    fire_ds["diurnal_curve"] = (domain_dims, np.stack(curve_values))
    return fire_ds
