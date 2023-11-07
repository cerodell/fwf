#!/Users/crodell/miniconda3/envs/fwx/bin/python

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

#################### INPUTS ####################


## define model domain and path to fwf data
save_fig = True

################## END INPUTS ####################

#################### OPEN FILES ####################

## open case study json file
with open(str(root_dir) + f"/json/fire-cases.json", "r") as fp:
    case_dict = json.load(fp)

case_list = list(case_dict)
remove = ["oak_fire", "caldor_fire"]
new_list = [x for x in case_list if x not in remove]
# "heather_lake_fire"
for case_study in ["boston_bar"]:
    # try:
    print("Starting   ", case_study)
    case_info = case_dict[case_study]
    domain = case_info["domain"]
    goes = case_info["goes"]

    date_range = pd.date_range(
        case_info["date_range"][0], case_info["date_range"][1], freq="10min"
    ) + pd.Timedelta(minutes=5)
    filein = f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/02/"

    def get_timestamp(file_name):
        return str(file_name).split("_")[-1].split(".")[0][1:]

    goeslist = sorted(
        Path(
            f"/Volumes/WFRT-Ext22/frp/goes/{goes}/{date_range[0].strftime('%Y')}/"
        ).glob(f"*"),
        key=get_timestamp,
    )
    goeslist_scan = np.array(
        [
            int(str(goeslist[i]).split("_")[-3].split(".")[0][5:8])
            for i in range(len(goeslist))
        ]
    )
    i = np.where(goeslist_scan == date_range[0].dayofyear)[0][0]
    j = np.where(goeslist_scan == date_range[-1].dayofyear)[0][0]

    goes_ds_zero = xr.open_dataset(goeslist[0])
    # # print(goes_ds_zero.attrs['platform_ID'])
    # # print(goes_ds_zero.t.values)
    # goes_ds_last = xr.open_dataset(goeslist[-1])
    # # print(goes_ds_last.t.values)
    # file_date_range = pd.date_range(str(goes_ds_zero.t.values)[:-13],str(goes_ds_last.t.values)[:-13], freq='10min')
    # i = file_date_range.get_loc(date_range[0])
    # j = file_date_range.get_loc(date_range[-1])
    goeslist = goeslist[i - 10 : j + 10]

    id = goes_ds_zero.attrs["platform_ID"]
    if (id == "G17") or (id == "G18"):
        # row_slice, column_slice = slice(300,1500), slice(2900,3800)
        # row_slice, column_slice = slice(180, 1200), slice(2900, 3650)
        row_slice, column_slice = slice(220, 1100), slice(3000, 3750)
        if case_study == "lazy_fire":
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
    goes_ds_zero = goes_ds_zero.assign_coords(
        lats=(("y", "x"), latlon_ds.latitude.values)
    )
    goes_ds_zero = goes_ds_zero.assign_coords(
        lons=(("y", "x"), latlon_ds.longitude.values)
    )
    lats, lons = goes_ds_zero.lats, goes_ds_zero.lons
    # print(f"Lat max {lats.max()}, min  {lats.min()}")
    # print(f"Lon max {lons.max()}, min  {lons.min()}")
    # print(np.unique(np.isnan(lats), return_counts= True))
    # print(np.unique(np.isnan(lons), return_counts= True))

    shape = lats.shape
    locs = pd.DataFrame({"lats": lats.values.ravel(), "lons": lons.values.ravel()})
    ## build kdtree
    goes_tree = KDTree(locs)
    # print("Fire KDTree built")
    yy, xx = [], []
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
    for index, row in df.iterrows():
        ## arange wx station lat and long in a formate to query the kdtree
        single_loc = np.array([row.lat, row.lon]).reshape(1, -1)
        ## query the kdtree retuning the distacne of nearest neighbor and index
        dist, ind = goes_tree.query(single_loc, k=1)
        ## set condition to pass on fire farther than 0.1 degrees
        if dist > 0.1:
            pass
        else:
            ## if condition passed reformate 1D index to 2D indexes
            ind_2d = np.unravel_index(int(ind), shape)
            ## append the indexes to lists
            yy.append(ind_2d[0])
            xx.append(ind_2d[1])
    lats, lons = lats.values, lons.values
    yy, xx = np.array(yy), np.array(xx)

    # print(f"Lower left {lats[yy[0],xx[0]]},  {lons[yy[0],xx[0]]}")
    # print(f"Upper left {lats[yy[1],xx[1]]},  {lons[yy[1],xx[1]]}")
    # print(f"Upper right {lats[yy[2],xx[2]]},  {lons[yy[2],xx[2]]}")
    # print(f"Lower right {lats[yy[3],xx[3]]},  {lons[yy[3],xx[3]]}")
    goes_ds_zero = goes_ds_zero.isel(
        y=slice(yy.min(), yy.max()), x=slice(xx.min(), xx.max())
    )
    x_slice = slice(xx.min(), xx.max())
    y_slice = slice(yy.min(), yy.max())

    def open_goes(path):
        ds = xr.open_dataset(path).isel(y=row_slice, x=column_slice)[
            ["Power", "Temp", "DQF", "Mask", "Area"]
        ]
        return ds.isel(y=y_slice, x=x_slice).chunk("auto")

    goes_ds_fire = xr.combine_nested([open_goes(path) for path in goeslist], "t")
    goes_ds_fire = goes_ds_fire.assign_coords(
        lats=(("y", "x"), goes_ds_zero.lats.values)
    )
    goes_ds_fire = goes_ds_fire.assign_coords(
        lons=(("y", "x"), goes_ds_zero.lons.values)
    )
    goes_ds_fire.to_netcdf(
        str(data_dir) + f"/frp/analysis/goes/{case_study}-goes-test.nc", mode="w"
    )

    print(np.unique(np.isnan(goes_ds_fire["Power"]), return_counts=True))
    print("-----------------------")
    print(case_study)
    print("PASS")
    print("-----------------------")
