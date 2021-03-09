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

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

## Define model/domain and datetime of interest
# date = pd.Timestamp("today")
date = pd.Timestamp(2018, 7, 20)
domain = "d02"
wrf_model = "wrf4"
save_file = f"/images/aspect-{wrf_model}-{domain}.png"
save_dir1 = str(data_dir) + save_file

save_file = f"/images/terrain-{wrf_model}-{domain}.png"
save_dir2 = str(data_dir) + save_file
## Path to hourly/daily fwi data
forecast_date = date.strftime("%Y%m%d06")
hourly_file_dir = (
    str(data_dir) + f"/FWF-WAN00CP-04/fwf-hourly-{domain}-{forecast_date}.zarr"
)

## Path to fuel converter spreadsheet
fuel_converter = str(data_dir) + "/fbp/fuel_converter.csv"
## Path to fuels data
fuelsin = str(data_dir) + f"/fbp/fuels-{wrf_model}-{domain}.zarr"
## Path to terrain data
# terrain = str(data_dir) + f"/terrain/hgt-{wrf_model}-{domain}.nc"
# terrain = f'/Users/rodell/Google Drive/Shared drives/WAN00CG-01/21030700/wrfout_{domain}_2021-03-08_02:00:00'


## Open hourly/daily fwi data
# hourly_ds = xr.open_zarr(hourly_file_dir)
# daily_ds = daily_merge_ds(forecast_date, domain, wrf_model)

## Open fuels converter
fc_df = pd.read_csv(fuel_converter)
fc_df = fc_df.drop_duplicates(subset=["CFFDRS"])
fc_df["Code"] = fc_df["National_FBP_Fueltypes_2014"]
## set index
fc_df = fc_df.set_index("CFFDRS")
fc_dict = fc_df.transpose().to_dict()
## Open gridded fuels
fuels_ds = xr.open_zarr(fuelsin)
## Open gridded terrain
terrain_ds = xr.open_dataset(terrain)


## Define Static Variables
ELV, LAT, LON, FUELS, dx, dy = (
    terrain_ds.HGT.values[0, :, :],
    terrain_ds.XLAT.values[0, :, :],
    terrain_ds.XLONG.values[0, :, :] * -1,
    fuels_ds.fuels.values.astype(int),
    # hourly_ds.WD,
    float(hourly_ds.attrs["DX"]),
    float(hourly_ds.attrs["DY"]),
)

# unique, count = np.unique(FUELS, return_counts=True)
# count[unique == fc_dict["M3"]["Code"]]

## create zeros array for easy conditional statements
shape = LAT.shape
zero_full = np.zeros(shape, dtype=float)
zero_full3D = np.zeros(hourly_ds.T.shape, dtype=float)


## Take gradient dx/dy of elevation, solve for, present group slope (GS) and slope azimuth angle (SAZ)
gradient = np.gradient(ELV)
y_grad = gradient[0]
x_grad = gradient[1]

## Solve Percent Ground Slope (37)
GS = 100 * np.sqrt((x_grad / dx) ** 2 + (y_grad / dy) ** 2)


ASPECT = np.arctan2((y_grad / dy), -(x_grad / dx)) * (180 / np.pi)


ASPECT = np.where(
    ASPECT < 0,
    90.0 - ASPECT,
    np.where(ASPECT > 90.0, 360.0 - ASPECT + 90.0, 90.0 - ASPECT),
)

# plt.contourf(LON, LAT, ASPECT)

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
if domain == "d02":
    res = "12 km"
elif domain == "d03":
    res = "4 km"
else:
    res = ""
Plot_Title = f"Aspect for WRF Domain {res}"
ax.set_title(Plot_Title, fontsize=20, weight="bold")

levels = np.arange(0, 360 + 22.5, 22.5)
cmap = cm.get_cmap("gist_rainbow", len(levels) - 2)  # PiYG
colors = []
for i in range(cmap.N):
    rgba = cmap(i)
    colors.append(matplotlib.colors.rgb2hex(rgba))

