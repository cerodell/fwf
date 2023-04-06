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

config = {"wrf": ["d02", "d03"], "eccc": ["rdps", "hrdps"]}


# model = 'wrf'
# domain = 'd02'
trail_name = "01"
# doi = pd.Timestamp("2021-06-28")
# date_range = pd.date_range("2021-01-01", "2022-10-31")
date_range = pd.date_range("2021-01-01", "2022-12-31")
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
]
drop_vars = ["DSR", "SNOWC", "r_o_hourly", "r_o_tomorrow", "SNOWH"]
drop_cords = ["XLAT", "XLONG", "west_east", "south_north", "XTIME"]
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


def get_locs(pyproj_srs):
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
    return x, y


def read_fwf(doi, model, domain):
    """
    opens datasets, index on day one forecast and drop variables not use for comparison
    """
    if model == "wrf":
        hour = "06"
    else:
        hour = "00"
    ds = salem.open_xr_dataset(
        fwf_dir
        + f"{model}/{domain}/{trail_name}/fwf-daily-{domain}-{doi.strftime('%Y%m%d')}{hour}.nc"
    )
    ds = ds.isel(time=0).chunk(chunks="auto")
    ds = ds.drop([var for var in list(ds) if var in drop_vars])
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

    x, y = get_locs(ds.attrs["pyproj_srs"])
    ds = ds.interp(west_east=x, south_north=y, method="linear")
    ds = ds.drop([var for var in list(ds) if var in drop_cords])
    ds = ds.expand_dims(dim={"domain": [domain]})
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


# test_ds = rename(read_fwf(pd.Timestamp("2021-01-01"), "wrf", "d02"), "d02")
# test_ds = test_ds.expand_dims(dim ={'time': [test_ds.Time.values]})

################# End Functions ####################

loop = datetime.now()
## open and loop model_configs and date_range than concat and merge them into one dataset
ds = xr.merge(
    [
        xr.concat(
            [rename(read_fwf(doi, model, domain), domain) for doi in date_range],
            dim="time",
        )  # .expand_dims(dim ={'domain': [domain]})
        for model in config
        for domain in config[model]
    ],
    compat="override",
)
ds = rechunk(ds)
print("Loop Time: ", datetime.now() - loop)

merge = datetime.now()
## merge the forecasted values at wx station with their observed values
final_ds = xr.merge([ds, ds_obs.expand_dims(dim={"domain": ["obs"]})])
for var in ["elev", "name", "prov", "id"]:
    final_ds[var] = final_ds[var].astype(str)

final_ds = rechunk(final_ds)
final_ds = final_ds.compute()
print("Merge Time: ", datetime.now() - merge)

# make a file directory based on user inputs to save dataset
make_dir = Path(str(data_dir) + f"/intercomp/{trail_name}/")
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

# print(final_ds.time.values)
### Timer
print("Total Run Time: ", datetime.now() - startTime)
