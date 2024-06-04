#!/bluesky/fireweather/miniconda3/envs/fwx/bin/python

"""
Create a json file  contains XX number of days of wmo weather station observations
along with fwf/met model output for comaprison. USed to make plots on website

"""

import context
import io
import json
import requests
from bson import json_util

import numpy as np
import pandas as pd
import xarray as xr
from glob import glob
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from wrf import ll_to_xy, xy_to_ll
from datetime import datetime, date, timedelta
from utils.make_intercomp import daily_merge_ds

from context import data_dir, root_dir, tzone_dir, fwf_dir

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


def rechunk(ds):
    ds = ds.load()
    ds = ds.chunk(chunks="auto")
    ds = ds.unify_chunks()
    for var in list(ds):
        ds[var].encoding = {}
    return ds


## Open color map json
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)
name_list = list(cmaps)

make_dir = Path("/bluesky/fireweather/fwf/web_dev/data/")
make_dir.mkdir(parents=True, exist_ok=True)

wrf_model = "wrf4"
date = pd.Timestamp("today")
# date = pd.Timestamp(2021, 2, 13)
forecast_date = date.strftime("%Y%m%d06")
obs_date = (date - np.timedelta64(1, "D")).strftime("%Y%m%d")
yesterday_forecast_date = obs_date + "06"


obs_d2_ds = xr.open_dataset(
    str(data_dir) + "/intercomp/" + f"intercomp-d02-{obs_date}.nc"
)
obs_d3_ds = xr.open_dataset(
    str(data_dir) + "/intercomp/" + f"intercomp-d03-{obs_date}.nc"
)

## make array of the wmo in each obs file
wmo_d2 = obs_d2_ds.wmo.values
wmo_d3 = obs_d3_ds.wmo.values
## subtrack make mask of like wmos
mask = np.array(list(set(wmo_d2) - set(wmo_d3)))
indices = np.nonzero(mask[:, None] == wmo_d2)[1]
## remove d3 wmo from d2
obs_d2_ds = obs_d2_ds.isel(wmo=indices)
## combine the obs to  final obs xarray
obs_final = xr.concat([obs_d2_ds, obs_d3_ds], dim="wmo")

coords_list = list(obs_final.coords)
dict_var = {}
for coords in coords_list:
    if coords != "time":
        if coords == "name":
            coord_array = obs_final[coords].values.astype(str)
            coord_array = coord_array.tolist()
            coord_array = [item.replace(",", "") for item in coord_array]
            dict_var.update({coords.lower(): str(coord_array)})
        else:
            coord_array = obs_final[coords].values
            coord_array = coord_array.tolist()
            dict_var.update({coords.lower(): str(coord_array)})
    else:
        pass


## Open datasets of both domains
hourly_file_dir = str(fwf_dir) + str(f"/fwf-hourly-d02-{forecast_date}.nc")
hourly_d2_ds = xr.open_dataset(hourly_file_dir)
daily_d2_ds = daily_merge_ds(forecast_date, "d02", wrf_model)
hourly_d2_ds, daily_d2_ds = rechunk(hourly_d2_ds), rechunk(daily_d2_ds)
hourly_file_dir = str(fwf_dir) + str(f"/fwf-hourly-d03-{forecast_date}.nc")
hourly_d3_ds = xr.open_dataset(hourly_file_dir)
daily_d3_ds = daily_merge_ds(forecast_date, "d03", wrf_model)
hourly_d3_ds, daily_d3_ds = rechunk(hourly_d3_ds), rechunk(daily_d3_ds)


# domain = "d02"

# hourly_file_dir = str(fwf_dir) + str(
#     f"/fwf-hourly-{domain}-{yesterday_forecast_date}.nc"
# )
# ### Open datasets
# my_dir = Path(hourly_file_dir)
# if my_dir.is_dir():
#     hourly_ds = xr.open_dataset(hourly_file_dir)

#     ### Get timezone mask
#     tzone_ds = xr.open_dataset(str(tzone_dir) + f"/tzone_wrf_{domain}.nc")
#     tzone = tzone_ds.Zone.values
#     shape = tzone.shape
#     ## create I, J for quick indexing
#     I, J = np.ogrid[: shape[0], : shape[1]]
#     time_array = hourly_ds.Time.values
#     try:
#         int_time = int(pd.Timestamp(time_array[0]).hour)
#     except:
#         int_time = int(pd.Timestamp(time_array).hour)

#     length = len(time_array) + 1
#     num_days = [i - 12 for i in range(1, length) if i % 24 == 0]
#     index = [
#         i - int_time if 12 - int_time >= 0 else i + 24 - int_time for i in num_days
#     ]
#     # print(f"index of times {index} with initial time {int_time}Z")

#     # try:
#     # except:
#     #     pass

#     ## loop every 24 hours
#     # var_list  = list(hourly_ds)
#     # remove = ["DSR", "F", "R", "S"]
#     # hourly_list = list(set(var_list) - set(remove))

#     # time+array = hourly_ds.Time.values.
#     # time_grid = []
#     # for i in range(len(hourly_ds.Time.values)):
#     #     time_layer = np.full_like(hourly_ds.XLAT.values, hourly_ds.Time.values[i])
#     #     time_grid.append(time_layer)

#     # time_grid = np.stack(time_grid)
#     mean_da = []
#     for var in ["F", "H", "R", "T", "W", "WD", "r_o"]:
#         # print(np.array(hourly_ds.Time[i]))
#         var_array = hourly_ds[var].values
#         noon = var_array[(index[0] + tzone), I, J]
#         time_hours = hourly_ds.Time.values[index[0]]
#         var_da = xr.DataArray(
#             noon,
#             name=var,
#             dims=("south_north", "west_east"),
#             # coords=hourly_ds.isel(time=i).coords,
#         )
#         var_da["Time"] = time_hours
#         var_da.attrs = hourly_ds[var].attrs
#         mean_da.append(var_da)

