import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from utils.make_intercomp import daily_merge_ds
from pylab import *

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.ndimage as ndimage
from scipy.ndimage.filters import gaussian_filter


from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta


date = pd.Timestamp(2018, 7, 18)
domain = "d02"
wrf_model = "wrf3"


## Path to hourly/daily fwi data
forecast_date = date.strftime("%Y%m%d06")
filein = str(data_dir) + f"/test/fpb-{domain}-{forecast_date}.zarr"
# filein = f'/Volumes/cer/fireweather/data/fwf-hourly-{domain}-2018040106-2018100106.zarr'
filein = f"/Users/rodell/Google Drive/Shared drives/Research/FireSmoke/ZARR_Data/fwf-hourly-{domain}-2018040106-2018100106.zarr"

ds = xr.open_zarr(filein)
ds.coords["time"] = ds.Time


var = "HFI"
levels = np.arange(0, 150000, 1000)

save_file = f"/images/{var}-{wrf_model}-{domain}.png"
save_dir = str(data_dir) + save_file
ds = ds.loc[dict(time="2018-08-18T20")]


day_hour = np.datetime_as_string(ds.Time, unit="h")
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
ax.tick_params(axis="both", which="major", labelsize=14)
ax.tick_params(axis="both", which="minor", labelsize=14)

## add title and adjust subplot buffers
if domain == "d02":
    res = "12 km"
elif domain == "d03":
    res = "4 km"
else:
    res = ""
Plot_Title = f"{ds.HFI.attrs['description']} at {day_hour} \n {wrf_model} {res}"
ax.set_title(Plot_Title, fontsize=20, weight="bold")


contourf = ax.contourf(
    ds.XLONG,
    ds.XLAT,
    ds[var],
    levels=levels,
    extend="both",
    cmap="RdYlBu_r",
    zorder=10,
    alpha=1,
)


Cnorm = matplotlib.colors.Normalize(
    vmin=int(np.min(levels)), vmax=int(np.max(levels)) + 1
)
# contourf = ax.pcolormesh(ds.XLONG, ds.XLAT, ds[var], zorder=10, norm=Cnorm, cmap="RdYlBu_r", shading='flat')
fig.add_axes(ax_cb)
cbar = plt.colorbar(contourf, cax=ax_cb)

## set map bounds
if wrf_model == "wrf3":
    ax.set_xlim([-140, -60])
    ax.set_ylim([36, 70])
elif wrf_model == "wrf4":
    ax.set_xlim([-174, -30])
    ax.set_ylim([25, 80])
else:
    pass


fig.savefig(save_dir, dpi=240)
