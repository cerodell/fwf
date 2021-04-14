#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

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


# Slicing with an out-of-order index is generating 124 times more chunks


startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

## Open color map json
with open(str(data_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)
name_list = list(cmaps)

forecast_date = pd.Timestamp("today").strftime("%Y%m%d00")
make_dir = Path(f"/bluesky/archive/fireweather/forecasts/{forecast_date}/data/")
make_dir.mkdir(parents=True, exist_ok=True)


date = pd.Timestamp("today")
# date = pd.Timestamp(2021, 2, 13)
forecast_date = date.strftime("%Y%m%d06")
obs_date = (date - np.timedelta64(1, "D")).strftime("%Y%m%d")


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
obs_final = xr.concat([obs_d2_ds, obs_d3_ds], dim="wmo")


coords_list = list(obs_final.coords)
dict_var = {}
for coords in coords_list:
    if coords != "time":
        coord_array = obs_final[coords].values
        coord_array = coord_array.tolist()
        if coords == "name":
            coord_array = [item.replace(",", "") for item in coord_array]
            dict_var.update({coords.lower(): str(coord_array)})
        else:
            dict_var.update({coords.lower(): str(coord_array)})
    else:
        pass


for var in ["F", "T"]:
    var_name = cmaps[var]["name"].upper()
    obs_array = obs_final[var_name].values.astype("float64")[-1, :]
    obs_array = np.round(obs_array, decimals=2)
    where_are_NaNs = np.isnan(obs_array)
    obs_array[where_are_NaNs] = -99
    obs_array = obs_array.tolist()
    dict_var.update({var_name.lower() + "_obs": str(obs_array)})


# values, counts = np.unique(obs_final.tz_correct.values, return_counts=True)

with open(str(make_dir) + f"/wx-keys-{obs_date}.json", "w") as f:
    json.dump(
        dict_var, f, default=json_util.default, separators=(",", ":"), indent=None
    )
print(
    f"{str(datetime.now())} ---> wrote json to:  "
    + str(make_dir)
    + f"/wx-keys-{obs_date}.json"
)


# ### Timer
print("Run Time: ", datetime.now() - startTime)
