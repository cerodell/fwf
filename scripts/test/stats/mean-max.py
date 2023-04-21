#!/Users/crodell/miniconda3/envs/fwf/bin/python


import context
import os
import json
import salem
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt


from datetime import datetime
from utils.wrf_ import read_wrf
from utils.eccc import read_eccc
from utils.era5 import read_era5

from context import data_dir, root_dir


startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))
model = "wrf"
domain = "d02"
trial_name = "02"
doi = pd.Timestamp("2021-02-02T06")
var_list = ["mFt", "mRt", "mSt", "mTt", "mWt", "mHt"]

date_range = pd.date_range("2021-04-01", "2021-11-01")


with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

static_ds = xr.open_dataset(str(data_dir) + f"/static/static-vars-{model}-{domain}.nc")
tzone = static_ds["ZoneST"].values
wrf_ds = salem.open_xr_dataset(
    str(data_dir) + f"/wrf/wrfout_{domain}_2021-01-14_00:00:00"
).isel(Time=0)
# masked_arr = np.ma.masked_where(wrf_ds["LANDMASK"] == 0, wrf_ds["LANDMASK"])
masked_arr = np.ma.masked_where(static_ds["LAND"] == 1, static_ds["LAND"])


try:
    mean_ds = salem.open_xr_dataset(
        str(data_dir) + f"/wrf/mean-daily-{domain}-{trial_name}.nc"
    )
except:
    filein_dir = f"/Volumes/WFRT-Ext24/fwf-data/{model}/{domain}/{trial_name}"
    openTime = datetime.now()
    ds = xr.concat(
        [
            salem.open_xr_dataset(
                filein_dir + f"/fwf-daily-{domain}-{doi.strftime('%Y%m%d06')}.nc",
            )[var_list]
            .isel(time=0)
            .chunk("auto")
            for doi in date_range
        ],
        dim="time",
    )
    print("Open Time: ", datetime.now() - openTime)

    meanTime = datetime.now()
    mean_ds = ds.mean(dim="time")  # .to_dataset()
    mean_ds.attrs = ds.attrs
    for var in mean_ds:
        mean_ds[var].attrs["pyproj_srs"] = ds.attrs["pyproj_srs"]

    print("Mean Time: ", datetime.now() - meanTime)
    mean_ds.to_netcdf(
        str(data_dir) + f"/wrf/mean-daily-{domain}-{trial_name}.nc", mode="w"
    )


for var in var_list:
    if var[1] == "H":
        ext = "MIN"
    else:
        ext = "MAX"
    var_name = cmaps[var[1]]["name"]
    masked_array = mean_ds[var].to_masked_array()
    masked_array.mask = masked_arr.mask
    mean_ds[var] = (("south_north", "west_east"), masked_array)
    mean_ds[var] = mean_ds[var] - 12
    mean_ds[var].attrs["pyproj_srs"] = mean_ds.attrs["pyproj_srs"]
    mean_ds[var].attrs["units"] = "Hours"
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(1, 1, 1)
    mean_ds[var].salem.quick_map(
        ax=ax,
        cmap="coolwarm",
        vmin=-12,
        vmax=12,
        oceans=True,
        lakes=True,
        states=True,
        prov=True,
    )
    ax.set_title(
        f"Average hour offset from noon for {ext} {var_name.upper()} \n during the 2021 Fire Season (April 1 - Nov 1) \n Mean: {round(float(mean_ds[var].mean()),2)}hrs,  Min: {round(float(mean_ds[var].min()),2)}hrs,  Max: {round(float(mean_ds[var].max()),2)}hrs"
    )

    plt.savefig(
        str(data_dir)
        + f"/images/spatial/{trial_name}/{var_name.lower()}-{domain}-mean-occurrence-of-max.png",
        dpi=250,
        bbox_inches="tight",
    )
