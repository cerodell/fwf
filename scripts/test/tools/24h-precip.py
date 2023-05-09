#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python


import context
import os
import json
import salem
import numpy as np
import pandas as pd
import xarray as xr


from datetime import datetime
from utils.wrf_ import read_wrf
from utils.eccc import read_eccc
from utils.era5 import read_era5

from context import data_dir

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))
model = "wrf"
domain = "d02"
timestep = "hourly"
doi = pd.Timestamp("2021-01-10T06")

## test fwf with an hourly_ds
filein_dir = f"/Volumes/Scratch/fwf-data/wrf/d02/"

filein_dir_old = f"/Volumes/WFRT-Ext24/fwf-data/wrf/d02/02"


hourly_ds = xr.open_dataset(
    str(filein_dir)
    + f"{doi.strftime('%Y%m')}/fwf-{timestep}-{domain}-{doi.strftime('%Y%m%d%H')}.nc"
)
daily_ds_og = salem.open_xr_dataset(
    str(filein_dir)
    + f"{doi.strftime('%Y%m')}/fwf-daily-{domain}-{doi.strftime('%Y%m%d%H')}.nc"
)

## Open gridded static
static_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
)
tzone_array = static_ds.ZoneST.values
shape = tzone_array.shape


## determine index for looping based on length of time array and initial time
time_array = hourly_ds.Time.values
tslice = slice(0, 24)


## loop and try and open datasets from today to four days in the past
previous_dss, days_of_max = [], []
for i in range(1, -1, -1):
    retrieve_time_np = time_array[0] - np.timedelta64(i, "D")
    retrieve_time = pd.to_datetime(retrieve_time_np).strftime("%Y%m%d%H")
    try:
        if (model == "wrf") or (model == "eccc"):
            int_file_dir = (
                str(filein_dir)
                + f"{pd.to_datetime(retrieve_time_np).strftime('%Y%m')}/fwf-{timestep}-{domain}-{retrieve_time}.nc"
            )
            da = xr.open_dataset(int_file_dir)
        elif model == "ecmwf":
            da = read_era5(pd.to_datetime(retrieve_time_np), model, domain)
        else:
            raise ValueError("Bad model input")
        if i == 0:
            da = da.chunk("auto")["r_o"]
        else:
            da = da.isel(time=tslice).chunk("auto")["r_o"]
        previous_dss.append(da)
        days_of_max.append(retrieve_time_np.astype("datetime64[D]"))
    except:
        pass
## combine the dataset into one continuous dataarray
rain_yesterday = previous_dss[0]
rain_toady = previous_dss[1] + rain_yesterday.isel(time=-1).values


int_ds = xr.combine_nested(
    [rain_yesterday, rain_toady],
    concat_dim="time",
).load()


## create I, J for quick indexing
I, J = np.ogrid[: shape[0], : shape[1]]

## determine index for looping based on length of time array and initial time
time_array = int_ds.Time.values
print(time_array[0])
int_time = int(pd.Timestamp(time_array[0]).hour)
length = len(time_array) + 1
num_days = [i - 12 for i in range(1, length) if i % 24 == 0]
index = [i - int_time if 12 - int_time >= 0 else i + 24 - int_time for i in num_days]
print(f"index of 12Z times {index} with initial time {int_time}Z")


np_startTime = datetime.now()
## loop every 24 hours at noon local
files_ds = []
for i in index:
    var_array = int_ds.values
    noon = var_array[(i + tzone_array), I, J]
    day = np.array(int_ds.Time[i + 1], dtype="datetime64[D]")
    var_da = xr.DataArray(
        noon,
        name="r_o",
        dims=("south_north", "west_east"),
        coords=int_ds.isel(time=i).coords,
    )
    var_da["Time"] = day
    files_ds.append(var_da)

daily_ds = xr.combine_nested(files_ds, "time")
print("numpy indexing time: ", datetime.now() - np_startTime)


new_rain = daily_ds.isel(time=1) - daily_ds.isel(time=0)
old_rain = daily_ds_og["r_o"].isel(time=0)
diff_rain = new_rain - old_rain

static_ds["new_rain"] = new_rain
static_ds["new_rain"].attrs = static_ds.attrs
static_ds["old_rain"] = old_rain
static_ds["old_rain"].attrs = static_ds.attrs
static_ds["diff_rain"] = (("south_north", "west_east"), diff_rain.values)
static_ds["diff_rain"].attrs = static_ds.attrs

static_ds["diff_rain"].salem.quick_map(vmin=10, vmax=10, cmap="coolwarm")


print(float(static_ds["diff_rain"].max()))
print(float(static_ds["diff_rain"].min()))
print(float(static_ds["diff_rain"].mean()))
