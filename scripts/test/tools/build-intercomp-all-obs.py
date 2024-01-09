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

# config = {"ecmwf": ["era5"]}
config = {"wrf": ["d02", "d03"]}
# config = {"eccc": ["hrdps", "rdps"], "wrf": ["d02", "d03"]}


trail_name = "04"
# model_save = list(config.keys())[0]
# domain_save = config[model_save][0]
model_save = "wrf"
domain_save = "d03"
lead_time = 1

# date_range = pd.date_range("2021-01-01", "2021-01-10")
date_range = pd.date_range("2021-01-01", "2022-12-31")
fwf_dir = f"/Volumes/WFRT-Ext24/fwf-data/"

# make a file directory based on user inputs to save dataset
save_dir = Path(str(data_dir) + f"/intercomp/{trail_name}/{model_save}/")
save_dir.mkdir(parents=True, exist_ok=True)

################## END INPUTS ##################

var_list = [
    # "TD",
    "S",
    "T",
    # "WD",
    "W",
    "P",
    "F",
    "r_o",
    "R",
    "H",
    "D",
    "U",
    # "FS",
    # "r_w",
    # "Df",
    # "TMAX",
    # "FS_days",
    # "dFS",
    "mF",
    "mR",
    "mS",
    "hF",
    "hR",
    "hS",
    "h16F",
    "h16R",
    "h16S",
    "mT",
    "mW",
    "mH",
    "mFt",
    "mRt",
    "mSt",
    "mTt",
    "mWt",
    "mHt",
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
ds_obs = xr.open_dataset(
    str(data_dir) + f"/obs/observations-{domain_save}-20191231-20230531.nc"
)
ds_obs = ds_obs.sel(
    time=slice(date_range[0].strftime("%Y-%m-%d"), date_range[-1].strftime("%Y-%m-%d"))
)

## drop stations right on domain boundaries, also station with bad data.
bad_wx = [2275, 3153, 3167, 3266, 3289, 71977, 71948, 71985, 721571, 5529, 70194]
for wx in bad_wx:
    ds_obs = ds_obs.drop_sel(wmo=wx)


## convert lat lon coordinate in master obs to meter base x y as define by wrf polar stere projection
df = pd.DataFrame(
    data={
        "lons": ds_obs.lons.values,
        "lats": ds_obs.lats.values,
        "wmo": ds_obs.wmo.values,
    }
)


############################### Functions #############################


def get_locs(pyproj_srs):
    # get_locs_time = datetime.now()
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
    # print("Locs Time: ", datetime.now() - get_locs_time)

    return x, y


x_d02, y_d02 = get_locs(
    xr.open_dataset(str(data_dir) + f"/static/static-vars-wrf-d02.nc").attrs[
        "pyproj_srs"
    ]
)
x_d03, y_d03 = get_locs(
    xr.open_dataset(str(data_dir) + f"/static/static-vars-wrf-d03.nc").attrs[
        "pyproj_srs"
    ]
)
x_rdps, y_rdps = get_locs(
    xr.open_dataset(str(data_dir) + f"/static/static-vars-eccc-rdps.nc").attrs[
        "pyproj_srs"
    ]
)
x_hrdps, y_hrdps = get_locs(
    xr.open_dataset(str(data_dir) + f"/static/static-vars-eccc-hrdps.nc").attrs[
        "pyproj_srs"
    ]
)


locs_dict = {
    "d02": [x_d02, y_d02],
    "d03": [x_d03, y_d03],
    "rdps": [x_rdps, y_rdps],
    "hrdps": [x_hrdps, y_hrdps],
}


def read_fwf(doi, model, domain, lead_time):
    """
    opens datasets, index on day one forecast and drop variables not use for comparison
    """
    print(doi.strftime("%Y%m%d"))
    if model == "wrf":
        hour = "06"
    else:
        hour = "00"
    if lead_time == 1:
        ds = (
            xr.open_dataset(
                fwf_dir
                + f"{model}/{domain}/{trail_name}/fwf-daily-{domain}-{doi.strftime('%Y%m%d')}{hour}.nc"
            )
            .isel(time=0)
            .chunk(chunks="auto")[var_list]
        )
    elif lead_time == 2:
        try:
            ds = (
                xr.open_dataset(
                    fwf_dir
                    + f"{model}/{domain}/{trail_name}/fwf-daily-{domain}-{(doi- np.timedelta64(1, 'D')).strftime('%Y%m%d')}{hour}.nc"
                )
                .isel(time=1)
                .chunk(chunks="auto")[var_list]
            )
        except:
            print(
                f"{model}/{domain}/{trail_name}/fwf-daily-{domain}-{doi.strftime('%Y%m%d')}{hour}.nc"
            )
            ds = (
                xr.open_dataset(
                    fwf_dir
                    + f"{model}/{domain}/{trail_name}/fwf-daily-{domain}-{doi.strftime('%Y%m%d')}{hour}.nc"
                )
                .isel(time=0)
                .chunk(chunks="auto")[var_list]
            )
            print(
                f"Could not find day 2 forecast for date {doi.strftime('%Y%m%d')}, using day one instead"
            )
    else:
        raise ValueError("Only a 1 or 2 lead_forecast time is valid")
    return ds


def rename(ds, domain):
    """
    renames datasets to match master observation dataset
    """
    for var in var_list:
        try:
            name_lower = cmaps[var]["name"].lower()
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

    x, y = locs_dict[domain]
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

######################################################################################################
############################### Use with single model/projection.  ###################################
loop_start = datetime.now()
ds = xr.combine_by_coords(
    [
        xr.combine_nested(
            [
                rename(read_fwf(doi, model, domain, lead_time=lead_time), domain)
                for doi in date_range
            ],
            concat_dim="time",
        ).chunk("auto")
        for model in config
        for domain in config[model]
    ]
)
print("Loop Time: ", datetime.now() - loop_start)
# print(final_ds)
load_start = datetime.now()
ds = ds.compute()
print("Load Time: ", datetime.now() - load_start)

######################################################################################################
############################### Use when merging with master obs.  ###################################

merge = datetime.now()
## merge the forecasted values at wx station with their observed values
final_ds = xr.combine_by_coords([ds, ds_obs.expand_dims(dim={"domain": ["obs"]})])
print("Merge Time: ", datetime.now() - merge)


# print(final_ds)
######################################################################################################
##################################### Write to netcdf  ###############################################

### Prepare to write
for var in ["elev", "name", "prov", "id"]:
    final_ds[var] = final_ds[var].astype(str)
for var in list(final_ds):
    final_ds[var] = final_ds[var].astype("float32")
final_ds = final_ds.drop("time")


write = datetime.now()
## write final dataset as netcdf
final_ds, encoding = compressor(final_ds, var_dict=None)
final_ds.to_netcdf(
    str(save_dir)
    + f'/{domain_save}-{date_range[0].strftime("%Y%m%d")}-{date_range[-1].strftime("%Y%m%d")}.nc',
    mode="w",
    encoding=encoding,
)
print("Write Time: ", datetime.now() - write)

# ######################################################################################################
# ####################################        Timer            #########################################
# ### Timer
print("Total Run Time: ", datetime.now() - startTime)
