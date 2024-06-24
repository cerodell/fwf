#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import context
import salem
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime


import matplotlib.pyplot as plt


from context import root_dir, data_dir


# fuels_wrf_d03 = salem.open_xr_dataset(str(data_dir) + '/fuel-load/fuels_wrf_d03.nc')
# fuels_wrf_d02 = salem.open_xr_dataset(str(data_dir) + '/fuel-load/fuels_wrf_d02.nc')


static_ds = salem.open_xr_dataset(str(data_dir) + "/static/static-rave-3km.nc")


def open_fuels(doi):
    fuel_dir = f"/Volumes/ThunderBay/CRodell/ecmwf/fuel-load/"
    fuels_ds = (
        salem.open_xr_dataset(
            fuel_dir
            + f'{doi.strftime("%Y")}/CFUEL_timemean_{doi.strftime("%Y")}_{doi.strftime("%m")}.nc'
        )
        .sel(lat=slice(90, 10), lon=slice(-180, -30))
        .chunk("auto")
    )
    fuels_ds.coords["time"] = pd.Timestamp(doi.strftime("%Y-%m"))
    return fuels_ds


# Create a date range from 2010 to 2020 for the month of June
date_range = pd.date_range(start="2021-01-01", end="2021-12-31", freq="ME")
# date_range = date_range[date_range.month == 6]

fuels_ds = xr.combine_nested([open_fuels(doi) for doi in date_range], concat_dim="time")

ds = fuels_ds.groupby("time.month").mean(dim="time")
for var in list(ds):
    ds[var].attrs = {"pyproj_srs": "+proj=longlat +datum=WGS84 +no_defs"}
ds.attrs = {"pyproj_srs": "+proj=longlat +datum=WGS84 +no_defs"}

ds_wrf = static_ds.salem.transform(ds, interp="spline")


ds_wrf = xr.where(static_ds["FUELS"] == 17, np.nan, ds_wrf)
for var in list(ds_wrf):
    ds_wrf[var] = xr.where(ds_wrf[var] < 0, 0, ds_wrf[var])

ds_wrf = ds_wrf.interpolate_na(
    dim="west_east", method="nearest", fill_value="extrapolate"
)
for var in list(ds_wrf):
    ds_wrf[var] = xr.where(ds_wrf[var] < 0, 0, ds_wrf[var])

ds_wrf = xr.where(static_ds["LAND"] == 1, 0, ds_wrf)
for var in list(ds_wrf):
    ds_wrf[var] = xr.where(ds_wrf[var] < 0, 0, ds_wrf[var])
    ds_wrf[var].attrs = static_ds.attrs
ds_wrf.attrs = static_ds.attrs

ds_wrf.to_netcdf(str(data_dir) + "/fuel-load/fuels_2021_rave_3km.nc", mode="w")


# test = fuels_wrf_d02 - ds_wrf
