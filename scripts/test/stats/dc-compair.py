import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import matplotlib.colors as colors

import cartopy.feature as cfeature
import cartopy.crs as ccrs
import salem

from context import data_dir

doi = "2022050106"
fwf_dir = "/Volumes/WFRT-Data02/FWF-WAN00CG/d02"

from cartopy.feature import NaturalEarthFeature
from netCDF4 import Dataset
from wrf import (
    to_np,
    getvar,
    smooth2d,
    get_cartopy,
    cartopy_xlim,
    cartopy_ylim,
    latlon_coords,
)


import pyproj

pyproj.datadir.get_data_dir()


ncfile = Dataset(str(data_dir) + f"/wrf/wrfout_d02_2021-01-14_00:00:00")

# Get the sea level pressure
slp = getvar(ncfile, "slp")

# Smooth the sea level pressure since it tends to be noisy near the
# mountains
smooth_slp = smooth2d(slp, 3, cenweight=4)

# Get the latitude and longitude points
lats, lons = latlon_coords(slp)

# Get the cartopy mapping object
cart_proj = get_cartopy(slp)


ds_05 = xr.open_dataset(fwf_dir + f"/WRF05/fwf/fwf-daily-d02-{doi}.nc").isel(time=0)
ds_06 = xr.open_dataset(fwf_dir + f"/WRF06/fwf/fwf-daily-d02-{doi}.nc").isel(time=0)


ds_05["D_dif"] = ds_05.D - ds_06.D


lons, lats, data = ds_05.XLONG.values, ds_05.XLAT.values, ds_05["D_dif"].values


# Create a figure
fig = plt.figure(figsize=(12, 6))
# Set the GeoAxes to the projection used by WRF
ax = plt.axes(projection=cart_proj)

# Download and add the states and coastlines
states = NaturalEarthFeature(
    category="cultural",
    scale="50m",
    facecolor="none",
    name="admin_1_states_provinces_shp",
)


# Cnorm = colors.Normalize(vmin= np.min(data), vmax =np.max(data))
divnorm = colors.TwoSlopeNorm(vmin=np.min(data), vcenter=0, vmax=np.max(data))


plt.contourf(
    lons,
    lats,
    data,
    10,
    transform=ccrs.PlateCarree(),
    cmap="coolwarm",
    norm=divnorm,
    # levels = np.arange(-100,800,50),
    extend="both",
)

# Add a color bar
plt.colorbar(ax=ax, shrink=0.98)

# Set the map bounds
ax.set_xlim(cartopy_xlim(smooth_slp))
ax.set_ylim(cartopy_ylim(smooth_slp))

# Add the gridlines
ax.gridlines(color="black", linestyle="dotted")

plt.title("Delta DC \n WRF05-WRF06")
ax.add_feature(cfeature.LAKES, zorder=10, facecolor=(1, 1, 1))
ax.add_feature(cfeature.OCEAN, zorder=10, facecolor=(1, 1, 1))
ax.add_feature(states, linewidth=0.5, edgecolor="black", zorder=10)
ax.coastlines("50m", linewidth=0.8, zorder=10)
ax.add_feature(cfeature.BORDERS, zorder=10, lw=0.7)
ax.add_feature(cfeature.COASTLINE, zorder=10, lw=0.7)


plt.show()