# except:
#     print("======================")
#     print(case_study)
#     print("FAIL")
#     print("======================")


# frp = frp_ds['Power'].mean(dim=['x','y'])
# frp_date_range = frp['t'].values
# keep_dates = np.where((frp_date_range <= pd.to_datetime('2020-01-01'))==False)
# frp = frp.isel(t = keep_dates[0])
# frp = frp.sortby('t')
# frp = frp.resample(t="1H").mean()
# frp = frp.interpolate_na(dim="t", method="linear")

# date_range = frp['t'].values
# date_range2 = pd.date_range(
#     date_range[0] - np.timedelta64(1, "D"),
#     date_range[-1] + np.timedelta64(2, "D"),
#     freq="D",
# )
# ## open fwf hourly
# hourly_ds = xr.combine_nested([open_fwf(doi, "hourly") for doi in date_range2], "time")
# hourly_ds["time"] = hourly_ds["Time"]


# shape = hourly_ds.XLAT.shape
# locs = pd.DataFrame({"lats": hourly_ds.XLAT.values.ravel(), "lons": hourly_ds.XLONG.values.ravel()})
# ## build kdtree
# fwf_tree = KDTree(locs)
# print("Fire KDTree built")
# yy, xx  = [], []
# df = pd.DataFrame(
#     {'lat': [case_info['min_lat'],case_info['max_lat'], case_info['max_lat'], case_info['min_lat']],
#      'lon': [case_info['min_lon'],case_info['min_lon'], case_info['max_lon'], case_info['max_lon']]
#     }
# )
# for index, row in df.iterrows():
#     ## arange wx station lat and long in a formate to query the kdtree
#     single_loc = np.array([row.lat, row.lon]).reshape(1, -1)
#     ## query the kdtree retuning the distacne of nearest neighbor and index
#     dist, ind = fwf_tree.query(single_loc, k=1)
#     ## set condition to pass on fire farther than 0.1 degrees
#     if dist > 0.1:
#         pass
#     else:
#         ## if condition passed reformate 1D index to 2D indexes
#         ind_2d = np.unravel_index(int(ind), shape)
#         ## append the indexes to lists
#         yy.append(ind_2d[0])
#         xx.append(ind_2d[1])
# yy, xx = np.array(yy), np.array(xx)

