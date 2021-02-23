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

### Open WRF domain
filein = str(wrf_dir) + f"/wrfout-{domain}-2018040106.zarr"
wrf_ds = xr.open_zarr(filein)

### Open tzone  domain
filein = str(tzone_dir) + f"/tzone_wrf_{domain}_old.nc"
tzone_ds = xr.open_dataset(filein)

## set plot title and save dir/name
Plot_Title = "Model Domains in Mercator Projection"
save_file = "/images/wrf4-hysplit-model-domains.png"
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
ax.gridlines()
ax.add_feature(cfeature.LAND, zorder=1)
ax.add_feature(cfeature.LAKES, zorder=1)
ax.add_feature(cfeature.OCEAN, zorder=1)
ax.add_feature(cfeature.BORDERS, zorder=1)
ax.add_feature(cfeature.COASTLINE, zorder=1)
ax.add_feature(states_provinces, edgecolor="gray", zorder=2)
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
ax.set_title(Plot_Title, fontsize=20, weight="bold")
fig.subplots_adjust(hspace=0.8)


## get d01 lats and lon
lats, lons = np.array(wrf_ds.XLAT), np.array(wrf_ds.XLONG)
# lats, lons = lats[0], lons[0]
lons = np.where(
    lons > -179, lons, np.nan
)  ## mask out past international dateline.....catorpy hates the dateline

## plot d01
ax.plot(lons[0], lats[0], color="green", linewidth=2, zorder=8, alpha=1)
ax.plot(lons[-1].T, lats[-1].T, color="green", linewidth=2, zorder=8, alpha=1)
ax.plot(lons[:, 0], lats[:, 0], color="green", linewidth=2, zorder=8, alpha=1)
ax.plot(
    lons[:, -1].T,
    lats[:, -1].T,
    color="green",
    linewidth=2,
    zorder=8,
    alpha=1,
    label="12 km WRF Domain",
)


levels = np.unique(tzone_ds.Zone)
# divider = make_axes_locatable(ax)

Cnorm = matplotlib.colors.Normalize(vmin=levels[0], vmax=levels[-1] + 1)

clb = ax.contourf(
    lons, lats, tzone_ds.Zone, zorder=8, alpha=0.5, levels=levels, norm=Cnorm
)
ax.contour(lons, lats, tzone_ds.Zone, zorder=8, alpha=1, levels=levels, norm=Cnorm)
# cax = divider.append_axes('right', size='5%', pad=0.05)
fig.colorbar(clb, orientation="vertical")


## set map bounds
ax.set_xlim([-150, -50])
ax.set_ylim([32, 70])

## add legend
ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, 1.0),
    ncol=5,
    fancybox=True,
    shadow=True,
)

## tighten up fig
plt.tight_layout()

## save as png
# fig.savefig(save_dir, dpi=240)
