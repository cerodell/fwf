#!/Users/crodell/miniconda3/envs/fwx/bin/python


"""
Used to generate netcdf for each fire case study. The netcdf contains a small domain covering the fire at a 10 min sampling period. These take a while to generate.
"""
import context
import json
import salem
import os


import numpy as np
import xarray as xr
import pandas as pd
import geopandas as gpd
from scipy import stats
from pathlib import Path

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from sklearn.neighbors import KDTree

# import cartopy.crs as ccrs
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1 import make_axes_locatable
from netCDF4 import Dataset
from wrf import ll_to_xy

from context import data_dir, root_dir
import warnings

warnings.simplefilter("ignore")

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


goes = "g17"

date_range = pd.date_range(
    "2020-09-09T00", "2020-09-09T23", freq="10min"
) + pd.Timedelta(minutes=5)


def get_timestamp(file_name):
    return str(file_name).split("_")[-1].split(".")[0][1:]


goeslist = sorted(
    Path(f"/Volumes/WFRT-Ext22/frp/goes/{goes}/{date_range[0].strftime('%Y')}/").glob(
        f"*"
    ),
    key=get_timestamp,
)
goeslist_scan = np.array(
    [
        int(str(goeslist[i]).split("_")[-3].split(".")[0][5:8])
        for i in range(len(goeslist))
    ]
)
# i = np.where(goeslist_scan == date_range[0].dayofyear)[0][0]
# j = np.where(goeslist_scan == date_range[-1].dayofyear)[0][0]
# goeslist = goeslist[i - 2 : j + 2]

goes_ds_zero = xr.open_dataset(goeslist[0])

id = goes_ds_zero.attrs["platform_ID"]
if (id == "G17") or (id == "G18"):
    # row_slice, column_slice = slice(300,1500), slice(2900,3800)
    # row_slice, column_slice = slice(180, 1200), slice(2900, 3650)
    row_slice, column_slice = slice(220, 1100), slice(3000, 3750)
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
print(f"Lat max {float(lats.max())}, min  {float(lats.min())}")
print(f"Lon max {float(lons.max())}, min  {float(lons.min())}")
# # print(np.unique(np.isnan(lats), return_counts= True))
# # print(np.unique(np.isnan(lons), return_counts= True))

# shape = lats.shape
# locs = pd.DataFrame({"lats": lats.values.ravel(), "lons": lons.values.ravel()})
# ## build kdtree
# goes_tree = KDTree(locs)
# # print("Fire KDTree built")
# yy, xx = [], []
# df = pd.DataFrame(
#     {
#         "lat": [
#             case_info["min_lat"],
#             case_info["max_lat"],
#             case_info["max_lat"],
#             case_info["min_lat"],
#         ],
#         "lon": [
#             case_info["min_lon"],
#             case_info["min_lon"],
#             case_info["max_lon"],
#             case_info["max_lon"],
#         ],
#     }
# )
# for index, row in df.iterrows():
#     ## arange wx station lat and long in a formate to query the kdtree
#     single_loc = np.array([row.lat, row.lon]).reshape(1, -1)
#     ## query the kdtree retuning the distacne of nearest neighbor and index
#     dist, ind = goes_tree.query(single_loc, k=1)
#     ## set condition to pass on fire farther than 0.1 degrees
#     if dist > 0.1:
#         pass
#     else:
#         ## if condition passed reformate 1D index to 2D indexes
#         ind_2d = np.unravel_index(int(ind), shape)
#         ## append the indexes to lists
#         yy.append(ind_2d[0])
#         xx.append(ind_2d[1])
# lats, lons = lats.values, lons.values
# yy, xx = np.array(yy), np.array(xx)

# # print(f"Lower left {lats[yy[0],xx[0]]},  {lons[yy[0],xx[0]]}")
# # print(f"Upper left {lats[yy[1],xx[1]]},  {lons[yy[1],xx[1]]}")
# # print(f"Upper right {lats[yy[2],xx[2]]},  {lons[yy[2],xx[2]]}")
# # print(f"Lower right {lats[yy[3],xx[3]]},  {lons[yy[3],xx[3]]}")
# goes_ds_zero = goes_ds_zero.isel(
#     y=slice(yy.min(), yy.max()), x=slice(xx.min(), xx.max())
# )
# x_slice = slice(xx.min(), xx.max())
# y_slice = slice(yy.min(), yy.max())

# def open_goes(path):
#     ds = xr.open_dataset(path).isel(y=row_slice, x=column_slice)[
#         ["Power", "Temp", "DQF", "Mask", "Area"]
#     ]
#     return ds.isel(y=y_slice, x=x_slice).chunk("auto")

# goes_ds_fire = xr.combine_nested([open_goes(path) for path in goeslist], "t")
# goes_ds_fire = goes_ds_fire.assign_coords(
#     lats=(("y", "x"), goes_ds_zero.lats.values)
# )
# goes_ds_fire = goes_ds_fire.assign_coords(
#     lons=(("y", "x"), goes_ds_zero.lons.values)
# )
# goes_ds_fire.to_netcdf(
#     str(data_dir) + f"/frp/analysis/goes/{case_study}-goes-test.nc", mode="w"
# )

# print(np.unique(np.isnan(goes_ds_fire["Power"]), return_counts=True))
# print("-----------------------")
# print(case_study)
# print("PASS")
# print("-----------------------")
