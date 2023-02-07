import context

import salem
import numpy as np
import xarray as xr
import geopandas as gpd
import pandas as pd
from context import data_dir


wrfd02_ds = salem.open_wrf_dataset(
    str(data_dir) + f"/wrf/wrfout_d02_2021-01-14_00:00:00"
)
tempd02 = wrfd02_ds.T2.isel(time=0)

## define the desired grid resolution in meters
resolution = 4_000  # grid cell size in meters

x0, x1 = float(wrfd02_ds.west_east.min()), float(wrfd02_ds.west_east.max())
y0, y1 = float(wrfd02_ds.south_north.min()), float(wrfd02_ds.south_north.max())

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

wrfd02_dsT = krig_ds.salem.transform(tempd02, interp="spline")
# lon, lat = wrfd02_dsT.salem.grid.ll_coordinates


wrfd03_ds = salem.open_wrf_dataset(
    str(data_dir) + f"/wrf/wrfout_d03_2021-01-14_00:00:00"
)
tempd03 = wrfd03_ds.T2.isel(time=0)

wrfd03_dsT = krig_ds.salem.transform(tempd03, interp="spline")


test = xr.where(wrfd03_dsT.notnull(), wrfd03_dsT, wrfd02_dsT)

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
