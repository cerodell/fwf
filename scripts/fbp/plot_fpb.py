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


date = pd.Timestamp(2018, 7, 18)
domain = "d02"
wrf_model = "wrf3"


## Path to fuel converter spreadsheet
fuel_converter = str(data_dir) + "/fbp/fuel_converter.csv"
fc_df = pd.read_csv(fuel_converter)
fc_df = fc_df.drop_duplicates(subset=["CFFDRS"])
fc_df["Code"] = fc_df["National_FBP_Fueltypes_2014"]
## set index
fc_df = fc_df.set_index("CFFDRS")
fc_dict = fc_df.transpose().to_dict()


# filein = f"/Volumes/cer/fireweather/data/fwf-hourly-{domain}-2018040106-2018100106.zarr"
# ds = xr.open_zarr(filein)

ds = xr.open_zarr(str(vol_dir) + "/fwf-daily-d02-2019040100-2019100100.zarr")
ds["time"] = ds.Time.values
ds = ds.sel(time="2019-05-11")


# ## Path to fuels data terrain data
# static_filein = str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}.zarr"
# static_ds = xr.open_zarr(static_filein)
# FUELS = static_ds.FUELS

# HFI = ds.HFI.values
# ROS = ds.ROS.values

# HFI_t = HFI[:, FUELS == fc_dict["C2"]["Code"]]
# ROS_t = ROS[:, FUELS == fc_dict["C2"]["Code"]]

# plt.plot(HFI_t[:, 1000])
# plt.plot(ROS_t[:, 1000])


# ds.coords["time"] = ds.Time


var = "HFI"
# levels = np.arange(0, 20000, 100)
levels = [0, 10, 500, 2000, 4000, 10000, 30000, 40000]
colors = ["#0000ff", "#00c0c0", "#008001", "#01e001", "#ffff00", "#dfa000", "#ff0000"]
save_file = f"/images/{var}-{wrf_model}-{domain}.png"
save_dir = str(data_dir) + save_file
# ds = ds.loc[dict(time="2018-08-18T20")]


day_hour = np.datetime_as_string(ds.Time, unit="h")
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
ax.tick_params(axis="both", which="major", labelsize=14)
ax.tick_params(axis="both", which="minor", labelsize=14)

## add title and adjust subplot buffers
if domain == "d02":
    res = "12 km"
elif domain == "d03":
    res = "4 km"
else:
    res = ""
Plot_Title = f"{'HFI'} at {day_hour} \n {wrf_model} {res}"
ax.set_title(Plot_Title, fontsize=20, weight="bold")

Cnorm = matplotlib.colors.Normalize(vmin=int(np.min(levels)), vmax=int(np.max(levels)))
contourf = ax.contourf(
    ds.XLONG,
    ds.XLAT,
    ds[var],
    levels=levels,
    extend="both",
    colors=colors,
    norm=Cnorm,
    zorder=10,
    alpha=1,
)

plt.scatter(-113.540, 56, zorder=10, color="hotpink", s=500)

# contourf = ax.pcolormesh(ds.XLONG, ds.XLAT, ds[var], zorder=10, norm=Cnorm, cmap="RdYlBu_r", shading='flat')
fig.add_axes(ax_cb)
cbar = plt.colorbar(contourf, cax=ax_cb)

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
