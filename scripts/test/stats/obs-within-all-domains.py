#!/Users/crodell/miniconda3/envs/fwf/bin/python

import context
import io
import json
import requests
import salem

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from glob import glob
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from wrf import ll_to_xy, xy_to_ll
from datetime import datetime, date, timedelta
from utils.compressor import compressor, file_size

from context import data_dir, root_dir

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

#################### INPUTS ####################

# config = {"wrf": ["d02", "d03"], "eccc": ["rdps", "hrdps"]}
# config = {"ecmwf": ["era5"]}
config = {"wrf": ["d02", "d03"]}

trail_name = "02"
model_save = "wrf_day2"
# date_range = pd.date_range("2021-04-01", "2021-11-01")
date_range = pd.date_range("2021-01-01", "2022-12-31")
fwf_dir = f"/Volumes/WFRT-Ext24/fwf-data/"

################## END INPUTS ##################

#################### Open static datasets ####################

## Open Data Attributes for writing
with open(str(root_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)

## open master obs file and slice along date range of interest
ds_obs = xr.open_dataset(str(data_dir) + f"/obs/observations-d02-20191231-20221231.nc")

ds_obs_d03 = xr.open_dataset(
    str(data_dir) + f"/obs/observations-d03-20191231-20221231.nc"
)

ds_obs = ds_obs.sel(wmo=ds_obs_d03.wmo)

hrdps_ds = xr.open_dataset(
    "/Volumes/WFRT-Ext24/fwf-data/eccc/hrdps/02/fwf-daily-hrdps-2021110700.nc"
)


## convert lat lon coordinate in master obs to meter base x y as define by wrf polar stere projection
df = pd.DataFrame(
    data={
        "lons": ds_obs.lons.values,
        "lats": ds_obs.lats.values,
        "wmo": ds_obs.wmo.values,
    }
)
#######################################################################


############################### Functions #############################

pyproj_srs = xr.open_dataset(
    str(data_dir) + f"/static/static-vars-eccc-hrdps.nc"
).attrs["pyproj_srs"]
print(pyproj_srs)
# pyproj_srs = "+proj=longlat +datum=WGS84 +no_defs"
gpm25 = gpd.GeoDataFrame(
    df,
    crs="EPSG:4326",
    #  crs="+init=epsg:4326",
    geometry=gpd.points_from_xy(df["lons"], df["lats"]),
).to_crs(pyproj_srs)

x = xr.DataArray(
    np.array(gpm25.geometry.x),
    dims="wmo",
    coords=dict(wmo=gpm25.wmo.values),
)
y = xr.DataArray(
    np.array(gpm25.geometry.y),
    dims="wmo",
    coords=dict(wmo=gpm25.wmo.values),
)


hrdps_wx = hrdps_ds.interp(south_north=y, west_east=x, method="linear")

hrdps_wx = hrdps_wx.dropna(dim="wmo")

final_ds = ds_obs.sel(wmo=hrdps_wx.wmo)

for var in ["elev", "name", "prov", "id"]:
    final_ds[var] = final_ds[var].astype(str)
for var in list(final_ds):
    final_ds[var] = final_ds[var].astype("float32")

write = datetime.now()
## write final dataset as netcdf
final_ds, encoding = compressor(final_ds, var_dict=var_dict)
final_ds.to_netcdf(
    str(data_dir) + f"/obs/observations-all-20191231-20221231.nc",
    mode="w",
    encoding=encoding,
)
print("Write Time: ", datetime.now() - write)
