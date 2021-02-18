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


from context import data_dir, root_dir, fwf_zarr_dir, wrf_dir

startTime = datetime.now()

domain = "d03"
# ## Set path to data
# filein = str(data_dir) + "/domain/n_hem.csv"

# ## Read data
# df = pd.read_csv(filein)

# ## Make 1D arrays of lat and lon
# lat = np.array(df["lat_degr"])
# lon = np.array(df["lon_degr"])

### Open old WRF domain
filein = str(wrf_dir) + f"/2021021700/wrfout_d01_2021-02-17_00:00:00"
wrf_d01 = xr.open_dataset(filein)

### Open new WRF domain
filein = str(wrf_dir) + f"/2021021700/wrfout_d02_2021-02-17_00:00:00"
wrf_d02 = xr.open_dataset(filein)

### Open new WRF domain
filein = str(wrf_dir) + f"/2021021700/wrfout_d03_2021-02-17_00:00:00"
wrf_d03 = xr.open_dataset(filein)

# ### Open new hysplit domain
filein = str(data_dir) + "/domain/dispersion.nc"
ds_hysplit = xr.open_dataset(filein)


Plot_Title = "Model Domains in Mercator Projection"
save_file = "/images/wrf4-hysplit-model-domains.png"
save_dir = str(data_dir) + save_file
# fig, ax = plt.subplots(figsize=[12, 8])
canada_east, canada_west = -20, -180
canada_north, canada_south = 90, 20

states_provinces = cfeature.NaturalEarthFeature(
    category="cultural",
    name="admin_1_states_provinces_lines",
    scale="50m",
    facecolor="none",
)


fig = plt.figure(figsize=[16, 8])
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(central_longitude=0))


ax.gridlines()
ax.add_feature(cfeature.LAND, zorder=1)
ax.add_feature(cfeature.LAKES, zorder=1)
ax.add_feature(cfeature.OCEAN, zorder=1)
ax.add_feature(cfeature.BORDERS, zorder=1)
ax.add_feature(cfeature.COASTLINE, zorder=1)
ax.add_feature(states_provinces, edgecolor="gray", zorder=2)
ax.set_xlabel("Longitude", fontsize=18)
ax.set_ylabel("Latitude", fontsize=18)

yticks = list(np.arange(10, 100, 10))
xticks = list(np.arange(10, 180, 10))

yticks[-1] = 89
ax.set_xticks(list(np.arange(-180, -10, 10)), crs=ccrs.PlateCarree())
ax.set_yticks(list(np.arange(10, 90, 10)), crs=ccrs.PlateCarree())
ax.yaxis.tick_right()
ax.yaxis.set_label_position("right")

ax.tick_params(axis="both", which="major", labelsize=14)
ax.tick_params(axis="both", which="minor", labelsize=14)

ax.set_title(Plot_Title, fontsize=20, weight="bold")
fig.subplots_adjust(hspace=0.8)
lats, lons = np.array(wrf_d01.XLAT), np.array(wrf_d01.XLONG)
lats, lons = lats[0], lons[0]
lons = np.where(lons > -179, lons, np.nan)
# lons += 180

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
    label="36 km WRF Domain",
)

lats, lons = np.array(wrf_d02.XLAT), np.array(wrf_d02.XLONG)
lats, lons = lats[0], lons[0]
# lons = np.where(lons < 179, lons, np.nan)
# lons += 180

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
    label="12 km WRF Domain",
)

lats, lons = np.array(wrf_d03.XLAT), np.array(wrf_d03.XLONG)
lats, lons = lats[0], lons[0]
# lons = np.where(lons < -179, lons, np.nan)
# lons += 180

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
    label="4 km WRF Domain",
)


lat_i, lon_i = ds_hysplit.YORIG, ds_hysplit.XORIG
nrows, ncols = ds_hysplit.NROWS, ds_hysplit.NCOLS
xcell, ycell = ds_hysplit.XCELL, ds_hysplit.YCELL
lat_f = (nrows * ycell) + lat_i
lon_f = (ncols * xcell) + lon_i
lats = np.arange(32, 70.1 + ycell, ycell)
lons = np.arange(-160, -52.4 + xcell, xcell)

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
    label="Hysplit Domain",
)


ax.set_xlim([-190, -30])
ax.set_ylim([20, 90])

ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, 1.0),
    ncol=4,
    fancybox=True,
    shadow=True,
)

plt.tight_layout()


fig.savefig(save_dir, dpi=240)
