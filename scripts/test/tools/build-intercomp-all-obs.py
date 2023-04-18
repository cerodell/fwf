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
config = {"ecmwf": ["era5"]}
# config = {"wrf": ["d02", "d03"]}


# model = 'wrf'
# domain = 'd02'
trail_name = "03"

# date_range = pd.date_range("2021-01-01", "2021-01-10")
date_range = pd.date_range("2020-01-01", "2022-12-31")
fwf_dir = f"/Volumes/WFRT-Ext24/fwf-data/"

################## END INPUTS ##################

var_list = [
    "TD",
    "Df",
    "S",
    "TMAX",
    "FS_days",
    "T",
    "dFS",
    "WD",
    "W",
    "r_w",
    "P",
    "F",
    "r_o",
    "FS",
    "R",
    "H",
    "D",
    "U",
    # 'mF',
    # 'mR',
    # 'mS',
    # 'hF',
    # 'hR',
    # 'hS',
    # 'mT',
    # 'mW',
    # 'mH',
    # 'mFt',
    # 'mRt',
    # 'mSt',
    # 'mTt',
    # 'mWt',
    # 'mHt',
]
drop_vars = ["DSR", "SNOWC", "r_o_hourly", "r_o_tomorrow", "SNOWH"]
drop_cords = ["XLAT", "XLONG", "west_east", "south_north", "XTIME", "time"]
#################### Open static datasets ####################

## open modle config file with varible names and attibutes
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

## Open Data Attributes for writing
with open(str(root_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)

## open master obs file and slice along date range of interest
ds_obs = xr.open_dataset(str(data_dir) + f"/obs/observations-d02-20191231-20221231.nc")
ds_obs = ds_obs.sel(
    time=slice(date_range[0].strftime("%Y-%m-%d"), date_range[-1].strftime("%Y-%m-%d"))
)

idx = np.where(
    (ds_obs.prov == "BC")
    | (ds_obs.prov == "AB")
    | (ds_obs.prov == "SA")
    | (ds_obs.prov == "YT")
    | (ds_obs.prov == "NT")
)[0]
ds_obs = ds_obs.isel(wmo=idx)

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

# pyproj_srs = '+proj=stere +lat_0=90 +lat_ts=53.25 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs'
pyproj_srs = "+proj=longlat +datum=WGS84 +no_defs"
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

# def get_locs(pyproj_srs):
# gpm25 = gpd.GeoDataFrame(
#     df,
#     crs="EPSG:4326",
#     #  crs="+init=epsg:4326",
#     geometry=gpd.points_from_xy(df["lons"], df["lats"]),
# ).to_crs(pyproj_srs)

# x = xr.DataArray(
#     np.array(gpm25.geometry.x),
#     dims="wmo",
#     coords=dict(wmo=gpm25.wmo.values),
# )
# y = xr.DataArray(
#     np.array(gpm25.geometry.y),
#     dims="wmo",
#     coords=dict(wmo=gpm25.wmo.values),
# )
# return x, y


def read_fwf(doi, model, domain):
    """
    opens datasets, index on day one forecast and drop variables not use for comparison
    """
    hour = "00"
    ds = (
        xr.open_dataset(
            fwf_dir
            + f"{model}/{domain}/{trail_name}/fwf-daily-{domain}-{doi.strftime('%Y%m%d')}{hour}.nc"
        )
        .isel(time=0)
        .chunk(chunks="auto")[var_list]
    )
    # print(ds.attrs["pyproj_srs"])
    return ds


def rename(ds, domain):
    """
    renames datasets to match master observation dataset
    """
    for var in var_list:
        try:
            name_lower = cmaps[var]["name"].lower()
            # print(name_lower)
            ds[name_lower] = ds[var]
            ds = ds.drop([var])
        except:
            try:
                ds[var.lower()] = ds[var]
                if var == "r_w":
                    pass
                else:
                    ds = ds.drop([var])
            except:
                pass

    # x, y = get_locs(ds.attrs["pyproj_srs"])
    ds = ds.interp(west_east=x, south_north=y, method="linear")
    ds = ds.drop([var for var in list(ds.coords) if var in drop_cords])
    ds = ds.expand_dims(dim={"domain": [domain]})
    return ds


def interp(ds, domain):
    ds = ds.interp(west_east=x, south_north=y, method="linear")
    ds = ds.drop([var for var in list(ds.coords) if var in drop_cords])
    ds = ds.expand_dims(dim={"domain": [domain]})
    return ds


def rechunk(ds):
    """
    rechucks datasets and unify them for better storage and use
    """
    ds = ds.chunk(chunks="auto")
    ds = ds.unify_chunks()
    for var in list(ds):
        ds[var].encoding = {}
    return ds


################# End Functions ####################
loop_start = datetime.now()
ds = xr.combine_by_coords(
    [
        xr.combine_nested(
            [rename(read_fwf(doi, model, domain), domain) for doi in date_range],
            concat_dim="time",
        ).chunk("auto")
        for model in config
        for domain in config[model]
    ]
)
print("Loop Time: ", datetime.now() - loop_start)

# loop_start = datetime.now()
# ## open and loop model_configs and date_range than concat and merge them into one dataset
# ds = xr.combine_by_coords(
#     [
#         interp(xr.combine_nested(
#             [rename(read_fwf(doi, model, domain), domain) for doi in date_range],
#             concat_dim="time",
#         ).chunk('auto'), domain)
#         for model in config
#         for domain in config[model]
#     ]
# )
# # ds = rechunk(ds)
# print("Loop Time: ", datetime.now() - loop_start)

# compute_start = datetime.now()
# ds = ds.compute()
# print("Compute Time: ", datetime.now() - compute_start)


merge = datetime.now()
## merge the forecasted values at wx station with their observed values
final_ds = xr.combine_by_coords([ds, ds_obs.expand_dims(dim={"domain": ["obs"]})])
for var in ["elev", "name", "prov", "id"]:
    final_ds[var] = final_ds[var].astype(str)
for var in list(ds):
    final_ds[var] = final_ds[var].astype("float32")
final_ds = final_ds.drop("time")
print("Merge Time: ", datetime.now() - merge)

# make a file directory based on user inputs to save dataset
make_dir = Path(str(data_dir) + f"/intercomp/{trail_name}/era5/")
make_dir.mkdir(parents=True, exist_ok=True)

write = datetime.now()
## write final dataset as netcdf
final_ds, encoding = compressor(final_ds, var_dict=None)
final_ds.to_netcdf(
    str(make_dir)
    + f'/{date_range[0].strftime("%Y%m%d")}-{date_range[-1].strftime("%Y%m%d")}.nc',
    mode="w",
    encoding=encoding,
)
print("Write Time: ", datetime.now() - write)

# # print(final_ds.time.values)
# ### Timer
# print("Total Run Time: ", datetime.now() - startTime)
