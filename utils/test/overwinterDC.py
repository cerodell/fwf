import context
import os
import math
import json
import numpy as np
import pandas as pd
import xarray as xr


from pathlib import Path
from datetime import datetime
from utils.wrf import readwrf
from utils.era5 import config_era5
from utils.compressor import compressor, file_size
from context import data_dir

# import h5py


timestep = "hourly"
domain = "d02"
iterator = "fwf"
## test fwf with an hourly_ds
filein_dir = "/Volumes/Scratch/FWF-WAN00CG/d02/202104/"

# hourly_list = [xr.open_dataset(str(filein_dir) + f"fwf-{timestep}-{domain}-202104{i}06.nc").isel(time=slice(0,24)).chunk("auto")  for i in range(10,30)]
# hourly_ds = xr.concat(hourly_list, dim="time", coords='minimal') #.load()

hourly_ds = xr.open_dataset(str(filein_dir) + f"fwf-{timestep}-{domain}-2021041006.nc")
# %%
## test era5 with an hourly_ds
# int_file_dir = f"/Volumes/WFRT-Data02/era5/fwf/fwf-{timestep}-{domain}-2020010106.nc"
# hourly_ds = xr.open_dataset(int_file_dir).chunk("auto")

## open a daily_ds as test
# daily_ds = xr.open_dataset(str(filein_dir) + f"fwf-daily-{domain}-2021010606.nc")

## Open gridded static
static_ds = xr.open_dataset(str(data_dir) + f"/static/static-vars-wrf4-{domain}.nc")

tzone = static_ds.ZoneST.values

shape = tzone.shape


## determine index for looping based on length of time array and initial time
time_array = hourly_ds.Time.values


"""########################################################################"""
""" ####### Creat and fire season mask and based on tmax condition ########"""
"""########################################################################"""


FSy = FSy
r_w = r_w
XLAT = hourly_ds.XLAT.values
XLONG = hourly_ds.XLONG.values

## define time slicing based on hourly or daily data
if timestep == "daily":
    tslice = 0
elif timestep == "hourly":
    tslice = slice(0, 24)
else:
    raise ValueError(
        f"Invalide timesept option of {timestep}, can only take daily or hourly"
    )

## loop and try and open datasets from today to four days in the past
previous_dss, days_of_max = [], []
for i in range(32, -1, -1):
    retrieve_time_np = time_array[0] - np.timedelta64(i, "D")
    retrieve_time = pd.to_datetime(retrieve_time_np).strftime("%Y%m%d%H")
    if iterator == "fwf":
        int_file_dir = (
            str(filein_dir.rsplit("/", 2)[0])
            + f"/{pd.to_datetime(retrieve_time_np).strftime('%Y%m')}/fwf-{timestep}-{domain}-{retrieve_time}.nc"
        )
    elif iterator == "era5":
        int_file_dir = (
            filein_dir.rsplit("/", 1)[0]
            + f"/fwf-{timestep}-{domain}-{retrieve_time}.nc"
        )
    else:
        raise ValueError("Bad iterator")

    try:
        if i == 0:
            da = xr.open_dataset(int_file_dir).chunk("auto").T
        else:
            da = xr.open_dataset(int_file_dir).isel(time=tslice).chunk("auto").T
        previous_dss.append(da)
        days_of_max.append(retrieve_time_np.astype("datetime64[D]"))
    except:
        pass

## combine the dataset into one continuous dataarray
cont_ds = xr.concat(previous_dss, dim="time", coords="minimal").load()
# print(cont_ds)
## find all index of 00Z in the continuous dataarray based on the inital time
time_array = cont_ds.Time.values
# print(time_array[0])
int_time = int(pd.Timestamp(time_array[0]).hour)
length = len(time_array) + 1
num_days = [i - 0 for i in range(1, length) if i % 24 == 0]
index = [i - int_time if 12 - int_time >= 0 else i + 24 - int_time for i in num_days]
index = index[:-1]
if (len(cont_ds.time) - index[-1]) < (24 + float(np.max(tzone))):
    index = index[:-1]
else:
    pass
if iterator == "fwf":
    pass
elif iterator == "era5":
    index = [0] + index
else:
    raise ValueError("Bad iterator")

print(f"index of 00Z times {index} with initial time {int_time}Z")
## loop every 00Z index and find daily max temps between local midnight to midnight using an array of utc offsets
da_j_list = []
for j in range(len(index)):
    da_i_list = []
    for i in range(index[j], index[j] + 24):
        ind_a = xr.DataArray(i + tzone, dims=["south_north", "west_east"])
        da_i = cont_ds.isel(time=ind_a)
        try:
            da_i = da_i.drop(["time"])
        except:
            pass
        da_i_list.append(da_i)
    da_j = xr.concat(da_i_list, dim="time").max(dim="time")
    da_j = da_j.assign_coords(
        {
            "Time": days_of_max[j],
            "XLAT": (("south_north", "west_east"), XLAT),
            "XLONG": (("south_north", "west_east"), XLONG),
        }
    )
    da_j_list.append(da_j)

