import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.ndimage as ndimage
from scipy.ndimage.filters import gaussian_filter

from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta


domain = "d02"
# date = pd.Timestamp("today")
date = pd.Timestamp(2018, 7, 20)
forecast_date = date.strftime("%Y%m%d06")

# file_dir = str(fwf_zarr_dir) + f"/fwf-hourly-{domain}-{forecast_date}.zarr"   # wrfout-{domain}-{forecast_date}.zarr
file_dir = (
    str(data_dir) + f"/FWF-WAN00CP-04/fwf-hourly-{domain}-{forecast_date}.zarr"
)  # wrfout-{domain}-{forecast_date}.zarr

file_dir = "/Volumes/cer/fireweather/data/FWF-WAN00CG-01/fwf-daily-d03-2021022106.zarr"
ds = xr.open_zarr(file_dir)


### Open color map json
with open(str(data_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

var, index = "F", 12
vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
name, colors, sigma = (
    str(cmaps[var]["name"]),
    cmaps[var]["colors18"],
    cmaps[var]["sigma"],
)

lngs = ds.XLONG.values
lats = ds.XLAT.values

fillarray = ds[var][index].values
fillarray = np.round(fillarray, 0)
fillarray = ndimage.gaussian_filter(fillarray, sigma=sigma)


## bring in state/prov boundaries
states_provinces = cfeature.NaturalEarthFeature(
    category="cultural",
    name="admin_1_states_provinces_lines",
    scale="50m",
    facecolor="none",
)


## make fig for make with projection
fig = plt.figure(figsize=[16, 8])
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

divider = make_axes_locatable(ax)
ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)

# cax = divider.append_axes('right', size='5%', pad=0.05)

## add map features
ax.gridlines()
ax.add_feature(cfeature.LAND, zorder=1)
ax.add_feature(cfeature.LAKES, zorder=10)
ax.add_feature(cfeature.OCEAN, zorder=10)
ax.add_feature(cfeature.BORDERS, zorder=1)
ax.add_feature(cfeature.COASTLINE, zorder=1)
ax.add_feature(states_provinces, edgecolor="gray", zorder=6)
ax.set_xlabel("Longitude", fontsize=18)
ax.set_ylabel("Latitude", fontsize=18)

## create tick mark labels and style
ax.set_xticks(list(np.arange(-160, -40, 10)), crs=ccrs.PlateCarree())
ax.set_yticks(list(np.arange(30, 80, 10)), crs=ccrs.PlateCarree())
# ax.yaxis.tick_right()
# ax.yaxis.set_label_position("right")
ax.tick_params(axis="both", which="major", labelsize=14)
ax.tick_params(axis="both", which="minor", labelsize=14)

## add title and adjust subplot buffers
Plot_Title = f"{ds[var].description}  \n {str(ds.Time.values[index])[:13]}"
ax.set_title(Plot_Title, fontsize=20, weight="bold")

lenght = len(colors)
levels = cmaps[var]["levels"]
Cnorm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)
contourf = ax.contourf(
    lngs,
    lats,
    fillarray,
    levels=levels,
    norm=Cnorm,
    colors=colors,
    extend="both",
    zorder=4,
    alpha=0.9,
)

fig.add_axes(ax_cb)
plt.colorbar(contourf, cax=ax_cb)


## set map bounds
ax.set_xlim([-140, -60])
ax.set_ylim([36, 70])

## tighten up fig
# plt.tight_layout()


# for var in list(ds):
#     # print(f"max of {var}: {str(ds.Time.values)}")
#     print(f"max of {var}: {float(ds[var].max(skipna= True))}")
#     print(f"min of {var}: {float(ds[var].min(skipna= True))}")
#     print(f"mean of {var}: {float(ds[var].mean(skipna= True))}")

# var = "F"
# for i in range(len(ds.time)):
#     print(str(ds.time.values[i]))
#     print(float(ds.isel(time=i)[var].max(skipna=True)))
#     print(float(ds.isel(time=i)[var].min(skipna=True)))
#     print(float(ds.isel(time=i)[var].mean(skipna=True)))

# air1d = ds[var].isel(wmo=200)

# air1d.plot()
