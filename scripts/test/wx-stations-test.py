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
from utils.make_intercomp import daily_merge_ds

from context import data_dir, fwf_dir, tzone_dir

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

wrf_model = "wrf4"
## make dir for that intercomp files if it doest not all ready exist
make_dir = Path(str(data_dir) + "/intercomp/")
make_dir.mkdir(parents=True, exist_ok=True)

### Open nested grid json
with open(str(data_dir) + "/json/nested-index.json") as f:
    nested_index = json.load(f)

### Open color map json
with open(str(data_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

## Get All Stations CSV
url = "https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/cwfis_allstn2019.csv"
stations_df_og = pd.read_csv(url, sep=",")
stations_df_og = stations_df_og.drop_duplicates(subset="wmo", keep="last")
stations_df_og = stations_df_og.drop(
    columns=["tmm", "ua", "the_geom", "h_bul", "s_bul", "hly", "syn"]
)

date = pd.Timestamp("today")
# date = pd.Timestamp(2021, 5, 1)
day1_obs_date = date - np.timedelta64(1, "D")
day1_obs_date = day1_obs_date.strftime("%Y%m%d06")
day2_obs_date = date - np.timedelta64(2, "D")
day2_obs_date = day2_obs_date.strftime("%Y%m%d06")


def rechunk(ds):
    ds = ds.chunk(chunks="auto")
    ds = ds.unify_chunks()
    for var in list(ds):
        ds[var].encoding = {}
    return ds


domain = "d02"

stations_df = stations_df_og

day1_ds = daily_merge_ds(day1_obs_date, domain, wrf_model)
# day1_ds = daily_merge_ds(day2_obs_date, domain, wrf_model)

day2_ds = daily_merge_ds(day2_obs_date, domain, wrf_model)

### Get a wrf file
wrf_filein = "/wrf/"
wrf_file_dir = str(data_dir) + wrf_filein
wrf_file_dir = sorted(Path(wrf_file_dir).glob(f"wrfout_{domain}_*"))
wrf_file = Dataset(wrf_file_dir[0], "r")

### Get Daily observations CSV
url2 = f"https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/current/cwfis_fwi_{day1_obs_date[:-2]}.csv"
headers = list(pd.read_csv(url2, nrows=0))
obs_df = pd.read_csv(url2, sep=",", names=headers)
obs_df = obs_df.drop_duplicates()
obs_df = obs_df.drop(obs_df.index[[0]])
obs_df["wmo"] = obs_df["WMO"].astype(str).astype(int)
del obs_df["WMO"]


## get index to remove boundary conditions
n, y1, y2, x1, x2 = (
    nested_index["n"],
    nested_index["y1_" + domain],
    nested_index["y2_" + domain],
    nested_index["x1_" + domain],
    nested_index["x2_" + domain],
)

### Drop stations out sie of model domain
xy_np = ll_to_xy(wrf_file, stations_df["lat"], stations_df["lon"])
stations_df["x"] = xy_np[0]
stations_df["y"] = xy_np[1]
shape = np.shape(day1_ds.XLAT)
stations_df = stations_df.drop(
    stations_df.index[np.where(stations_df["x"] > (shape[1] - x2 - 1))]
)
stations_df = stations_df.drop(
    stations_df.index[np.where(stations_df["y"] > (shape[0] - y2 - 1))]
)
stations_df = stations_df.drop(stations_df.index[np.where(stations_df["x"] < x1 - 1)])
stations_df = stations_df.drop(stations_df.index[np.where(stations_df["y"] < y1 - 1)])


wmo_df = stations_df
final_df = wmo_df.merge(obs_df, on="wmo", how="outer")

wmos = final_df.wmo.values


prov_df = stations_df[stations_df.prov == "NT"]

prov_df.to_csv("nwt_wxstations.csv")

prov = stations_df.prov.values

index, count = np.unique(prov, return_counts=True)

for i in index:
    print(f"In {i} there are {int(count[index==i])} wx stations")


test = stations_df[stations_df.wmo == obs_df.wmo]
