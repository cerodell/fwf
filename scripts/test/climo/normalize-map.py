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

from datetime import datetime, timedelta
from pylab import *

from context import data_dir, root_dir
from utils.geoutils import make_KDtree

plt.rcParams["text.usetex"] = False


save_fig = True
doi = pd.Timestamp("2021-06-29-06")
domain = "d02"
model = "wrf"
var = "S"


## Open gridded static
static_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-{model.lower()}-{domain}.nc"
)
climo_ds = xr.open_zarr(
    f"/Volumes/WFRT-Ext23/ecmwf/era5-land/{var}-hourly-climatology-19910101-20201231-compressed.zarr"
)[var]

# era_ds = salem.open_xr_dataset(
#     f"/Volumes/WFRT-Ext23/fwf-data/ecmwf/era5-land/04/fwf-hourly-era5-land-{doi.strftime('%Y%m%d%H')}.nc"
# )[var]
# era5L = xr.open_dataset(f'/Volumes/WFRT-Ext25/ecmwf/era5-land/202310/era5-land-{doi.strftime("%Y%m%d%H")}.nc')

fwf_ds = salem.open_xr_dataset(
    f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/01/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc"
)[
    var
]  # .isel(time=slice(0,24))

try:
    wrf_ds = salem.open_xr_dataset(
        f"/Volumes/Scratch/fwf-data/wrf/{domain}/{doi.strftime('%Y%m')}/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc"
    )  # .isel(time=slice(0,24))
except:
    wrf_ds = salem.open_xr_dataset(
        f"/Volumes/WFRT-Ext23/fwf-data/wrf/{domain}/{doi.strftime('%Y%m')}/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc"
    )  # .isel(time=slice(0,24))

fwf_ds = fwf_ds.where(wrf_ds["SNOWC"].values < 0.5, 0)

### Open color map json
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)
name, colors, sigma, levels = (
    str(cmaps[var]["name"]),
    cmaps[var]["colors18"],
    cmaps[var]["sigma"],
    cmaps[var]["levels"],
)

hourly_ds = fwf_ds
hourly_ds["time"] = hourly_ds["Time"]
date_range = pd.to_datetime(hourly_ds["Time"])

dayofyear = xr.DataArray(
    date_range.dayofyear, dims="time", coords=dict(time=date_range)
)
hours = xr.DataArray(date_range.hour, dims="time", coords=dict(time=date_range))

# dayofyear_first = date_range.dayofyear[0]
# dayofyear_last = date_range.dayofyear[-1]
# maxS = (
#     climo_ds.sel(dayofyear=slice(dayofyear_first - 7, dayofyear_last + 7), quantile=1)
#     .max(dim="dayofyear")
#     .isel(hour=hours)
# )
# minS = (
#     climo_ds.sel(dayofyear=slice(dayofyear_first - 7, dayofyear_last + 7), quantile=0)
#     .min(dim="dayofyear")
#     .isel(hour=hours)
# )
maxS = climo_ds.sel(dayofyear=dayofyear, hour=hours, quantile=1)
minS = climo_ds.sel(dayofyear=dayofyear, hour=hours, quantile=0)

# fig = plt.figure(figsize=(14, 8))
# ax = fig.add_subplot(1,1,1)
# maxS.isel(time = 0).salem.quick_map(cmap='jet',vmax=100, ax= ax, oceans=True, states=True, prov=True)
# plt.savefig(str(data_dir) + f"/images/norm/max-{var}-{doi.strftime('%Y%m%d')}")

# fig = plt.figure(figsize=(14, 8))
# ax = fig.add_subplot(1,1,1)
# minS.isel(time = 0).salem.quick_map(cmap='jet', vmax=30, ax= ax, oceans=True, states=True, prov=True)
# plt.savefig(str(data_dir) + f"/images/norm/min-{var}-{doi.strftime('%Y%m%d')}")

quantiles = climo_ds.sel(
    dayofyear=dayofyear, hour=hours, quantile=[0.25, 0.5, 0.75, 0.90, 0.95, 0.99]
)
maxS = hourly_ds.salem.transform(maxS)
minS = hourly_ds.salem.transform(minS)
quantiles = hourly_ds.salem.transform(quantiles)

# fig = plt.figure(figsize=(14, 8))
# ax = fig.add_subplot(1,1,1)
# maxS.isel(time = 0).salem.quick_map(cmap='jet',vmax=100, ax= ax, oceans=True, states=True, prov=True)
# plt.savefig(str(data_dir) + f"/images/norm/maxT-{var}-{doi.strftime('%Y%m%d')}")

# fig = plt.figure(figsize=(14, 8))
# ax = fig.add_subplot(1,1,1)
# minS.isel(time = 0).salem.quick_map(cmap='jet', vmax=30, ax= ax, oceans=True, states=True, prov=True)
# plt.savefig(str(data_dir) + f"/images/norm/minT-{var}-{doi.strftime('%Y%m%d')}")

# nomr_ds = (hourly_ds - minS) / (maxS - minS)
nomr_ds = (hourly_ds - minS.min(dim="time")) / (
    maxS.max(dim="time") - minS.min(dim="time")
)
nomr_ds = xr.where(nomr_ds == np.inf, 0, nomr_ds)
print(float(nomr_ds.max()))
nomr_ds.attrs["pyproj_srs"] = hourly_ds.attrs["pyproj_srs"]

fig = plt.figure(figsize=(14, 5))
# fig.suptitle(f"Normalized HFWI vs HFWI\n on {(doi + pd.Timedelta(hours=18)).strftime('%Y%m%dT%H')}", fontsize = 20)
fig.suptitle(f"Normalized HFWI vs HFWI\n on {doi.strftime('%Y%m%dT%H')}", fontsize=20)
ax = fig.add_subplot(1, 2, 1)
nomr_ds.isel(time=0).salem.quick_map(
    cmap="jet",
    levels=np.arange(0.1, 1.0, 0.05),
    ax=ax,
    oceans=True,
    states=True,
    prov=True,
)
ax.set_title("Normalized HFWI", fontsize=18)
# if save_fig == True:
#     plt.savefig(str(data_dir) + f"/images/norm/{var}-norm-{doi.strftime('%Y%m%d')}")

# fig = plt.figure(figsize=(14, 8))
ax = fig.add_subplot(1, 2, 2)
hourly_ds.isel(time=0).salem.quick_map(
    cmap="jet", levels=levels, ax=ax, oceans=True, states=True, prov=True
)
ax.set_title("HFWI", fontsize=18)
fig.tight_layout()
if save_fig == True:
    plt.savefig(str(data_dir) + f"/images/norm/{var}-sub-{doi.strftime('%Y%m%d')}-test")


### Open color map json
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)


cmap = cmaps[var]["colors"]
levels = cmaps[var]["levels"][:-1]
vmin = cmaps[var]["vmin"]
vmax = cmaps[var]["vmax"]
