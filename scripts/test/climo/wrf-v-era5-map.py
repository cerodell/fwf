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


var_name = "fwi"
var = "S"


def add_proj(proj, ds):
    ds.attrs = proj.attrs
    for var in list(ds):
        ds[var].attrs = proj.attrs
    return ds


fwf_grid = salem.open_xr_dataset(str(data_dir) + "/static/static-vars-wrf-d02.nc")
era5_grid = salem.open_xr_dataset(
    str(data_dir) + "/static/static-vars-ecmwf-era5-land.nc"
)


wrf_ds = add_proj(
    fwf_grid,
    xr.open_zarr(f"/Volumes/WFRT-Ext22/ecmwf/era5-land/wrf-{var_name}-2021-2023.zarr"),
)
era5_ds = add_proj(
    era5_grid,
    xr.open_zarr(f"/Volumes/WFRT-Ext22/ecmwf/era5-land/era5-{var_name}-2021-2023.zarr"),
)  # .isel(expver =0).rename({'latitude': 'south_north' , 'longitude': 'west_east'})
# era5_ds[var] =era5_ds[var] *3.6

era5_ds = fwf_grid.salem.transform(era5_ds)


diff_ds = era5_ds - wrf_ds

# diff_ds[var].isel(month = 0).plot(bins = 500, xlim = (-10,10))

diff_ds.attrs = fwf_grid.attrs
for var in list(diff_ds):
    diff_ds[var].attrs = fwf_grid.attrs

vmin, vmax = -5, 5
fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(1, 1, 1)
month, hour = 6, 0
diff_ds[var].isel(month=month, hour=hour).salem.quick_map(
    vmin=vmin,
    vmax=vmax,
    cmap="coolwarm",
    extend="both",
    oceans=True,
    prov=True,
    states=True,
    ax=ax,
)
plt.savefig(str(data_dir) + f"/images/climo/{var_name}-month{month-1}-hour{hour}.png")

# mean_month = add_proj(fwf_grid, diff_ds.mean(dim = 'month'))
# fig = plt.figure(figsize=(12,6))
# ax = fig.add_subplot(1,1,1)
# mean_month[var].isel(hour = hour).salem.quick_map(vmin = vmin, vmax = vmax, cmap ='coolwarm', extend='both', oceans = True, prov = True, states =True, ax = ax)
# plt.savefig(str(data_dir) + f'/images/climo/{var_name}-monthALL-hour{hour}.png')

# mean_hour = add_proj(fwf_grid, diff_ds.mean(dim = 'hour'))
# fig = plt.figure(figsize=(12,6))
# ax = fig.add_subplot(1,1,1)
# mean_hour[var].isel(month = month).salem.quick_map(vmin = vmin, vmax = vmax, cmap ='coolwarm', extend='both', oceans = True, prov = True, lakes = True, states =True, ax = ax)
# plt.savefig(str(data_dir) + f'/images/climo/{var_name}-month{month}-hourALL.png')

mean_ds = add_proj(fwf_grid, diff_ds.mean(dim=["month", "hour"]))
fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(1, 1, 1)
mean_ds[var].salem.quick_map(
    vmin=vmin,
    vmax=vmax,
    cmap="coolwarm",
    extend="both",
    oceans=True,
    lakes=True,
    prov=True,
    states=True,
    ax=ax,
)
plt.savefig(
    str(data_dir) + f"/images/climo/{var_name}-monthALL-hourALL.png", transparent=True
)

# fig = plt.figure(figsize=(12,6))
# ax = fig.add_subplot(1,1,1)
# fwf_grid['HGT'].salem.quick_map(cmap = 'terrain', oceans = True, lakes = True, prov = True, states =True, ax = ax)
# plt.savefig(str(data_dir) + f'/images/climo/dem.png', transparent=True)

# wrf_F = wrf_F.where(era_F['F'].notnull().isel(time = 0).values)
# wrf_W = wrf_W.where(era_F['F'].notnull().isel(time = 0).values)

# wrf_WSP = wrf_W['W'].values.ravel()
# wrf_WSP = wrf_WSP[~np.isnan(wrf_WSP)]
# wrf_WSP = wrf_WSP[np.isfinite(wrf_WSP)]

# era_WSP = era_W['W'].values.ravel()
# era_WSP = era_WSP[~np.isnan(era_WSP)]
# era_WSP = era_WSP[np.isfinite(era_WSP)]


# fig = plt.figure(figsize=(8,6))
# ax = fig.add_subplot(1,1,1)
# sc = ax.hexbin(wrf_WSP, era_WSP, cmap = 'cubehelix_r')
# ax.axline((0, 0), slope=1, color = 'k', lw =0.5)
# ax.set_xlabel('WRF')
# ax.set_ylabel('ERA-Land')
# ax.set_title('Wind Speed')

# # Create color bar
# cbar = fig.colorbar(sc, ax=ax)
# cbar.set_label('Count')
