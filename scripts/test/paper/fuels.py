import context
import json
import random
import salem

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

from context import data_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

## Choose wrf domain
domain = "d03"
wrf_model = "wrf4"
save_file = f"/images/cffdrs-{wrf_model}-{domain}-test.png"
save_dir = str(data_dir) + save_file

## Path to Fuel converter spreastatic_dsheet
fuel_converter = str(data_dir) + "/fbp/fuel_converter.csv"
## Path to any wrf file used in transformation
fuelsin = str(data_dir) + f"/fbp/fuels-{wrf_model}-{domain}-test.zarr"
## Open all files mentioned above
fc_df = pd.read_csv(fuel_converter)
fc_df = fc_df.drop_duplicates(subset=["CFFDRS"])
fc_df["Code"] = fc_df["National_FBP_Fueltypes_2014"]
# fc_df = fc_df.set_index("CFFDRS")
fc_dict = fc_df.transpose().to_dict()

static_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
)

fuels = static_ds.FUELS.values

# XLAT = static_ds.XLAT.values.ravel()
# fuels = static_ds.fuels.values.ravel()
# mask = list(np.where((XLAT< 56.0) & (fuels == 122))[0])
# fuels[mask] = np.random.choice([113,116],len(mask))
# mask = list(np.where((XLAT< 56.0) & (fuels == 113))[0])
# fuels[mask] = np.random.choice([113,116],len(mask))

# fuels = np.reshape(fuels, static_ds.fuels.shape)


# # static_ds['fuels'] = fuels


# unique, count = np.unique(static_ds.fuels.values, return_counts=True)
# count[unique==fc_dict["S1"]["Code"]]

# unique = unique.astype(int)
# fuels = static_ds.fuels


# fuels = xr.where((static_ds.XLAT.values< 55.0) & (fuels == 122), 113, fuels)
# fuels = xr.where(fuels == 122, 116, fuels)

# drop_levels = list(
#     set(list(unique.astype(str)))
#     ^ set(list(fc_df.National_FBP_Fueltypes_2014.astype(str)))
# )

# for level in drop_levels:
#     fc_df = fc_df[fc_df.National_FBP_Fueltypes_2014 != int(level)]

lngs = static_ds.XLONG.values
lats = static_ds.XLAT.values

fillarray = fuels

levels = []
for i in range(0, len(fc_df.National_FBP_Fueltypes_2014.values)):
    fillarray[fillarray == fc_df.National_FBP_Fueltypes_2014.values[i]] = i
    levels.append(i)


## make fig for make with projection
fig = plt.figure(figsize=[16, 8])
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

divider = make_axes_locatable(ax)
ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)

# cax = divider.append_axes('right', size='5%', pad=0.05)
## bring in state/prov boundaries
states_provinces = cfeature.NaturalEarthFeature(
    category="cultural",
    name="admin_1_states_provinces_lines",
    scale="50m",
    facecolor="none",
)


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
Plot_Title = f"Canadian Forest FBP Fuel Type Grid for WRF Domain {res}"
ax.set_title(Plot_Title, fontsize=20, weight="bold")


colors = fc_df.Colors.values.tolist()
cmap = matplotlib.colors.ListedColormap(colors)
Cnorm = matplotlib.colors.BoundaryNorm(levels, cmap.N)
# Cnorm = matplotlib.colors.Normalize(vmin=int(np.min(levels)), vmax=int(np.max(levels)) + 1)

# length = len(fc_df.Colors.values)
# colors = fc_df.Colors.values
# Cnorm = matplotlib.colors.Normalize(vmin=int(np.min(levels)), vmax=int(np.max(levels)) + 1)

contourf = ax.pcolormesh(lngs, lats, fillarray + 0.5, zorder=10, norm=Cnorm, cmap=cmap)
fig.add_axes(ax_cb)
# ticks = fc_df.CFFDRS.values[:-4]
ticks = fc_df.CFFDRS.values

# tick_levels = fc_df.National_FBP_Fueltypes_2014.values[:-3].astype(float)
tick_levels = list(np.array(levels) - 0.5)
# tick_levels[-1] = levels[-1]
cbar = plt.colorbar(contourf, cax=ax_cb, ticks=tick_levels)
# cbar = plt.colorbar(contourf, cax=ax_cb)
cbar.ax.set_yticklabels(ticks)  # set ticks of your format
cbar.ax.axes.tick_params(length=0)


## set map bounstatic_ds
if wrf_model == "wrf3":
    ax.set_xlim([-140, -60])
    ax.set_ylim([36, 70])
elif wrf_model == "wrf4":
    ax.set_xlim([-174, -30])
    ax.set_ylim([25, 80])
else:
    pass

# fig.savefig(save_dir, dpi=240)
# print(f"Saved:  {save_dir}")
# ### Timer
# print("Total Run Time: ", datetime.now() - startTime)
