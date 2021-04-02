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


domain = "d02"
wrf_model = "wrf3"

### Open any wrf dataset
### Get a wrf file
if wrf_model == "wrf3":
    wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CP-04/18072000/wrfout_{domain}_2018-07-20_11:00:00"
else:
    wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CG-01/21022000/wrfout_{domain}_2021-02-20_11:00:00"
wrf_ds = xr.open_dataset(wrf_filein)
dx, dy = float(wrf_ds.attrs["DX"]), float(wrf_ds.attrs["DY"])

wrf_ds = wrf_ds.HGT.to_dataset()
wrf_ds = wrf_ds.isel(Time=0)
try:
    wrf_ds = wrf_ds.drop_vars("XTIME")
except:
    pass


### Open tzone ST dataset
tzone_st_filein = str(tzone_dir) + f"/tzone_{wrf_model}_{domain}-ST.zarr"
tzone_st_ds = xr.open_zarr(tzone_st_filein)
tzone_st_ds["ZoneST"] = tzone_st_ds["Zone"]
tzone_st_ds = tzone_st_ds.drop_vars("Zone")

### Open tzone DT dataset
tzone_dt_filein = str(tzone_dir) + f"/tzone_{wrf_model}_{domain}-DT.zarr"
tzone_dt_ds = xr.open_zarr(tzone_dt_filein)
tzone_dt_ds["ZoneDT"] = tzone_dt_ds["Zone"]
tzone_dt_ds = tzone_dt_ds.drop_vars("Zone")

### Open fuels  dataset
fuels_fielin = str(data_dir) + f"/fbp/fuels-{wrf_model}-{domain}-test.zarr"
fuels_ds = xr.open_zarr(fuels_fielin)
fuels_ds["FUELS"] = fuels_ds["fuels"]
fuels_ds = fuels_ds.drop_vars("fuels")


## Solve a few static variable in the FBP system and add to terrain dataframe
## Take gradient dz/dx and dz/dy of elevation
gradient = np.gradient(wrf_ds.HGT)
y_grad = gradient[0]
x_grad = gradient[1]

## Solve Percent Ground Slope (37)
GS = 100 * np.sqrt((x_grad / dx) ** 2 + (y_grad / dy) ** 2)
GS = xr.DataArray(GS, name="GS", dims=("south_north", "west_east"))
wrf_ds["GS"] = GS
wrf_ds["GS"].attrs = {
    "FieldType": 104,
    "MemoryOrder": "XY ",
    "description": "Percent Ground Slope",
    "projection": "PolarStereographic(stand_lon=-110.0, moad_cen_lat=53.99999237060547, truelat1=57.0, truelat2=90.0, pole_lat=90.0, pole_lon=0.0)",
    "units": "%",
}
# Solve for slope Aspect
ASPECT = np.arctan2((y_grad / dy), -(x_grad / dx)) * (180 / np.pi) + 180
ASPECT = xr.DataArray(ASPECT, name="ASPECT", dims=("south_north", "west_east"))
wrf_ds["ASPECT"] = ASPECT
wrf_ds["ASPECT"].attrs = {
    "FieldType": 104,
    "MemoryOrder": "XY ",
    "description": "Terrain Slope Aspect",
    "projection": "PolarStereographic(stand_lon=-110.0, moad_cen_lat=53.99999237060547, truelat1=57.0, truelat2=90.0, pole_lat=90.0, pole_lon=0.0)",
    "units": "degrees",
}

# Solve for Uphill slope Azimuth Angle (SAZ)
SAZ = np.where(
    ASPECT < 0,
    90.0 - ASPECT,
    np.where(ASPECT > 90.0, 360.0 - ASPECT + 90.0, 90.0 - ASPECT),
)
SAZ = xr.DataArray(SAZ, name="SAZ", dims=("south_north", "west_east"))
wrf_ds["SAZ"] = SAZ
wrf_ds["SAZ"].attrs = {
    "FieldType": 104,
    "MemoryOrder": "XY ",
    "description": "Terrain Slope Azimuth Angle",
    "projection": "PolarStereographic(stand_lon=-110.0, moad_cen_lat=53.99999237060547, truelat1=57.0, truelat2=90.0, pole_lat=90.0, pole_lon=0.0)",
    "units": "degrees",
}

## Merge all static zarr files
static_ds = xr.merge([tzone_st_ds, tzone_dt_ds, fuels_ds, wrf_ds])
static_ds = static_ds.drop_vars("south_north")
static_ds = static_ds.drop_vars("west_east")
try:
    static_ds = static_ds.drop_vars("XTIME")
except:
    pass

## set attributes for each static file
static_ds.ZoneDT.attrs = {
    "FieldType": 104,
    "MemoryOrder": "XY ",
    "description": "Day Light Savings Time Zone Offsets From UTC",
    "pyproj_srs": "+proj=stere +lat_0=90 +lat_ts=57 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs",
    "units": "hours_",
}

static_ds.ZoneST.attrs = {
    "FieldType": 104,
    "MemoryOrder": "XY ",
    "description": "Standard Time Time Zone Offsets From UTC",
    "pyproj_srs": "+proj=stere +lat_0=90 +lat_ts=57 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs",
    "units": "hours_",
}

static_ds.HGT.attrs = {
    "FieldType": 104,
    "MemoryOrder": "XY ",
    "description": "Terrain Height",
    "pyproj_srs": "+proj=stere +lat_0=90 +lat_ts=57 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs",
    "units": "meters",
}

static_ds.FUELS.attrs = {
    "FieldType": 104,
    "MemoryOrder": "XY ",
    "description": "CFFDRS Fuels Type",
    "pyproj_srs": "+proj=stere +lat_0=90 +lat_ts=57 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs",
    "units": "fuel type code",
}

## Write to static dataset to zarr file
static_ds = static_ds.compute()

static_ds.to_zarr(
    str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}.zarr", mode="w"
)
print(f"Wrote: {str(data_dir)}/static/static-vars-{wrf_model}-{domain}.zarr")
