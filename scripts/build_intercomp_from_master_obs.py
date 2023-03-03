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
from utils.make_intercomp import daily_merge_ds
from utils.compressor import compressor, file_size

from context import data_dir

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

#################### INPUTS ####################
wrf_model = "wrf4"
domain = "d02"
date_range = pd.date_range("2021-01-01", "2022-10-31")
# date_range = pd.date_range("2021-01-0", "2021-01-10")

fwf_dir = "/Volumes/WFRT-Data02/FWF-WAN00CG/d02/"
model_config = ["_wrf03", "_wrf04", "_wrf05", "_wrf06", "_wrf07"]

trail_name = "WRF" + "".join(model_config).replace("_wrf", "").upper()
model_name = "fwf"

# model_config = [ "_era505",  "_era506"]
# trail_name = 'ERA50506'
# model_name = 'era5'
################## END INPUTS ##################


## Define varible to remove from forecasts datasets
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
]

if model_name == "fwf":
    time_formate = "%Y%m%d06"
    drop_vars = ["DSR", "SNOWC", "r_o_hourly", "r_o_tomorrow"]
    drop_vars2 = ["XLAT", "XLONG", "west_east", "south_north", "XTIME"]
elif model_name == "era5":
    time_formate = "%Y%m%d00"
    drop_vars = ["DSR", "SNOWH", "r_o_hourly", "r_o_tomorrow"]
    drop_vars2 = ["XLAT", "XLONG", "west_east", "south_north", "time"]
else:
    raise ValueError(f"Invalid model name {model_name}")

## open modle config file with varible names and attibutes
with open(str(data_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

## Open Data Attributes for writing
with open(str(data_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)

## open master obs file and slice along date range of interest
# ds_obs = xr.open_zarr(str(data_dir) + "/obs/observations-d02-20191231-20221231.zarr")
ds_obs = xr.open_dataset(str(data_dir) + "/obs/observations-d02-20191231-20221231.nc")
ds_obs = ds_obs.sel(
    time=slice(date_range[0].strftime("%Y-%m-%d"), date_range[-1].strftime("%Y-%m-%d"))
)

## convert lat lon cordniate in master obs to meter base x y as define by wrf polar stere projection
df = pd.DataFrame(
    data={
        "lons": ds_obs.lons.values,
        "lats": ds_obs.lats.values,
        "wmo": ds_obs.wmo.values,
    }
)
gpm25 = gpd.GeoDataFrame(
    df,
    crs="EPSG:4326",
    #  crs="+init=epsg:4326",
    geometry=gpd.points_from_xy(df["lons"], df["lats"]),
).to_crs(
    "+proj=stere +lat_0=90 +lat_ts=53.25 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs"
)

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


#################### Functions ####################


def read_fwf(doi, model):
    """
    opens datasets, index on day one forecast and drop variables not use for comparison
    """
    ds = salem.open_xr_dataset(
        fwf_dir
        + f"/{model.strip('_').upper()}/{model_name}/fwf-daily-{domain}-{doi}.nc"
    )
    ds = ds.isel(time=0).chunk(chunks="auto")
    ds = ds.drop(drop_vars)
    return ds


def interpolate(ds, x, y, method):
    """
    interpolates datasets to wxstation locations
    """
    ds = ds.interp(west_east=x, south_north=y, method=method)
    return ds


def rename(ds, model):
    """
    renames datasets to match master observation dataset
    """
    for var in var_list:
        try:
            name_lower = cmaps[var]["name"].lower()
            # print(name_lower)
            ds[name_lower + model] = ds[var]
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

    ds = ds.interp(west_east=x, south_north=y, method="linear")
    ds = ds.drop(drop_vars2)
    return ds


def rechunk(ds):
    """
    rechucks datasets and unifys them for better storage and use
    """
    ds = ds.chunk(chunks="auto")
    ds = ds.unify_chunks()
    for var in list(ds):
        ds[var].encoding = {}
    return ds


################# End Functions ####################

loop = datetime.now()
## open and loop model_configs and date_range than concat and merge them into one dataset
ds = xr.merge(
    [
        xr.concat(
            [
                rename(read_fwf(doi.strftime(time_formate), model), model)
                for doi in date_range
            ],
            dim="time",
        )
        for model in model_config
    ],
    compat="override",
)
ds = rechunk(ds)
print("Loop Time: ", datetime.now() - loop)

merge = datetime.now()
## merge the forecasted values at wx station with their observed values
final_ds = xr.merge([ds, ds_obs])
for var in ["elev", "name", "prov", "id"]:
    final_ds[var] = final_ds[var].astype(str)

final_ds = rechunk(final_ds)
final_ds = final_ds.compute()
print("Merge Time: ", datetime.now() - merge)

## make a file directory based on user inputs to save dataset
make_dir = Path(str(data_dir) + f"/intercomp/{domain}/{trail_name}/")
make_dir.mkdir(parents=True, exist_ok=True)

write = datetime.now()
## write final dataset as netcdf
# final_ds, encoding = compressor(final_ds, var_dict)
final_ds.to_netcdf(
    str(make_dir)
    + f'/{date_range[0].strftime("%Y%m%d")}-{date_range[-1].strftime("%Y%m%d")}.nc',
    mode="w",
    # encoding=encoding,
)
print("Write Time: ", datetime.now() - write)

# print(final_ds.time.values)
### Timer
print("Total Run Time: ", datetime.now() - startTime)
