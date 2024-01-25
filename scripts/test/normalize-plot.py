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
import matplotlib.colors

from datetime import datetime, timedelta
from utils.wrf_ import read_wrf
from utils.eccc import read_eccc
from netCDF4 import Dataset

from context import data_dir, root_dir
from utils.frp import build_tree


test = np.random.rand(30)
test[:29] = 0
np.quantile(test, 1)


doi = pd.Timestamp("1994-01-01")
domain = "d02"
var = "S"
era_ds = salem.open_xr_dataset(
    f"/Volumes/WFRT-Ext23/fwf-data/ecmwf/era5-land/04/fwf-hourly-era5-land-{doi.strftime('%Y%m%d%H')}.nc"
)["S"]
# fwf_ds = salem.open_xr_dataset(f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/04/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc")["S"].isel(time=slice(0,24))
era_ds.isel(time=0).plot(vmax=1)

hourly_climo = salem.open_xr_dataset(
    "/Volumes/WFRT-Ext22/ecmwf/era5-land/S-hourly-climatology-19910101-20201231-quant.zarr"
)
hourly_climo["S"].isel(dayofyear=0, hour=0, quantile=-1).salem.quick_map(vmax=1)


### Open color map json
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)


vmin, vmax = 0, 1
name, colors, sigma = (
    str(cmaps[var]["name"]),
    cmaps[var]["colors18"],
    cmaps[var]["sigma"],
)
# levels = cmaps[var]["levels"]
levels = np.arange(0, 1.1, 0.1)
Cnorm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)

# mask = xr.open_dataset("/Volumes/WFRT-Ext25/ecmwf/era5-land/202208/era5-land-2022080100.nc").isel(time =0).notnull().rename({'t2m': 'S'})['S'].values
#
# era_dsT = fwf_ds.salem.transform(era_ds)

# time = 0
# era_dsT.isel(time = time).salem.quick_map(vmax = 80, vmin = 0)
# fwf_ds.isel(time = time).salem.quick_map(vmax = 80, vmin = 0)

# (fwf_ds.isel(time = time) - era_dsT.isel(time = time)).plot()

# south_north, west_east = 55.022, -103.842
# yy, xx = build_tree('', {'domain':domain}, [south_north], [west_east])

# fig = plt.figure(figsize=(12,6))
# ax = fig.add_subplot(1,1,1)
# fwf_ds.isel(south_north = yy, west_east = xx).plot(ax=ax, color= 'red')
# era_ds.interp(south_north = south_north, west_east = west_east).plot(ax=ax, color= 'green')


static_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-ecmwf-era5-land.nc"
)


hourly_ds = era_ds
# # hourly_ds["south_north"] = static_ds["south_north"]
# # hourly_ds["west_east"] = static_ds["west_east"]
hourly_ds["time"] = hourly_ds["Time"]
date_range = pd.to_datetime(hourly_ds["Time".convert_calendar("noleap")])

dayofyear = xr.DataArray(
    date_range.dayofyear, dims="time", coords=dict(time=date_range)
)
hours = xr.DataArray(date_range.hour, dims="time", coords=dict(time=date_range))
dayofyear = date_range.dayofyear[0]

# hclimoT = hourly_climo.sel(dayofyear =dayofyear-1, hour = hours, quantile = [1,0])

maxS = (
    hourly_climo.sel(dayofyear=slice(dayofyear - 7, dayofyear + 7), quantile=1)
    .max(dim="dayofyear")
    .isel(hour=hours)
)
minS = (
    hourly_climo.sel(dayofyear=slice(dayofyear - 7, dayofyear + 7), quantile=0)
    .min(dim="dayofyear")
    .isel(hour=hours)
)


# # hclimoT = hourly_ds.salem.transform(hclimo)

nomr_ds = (hourly_ds - minS) / (maxS - minS)

# nomr_ds = (hourly_ds - hclimoT["S"].sel(quantile =0)) / (hclimoT["S"].sel(quantile =1) - hclimoT["S"].sel(quantile =0))

# nomr_ds = nomr_ds.where(mask)
nomr_ds = nomr_ds.where(np.isfinite(nomr_ds), drop=True)

# (hourly_climo['S'].sel(dayofyear =dayofyear+1, quantile =1).isel(hour = 0)- hourly_ds.isel(time = 0)).min()
# nomr_ds = (hourly_ds - hclimoT["S_min"]) / (daily_ds["S_max"] - daily_ds["S_min"])

# nomr_ds["Time"] = hourly_ds["Time"]
# static_ds["S_norm"] = nomr_ds
# static_ds["S_norm"].attrs = static_ds.attrs

# fig = plt.figure(figsize=(12, 4))
# ax = fig.add_subplot(1, 1, 1)
# static_ds["S_norm"].isel(time = 0).salem.quick_map(
#     prov=True, states=True, oceans=True, vmax=1, vmin=vmin, cmap="jet", ax=ax
# )


# plt.savefig(
#     str(data_dir) + f"/images/norm/fwf-{doi}-norm.png",
#     dpi=250,
#     bbox_inches="tight",
# )

# fig = plt.figure(figsize=(12, 4))
# ax = fig.add_subplot(1, 1, 1)
# hourly_ds.salem.quick_map(
#     prov=True, states=True, oceans=True, cmap="jet", vmax=30, ax=ax
# )


# plt.savefig(
#     str(data_dir) + f"/images/norm/fwf-{doi}.png",
#     dpi=250,
#     bbox_inches="tight",
# )


# static_ds['S'] = houlry_ds['S_max']
# static_ds['S'].attrs = static_ds.attrs
# static_ds['S'].salem.quick_map()
# static_ds['S_max_daily'] = (daily_ds['S_max']- houlry_ds['S_max'])
# static_ds['S_max_daily'].attrs = static_ds.attrs
# static_ds['S_max_daily'].salem.quick_map(vmin = -20, vmax = 20, cmap ='coolwarm', prov = True, states= True, oceans =True)

# hourly_ds =salem.open_xr_dataset(f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/02/fwf-hourly-{domain}-2023081706.nc")['S'].isel(time = 0)
# hourly_ds.salem.quick_map(prov = True, states= True, oceans =True, vmax = 40)
