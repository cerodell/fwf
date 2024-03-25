#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import salem
import json
import math
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
import geopandas as gpd

import matplotlib.pyplot as plt
import cartopy.crs as crs
import cartopy.feature as cfeature
import matplotlib.colors
import zarr

from datetime import datetime, timedelta

from context import data_dir, root_dir
from utils.frp import build_tree
from utils.geoutils import get_pyproj_loc
from utils.open import read_dataset
from dask.distributed import LocalCluster, Client

plt.rcParams["text.usetex"] = False
runTime = datetime.now()


month = 6
hour = 0
var_name = "fwi"
var = "S"
var_title = "Fire Weather Index"


def add_proj(proj, ds):
    ds.attrs = proj.attrs
    for var in list(ds):
        ds[var].attrs = proj.attrs
    return ds


wrf_grid = salem.open_xr_dataset(str(data_dir) + "/static/static-vars-wrf-d02.nc")
era5_grid = salem.open_xr_dataset(
    str(data_dir) + "/static/static-vars-ecmwf-era5-land.nc"
)


wrf_ds = add_proj(
    wrf_grid,
    xr.open_zarr(f"/Volumes/WFRT-Ext22/ecmwf/era5-land/wrf-{var_name}-2021-2023.zarr"),
).isel(month=month, hour=hour)
era5_ds = add_proj(
    era5_grid,
    xr.open_zarr(f"/Volumes/WFRT-Ext22/ecmwf/era5-land/era5-{var_name}-2021-2023.zarr"),
).isel(month=month, hour=hour)
try:
    era5_ds = era5_ds.isel(expver=0).rename(
        {"latitude": "south_north", "longitude": "west_east"}
    )
except:
    pass
if var == "W":
    era5_ds[var] = era5_ds[var] * 3.6

era5_ds = wrf_grid.salem.transform(era5_ds)

wrf_ds = wrf_ds.where(era5_ds[var].notnull().values)
wrf_grid = wrf_grid.where(era5_ds[var].notnull().values)


wrf_array = wrf_ds[var].values.ravel()
wrf_array = wrf_array[~np.isnan(wrf_array)]
wrf_array = wrf_array[np.isfinite(wrf_array)]

dem_array = wrf_grid["HGT"].values.ravel()
dem_array = dem_array[~np.isnan(dem_array)]
dem_array = dem_array[np.isfinite(dem_array)]

era5_array = era5_ds[var].values.ravel()
era5_array = era5_array[~np.isnan(era5_array)]
era5_array = era5_array[np.isfinite(era5_array)]


def get_month_name(month_number):
    return pd.Timestamp(month=int(month_number), year=2020, day=1).strftime("%B")


fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(1, 1, 1)
sc = ax.scatter(wrf_array, era5_array, c=dem_array, cmap="terrain")
ax.axline((0, 0), slope=1, color="k", lw=0.5)
ax.set_xlabel("WRF")
ax.set_ylabel("ERA-Land")
num_str = "{:02d}".format(hour)
ax.set_title(
    f"{var_title} at {num_str}Z {get_month_name(era5_ds.month.values)}  \n Averaged over 2021-2023"
)
# Create color bar
cbar = fig.colorbar(sc, ax=ax)
cbar.set_label("Elevation")
plt.savefig(
    str(data_dir) + f"/images/climo/scatter-{var_name}-month{month}-hour{hour}.png"
)
