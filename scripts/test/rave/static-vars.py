#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import context
import salem
import dask
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime

from context import root_dir, data_dir


adda_dem = salem.open_xr_dataset(
    str(data_dir) + "/adda/wrfout_d01_2001-06-30_21_00_00"
).isel(Time=0)

rave_static = salem.open_xr_dataset(str(data_dir) + "/static/static-rave-3km-grid.nc")
adda_static = salem.open_xr_dataset(
    str(data_dir) + "/static/static-vars-adda-d01-old.nc"
).drop_vars("blank")

dx, dy = float(adda_dem.attrs["DX"]), float(adda_dem.attrs["DY"])


## Solve a few static variable in the FBP system and add to terrain dataframe
## Take gradient dz/dx and dz/dy of elevation
gradient = np.gradient(adda_dem["HGT"])
y_grad = gradient[0]
x_grad = gradient[1]

## Solve Percent Ground Slope (37)
GS = 100 * np.sqrt((x_grad / dx) ** 2 + (y_grad / dy) ** 2)
GS = xr.DataArray(GS, name="GS", dims=("south_north", "west_east"))
adda_static["GS"] = GS
adda_static["GS"].attrs = {
    "description": "Percent Ground Slope",
    "units": "%",
}
# Solve for slope Aspect
ASPECT = np.arctan2((y_grad / dy), -(x_grad / dx)) * (180 / np.pi) + 180
ASPECT = np.where(ASPECT > 360, ASPECT - 360, ASPECT)
ASPECT = xr.DataArray(ASPECT, name="ASPECT", dims=("south_north", "west_east"))
adda_static["ASPECT"] = ASPECT
adda_static["ASPECT"].attrs = {
    "description": "Terrain Slope Aspect",
    "units": "degrees",
}

# Solve for Uphill slope Azimuth Angle (SAZ)
SAZ = np.where(
    ASPECT < 0,
    90.0 - ASPECT,
    np.where(ASPECT > 90.0, 360.0 - ASPECT + 90.0, 90.0 - ASPECT),
)
SAZ = xr.DataArray(SAZ, name="SAZ", dims=("south_north", "west_east"))
adda_static["SAZ"] = SAZ
adda_static["SAZ"].attrs = {
    "description": "Terrain Slope Azimuth Angle",
    "units": "degrees",
}


for var in list(adda_static):
    adda_static[var].attrs["pyproj_srs"] = adda_static.attrs["pyproj_srs"]


rave_dem = rave_static.salem.transform(adda_static, interp="nearest")

rave_dem = rave_dem.sel(
    x=slice(-180, -27), y=slice(20, 75)
)  # Select a specific spatial region
rave_dem.to_netcdf(str(data_dir) + "/static/static-rave-3km.nc", mode="w")
