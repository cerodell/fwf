import context
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
from mpl_toolkits.axes_grid1 import make_axes_locatable

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from datetime import datetime, date, timedelta

from wrf import to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ll_to_xy, xy_to_ll


from context import data_dir, root_dir, fwf_zarr_dir, wrf_dir, tzone_dir

startTime = datetime.now()


domain = "d02"
wrf_model = "wrf3"

### Open tzone  domain
filein = str(tzone_dir) + f"/tzone_{wrf_model}_{domain}.zarr"
tzone_ds = xr.open_zarr(filein)


## set plot title and save dir/name
if domain == "d02":
    res = "12 km"
else:
    res = "4 km"

Plot_Title = f"Time Zone Offsets From UTC \n {wrf_model.upper()} {res} Domain"
save_file = f"/images/{wrf_model}-{domain}-tzone.png"
save_dir = str(data_dir) + save_file


## bring in state/prov boundaries
states_provinces = cfeature.NaturalEarthFeature(
    category="cultural",
    name="admin_1_states_provinces_lines",
    scale="50m",
    facecolor="none",
)


## make fig for make with projection
fig = plt.figure(figsize=[16, 8])
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(central_longitude=0))

## add map features
ax.gridlines(zorder=10)
ax.add_feature(cfeature.LAND, zorder=1)
ax.add_feature(cfeature.LAKES, zorder=1)
ax.add_feature(cfeature.OCEAN, zorder=9)
ax.add_feature(cfeature.BORDERS, zorder=10)
ax.add_feature(cfeature.COASTLINE, zorder=10)
ax.add_feature(states_provinces, edgecolor="gray", zorder=2)
ax.set_xlabel("Longitude", fontsize=18, zorder=10)
ax.set_ylabel("Latitude", fontsize=18, zorder=10)

## create tick mark labels and style
ax.set_xticks(list(np.arange(-170, -20, 10)), crs=ccrs.PlateCarree())
ax.set_yticks(list(np.arange(20, 90, 10)), crs=ccrs.PlateCarree())
# ax.yaxis.tick_right()
# ax.yaxis.set_label_position("right")
ax.tick_params(axis="both", which="major", labelsize=14)
ax.tick_params(axis="both", which="minor", labelsize=14)

## add title and adjust subplot buffers
ax.set_title(Plot_Title, fontsize=20, weight="bold")
fig.subplots_adjust(hspace=0.8)
divider = make_axes_locatable(ax)
ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)

## get d01 lats and lon
lats, lons = tzone_ds.XLAT.values, tzone_ds.XLONG.values
lons = np.where(
    lons > -179, lons, np.nan
)  ## mask out past international dateline.....catorpy hates the dateline

## plot d01
ax.plot(lons[0], lats[0], color="k", linewidth=2, zorder=10, alpha=1)
ax.plot(lons[-1].T, lats[-1].T, color="k", linewidth=2, zorder=10, alpha=1)
ax.plot(lons[:, 0], lats[:, 0], color="k", linewidth=2, zorder=10, alpha=1)
ax.plot(
    lons[:, -1].T,
    lats[:, -1].T,
    color="k",
    linewidth=2,
    zorder=10,
    alpha=1,
)


levels = np.unique(tzone_ds.Zone.values)
if wrf_model == "wrf3":
    levels = [3, 4, 5, 6, 7, 8, 9, 10]
    levels = [-10, -9, -8, -7, -6, -5, -4, -3]
elif wrf_model == "wrf4":
    levels = [3, 4, 5, 6, 7, 8, 9, 10]
    levels = [-10, -9, -8, -7, -6, -5, -4, -3]
else:
    pass

# divider = make_axes_locatable(ax)


contourf = ax.contourf(
    lons,
    lats,
    (tzone_ds.Zone + 0.5) * -1,
    zorder=8,
    alpha=0.5,
    levels=levels,
    cmap="Dark2_r",
)

fig.add_axes(ax_cb)
ticks = levels[1:]
tick_levels = list(np.array(levels) - 0.5)
cbar = plt.colorbar(contourf, cax=ax_cb, ticks=tick_levels)
cbar.ax.set_yticklabels(ticks)  # set ticks of your format
cbar.ax.axes.tick_params(length=0)

## set map bounds
## set map bounds
if wrf_model == "wrf3":
    ax.set_xlim([-150, -54])
    ax.set_ylim([34, 70])
elif wrf_model == "wrf4":
    ax.set_xlim([-179.9, -29])
    ax.set_ylim([20, 80])
else:
    pass


## tighten up fig
plt.tight_layout()
## save as png
fig.savefig(save_dir, dpi=240)