# hourly_ds_test = hourly_ds.isel(south_north = slice(yy.min(),yy.max()), west_east= slice(xx.min(),xx.max())).sel(time = slice(date_range[0], date_range[-1]))
# hourly_ds_test = hourly_ds_test.mean(dim = ['south_north', 'west_east'])


# frp_slice = frp.sel(t = slice('2021-09-16T00', '2021-09-29T00'))
# hourly_ds_slice = hourly_ds_test.sel(time = slice('2021-09-16T00', '2021-09-29T00'))

# fig = plt.figure(figsize=(12, 6))
# ax = fig.add_subplot(1, 1, 1)
# ax.plot(hourly_ds_slice.Time, hourly_ds_slice['S'].values, color="tab:blue", lw=1.2, label="Hourly")
# ax2 = ax.twinx()
# ax2.plot(frp_slice.t, frp_slice, color="tab:red", lw=1.2, label="FRP")


# fwi_t = hourly_ds_slice['S'].values
# frp_t = frp_slice.values
# nas = np.logical_or(np.isnan(fwi_t), np.isnan(frp_t))
# pearsonr_h_interp_final = stats.pearsonr(fwi_t[~nas], frp_t[~nas])
# print(pearsonr_h_interp_final[0])
# # ## get py projection as str
# # proj = '+proj=geos +a=6378137.0 +b=6356752.31414 +rf=298.2572221 +lon_0=-75.0 +lat_0=0.0 +h=35786023.0 +x_0=0 +y_0=0 +units=m +sweep=x +no_defs +type=crs'


# # ## get domains rotated lat and lon and attributes
# # lons = goes_ds.x.values
# # lats = goes_ds.y.values
# # # nx, ny = ds_grib[var].attrs["GRIB_Nx"], ds_grib[var].attrs["GRIB_Ny"]
# # # dx, dy = (
# # #     ds_grib[var].attrs["GRIB_iDirectionIncrementInDegrees"],
# # #     ds_grib[var].attrs["GRIB_jDirectionIncrementInDegrees"],
# # # )

# # ## get domain lower left corner as lat and lon
# # x = [lons[0, 0]]
# # y = [lats[0, 0]]

# # ## make a dataframe of domain's lower left corner as lat and lon
# # d = {"lats": y, "lons": x}
# # df = pd.DataFrame(data=d)

# # ## transform lat and lon cords from a lat-lon grid to eccc grid
# # gdf = gpd.GeoDataFrame(
# #     df,
# #     crs="EPSG:4326",
# #     geometry=gpd.points_from_xy(df["lons"], df["lats"]),
# # ).to_crs(proj)
# # gdf["Easting"], gdf["Northing"] = gdf.geometry.x, gdf.geometry.y
# # # gdf.head()

# # ## make grid with associated py projection
# # domain_grid = salem.Grid(
# #     nxny=(nx, ny),
# #     dxdy=(dx, dy),
# #     x0y0=(gdf["Easting"].values[0], gdf["Northing"].values[0]),
# #     proj=proj,
# # ).to_dataset()

# # lon, lat = domain_grid.salem.grid.ll_coordinates

# # domain_grid["XLAT"] = (("south_north", "west_east"), lon)
# # domain_grid["XLONG"] = (("south_north", "west_east"), lat)
# # domain_grid = domain_grid.set_coords(["XLAT", "XLONG"])
# # domain_grid = domain_grid.rename_dims(
# #     {
# #         "x": "west_east",
# #         "y": "south_north",
# #     }
# # )
# # domain_grid = domain_grid.rename(
# #     {
# #         "x": "west_east",
# #         "y": "south_north",
# #     }
# # )
# # domain_grid.to_netcdf(str(data_dir) + f"/eccc/{domain}-grid.nc", mode="w")