TMAX_da = xr.concat(da_j_list, dim="time")

## apply a try condition for when datas in the past doesn't exist
## TODO this is hacky, needs to be more robust for longer NWP forecast (only good for two day forecasts)
try:
    TMAX_yesterday = (
        TMAX_da.isel(time=slice(0, 3))
        .max(dim="time")
        .assign_coords({"Time": days_of_max[-2]})
    )
    TMAX_today = (
        TMAX_da.isel(time=slice(1, 4))
        .max(dim="time")
        .assign_coords({"Time": days_of_max[-1]})
    )
    TMAX = xr.concat([TMAX_yesterday, TMAX_today], dim="time")
except:
    TMAX = xr.concat(
        [
            TMAX_da.assign_coords({"Time": days_of_max[0] - np.timedelta64(1, "D")}),
            TMAX_da.assign_coords({"Time": days_of_max[0]}),
        ],
        dim="time",
    )
# if len(daily_ds.time) == 1:
#     TMAX = xr.concat([TMAX_yesterday], dim="time")
# else:
#     pass

TMAX = TMAX_da

# %%
# TMAX = xr.concat(
#     [
#         TMAX_da.isel(time=slice(i, i + 3))
#         .max(dim="time")
#         .assign_coords({"Time": days_of_max[i]})
#         for i in range(int(len(days_of_max) / 3))
#     ],
#     dim="time",
# )


# %%
## apply fire season onset condtions and create binary mask

FSy = np.full(shape, 0, dtype=float)
FSy = xr.DataArray(FSy, name="FSy", dims=("south_north", "west_east"))

r_w = np.random.randint(0, 300, size=shape)
r_w = xr.DataArray(r_w, name="r_w", dims=("south_north", "west_east"))

FS_days = np.full(shape, 30, dtype=float)
FS_days = xr.DataArray(FS_days, name="FS_days", dims=("south_north", "west_east"))

dFS_list, FS_list, r_w_list, FS_days_list = [], [], [], []
for i in range(len(TMAX)):
    FS_days = FS_days + 1
    TMAXi = TMAX.isel(time=i)
    nan_full = np.full(TMAXi.shape, np.nan)
    # FSi = xr.where(TMAXi < 5, 1, nan_full)
    # FSi = xr.where(TMAXi > 12, 0, FSi)

    FSi = xr.where((TMAXi < 5) & (FS_days > 30), 1, nan_full)
    FSi = xr.where((TMAXi > 12) & (FS_days > 30), 0, FSi)

    ## take difference of yesterdays FS mask minus intermediate FS mask for an delta FS mask
    dFS = FSy - FSi

    ## check where onset of summer or winter have occurred in the past month
    ## if onset has happened in the past month do nothing
    # dFS = np.where((FS_days < 30) & (dFSi == -1), -1, nan_full)
    # dFS = np.where((FS_days < 30) & (dFSi == 1), 1, dFS)

    dFS = xr.DataArray(dFS, name="dFS", dims=("south_north", "west_east"))
    dFS_list.append(dFS)

    FS_days = np.where((dFS == -1) | (dFS == 1), 0, FS_days)
    FS_days = xr.DataArray(FS_days, name="FS_days", dims=("south_north", "west_east"))
    FS_days_list.append(FS_days)

    ## create todays FS binary mask
    FS = xr.where(dFS == -1, 1, FSy)
    FS = xr.where(dFS == 1, 0, FS)
    FS = xr.DataArray(FS, name="FS", dims=("south_north", "west_east"))
    FS_list.append(FS)

    ## replace FSy with FS for next day's forecast
    FSy = FS
    FS_daysY = FS_days
    ## accumulated precipitations on model grids that are in winter
    # r_w = r_w + daily_ds["r_o"].isel(time=i)

    ## Apply dFS mask to zero out r_w if winter onset occurred
    r_w = np.where(dFS == -1, 0, r_w)

    ## create dataarray of winter accumulated precipitation
    r_w = xr.DataArray(r_w, name="r_w", dims=("south_north", "west_east"))
    r_w_list.append(r_w)

dFS = xr.concat(dFS_list, dim="time")
FS = xr.concat(FS_list, dim="time")
FS_days = xr.concat(FS_days_list, dim="time")
r_w = xr.concat(r_w_list, dim="time")


print(
    f"dFS == 0 (no change of season)  {np.unique(dFS.isel(time = 32) == 0, return_counts = True)}"
)
print(
    f"dFS == 1 (onset of summer)      {np.unique(dFS.isel(time = 32) == 1, return_counts = True)}"
)
print(
    f"dFS == -1 (onset of winter)     {np.unique(dFS.isel(time = 32) == -1, return_counts = True)}"
)


import plotly.express as px

df = dFS.isel(south_north=100, west_east=300).to_dataframe()
df = df.reset_index()

fig = px.line(df, x="time", y=["dFS"])
fig.show()
# daily_ds["TMAX"] = TMAX
# daily_ds["dFS"] = dFS
# daily_ds["FS"] = FS
# daily_ds["r_w"] = r_w

# %%
