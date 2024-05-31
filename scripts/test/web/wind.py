import context
import os
import salem
from salem import wgs84
import json
import math
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
import geopandas as gpd

import matplotlib.pyplot as plt

from datetime import datetime, timedelta

from context import data_dir, root_dir


model = "wrf"
domain = "d02"
# doi = pd.Timestamp("today")
doi = pd.Timestamp("2023-05-15T06")


def solve_W_WD(ds):

    ## Define the latitude and longitude arrays in degrees
    lons_rad = np.deg2rad(ds["XLONG"])
    lats_rad = np.deg2rad(ds["XLAT"])

    ## Calculate rotation angle
    theta = np.arctan2(np.cos(lats_rad) * np.sin(lons_rad), np.sin(lats_rad))

    ## Calculate sine and cosine of rotation angle
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    ## Define the u and v wind components in domain coordinates
    u_domain = ds["U10"]
    v_domain = ds["V10"]

    ## Rotate the u and v wind components to Earth coordinates
    u_earth = u_domain * cos_theta - v_domain * sin_theta
    v_earth = u_domain * sin_theta + v_domain * cos_theta
    ds["U10e"] = u_earth
    ds["V10e"] = v_earth

    ## Solve for wind speed
    wsp = np.sqrt(u_earth ** 2 + v_earth ** 2)
    ds["W"] = wsp

    ## Solve for wind direction on Earth coordinates
    wdir = 180 + ((180 / np.pi) * np.arctan2(u_earth, v_earth))
    ds["WD"] = wdir

    return ds




ds = salem.open_xr_dataset(
    f'/bluesky/archive/fireweather/data/fwf-hourly-d03-{doi.strftime("%Y%m%d06")}.nc'
)



ds = ds[["U10", "V10", "W", "WD"]]
ds = solve_W_WD(ds)
for var in ds:
    ds[var].attrs["pyproj_srs"] = ds.attrs["pyproj_srs"]
grid = ds.salem.grid

extent = np.round(grid.extent_in_crs(crs=wgs84), 1)

forecastBounds = [[32.0, -160.0], [70.0, -52.0]]

## define the desired  grid resolution in degrees
resolution = .05  # grid cell size in degress

## make grid based on dataset bounds and resolution
g_lon = np.arange(
    extent[0],
    extent[1] + resolution,
    resolution,
)
g_lat = np.arange(
    extent[2],
    extent[3] + resolution,
    resolution,
)

## use salem to create a dataset with the grid.
target_grid = salem.Grid(
    nxny=(len(g_lon), len(g_lat)),
    dxdy=(resolution, resolution),
    x0y0=(extent[0], extent[2]),
    proj="EPSG:4326",
    pixel_ref="corner",
).to_dataset()
## print dataset
target_grid


ds_trans = target_grid.salem.transform(ds, interp="spline")


# ds_trans['W'] = (('y','x'),np.sqrt(ds_trans['U10'].values**2+ ds_trans['V10'].values**2))
# ds_trans['W'].attrs
lenght = len(ds_trans.Time)
index = np.arange(0, lenght, 3, dtype=int)
timestamp = np.array(ds_trans.Time.dt.strftime("%Y%m%d%H")).tolist()

for i in index:
    ds_i = ds_trans.isel(time=i)
    U10 = ds_i["U10"].values[::-1].ravel()  # [::-1]
    V10 = ds_i["V10"].values[::-1].ravel()
    XLAT = ds_i["y"].values.ravel()
    XLONG = ds_i["x"].values.ravel()

    U10[np.isnan(U10)] = 0.0
    V10[np.isnan(V10)] = 0.0
    U10 = np.round(U10, 2)
    V10 = np.round(V10, 2)

    # fig = plt.figure(figsize=(12, 6))
    # ax = fig.add_subplot(1, 1, 1)
    # xx, yy = np.meshgrid(g_lon, g_lat)
    # ax.quiver(xx, yy, ds_i["U10e"].values, ds_i["V10e"].values, zorder=10)
    # ds_i['WD'].salem.quick_map(ax = ax, vmin = 0, vmax = 360)
    # xx, yy = np.meshgrid(g_lon, g_lat)

    u_json = {
        "header": {
            "parameterUnit": "m.s-1",
            "parameterNumber": 2,
            "parameterNumberName": "eastward_wind",
            "parameterCategory": 2,
            "nx": len(XLONG),
            "ny": len(XLAT),
            "refTime": "2017-02-01 23:00:00",
            "lo1": extent[0] + 360,
            "la1": extent[3],
            "lo2": extent[1] + 360,
            "la2": extent[2],
            "dx": resolution,
            "dy": resolution,
        },
        "data": U10.tolist(),
    }

    v_json = {
        "header": {
            "parameterUnit": "m.s-1",
            "parameterNumber": 3,
            "parameterNumberName": "northward_wind",
            "parameterCategory": 2,
            "nx": len(XLONG),
            "ny": len(XLAT),
            "refTime": "2017-02-01 23:00:00",
            "lo1": extent[0] + 360,
            "la1": extent[3],
            "lo2": extent[1] + 360,
            "la2": extent[2],
            "dx": resolution,
            "dy": resolution,
        },
        "data": V10.tolist(),
    }


    with open(f"/bluesky/fireweather/fwf/web_dev/data/map/wd-{timestamp[i]}.json", "w") as outfile:
        json.dump([u_json, v_json], outfile, indent=4)


# os.system(
#     "scp -r /Users/crodell/fwf/json/wind.json fwfop@bluesky2.eoas.ubc.ca:/bluesky/fireweather/fwf/web_dev/data/"
# )
