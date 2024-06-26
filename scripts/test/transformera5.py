import context

import numpy as np
import xarray as xr
import geopandas as gpd
import pandas as pd


import salem

from netCDF4 import Dataset
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from context import data_dir
from pykrige.ok import OrdinaryKriging
from datetime import datetime


from wrf import (to_np, getvar, smooth2d, get_cartopy, cartopy_xlim,
                 cartopy_ylim, latlon_coords)

# Open the NetCDF file
ncfile = Dataset(str(data_dir) + f"/wrf/wrfout_d02_2021-01-14_00:00:00")

# Get the sea level pressure
slp = getvar(ncfile, "slp")

cart_proj = get_cartopy(slp)


era5_ds = salem.open_xr_dataset(str(data_dir) + f"/era5/download.nc")
era5_ds = era5_ds.isel(time = 20)
era5_ds["tp"] = era5_ds["tp"]*1000
df = era5_ds["tp"].to_dataframe().reset_index()

wrfd02_ds = salem.open_wrf_dataset(str(data_dir) + f"/wrf/wrfout_d02_2021-01-14_00:00:00")
tempd02 =  wrfd02_ds.T2.isel(time = 0)

## define the desired grid resolution in meters
resolution = 4_000  # grid cell size in meters

x0, x1 = float(wrfd02_ds.west_east.min()),  float(wrfd02_ds.west_east.max())
y0, y1 = float(wrfd02_ds.south_north.min()),  float(wrfd02_ds.south_north.max())

## make grid based on dataset bounds and resolution
gridx = np.arange(x0, x1, resolution)
gridy = np.arange(y0, y1, resolution)

## use salem to create a dataset with the grid.
krig_ds = salem.Grid(
    nxny=(len(gridx), len(gridy)),
    dxdy=(resolution, resolution),
    x0y0=(x0, y0),
    proj="+R=6370000 +lat_0=90 +lat_ts=53.25 +lon_0=-110 +no_defs+proj=stere +units=m +x_0=0 +y_0=0",
    pixel_ref="corner",
).to_dataset()
## print dataset
krig_ds

wrfd02_dsT = krig_ds.salem.transform(tempd02, interp='spline')
# lon, lat = wrfd02_dsT.salem.grid.ll_coordinates



wrfd03_ds = salem.open_wrf_dataset(str(data_dir) + f"/wrf/wrfout_d03_2021-01-14_00:00:00")
tempd03 =  wrfd03_ds.T2.isel(time = 0)

wrfd03_dsT = krig_ds.salem.transform(tempd03, interp='spline')



test = xr.where(wrfd03_dsT.notnull(),wrfd03_dsT+10, wrfd02_dsT )

resolution = 1000
## make grid based on dataset bounds and resolution
gridx = np.arange(x0, x1, resolution)
gridy = np.arange(y0, y1, resolution)

## use salem to create a dataset with the grid.
krig_ds = salem.Grid(
    nxny=(len(gridx), len(gridy)),
    dxdy=(resolution, resolution),
    x0y0=(x0, y0),
    proj="+R=6370000 +lat_0=90 +lat_ts=53.25 +lon_0=-110 +no_defs+proj=stere +units=m +x_0=0 +y_0=0",
    pixel_ref="corner",
).to_dataset()
## print dataset
krig_ds


testT = krig_ds.salem.transform(test, interp='spline')
















# wrfd02_dsT['lon'], wrfd02_dsT['lat'] = lon, lat
# gpm25 = gpd.GeoDataFrame(
#     df,
#     crs="EPSG:4326",
#     geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
# ).to_crs("North_Pole_Stereographic")
# gpm25["Easting"], gpm25["Northing"] = gpm25.geometry.x, gpm25.geometry.y
# gpm25.head()


# nlags = 15
# variogram_model = "spherical"

# startTime = datetime.now()
# krig = OrdinaryKriging(
#     x=gpm25["Easting"],
#     y=gpm25["Northing"],
#     z=gpm25["tp"],
#     variogram_model=variogram_model,
#     # enable_statistics=True,
#     nlags=nlags,
# )
# print(f"OK build time {datetime.now() - startTime}")


# ax = plt.axes(projection=cart_proj)
# ax.set_global()
# era5_dsT["tp"].plot(
#     ax=ax,
#     transform=ccrs.PlateCarree(),
#     # levels=[0, 5, 10, 20, 40, 80, 160, 300, 600],
#     cmap="Reds",
# )
# ax.coastlines()
# ax.set_extent([-180, -49, 25, 80], crs=ccrs.PlateCarree())