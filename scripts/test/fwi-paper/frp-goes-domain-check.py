#!/Users/crodell/miniconda3/envs/fwf/bin/python

import context
import json

import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path

import cartopy.crs as ccrs
import matplotlib.pyplot as plt

from context import data_dir, root_dir


__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

#################### INPUTS ####################


case_study = "lazy_fire"
print(case_study)
################## END INPUTS ####################

#################### OPEN FILES ####################
## open case study json file
with open(str(root_dir) + f"/json/fire-cases.json", "r") as fp:
    case_dict = json.load(fp)

case_info = case_dict[case_study]
domain = case_info["domain"]
goes = case_info["goes"]
df = pd.DataFrame(
    {
        "lat": [
            case_info["min_lat"],
            case_info["max_lat"],
            case_info["max_lat"],
            case_info["min_lat"],
        ],
        "lon": [
            case_info["min_lon"],
            case_info["min_lon"],
            case_info["max_lon"],
            case_info["max_lon"],
        ],
    }
)

date_range = pd.date_range(
    case_info["date_range"][0], case_info["date_range"][1], freq="10min"
) + pd.Timedelta(minutes=5)
filein = f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/02/"


def get_timestamp(file_name):
    return str(file_name).split("_")[-1].split(".")[0][1:]


goeslist = sorted(
    Path(f"/Volumes/WFRT-Ext22/frp/goes/{goes}/{date_range[0].strftime('%Y')}/").glob(
        f"*"
    ),
    key=get_timestamp,
)
goes_ds_zero = xr.open_dataset(goeslist[0])
print(goes_ds_zero.attrs["platform_ID"])
print(goes_ds_zero.t.values)
goes_ds_last = xr.open_dataset(goeslist[-1])
print(goes_ds_last.t.values)
file_date_range = pd.date_range(
    str(goes_ds_zero.t.values)[:-13], str(goes_ds_last.t.values)[:-13], freq="10min"
)
i = file_date_range.get_loc(date_range[0])
j = file_date_range.get_loc(date_range[-1])
goeslist = goeslist[i - 10 : j + 10]

id = goes_ds_zero.attrs["platform_ID"]
if (id == "G17") or (id == "G18"):
    row_slice, column_slice = slice(220, 1100), slice(3000, 3750)
    row_slice, column_slice = slice(800, 1600), slice(3500, 4500)
    latlon_ds = xr.open_dataset(
        str(data_dir) + f"/frp/goes/goes18_abi_full_disk_lat_lon.nc"
    ).isel(rows=row_slice, columns=column_slice)
elif id == "G16":
    row_slice, column_slice = slice(285, 1100), slice(1530, 3150)
    latlon_ds = xr.open_dataset(
        str(data_dir) + f"/frp/goes/goes16_abi_full_disk_lat_lon.nc"
    ).isel(rows=row_slice, columns=column_slice)
else:
    raise ValueError("Cant find static lat/lon DS for GOES file")

goes_ds_zero = goes_ds_zero.isel(y=row_slice, x=column_slice)
goes_ds_zero = goes_ds_zero.assign_coords(lats=(("y", "x"), latlon_ds.latitude.values))
goes_ds_zero = goes_ds_zero.assign_coords(lons=(("y", "x"), latlon_ds.longitude.values))
lats, lons = goes_ds_zero.lats, goes_ds_zero.lons

import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
import cartopy.crs as crs
from cartopy.feature import NaturalEarthFeature


print(np.unique(np.isnan(lats), return_counts=True))
# Create a figure
fig = plt.figure(figsize=(12, 6))
# Set the GeoAxes to the projection used by WRF
if (id == "G17") or (id == "G18"):
    ax = plt.axes(
        projection=crs.Geostationary(
            central_longitude=-136.9,
            satellite_height=35786.0234375 * 1000,
            false_easting=0,
            false_northing=0,
            globe=None,
            sweep_axis="x",
        )
    )
elif id == "G16":
    ax = plt.axes(
        projection=crs.Geostationary(
            central_longitude=-75.2,
            satellite_height=35786.0234375 * 1000,
            false_easting=0,
            false_northing=0,
            globe=None,
            sweep_axis="x",
        )
    )
# Download and add the states and coastlines
states = NaturalEarthFeature(
    category="cultural",
    scale="50m",
    facecolor="none",
    name="admin_1_states_provinces_shp",
)
ax.add_feature(states, linewidth=0.5, edgecolor="black")
ax.coastlines("50m", linewidth=0.8)

# Make the contour outlines and filled contours for the smoothed sea level
# pressure.
plt.contourf(lons, lats, np.zeros_like(lats) + 2, 10, transform=crs.PlateCarree())

for index, row in df.iterrows():
    plt.scatter(row["lon"], row["lat"], transform=crs.PlateCarree(), color="red")
# Add a color bar
plt.colorbar(ax=ax, shrink=0.98)

# Set the map bounds
# ax.set_xlim(cartopy_xlim(smooth_slp))
# ax.set_ylim(cartopy_ylim(smooth_slp))

# Add the gridlines
ax.gridlines(color="black", linestyle="dotted")

# plt.title("Sea Level Pressure (hPa)")

plt.show()
