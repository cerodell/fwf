#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

"""
Builds a dataset of wrfout/fwf model versus all wmo weather station
observations within model domain. Writes Dataset as zarr with attribute of of wmo.

"""

import context
import io
import json
import requests

import numpy as np
import pandas as pd
import xarray as xr
from glob import glob
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from wrf import ll_to_xy, xy_to_ll
from datetime import datetime, date, timedelta
from dev_utils.make_intercomp import daily_merge_ds

from context import data_dir, root_dir, wrf_dir_new, tzone_dir

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


### Open color map json
with open("/bluesky/fireweather/fwf/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

## Get All Stations CSV
url = "https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/cwfis_allstn2019.csv"
stations_df = pd.read_csv(url, sep=",")
stations_df = stations_df.drop_duplicates(subset="wmo", keep="last")
stations_df = stations_df.drop(
    columns=["tmm", "ua", "the_geom", "h_bul", "s_bul", "hly", "syn"]
)


### Get Path to most recent FWI forecast and open
domain = "d03"
# for i in range(13,1,-1):
# print(i)
d = datetime.today() - timedelta(days=4)
day1_obs_date = d.strftime("%Y%m%d")
print(day1_obs_date)
day1_ds = daily_merge_ds(day1_obs_date, domain)

d = d - timedelta(days=1)
day2_obs_date = d.strftime("%Y%m%d")
day2_ds = daily_merge_ds(day2_obs_date, domain)


### Get a wrf file
# wrf_filein = date.today().strftime('/%y%m%d00/')
# wrf_filein = "/20122400/"
# wrf_file_dir = str(wrf_dir_new) + wrf_filein
wrf_filein = "/wrf/"
wrf_file_dir = str(data_dir) + wrf_filein
wrf_file_dir = sorted(Path(wrf_file_dir).glob(f"wrfout_{domain}_*"))
wrf_file = Dataset(wrf_file_dir[0], "r")


### Get Daily observations CSV
url2 = f"https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/current/cwfis_fwi_{day1_obs_date}.csv"
headers = list(pd.read_csv(url2, nrows=0))
obs_df = pd.read_csv(url2, sep=",", names=headers)
obs_df = obs_df.drop_duplicates()
obs_df = obs_df.drop(obs_df.index[[0]])
obs_df["wmo"] = obs_df["WMO"].astype(str).astype(int)
del obs_df["WMO"]


### Drop stations out sie of model domain
xy_np = ll_to_xy(wrf_file, stations_df["lat"], stations_df["lon"])
stations_df["x"] = xy_np[0]
stations_df["y"] = xy_np[1]
shape = np.shape(day1_ds.XLAT)
stations_df = stations_df.drop(
    stations_df.index[np.where(stations_df["x"] > (shape[1] - 1))]
)
stations_df = stations_df.drop(
    stations_df.index[np.where(stations_df["y"] > (shape[0] - 1))]
)
stations_df = stations_df.drop(stations_df.index[np.where(stations_df["x"] < -1)])
stations_df = stations_df.drop(stations_df.index[np.where(stations_df["y"] < -1)])


wmo_df = stations_df
final_df = wmo_df.merge(obs_df, on="wmo", how="left")
final_df = final_df.replace("NULL", np.nan)
final_df = final_df.replace(" NULL", np.nan)
final_df = final_df.replace("  NULL", np.nan)
final_df = final_df.drop_duplicates(subset=["wmo"], keep="last")
final_df = final_df.astype(
    {
        "TEMP": "float32",
        "RH": "float32",
        "WS": "float32",
        "WDIR": "float32",
        "PRECIP": "float32",
        "FFMC": "float32",
        "DMC": "float32",
        "DC": "float32",
        "BUI": "float32",
        "ISI": "float32",
        "FWI": "float32",
        "DSR": "float32",
    }
)
# for column in final_df:
#     final_df = final_df[final_df[column] != ' NULL']
#     final_df = final_df[final_df[column] != '  NULL']


south_north, west_east = final_df["y"].values, final_df["x"].values
var_list = list(day1_ds)
remove = ["r_o_tomorrow", "SNOWC"]
var_list = list(set(var_list) - set(remove))
final_var_list = []
for var in var_list:
    name_upper = cmaps[var]["name"].upper()
    var_columns = day1_ds[var].values[:, south_north, west_east]
    var_columns = np.array(var_columns, dtype="float32")
    final_df[name_upper + "_day1"] = var_columns[0, :]

    if day2_ds is None:
        # print('day2_ds is none')
        a = np.empty(len(south_north))
        a[:] = np.nan
        a = np.array(a, dtype="float32")
        final_df[name_upper + "_day2"] = a
    else:
        # print('day2_ds is a ds')
        var_columns = day2_ds[var].values[:, south_north, west_east]
        var_columns = np.array(var_columns, dtype="float32")
        final_df[name_upper + "_day2"] = var_columns[1, :]

    final_var_list.append(name_upper)
    final_var_list.append(name_upper + "_day1")
    final_var_list.append(name_upper + "_day2")


wmos = final_df["wmo"].values
_, index, count = np.unique(wmos, return_index=True, return_counts=True)
ids = final_df["id"].values.astype(str)
names = final_df["name"].values.astype(str)
provs = final_df["prov"].values.astype(str)
lons = final_df["lon"].values.astype("float32")
lats = final_df["lat"].values.astype("float32")
elevs = final_df["elev"].values.astype("float32")
tz_correct = final_df["tz_correct"].values.astype(int)
day = np.array(day1_ds.Time[0], dtype="datetime64[D]")


xr_list = []
for var in final_var_list:
    var_array = np.array(final_df[var], dtype="float32")
    x = np.stack((final_df[var].values, final_df[var].values))
    xr_var = xr.DataArray(
        x,
        name=f"{var}",
        coords={
            "wmo": wmos,
            "time": [day, day],
            "lats": ("wmo", lats),
            "lons": ("wmo", lons),
            "elev": ("wmo", elevs),
            "name": ("wmo", names),
            "prov": ("wmo", provs),
            "id": ("wmo", ids),
            "tz_correct": ("wmo", tz_correct),
        },
        dims=("time", "wmo"),
    )

    xr_list.append(xr_var)

intercomp_today = xr.merge(xr_list)
intercomp_today = intercomp_today.compute()
intercomp_today = intercomp_today.isel(time=0)


my_dir = Path(
    str(data_dir) + "/intercomp/" + f"intercomp-{day2_obs_date}-{domain}.zarr"
)
if my_dir.is_dir():
    intercomp_yesterday = xr.open_zarr(
        str(data_dir) + "/intercomp/" + f"intercomp-{day2_obs_date}-{domain}.zarr"
    )
    intercomp_yesterday = intercomp_yesterday.compute()
    final_ds = xr.combine_nested([intercomp_yesterday, intercomp_today], "time")
    final_ds = final_ds.compute()
    final_ds.to_zarr(
        str(data_dir) + "/intercomp/" + f"intercomp-{day1_obs_date}-{domain}.zarr", "w"
    )
else:
    final_ds = intercomp_today
    final_ds.to_zarr(
        str(data_dir) + "/intercomp/" + f"intercomp-{day1_obs_date}-{domain}.zarr", "w"
    )


### Timer
print("Total Run Time: ", datetime.now() - startTime)