#     mean_ds = xr.merge(mean_da)
#     # files_ds.append(mean_ds)

#     hourly_daily_ds = xr.combine_nested(files_ds, "time")
#     final_ds = xr.merge([daily_ds, hourly_daily_ds], compat="override")
#     final_ds.attrs = hourly_ds.attrs


def wmo_locs(hourly_ds, daily_ds, obs_ds, domain):
    ## Get a wrf file
    wrf_filein = "/wrf/"
    wrf_file_dir = str(data_dir) + wrf_filein
    wrf_file_dir = sorted(Path(wrf_file_dir).glob(f"wrfout_{domain}_*"))
    wrf_file = Dataset(wrf_file_dir[0], "r")
    # print(wrf_file_dir)

    ## Get gridded index of wmo locations
    xy_np = ll_to_xy(wrf_file, obs_ds.lats.values, obs_ds.lons.values)
    south_north, west_east = xy_np[1], xy_np[0]

    ## Index datasets by wmo locations
    hourly_ds = hourly_ds.isel(south_north=south_north, west_east=west_east)
    daily_ds = daily_ds.isel(south_north=south_north, west_east=west_east)

    return hourly_ds, daily_ds


hourly_d2_ds, daily_d2_ds = wmo_locs(hourly_d2_ds, daily_d2_ds, obs_d2_ds, "d02")
hourly_d3_ds, daily_d3_ds = wmo_locs(hourly_d3_ds, daily_d3_ds, obs_d3_ds, "d03")

hourly_ds = xr.concat([hourly_d2_ds, hourly_d3_ds], dim="idx")
# hourly_ds = hourly_ds.compute()
daily_ds = xr.concat([daily_d2_ds, daily_d3_ds], dim="idx")
# daily_ds = daily_ds.compute()


time = np.array(hourly_ds.Time.dt.strftime("%Y-%m-%dT%H"), dtype="<U13")
day = np.array(daily_ds.Time.dt.strftime("%Y-%m-%d"), dtype="<U10")
time_obs = np.array(obs_final.time.dt.strftime("%Y-%m-%d"), dtype="<U10")

## Get first timestamp of forecast and make dir to store files
timestamp = datetime.strptime(str(time[0]), "%Y-%m-%dT%H").strftime("%Y%m%d%H")


## Get uniquie variables from all the datasets
var_list = list(hourly_ds)
obs_list = list(obs_final)
hourly_list = []
for var in var_list:
    if var in name_list:
        name = cmaps[var]["name"].upper()
        if name in obs_list:
            hourly_list.append(var)
remove = ["DSR", "S"]
hourly_list = list(set(hourly_list) - set(remove))

dict_var.update(
    {"time_fch": time.tolist(), "time_fcd": day.tolist(), "time_obs": time_obs.tolist()}
)
for var in hourly_list:
    var_name = cmaps[var]["name"].upper()
    fc_array = hourly_ds[var].values.astype("float64")
    fc_array = np.round(fc_array, decimals=2)
    fc_array = fc_array.tolist()
    dict_var.update({var_name.lower() + "_fc": str(fc_array)})

    obs_array = obs_final[var_name].values.astype("float64")
    obs_array = np.round(obs_array, decimals=2)
    where_are_NaNs = np.isnan(obs_array)
    obs_array[where_are_NaNs] = -99
    obs_array = obs_array.tolist()
    dict_var.update({var_name.lower() + "_obs": str(obs_array)})

    pfc_array = obs_final[var_name + "_day1"].values.astype("float64")
    pfc_array = np.round(pfc_array, decimals=2)
    pfc_array = pfc_array.tolist()
    dict_var.update({var_name.lower() + "_pfc": str(pfc_array)})


# var_list = list(daily_ds)
# obs_list = list(obs_final)
# daily_list = []
# for var in var_list:
#   if var in name_list:
#     name = cmaps[var]['name'].upper()
#     if name in obs_list:
#       daily_list.append(var)

daily_list = ["D", "P", "U", "DSR", "S"]
for var in daily_list:
    var_name = cmaps[var]["name"].upper()
    fc_array = daily_ds[var].values.astype("float64")
    fc_array = np.round(fc_array, decimals=2)
    fc_array = fc_array.tolist()
    dict_var.update({var_name.lower() + "_fc": str(fc_array)})

    obs_array = obs_final[var_name].values.astype("float64")
    obs_array = np.round(obs_array, decimals=2)
    where_are_NaNs = np.isnan(obs_array)
    obs_array[where_are_NaNs] = -99
    obs_array = obs_array.tolist()
    dict_var.update({var_name.lower() + "_obs": str(obs_array)})

    pfc_array = obs_final[var_name + "_day1"].values.astype("float64")
    pfc_array = np.round(pfc_array, decimals=2)
    pfc_array = pfc_array.tolist()
    dict_var.update({var_name.lower() + "_pfc": str(pfc_array)})

with open(str(make_dir) + f"/wx-{timestamp}.json", "w") as f:
    json.dump(
        dict_var, f, default=json_util.default, separators=(",", ":"), indent=None
    )
print(
    f"{str(datetime.now())} ---> wrote json to:  "
    + str(make_dir)
    + f"/wx-{timestamp}.json"
)


# ### Timer
print("Run Time: ", datetime.now() - startTime)
