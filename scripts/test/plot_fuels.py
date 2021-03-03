import context
import json
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

from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

## Choose wrf domain
domain = "d02"
wrf_model = "wrf3"
save_file = f"/images/cffdrs-{wrf_model}-{domain}.png"
save_dir = str(data_dir) + save_file

## Path to Fuel converter spreadsheet
fuel_converter = str(data_dir) + "/fbp/fuel_converter.csv"
## Path to any wrf file used in transformation
fuelsin = str(data_dir) + f"/fbp/fuels-{wrf_model}-{domain}.zarr"
## Open all files mentioned above
fc_df = pd.read_csv(fuel_converter)
fc_df = fc_df.drop_duplicates(subset=["CFFDRS"])
ds = xr.open_zarr(fuelsin)

unique, count = np.unique(ds.fuels.values, return_counts=True)

unique = unique.astype(int)
drop_levels = list(
    set(list(unique.astype(str)))
    ^ set(list(fc_df.National_FBP_Fueltypes_2014.astype(str)))
)

for level in drop_levels:
    fc_df = fc_df[fc_df.National_FBP_Fueltypes_2014 != int(level)]


lngs = ds.XLONG.values
lats = ds.XLAT.values

fillarray = ds["fuels"].values

# fillarray = np.round(fillarray, 0)
# fillarray = ndimage.gaussian_filter(fillarray, sigma=0)


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
Plot_Title = f"Canadian Forest FBP Fuel Type Grid for WRF Domain {res}"
ax.set_title(Plot_Title, fontsize=20, weight="bold")


length = len(fc_df.Colors.values[:-3])
colors = fc_df.Colors.values[:-3]
levels = unique
# levels = np.linspace(levels[0], levels[-1] + 1, length + 1).astype(int)

# levels[-1] = 122
# Cnorm = matplotlib.colors.Normalize(vmin=levels.min(), vmax=levels.max() + 1)
contourf = ax.contourf(
    lngs,
    lats,
    fillarray + 0.5,
    levels=levels,
    # norm=Cnorm,
    colors=colors,
    extend="max",
    zorder=4,
    alpha=0.9,
)

fig.add_axes(ax_cb)
ticks = fc_df.CFFDRS.values[:-4]
# tick_levels = fc_df.National_FBP_Fueltypes_2014.values[:-3].astype(float)
tick_levels = list(np.array(levels) - 0.5)
# tick_levels[-1] = levels[-1]
cbar = plt.colorbar(contourf, cax=ax_cb, ticks=tick_levels)
cbar.ax.set_yticklabels(ticks)  # set ticks of your format
cbar.ax.axes.tick_params(length=0)


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
print(f"Saved:  {save_dir}")
### Timer
print("Total Run Time: ", datetime.now() - startTime)