colors = [
    "#ff0029",
    "#ff3900",
    "#ff9c00",
    "#fffe00",
    "#9eff00",
    "#3bff00",
    "#00ff27",
    "#00ff89",
    "#00ffeb",
    "#00b0ff",
    "#004dff",
    "#1600ff",
    "#7900ff",
    "#dc00ff",
    "#ff00bf",
    "#ff0029",
]

contourf = ax.contourf(
    LON * -1,
    LAT,
    ASPECT,
    levels=levels,
    colors=colors,
    zorder=10,
    alpha=0.9,
)
fig.add_axes(ax_cb)
cbar = plt.colorbar(contourf, cax=ax_cb)
cbar.ax.axes.tick_params(length=0)

# ax.set_xlim([-126, -121])
# ax.set_ylim([48, 52])

if wrf_model == "wrf3":
    ax.set_xlim([-150, -54])
    ax.set_ylim([34, 70])
elif wrf_model == "wrf4":
    ax.set_xlim([-179.9, -29])
    ax.set_ylim([20, 80])
else:
    pass


fig.savefig(save_dir1, dpi=240)
print(f"Saved:  {save_dir1}")


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
if domain == "d02":
    res = "12 km"
elif domain == "d03":
    res = "4 km"
else:
    res = ""
Plot_Title = f"Terrain for WRF Domain {res}"
ax.set_title(Plot_Title, fontsize=20, weight="bold")


levels = np.arange(0, 3550, 50)

contourf = ax.contourf(
    LON * -1,
    LAT,
    ELV,
    levels=levels,
    cmap="terrain",
    zorder=10,
    alpha=0.9,
)

fig.add_axes(ax_cb)
cbar = plt.colorbar(contourf, cax=ax_cb)
cbar.ax.axes.tick_params(length=0)

# ax.set_xlim([-126, -121])
# ax.set_ylim([48, 52])

if wrf_model == "wrf3":
    ax.set_xlim([-150, -54])
    ax.set_ylim([34, 70])
elif wrf_model == "wrf4":
    ax.set_xlim([-179.9, -29])
    ax.set_ylim([20, 80])
else:
    pass


fig.savefig(save_dir2, dpi=240)
print(f"Saved:  {save_dir2}")
### Timer
print("Total Run Time: ", datetime.now() - startTime)


# grid = np.zeros((9,9))
# for i in range(9):
#   grid[i:,i:] = i

# lats = np.zeros((9,9))
# for i in range(9):
#   lats[-i-1,:] = (i+1) *10

# lngs = np.zeros((9,9))
# for i in range(9):
#   lngs[:,i] = (i+1) *20


# gradient = np.gradient(grid[:,::-1])
# y_grad = gradient[0]
# x_grad = gradient[1]

# dx, dy = 4,4
# GS = 100 * np.sqrt((x_grad / dx) ** 2 + (y_grad / dy) ** 2)

# ASPECT = np.arctan2((y_grad / dy), -(x_grad / dx)) * (180/np.pi)
# ASPECT = np.where(ASPECT < 0,
#             90.0 - ASPECT,
#             np.where(ASPECT > 90.0,
#             360.0 - ASPECT + 90.0,
#             90.0 - ASPECT))

# levels = np.arange(0,360+22.5,22.5)
# cmap = cm.get_cmap("gist_rainbow", len(levels)-2)  # PiYG
# colors = []
# for i in range(cmap.N):
#     rgba = cmap(i)
#     colors.append(matplotlib.colors.rgb2hex(rgba))

# colors =  ['#ff0029', '#ff3900', '#ff9c00', '#fffe00', '#9eff00', '#3bff00', '#00ff27', '#00ff89', '#00ffeb', '#00b0ff', '#004dff', '#1600ff', '#7900ff', '#dc00ff', '#ff00bf','#ff0029']

# contourf = plt.contourf(lngs, lats, ASPECT,
#     levels =levels,
#     colors= colors,
#     zorder=10,
#     alpha=0.9,
# )
# cbar = plt.colorbar(contourf)
