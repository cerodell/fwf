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
from utils.frp import build_tree
from utils.geoutils import get_pyproj_loc

plt.rcParams["text.usetex"] = False


save_fig = True
doi = pd.Timestamp("2023-06-04")
domain = "d02"
model = "wrf"
var = "S"
lat, lon = 39.9, -105.178


## Open gridded static
static_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-{model.lower()}-{domain}.nc"
)
climo_ds = xr.open_zarr(
    f"/Volumes/WFRT-Ext22/ecmwf/era5-land/{var}-hourly-climatology-19910101-20201231-compressed.zarr"
)[var]

era_ds = salem.open_xr_dataset(
    f"/Volumes/WFRT-Ext23/fwf-data/ecmwf/era5-land/04/fwf-hourly-era5-land-{doi.strftime('%Y%m%d%H')}.nc"
)[var]

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

maxS = climo_ds.sel(dayofyear=dayofyear, hour=hours, quantile=1)
minS = climo_ds.sel(dayofyear=dayofyear, hour=hours, quantile=0)

quantiles = climo_ds.sel(
    dayofyear=dayofyear, hour=hours, quantile=[0.25, 0.5, 0.75, 0.90, 0.95, 0.99]
)
maxS = hourly_ds.salem.transform(maxS)
minS = hourly_ds.salem.transform(minS)
quantiles = hourly_ds.salem.transform(quantiles)

nomr_ds = (hourly_ds - minS) / (maxS - minS)


x, y = get_locs(pyproj_srs=hourly_ds.attrs["pyproj_srs"], df=None, lat=lat, lon=lon)

offset = int(static_ds["ZoneST"].interp(south_north=y, west_east=x))
hourly_ds["time"] = hourly_ds["Time"] - np.timedelta64(offset, "h")
quantiles["time"] = hourly_ds["Time"] - np.timedelta64(offset, "h")
quantiles_interp = quantiles.interp(south_north=y, west_east=x).isel(loc=0)

cmap = cm.get_cmap("Reds", len(quantiles_interp["quantile"]))  # PiYG

hex_color = []
for i in range(cmap.N):
    rgba = cmap(i)
    hex_color.append(matplotlib.colors.rgb2hex(rgba))

fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(1, 1, 1)

for i in range(len(quantiles_interp["quantile"])):

    ax.plot(
        quantiles.time,
        quantiles_interp.isel(quantile=i),
        label=str(float(quantiles_interp.isel(quantile=i)["quantile"])),
        color=hex_color[i],
    )
    try:
        ax.fill_between(
            quantiles.time,
            quantiles_interp.isel(quantile=i + 1),
            quantiles_interp.isel(quantile=i),
            alpha=0.2,
            color=hex_color[i],
        )
    except:
        pass
    if i == 0:
        ax.fill_between(
            quantiles.time,
            quantiles_interp.isel(quantile=i),
            0,
            alpha=0.2,
            color=hex_color[i],
        )

ax.plot(
    hourly_ds.time, hourly_ds.interp(south_north=y, west_east=x), color="k", label="fct"
)
ax.legend(
    bbox_to_anchor=(1.05, 1.14),
    ncol=7,
    fancybox=True,
    shadow=True,
    fontsize=13,
).set_zorder(10)
fig.autofmt_xdate(rotation=45)
if save_fig == True:
    plt.savefig(
        str(data_dir)
        + f"/images/norm/{var}-timeseries-exceedance-{lat}-{lon}-{doi.strftime('%Y%m%d%H')}.png"
    )
