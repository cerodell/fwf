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

from utils.frp import (
    open_frp,
)

plt.rcParams["text.usetex"] = False


save_fig = False
doi = pd.Timestamp("2022-07-23")
domain = "d02"
model = "wrf"
var = "S"
lat, lon = 48.9610, -76.4048
lat, lon = 50.6886, -120.3540
case_study = "oak_fire"  # ['barrington_lake_fire', 'wildcat', 'marshall_fire', 'oak_fire', 'caldor_fire', 'fire_east_tulare', 'rossmoore_fire', 'crater_creek', 'lytton_creek]

## open case study json file
with open(str(root_dir) + f"/json/fire-cases.json", "r") as fp:
    case_dict = json.load(fp)
#
print(case_study)
case_info = case_dict[case_study]

(frp_ds, frp_da, frp_da_og, frp_lats, frp_lons, utc_offset, start, stop) = open_frp(
    case_study, case_info
)
lat, lon = float(frp_lats.mean()), float(frp_lons.mean())


## Open gridded static
static_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-{model.lower()}-{domain}.nc"
)
climo_ds = xr.open_zarr(
    f"/Volumes/WFRT-Ext22/ecmwf/era5-land/{var}-hourly-climatology-19910101-20201231-compressed.zarr"
)[var]

era_ds = salem.open_xr_dataset(
    f"/Volumes/WFRT-Ext23/fwf-data/ecmwf/era5-land/04/fwf-hourly-era5-land-{doi.strftime('%Y%m%d%H')}.nc"
)[var].isel(time=slice(6, 24))

fwf_ds = salem.open_xr_dataset(
    f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/01/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc"
)[var].isel(time=slice(0, 18))

try:
    wrf_ds = salem.open_xr_dataset(
        f"/Volumes/Scratch/fwf-data/wrf/{domain}/{doi.strftime('%Y%m')}/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc"
    ).isel(time=slice(0, 18))
except:
    wrf_ds = salem.open_xr_dataset(
        f"/Volumes/WFRT-Ext23/fwf-data/wrf/{domain}/{doi.strftime('%Y%m')}/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc"
    ).isel(time=slice(0, 18))

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

if model == "wrf":
    hourly_ds = fwf_ds
else:
    hourly_ds = era_ds

hourly_ds["time"] = hourly_ds["Time"]
date_range = pd.to_datetime(hourly_ds["Time"])

dayofyear = xr.DataArray(
    date_range.dayofyear, dims="time", coords=dict(time=date_range)
)
hours = xr.DataArray(date_range.hour, dims="time", coords=dict(time=date_range))

maxS = (climo_ds.sel(dayofyear=dayofyear, hour=hours, quantile=1)).load()
minS = (climo_ds.sel(dayofyear=dayofyear, hour=hours, quantile=0)).load()

quantiles = climo_ds.sel(
    dayofyear=dayofyear,
    hour=hours,
    quantile=[0.0, 0.25, 0.5, 0.75, 0.90, 0.95, 0.99, 1.0],
).load()
maxS = hourly_ds.salem.transform(maxS)
minS = hourly_ds.salem.transform(minS)
quantiles = hourly_ds.salem.transform(quantiles)

# nomr_ds = (hourly_ds - minS) / (maxS - minS)

nomr_ds = (hourly_ds - minS.min(dim="time")) / (
    maxS.max(dim="time") - minS.min(dim="time")
)

# y, x  = make_KDtree('ecmwf', 'era5-land', lat, lon)
y, x = make_KDtree(model, domain, lat, lon)

# (maxS.isel(south_north = y ,west_east =x ) - maxSW.isel(south_north = yW ,west_east =xW )).plot(color = 'k')
# maxSW.isel(south_north = yW,west_east =xW ).plot(color = 'red')

# %%
offset = int(static_ds["ZoneST"].isel(south_north=y, west_east=x))
utc_offset = int(offset)
hourly_ds["time"] = hourly_ds["Time"] - np.timedelta64(utc_offset, "h")
quantiles["time"] = hourly_ds["Time"] - np.timedelta64(utc_offset, "h")
nomr_ds["time"] = hourly_ds["Time"] - np.timedelta64(utc_offset, "h")
maxS["time"] = hourly_ds["Time"] - np.timedelta64(utc_offset, "h")
minS["time"] = hourly_ds["Time"] - np.timedelta64(utc_offset, "h")
y, x = int(y), int(x)
quantiles_interp = quantiles.isel(south_north=y, west_east=x)

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

# ax.plot(maxS.time, maxS.interp(south_north= y, west_east=x), color = 'green', label = 'MAX')
# ax.plot(maxS.time, minS.isel(south_north= y, west_east=x), color = 'blue', label = 'MIN')
ax.plot(
    hourly_ds.time, hourly_ds.isel(south_north=y, west_east=x), color="k", label="fct"
)
ax.plot(
    hourly_ds.time,
    hourly_ds.isel(south_north=y, west_east=x),
    color="k",
    ls="--",
    label="norm fct",
    zorder=1,
)

ax2 = ax.twinx()
ax2.plot(
    nomr_ds.time,
    nomr_ds.isel(south_north=y, west_east=x),
    color="k",
    ls="--",
    label="norm fct",
)
ax2.set_ylim(0, 1)
ax.legend(
    bbox_to_anchor=(0.8, 1.2),
    ncol=4,
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


# %%


# MAX =maxS.interp(south_north= y, west_east=x).values.ravel()
# MIN =minS.interp(south_north= y, west_east=x).values.ravel()
# FWI = hourly_ds.interp(south_north= y, west_east=x).values.ravel()

# NORM = (FWI-MIN.min())/ (MAX.max()-MIN.min())

# plt.plot(NORM)
