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
wrf_model = "wrf4"

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
fuels_fielin = str(data_dir) + f"/fbp/fuels-{wrf_model}-{domain}.zarr"
fuels_ds = xr.open_zarr(fuels_fielin)
fuels_ds["FUELS"] = fuels_ds["fuels"]
fuels_ds = fuels_ds.drop_vars("fuels")

### Open terrain  dataset
if wrf_model == "wrf3":
    terrain_filein = str(data_dir) + f"/terrain/hgt-{wrf_model}-{domain}.nc"
    terrain_ds = xr.open_dataset(terrain_filein)
else:
    terrain_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CG-01/21030700/wrfout_{domain}_2021-03-08_02:00:00"
    terrain_ds = xr.open_dataset(terrain_filein)
    terrain_ds = terrain_ds.HGT.to_dataset()
    terrain_ds = terrain_ds.isel(Time=0)
    terrain_ds = terrain_ds.drop_vars("XTIME")

## Merge all static zarr files
static_ds = xr.merge([tzone_st_ds, tzone_dt_ds, fuels_ds, terrain_ds])
static_ds = static_ds.drop_vars("south_north")
static_ds = static_ds.drop_vars("west_east")
static_ds = static_ds.drop_vars("XTIME")

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
