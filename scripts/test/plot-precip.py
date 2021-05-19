import context
import json
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
from netCDF4 import Dataset
import cartopy.crs as crs

from datetime import datetime
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import shapely.geometry as sgeom
import matplotlib.ticker as mticker
from mpl_toolkits.axes_grid1 import make_axes_locatable

import scipy.ndimage as ndimage

from scipy.ndimage.filters import gaussian_filter


from datetime import datetime, date, timedelta

from wrf import to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ll_to_xy, xy_to_ll


from context import data_dir, root_dir, fwf_zarr_dir, wrf_dir

startTime = datetime.now()

## define variable
var, index = "r_o", 18

wrf_dir = "/Users/rodell/Google Drive/Shared drives/WAN00CG-01/21041100"

### Open WRF d02 domain
filein = str(wrf_dir) + f"/wrfout_d02_2021-04-14_00:00:00"
wrf_ds = xr.open_dataset(filein)

# ### Open WRF d03 domain
# filein = str(wrf_dir) + f"/wrfout_d03_2021-04-11_00:00:00"
# wrf_ds = xr.open_dataset(filein)

### Open color map json
with open(str(data_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

## open ploting colorbar info
# vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
# name, colors, sigma = (
#     str(cmaps[var]["name"]),
#     cmaps[var]["colors18"],
#     cmaps[var]["sigma"],
# )

# colors= colors[1:]

vmin, vmax = 0, 140
colors = [
    "#a9a5a5",
    "#6e6e6e",
    "#b3f9a9",
    "#79f572",
    "#50f150",
    "#1fb51e",
    "#0ca10d",
    "#1563d3",
    "#54a8f5",
    "#b4f1fb",
    "#ffe978",
    "#ffa100",
    "#ff3300",
    "#a50000",
    "#b58d83",
    "#9886ba",
    "#8d008d",
]

wrf_ds = wrf_ds.isel(Time=0)
fillarray = wrf_ds["RAINC"] + wrf_ds["RAINSH"] + wrf_ds["RAINNC"]
# fillarray = np.round(fillarray, 0)
# fillarray = ndimage.gaussian_filter(fillarray, sigma=sigma)


## set plot title and save dir/name
Plot_Title = "Precipitation"
# save_file = "/images/wrf4-hysplit-model-domains.png"
save_file = "/images/wrf-precip.png"
save_dir = str(data_dir) + save_file


## bring in state/prov boundaries
states_provinces = cfeature.NaturalEarthFeature(
    category="cultural",
    name="admin_1_states_provinces_lines",
    scale="50m",
    facecolor="none",
)

## chose where to center longitude..
##..by shiftting 180 you can plot over international dateline
## NOTE once you do this you also have to shift you longitdues in your data
## i did this by adding 180 to the lons...see line 107-110 as example
proj = ccrs.PlateCarree(central_longitude=180)
# box_proj = ccrs.PlateCarree(central_longitude=0)

## make fig for make with projection
fig = plt.figure(figsize=[16, 8])
ax = fig.add_subplot(1, 1, 1, projection=proj)

## add map features
gl = ax.gridlines(
    draw_labels=True,
    crs=ccrs.PlateCarree(),
    linewidth=0.5,
    color="gray",
    alpha=0.5,
    linestyle="--",
)
gl.xlabels_top = False
gl.xlocator = mticker.FixedLocator(list(np.arange(-180, 180, 10)))
ax.add_feature(cfeature.LAND, zorder=1)
ax.add_feature(cfeature.LAKES, zorder=1)
ax.add_feature(cfeature.OCEAN, zorder=1)
ax.add_feature(cfeature.BORDERS, zorder=1)
ax.add_feature(cfeature.COASTLINE, zorder=1)
ax.add_feature(states_provinces, edgecolor="gray", zorder=2)
ax.set_xlabel("Longitude", fontsize=18)
ax.set_ylabel("Latitude", fontsize=18)

## create tick mark labels and style
ax.yaxis.tick_right()
ax.yaxis.set_label_position("right")
ax.tick_params(axis="both", which="major", labelsize=14)
ax.tick_params(axis="both", which="minor", labelsize=14)

## add title and adjust subplot buffers
fig.suptitle(Plot_Title, fontsize=20, weight="bold", y=0.9)


divider = make_axes_locatable(ax)
ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)


## get lats and lon
lats, lons = np.array(wrf_ds.XLAT), np.array(wrf_ds.XLONG)
# lats, lons = lats[0], lons[0]
lons += 180

# levels = cmaps[var]["levels"]
levels = [0.5, 1, 2, 3, 6, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 100, 140, 141]
Cnorm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)
contourf = ax.contourf(
    lons,
    lats,
    fillarray,
    levels=levels,
    norm=Cnorm,
    colors=colors,
    extend="max",
    zorder=4,
    alpha=0.9,
)

fig.add_axes(ax_cb)
plt.colorbar(contourf, cax=ax_cb)


## tighten up fig
plt.tight_layout(w_pad=2)

## save as png
fig.savefig(save_dir, dpi=240)
