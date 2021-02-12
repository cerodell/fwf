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

from datetime import datetime, date, timedelta

from wrf import to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ll_to_xy, xy_to_ll


from context import data_dir, root_dir, wrf_dir

startTime = datetime.now()

domain = "d03"
## Set path to data
filein = str(data_dir) + "/domain/n_hem.csv"

## Read data
df = pd.read_csv(filein)

## Make 1D arrays of lat and lon
lat = np.array(df["lat_degr"])
lon = np.array(df["lon_degr"])

### Open old WRF domain
filein = str(data_dir) + f"/domain/wrfout_d01_new.nc"
ds_wrf_old = xr.open_dataset(filein)

### Open new WRF domain
# filein = str(data_dir) + f"/wrf/wrfout_{domain}_2021-01-14_00:00:00"
filein = str(data_dir) + f"/domain/wrfout_d02_new.nc"
ds_wrf_new = xr.open_dataset(filein)

### Open new hysplit domain
filein = str(data_dir) + "/domain/dispersion.nc"
ds_hysplit = xr.open_dataset(filein)


Plot_Title = "Model Domains in Mercator Projection"
save_file = "model-domains"
# fig, ax = plt.subplots(figsize=[12, 8])


states_provinces = cfeature.NaturalEarthFeature(
    category="cultural",
    name="admin_1_states_provinces_lines",
    scale="50m",
    facecolor="none",
)

fig = plt.figure(figsize=[18, 8])
# fig.tight_layout()
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
# ax.set_extent([canada_west, canada_east, canada_south, canada_north])

ax.gridlines()
ax.add_feature(cfeature.LAND, zorder=1)
ax.add_feature(cfeature.LAKES, zorder=1)
ax.add_feature(cfeature.OCEAN, zorder=1)
ax.add_feature(cfeature.BORDERS, zorder=1)
ax.add_feature(cfeature.COASTLINE, zorder=1)
ax.add_feature(states_provinces, edgecolor="gray", zorder=2)
ax.set_xlabel("Longitude", fontsize=18)
ax.set_ylabel("Latitude", fontsize=18)


ax.set_xticks(list(np.arange(-180, -30, 10)), crs=ccrs.PlateCarree())
ax.set_yticks(list(np.arange(10, 90, 10)), crs=ccrs.PlateCarree())


ax.set_title(Plot_Title, fontsize=20, weight="bold")
fig.subplots_adjust(hspace=0.8)
lats, lons = np.array(ds_wrf_old.XLAT), np.array(ds_wrf_old.XLONG)
lats, lons = lats[0], lons[0]
lons = np.where(lons < 179, lons, np.nan)


ax.plot(lons[0], lats[0], color="blue", linewidth=2, zorder=8, alpha=1)
ax.plot(lons[-1].T, lats[-1].T, color="blue", linewidth=2, zorder=8, alpha=1)
ax.plot(lons[:, 0], lats[:, 0], color="blue", linewidth=2, zorder=8, alpha=1)
ax.plot(
    lons[:, -1].T,
    lats[:, -1].T,
    color="blue",
    linewidth=2,
    zorder=8,
    alpha=1,
    label="New 36 km WRF",
)

lats, lons = np.array(ds_wrf_new.XLAT), np.array(ds_wrf_new.XLONG)
lats, lons = lats[0], lons[0]
lons = np.where(lons < 179, lons, np.nan)

ax.plot(lons[0], lats[0], color="red", linewidth=2, zorder=8, alpha=1)
ax.plot(lons[-1].T, lats[-1].T, color="red", linewidth=2, zorder=8, alpha=1)
ax.plot(lons[:, 0], lats[:, 0], color="red", linewidth=2, zorder=8, alpha=1)
ax.plot(
    lons[:, -1].T,
    lats[:, -1].T,
    color="red",
    linewidth=2,
    zorder=8,
    alpha=1,
    label="New 12 km WRF",
)


lat_i, lon_i = ds_hysplit.YORIG, ds_hysplit.XORIG
nrows, ncols = ds_hysplit.NROWS, ds_hysplit.NCOLS
xcell, ycell = ds_hysplit.XCELL, ds_hysplit.YCELL
lat_f = (nrows * ycell) + lat_i
lon_f = (ncols * xcell) + lon_i
lats = np.arange(lat_i, lat_f + ycell, ycell)
lons = np.arange(lon_i, lon_f + xcell, xcell)
lons, lats = np.meshgrid(lons, lats)


lats = np.arange(lat_i, lat_f + ycell, ycell)
lons = np.arange(lon_i, lon_f + xcell, xcell)
lons, lats = np.meshgrid(lons, lats)


ax.plot(lons[0], lats[0], color="k", linewidth=2, zorder=8, alpha=1)
ax.plot(lons[-1].T, lats[-1].T, color="k", linewidth=2, zorder=8, alpha=1)
ax.plot(lons[:, 0], lats[:, 0], color="k", linewidth=2, zorder=8, alpha=1)
ax.plot(
    lons[:, -1].T,
    lats[:, -1].T,
    color="k",
    linewidth=2,
    zorder=8,
    alpha=1,
    label="Old Hysplit",
)


lats = np.arange(32, lat_f + ycell, ycell)
lons = np.arange(-156, lon_f + xcell, xcell)
lons, lats = np.meshgrid(lons, lats)


ax.plot(lons[0], lats[0], color="yellow", linewidth=2, zorder=8, alpha=1)
ax.plot(lons[-1].T, lats[-1].T, color="yellow", linewidth=2, zorder=8, alpha=1)
ax.plot(lons[:, 0], lats[:, 0], color="yellow", linewidth=2, zorder=8, alpha=1)
ax.plot(
    lons[:, -1].T,
    lats[:, -1].T,
    color="yellow",
    linewidth=2,
    zorder=8,
    alpha=1,
    label="New Hysplit",
)

# ax.plot(lon, lat)
ax.set_xlabel("Lon")
ax.set_ylabel("Lat")

ax.set_xlim([-190, -25])
ax.set_ylim([10, 90])

ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, 1.01),
    ncol=2,
    fancybox=True,
    shadow=True,
)

# fig.tight_layout()
# plt.show()

fig.savefig(f"/Users/rodell/Desktop/d02-d01-" + save_file + ".png", dpi=240)
