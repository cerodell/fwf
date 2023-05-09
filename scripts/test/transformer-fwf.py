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

fwf_d02_ds =xr.open_dataset("/Volumes/Scratch/FWF-WAN00CG/d02/202107/fwf-daily-d02-2021070106.nc")
fwf_d03_ds = xr.open_dataset("/Volumes/Scratch/FWF-WAN00CG/d03/202107/fwf-daily-d03-2021070106.nc")

wrf_d02_ds = salem.open_wrf_dataset(str(data_dir) + f"/wrf/wrfout_d02_2021-01-14_00:00:00")
wrf_d03_ds = salem.open_wrf_dataset(str(data_dir) + f"/wrf/wrfout_d03_2021-01-14_00:00:00")

grid_d02 = wrf_d02_ds.salem.grid.to_dataset()
grid_d03 = wrf_d03_ds.salem.grid.to_dataset()

fwf_d02_ds = xr.merge([grid_d02, fwf_d02_ds])
fwf_d03_ds = xr.merge([grid_d03, fwf_d03_ds])




# tempd02 =  wrf_d02_ds.T2.isel(time = 0)

# ## define the desired grid resolution in meters
# resolution = 4_000  # grid cell size in meters

# x0, x1 = float(wrf_d02_ds.west_east.min()),  float(wrf_d02_ds.west_east.max())
# y0, y1 = float(wrf_d02_ds.south_north.min()),  float(wrf_d02_ds.south_north.max())

# ## make grid based on dataset bounds and resolution
# gridx = np.arange(x0, x1, resolution)
# gridy = np.arange(y0, y1, resolution)

# ## use salem to create a dataset with the grid.
# krig_ds = salem.Grid(
#     nxny=(len(gridx), len(gridy)),
#     dxdy=(resolution, resolution),
#     x0y0=(x0, y0),
#     proj="+R=6370000 +lat_0=90 +lat_ts=53.25 +lon_0=-110 +no_defs+proj=stere +units=m +x_0=0 +y_0=0",
#     pixel_ref="corner",
# ).to_dataset()
# ## print dataset
# krig_ds

# wrf_d02_dsT = krig_ds.salem.transform(tempd02, interp='spline')
# # lon, lat = wrf_d02_dsT.salem.grid.ll_coordinates



# wrf_d03_ds = salem.open_wrf_dataset(str(data_dir) + f"/wrf/wrfout_d03_2021-01-14_00:00:00")
# tempd03 =  wrf_d03_ds.T2.isel(time = 0)

# wrf_d03_dsT = krig_ds.salem.transform(tempd03, interp='spline')



# test = xr.where(wrf_d03_dsT.notnull(),wrf_d03_dsT+10, wrf_d02_dsT )

# resolution = 1000
# ## make grid based on dataset bounds and resolution
# gridx = np.arange(x0, x1, resolution)
# gridy = np.arange(y0, y1, resolution)

# ## use salem to create a dataset with the grid.
# krig_ds = salem.Grid(
#     nxny=(len(gridx), len(gridy)),
#     dxdy=(resolution, resolution),
#     x0y0=(x0, y0),
#     proj="+R=6370000 +lat_0=90 +lat_ts=53.25 +lon_0=-110 +no_defs+proj=stere +units=m +x_0=0 +y_0=0",
#     pixel_ref="corner",
# ).to_dataset()
# ## print dataset
# krig_ds


# testT = krig_ds.salem.transform(test, interp='spline')
















# wrf_d02_dsT['lon'], wrf_d02_dsT['lat'] = lon, lat
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