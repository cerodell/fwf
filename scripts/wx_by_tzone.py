#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

"""
Create a json file  contains XX number of days of wmo weather station observations
along with fwf/met model output for comaprison. USed to make plots on website

gzip -k wx-zone-5-2021021506.json

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


wrf_model = "wrf4"
## Open color map json
with open(str(data_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)
name_list = list(cmaps)


forecast_date = pd.Timestamp("today").strftime("%Y%m%d00")
make_dir = Path(f"/bluesky/archive/fireweather/forecasts/{forecast_date}/data/")
make_dir.mkdir(parents=True, exist_ok=True)


date = pd.Timestamp("today")
# date = pd.Timestamp(2021, 2, 22)
forecast_date = date.strftime("%Y%m%d06")
obs_date = (date - np.timedelta64(1, "D")).strftime("%Y%m%d")
obs_date_int = (date - np.timedelta64(14, "D")).strftime("%Y%m%d")

yesterday_forecast_date = obs_date + "06"


obs_d2_ds = xr.open_zarr(
    str(data_dir) + "/intercomp/" + f"intercomp-d02-{obs_date}.zarr"
)
obs_d3_ds = xr.open_zarr(
    str(data_dir) + "/intercomp/" + f"intercomp-d03-{obs_date}.zarr"
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
obs_ds = xr.concat([obs_d2_ds, obs_d3_ds], dim="wmo")

obs_ds = obs_ds.sel(time=slice(obs_date_int, obs_date))

## Open todays datasets of both domains
hourly_file_dir = str(fwf_dir) + str(f"/fwf-hourly-d02-{forecast_date}.nc")
hourly_d2_ds = xr.open_dataset(hourly_file_dir)
daily_d2_ds = daily_merge_ds(forecast_date, "d02", wrf_model)

hourly_file_dir = str(fwf_dir) + str(f"/fwf-hourly-d03-{forecast_date}.nc")
hourly_d3_ds = xr.open_dataset(hourly_file_dir)
daily_d3_ds = daily_merge_ds(forecast_date, "d03", wrf_model)

## Open yesterdays datasets of both domains
hourly_file_dir = str(fwf_dir) + str(f"/fwf-hourly-d02-{yesterday_forecast_date}.nc")
hourly_d2_yester_ds = xr.open_dataset(hourly_file_dir)
daily_d2_yester_ds = daily_merge_ds(yesterday_forecast_date, "d02", wrf_model)

hourly_file_dir = str(fwf_dir) + str(f"/fwf-hourly-d03-{yesterday_forecast_date}.nc")
hourly_d3_yester_ds = xr.open_dataset(hourly_file_dir)
daily_d3_yester_ds = daily_merge_ds(yesterday_forecast_date, "d03", wrf_model)


def rechunk(ds):
    ds = ds.chunk(chunks="auto")
    ds = ds.unify_chunks()
    # for var in list(ds):
    #     ds[var].encoding = {}
    return ds


def reindex_ds(ds_d2, ds_d3, info):
    ds_d2, ds_d3 = rechunk(ds_d2), rechunk(ds_d3)
    ds_d2["time"], ds_d3["time"] = (
        ds_d2.Time.astype("datetime64[h]"),
        ds_d3.Time.astype("datetime64[h]"),
    )
    if len(ds_d3.time) != len(ds_d2.time):
        print(f"Unequal lenght datasets for {info}")
        if len(ds_d3.time) > len(ds_d2.time):
            print("d03 in longer")
            time_array = ds_d2.Time.values.astype("datetime64[h]")
            ds_d3 = ds_d3.sel(time=slice(str(time_array[0]), str(time_array[-1])))
            print(
                f"reindex d03 from {str(time_array[0])} - {str(time_array[-1])} for {info}"
            )
        elif len(ds_d3.time) < len(ds_d2.time):
            print("d02 in longer")
            time_array = ds_d3.Time.values.astype("datetime64[h]")
            ds_d2 = ds_d2.sel(time=slice(str(time_array[0]), str(time_array[-1])))
            print(
                f"reindex d02 from {str(time_array[0])} - {str(time_array[-1])} for {info}"
            )
        else:
            print("Faild")
    else:
        ds_d2, ds_d3 = ds_d2, ds_d3

    return ds_d2, ds_d3


## reindex in datasets have unequal leght time series
hourly_d2_ds, hourly_d3_ds = reindex_ds(hourly_d2_ds, hourly_d3_ds, "hourly_ds")
daily_d2_ds, daily_d3_ds = reindex_ds(daily_d2_ds, daily_d3_ds, "daily_ds")

## reindex in datasets have unequal leght time series
hourly_d2_yester_ds, hourly_d3_yester_ds = reindex_ds(
    hourly_d2_yester_ds, hourly_d3_yester_ds, "hourly_yesterday_ds"
)
daily_d2_yester_ds, daily_d3_yester_ds = reindex_ds(
    daily_d2_yester_ds, daily_d3_yester_ds, "daily_yesterday_ds"
)


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

hourly_d2_yester_ds, daily_d2_yester_ds = wmo_locs(
    hourly_d2_yester_ds, daily_d2_yester_ds, obs_d2_ds, "d02"
)
hourly_d3_yester_ds, daily_d3_yester_ds = wmo_locs(
    hourly_d3_yester_ds, daily_d3_yester_ds, obs_d3_ds, "d03"
)

hourly_ds = xr.concat([hourly_d2_ds, hourly_d3_ds], dim="idx")
hourly_yester_ds = xr.concat([hourly_d2_yester_ds, hourly_d3_yester_ds], dim="idx")

daily_ds = xr.concat([daily_d2_ds, daily_d3_ds], dim="idx")
daily_yester_ds = xr.concat([daily_d2_yester_ds, daily_d3_yester_ds], dim="idx")


## Get uniquie variables from all the datasets
var_list = list(hourly_ds)
obs_list = list(obs_ds)
hourly_list = []
for var in var_list:
    if var in name_list:
        name = cmaps[var]["name"].upper()
        if name in obs_list:
            hourly_list.append(var)
remove = ["DSR", "S"]
hourly_list = list(set(hourly_list) - set(remove))


int_time = int(pd.Timestamp(str(hourly_ds.Time.values[0])).hour)
length = len(hourly_ds.Time.values) + 1
num_days = [i - 12 for i in range(1, length) if i % 24 == 0]
index = [i - int_time if 12 - int_time >= 0 else i + 24 - int_time for i in num_days]
print(f"index of times {index} with time {int_time}Z")


tzone_array = obs_ds.tz_correct.values
unique, counts = np.unique(tzone_array, return_counts=True)


for ztu in unique:
    ind = [i for i, n in enumerate(tzone_array) if n == ztu]

    wx_hourly_ds = hourly_ds.isel(idx=ind)
    wx_hourly__yester_ds = hourly_yester_ds.isel(idx=ind)
    wx_daily_ds = daily_ds.isel(idx=ind)
    wx_obs_ds = obs_ds.isel(wmo=ind)

    try:
        wx_hourly__yester_ds = wx_hourly__yester_ds.isel(
            time=slice(index[0] + abs(ztu), 24)
        )
    except:
        wx_hourly__yester_ds = wx_hourly__yester_ds.isel(
            time=slice(index + abs(ztu), 24)
        )

    wx_hourly_ds["r_o"] = wx_hourly__yester_ds.r_o.values[-1] + wx_hourly_ds.r_o

    fianl_hourly_ds = xr.combine_nested(
        [wx_hourly__yester_ds, wx_hourly_ds], concat_dim="time"
    )

    wx_daily_ds["Noon"] = wx_daily_ds.Time.values + np.timedelta64(12 + abs(ztu), "h")
    wx_obs_ds["Noon"] = wx_obs_ds.time.values + np.timedelta64(12 + abs(ztu), "h")

    time = np.array(fianl_hourly_ds.Time.dt.strftime("%Y-%m-%dT%H"), dtype="<U13")
    day = np.array(wx_daily_ds.Noon.dt.strftime("%Y-%m-%dT%H"), dtype="<U13")
    time_obs = np.array(wx_obs_ds.Noon.dt.strftime("%Y-%m-%dT%H"), dtype="<U13")

    # coords_list = list(obs_ds.coords)
    coords_list = ["time", "wmo"]
    dict_var = {}
    for coords in coords_list:
        if coords != "time":
            coord_array = wx_obs_ds[coords].values
            coord_array = coord_array.tolist()
            if coords == "name":
                coord_array = [item.replace(",", "") for item in coord_array]
                dict_var.update({coords.lower(): str(coord_array)})
            else:
                dict_var.update({coords.lower(): str(coord_array)})
        else:
            pass

    dict_var.update(
        {
            "time_fch": time.tolist(),
            "time_fcd": day.tolist(),
            "time_obs": time_obs.tolist(),
        }
    )

    for var in hourly_list:
        var_name = cmaps[var]["name"].upper()
        fc_array = fianl_hourly_ds[var].values.astype("float64")
        fc_array = np.round(fc_array, decimals=2)
        fc_array = fc_array.tolist()
        dict_var.update({var_name.lower() + "_fc": str(fc_array)})

        obs_array = wx_obs_ds[var_name].values.astype("float64")
        obs_array = np.round(obs_array, decimals=2)
        where_are_NaNs = np.isnan(obs_array)
        obs_array[where_are_NaNs] = -99
        obs_array = obs_array.tolist()
        dict_var.update({var_name.lower() + "_obs": str(obs_array)})

        pfc_array = wx_obs_ds[var_name + "_day1"].values.astype("float64")
        pfc_array = np.round(pfc_array, decimals=2)
        pfc_array = pfc_array.tolist()
        dict_var.update({var_name.lower() + "_pfc": str(pfc_array)})

    daily_list = ["D", "P", "U", "DSR", "S"]
    for var in daily_list:
        var_name = cmaps[var]["name"].upper()
        fc_array = wx_daily_ds[var].values.astype("float64")
        fc_array = np.round(fc_array, decimals=2)
        fc_array = fc_array.tolist()
        dict_var.update({var_name.lower() + "_fc": str(fc_array)})

        obs_array = wx_obs_ds[var_name].values.astype("float64")
        obs_array = np.round(obs_array, decimals=2)
        where_are_NaNs = np.isnan(obs_array)
        obs_array[where_are_NaNs] = -99
        obs_array = obs_array.tolist()
        dict_var.update({var_name.lower() + "_obs": str(obs_array)})

        pfc_array = wx_obs_ds[var_name + "_day1"].values.astype("float64")
        pfc_array = np.round(pfc_array, decimals=2)
        pfc_array = pfc_array.tolist()
        dict_var.update({var_name.lower() + "_pfc": str(pfc_array)})

    with open(str(make_dir) + f"/wx-zone-{abs(ztu)}-{obs_date}.json", "w") as f:
        json.dump(
            dict_var, f, default=json_util.default, separators=(",", ":"), indent=None
        )
    print(
        f"{str(datetime.now())} ---> wrote json to:  "
        + str(make_dir)
        + f"/wx-zone-{abs(ztu)}-{obs_date}.json"
    )


# ### Timer
print("Run Time: ", datetime.now() - startTime)
