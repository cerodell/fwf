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

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import shapely.geometry as sgeom
import matplotlib.ticker as mticker
from mpl_toolkits.axes_grid1 import make_axes_locatable


from context import data_dir

startTime = datetime.now()


domain = "d02"
wrf_model = "wrf3"

### Open tzone  domain
filein = str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}.zarr"
static_ds = xr.open_zarr(filein)

filein = str(data_dir) + f"/static/static-vars-{wrf_model}-d03.zarr"
static_d03_ds = xr.open_zarr(filein)

## set plot title and save dir/name
if domain == "d02":
    res = "12 km"
else:
    res = "4 km"

# Plot_Title = f"Time Zone Offsets From UTC during Summer \n {wrf_model.upper()} {res} Domain"
Plot_Title = f"Weather Research Forecast (WRF) Model Domains \n"

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
gl = ax.gridlines(
    draw_labels=True,
    crs=ccrs.PlateCarree(),
    linewidth=0.5,
    color="gray",
    alpha=0.5,
    linestyle="--",
    zorder=10,
)
gl.xlabels_top = False
gl.ylabels_right = False

gl.xlocator = mticker.FixedLocator(list(np.arange(-180, 180, 10)))
ax.add_feature(cfeature.LAND, zorder=1)
ax.add_feature(cfeature.LAKES, zorder=1)
ax.add_feature(cfeature.OCEAN, zorder=9)
ax.add_feature(cfeature.BORDERS, zorder=9)
ax.add_feature(cfeature.COASTLINE, zorder=9)
ax.add_feature(states_provinces, edgecolor="gray", zorder=2)
ax.set_xlabel("Longitude", fontsize=18)
ax.set_ylabel("Latitude", fontsize=18)

# ## create tick mark labels and style
# ax.set_xticks(list(np.arange(-170, -20, 10)), crs=ccrs.PlateCarree())
# ax.set_yticks(list(np.arange(20, 90, 10)), crs=ccrs.PlateCarree())
# # ax.yaxis.tick_right()
# # ax.yaxis.set_label_position("right")
ax.tick_params(axis="both", which="major", labelsize=14)
ax.tick_params(axis="both", which="minor", labelsize=14)

## add title and adjust subplot buffers
ax.set_title(Plot_Title, fontsize=20, weight="bold")
fig.subplots_adjust(hspace=0.8)
divider = make_axes_locatable(ax)
ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)

## get d01 lats and lon
lats, lons = static_ds.XLAT.values, static_ds.XLONG.values
lons = np.where(
    lons > -180, lons, np.nan
)  ## mask out past international dateline.....catorpy hates the dateline

## plot d01
ax.plot(lons[0], lats[0], color="blue", linewidth=2, zorder=10, alpha=1)
ax.plot(lons[-1].T, lats[-1].T, color="blue", linewidth=2, zorder=10, alpha=1)
ax.plot(lons[:, 0], lats[:, 0], color="blue", linewidth=2, zorder=10, alpha=1)
ax.plot(
    lons[:, -1].T,
    lats[:, -1].T,
    color="blue",
    linewidth=2,
    zorder=10,
    alpha=1,
    label="12 km WRF",
)
lats, lons = static_d03_ds.XLAT.values, static_d03_ds.XLONG.values
## plot d03
ax.plot(lons[0], lats[0], color="green", linewidth=2, zorder=10, alpha=1)
ax.plot(lons[-1].T, lats[-1].T, color="green", linewidth=2, zorder=10, alpha=1)
ax.plot(lons[:, 0], lats[:, 0], color="green", linewidth=2, zorder=10, alpha=1)
ax.plot(
    lons[:, -1].T,
    lats[:, -1].T,
    color="green",
    linewidth=2,
    zorder=10,
    alpha=1,
    label="4 km WRF",
)


levels = np.unique(static_ds.ZoneDT.values)
if wrf_model == "wrf3":
    levels = [3, 4, 5, 6, 7, 8, 9, 10]
    levels = [-10, -9, -8, -7, -6, -5, -4, -3]
elif wrf_model == "wrf4":
    levels = [3, 4, 5, 6, 7, 8, 9, 10]
    levels = [-10, -9, -8, -7, -6, -5, -4, -3]
else:
    pass

# divider = make_axes_locatable(ax)


# contourf = ax.contourf(
#     lons,
#     lats,
#     (static_ds.ZoneDT + 0.5) * -1,
#     zorder=8,
#     alpha=0.5,
#     levels=levels,
#     cmap="Dark2_r",
# )

# fig.add_axes(ax_cb)
# ticks = levels[1:]
# tick_levels = list(np.array(levels) - 0.5)
# cbar = plt.colorbar(contourf, cax=ax_cb, ticks=tick_levels)
# cbar.ax.set_yticklabels(ticks)  # set ticks of your format
# cbar.ax.axes.tick_params(length=0)

## set map bounds
## set map bounds
if wrf_model == "wrf3":
    ax.set_xlim([-150, -54])
    ax.set_ylim([34, 70])
elif wrf_model == "wrf4":
    ax.set_xlim([-179.9, -38])
    ax.set_ylim([20, 80])
else:
    pass

ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, 1.08),
    ncol=5,
    fancybox=True,
    shadow=True,
)
## tighten up fig
# plt.tight_layout()
## save as png
fig.savefig(save_dir, dpi=240)
