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
doi = pd.Timestamp("2021-02-02T06")


date_range = pd.date_range("2021-04-01", "2021-11-01")
static_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-{model}-{domain}.nc"
)
wrf_ds = salem.open_xr_dataset(
    str(data_dir) + f"/wrf/wrfout_d02_2021-01-14_00:00:00"
).isel(Time=0)

landmask = wrf_ds["LANDMASK"]
masked_arr = np.ma.masked_where(
    (wrf_ds["LAKEMASK"] == 1) | (wrf_ds["LANDMASK"] == 0) | (static_ds["LAND"]),
    wrf_ds["LANDMASK"],
)

with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

try:
    ds = salem.open_xr_dataset(str(data_dir) + f"/wrf/mean-hourly-{domain}.nc")
except:
    tzone = static_ds["ZoneST"].values

    filein_dir = f"/Volumes/WFRT-Ext24/fwf-data/{model}/{domain}/01"
    openTime = datetime.now()
    ds = xr.combine_nested(
        [
            salem.open_xr_dataset(
                filein_dir + f"/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc",
            )
            .isel(time=slice(0, 24))
            .chunk("auto")
            for doi in date_range
        ],
        concat_dim="time",
    )
    print("Open Time: ", datetime.now() - openTime)

    meanTime = datetime.now()
    mean_ds = ds.groupby("Time.hour").mean("time")
    print("Mean Time: ", datetime.now() - meanTime)

    compTime = datetime.now()
    mean_ds = mean_ds.compute()
    print("Compute Time: ", datetime.now() - compTime)

    idxTime = datetime.now()
    ds_i_list = []
    for i in range(0, 24):
        tzone_i = i + tzone
        tzone_i = np.where(tzone_i < 24, tzone_i, -1 * (tzone_i - 23))
        ds_i = mean_ds.isel(
            hour=xr.DataArray(tzone_i, dims=["south_north", "west_east"])
        )
        ds_i_list.append(ds_i.drop("hour"))

    ds = xr.combine_nested(ds_i_list, concat_dim="hour")
    ds.attrs = static_ds.attrs
    for var in mean_ds:
        ds[var].attrs["pyproj_srs"] = static_ds.attrs["pyproj_srs"]
    print("Index and combine Time: ", datetime.now() - idxTime)

    writeTime = datetime.now()
    ds.to_netcdf(str(data_dir) + f"/wrf/mean-hourly-{domain}.nc", mode="w")
    print("Write Time: ", datetime.now() - writeTime)


var = "T"
for var in ds:
    var_name = cmaps[var]["name"]
    if var == "H":
        ext = "MIN"
        ds[var + ext] = ds[var].argmin(dim="hour") - 12
    else:
        ext = "MAX"
        ds[var + ext] = ds[var].argmax(dim="hour") - 12
    masked_array = ds[var + ext].to_masked_array()
    masked_array.mask = masked_arr.mask
    ds[var + ext] = (("south_north", "west_east"), masked_array)
    ds[var + ext].attrs["pyproj_srs"] = ds.attrs["pyproj_srs"]
    ds[var + ext].attrs["units"] = "Hours"
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(1, 1, 1)
    ds[var + ext].salem.quick_map(cmap="coolwarm", vmin=-12, vmax=12, ax=ax)
    ax.set_title(
        f"Average hour offset from noon for {ext} {var_name.upper()} \n during the 2021 Fire Season (April 1 - Nov 1) \n Mean: {round(float(ds[var+ext].mean()),2)}hrs,  Min: {round(float(ds[var+ext].min()),2)}hrs,  Max: {round(float(ds[var+ext].max()),2)}hrs"
    )
    plt.savefig(
        str(data_dir) + f"/images/spatial/{var_name.lower()}-{domain}-method-2.png",
        dpi=250,
        bbox_inches="tight",
    )
