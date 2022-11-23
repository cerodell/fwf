import context
import os
import math
import json
import numpy as np
import pandas as pd
import xarray as xr


from pathlib import Path
from datetime import datetime
from utils.read_wrfout import readwrf
from utils.era5 import config_era5
from utils.compressor import compressor, file_size
from context import data_dir

# import h5py


timestep = "hourly"
domain = "d02"
iterator_dir = "/Volumes/WFRT-Data02/FWF-WAN00CG/d02/WRF02/fwf"
# int_time =  xr.open_dataset(str(iterator_dir) + f"/fwf-{timestep}-{domain}-2021050106.nc").Time.values
hourly_ds = xr.open_dataset(
    str(iterator_dir) + f"/fwf-{timestep}-{domain}-2021010606.nc"
).chunk("auto")
# hourly_dsY = xr.open_dataset(str(iterator_dir) + f"/fwf-{timestep}-{domain}-2021043006.nc")


daily_ds = xr.open_dataset(str(iterator_dir) + f"/fwf-daily-{domain}-2021010606.nc")

## Open gridded static
static_ds = xr.open_dataset(str(data_dir) + f"/static/static-vars-wrf4-{domain}.nc")

tzone = static_ds.ZoneST.values

shape = tzone.shape

FSy = np.full(shape, 0, dtype=float)
FSy = xr.DataArray(FSy, name="FSy", dims=("south_north", "west_east"))

## create I, J for quick indexing
# I, J = np.ogrid[: shape[0], : shape[1]]

## determine index for looping based on length of time array and initial time
time_array = hourly_ds.Time.values

# retrieve_time_np = time_array[0] - np.timedelta64(1, "D")
# retrieve_time = pd.to_datetime(retrieve_time_np).strftime("%Y%m%d06")
# int_file_dir = (
#     str(iterator_dir) + f"/fwf-{timestep}-{domain}-{retrieve_time}.nc"
# )
# ds_yesterday = xr.open_dataset(str(iterator_dir) + f"/fwf-{timestep}-{domain}-{retrieve_time}.nc").isel(time = slice(0,24)).chunk('auto')
# hourly_ds_merge = xr.concat([ds_yesterday, hourly_ds], dim = 'time')


if timestep == "daily":
    tslice = 0
elif timestep == "hourly":
    tslice = slice(0, 24)
else:
    raise ValueError(
        f"Invalide timesept option of {timestep}, can only take daily or hourly"
    )

previous_dss, days_of_max = [], []
for i in range(4, -1, -1):
    retrieve_time_np = time_array[0] - np.timedelta64(i, "D")
    retrieve_time = pd.to_datetime(retrieve_time_np).strftime("%Y%m%d06")
    int_file_dir = str(iterator_dir) + f"/fwf-{timestep}-{domain}-{retrieve_time}.nc"
    try:
        if i == 0:
            da = xr.open_dataset(int_file_dir).chunk("auto").T
        else:
            da = xr.open_dataset(int_file_dir).isel(time=tslice).chunk("auto").T
        # da = xr.open_dataset(int_file_dir).isel(time = tslice).chunk('auto').SNOWC.mean(dim = 'time')
        previous_dss.append(da)
        days_of_max.append(retrieve_time_np.astype("datetime64[D]"))
    except:
        pass


cont_ds = xr.concat(previous_dss, dim="time").load()


time_array = cont_ds.Time.values

print(time_array[0])
int_time = int(pd.Timestamp(time_array[0]).hour)
length = len(time_array) + 1
num_days = [i - 0 for i in range(1, length) if i % 24 == 0]
index = [i - int_time if 12 - int_time >= 0 else i + 24 - int_time for i in num_days]
index = index[:-1]
print(f"index of times {index} with initial time {int_time}Z")


da_j_list = []
for j in range(len(index)):
    print(j)
    da_i_list = []
    for i in range(index[j], index[j] + 24):
        print(i)
        ind_a = xr.DataArray(i + tzone, dims=["south_north", "west_east"])
        da_i = cont_ds.isel(time=ind_a)
        da_i_list.append(da_i)
    da_j = xr.concat(da_i_list, dim="time").max(dim="time")
    da_j = da_j.assign_coords({"Time": days_of_max[j]})
    da_j_list.append(da_j)

TMAX_da = xr.concat(da_j_list, dim="time")


## TODO this is hacky, needs to be more robust for longer NWP forecast (only good for two day forecasts)
try:
    TMAX_today = (
        TMAX_da.isel(time=slice(0, 3))
        .max(dim="time")
        .assign_coords({"Time": days_of_max[-1]})
    )
    TMAX_tomorrow = (
        TMAX_da.isel(time=slice(1, 4))
        .max(dim="time")
        .assign_coords({"Time": days_of_max[-1] + np.timedelta64(1, "D")})
    )
    TMAX = xr.concat([TMAX_today, TMAX_tomorrow], dim="time")
except:
    TMAX = xr.concat(
        [
            TMAX_da.assign_coords({"Time": days_of_max[0]}),
            TMAX_da.assign_coords({"Time": days_of_max[0] + np.timedelta64(1, "D")}),
        ],
        dim="time",
    )


## apply fire season onset condtions and create binary mask
dFS_list, FS_list = [], []
for i in range(len(TMAX)):
    TMAXi = TMAX.isel(time=i)
    nan_full = np.full(TMAXi.shape, np.nan)
    FSi = xr.where(TMAXi < 5, 1, nan_full)
    FSi = xr.where(TMAXi > 12, 0, FSi)
    print("FSi")
    print(FSi)

    ## take dif of yesterdays FS mask minus intermediate FS mask
    dFS = FSy - FSi
    print("dFS")
    print(dFS)
    dFS = xr.DataArray(dFS, name="dFS", dims=("south_north", "west_east"))
    dFS_list.append(dFS)
    ## create todays FS binary mask
    FS = xr.where(dFS == -1, 1, FSy)
    FS = xr.where(dFS == 1, 0, FS)
    print("FS")
    print(FS)
    FS = xr.DataArray(FS, name="FS", dims=("south_north", "west_east"))
    FS_list.append(FS)
dFS = xr.concat(dFS_list, dim="time")
FS = xr.concat(FS_list, dim="time")

daily_ds["FS"] = FS


# try:
#     da_j_list = []
#     for j in range(len(index)):
#         print(j)
#         da_i_list = []
#         for i in range(index[j], index[j] + 24):
#             print(i)
#             ind_a = xr.DataArray(i + tzone, dims=["south_north", "west_east"])
#             da_i = cont_ds.isel(time=ind_a)
#             da_i_list.append(da_i)
#         da_j = xr.concat(da_i_list, dim="time").max(dim="time")
#         da_j = da_j.assign_coords({"Time": days_of_max[j]})
#         da_j_list.append(da_j)

#     TMAX_da = xr.concat(da_j_list, dim="time")
#     print('yay')
# except:
#     da_i_list = []
#     for i in range(index[0], index[0]+23):
#         ind_a = xr.DataArray(index[0] + tzone, dims=["south_north", "west_east"])
#         da_i = cont_ds.isel(time=ind_a)
#         da_i_list.append(da_i)
#         da = xr.concat(da_i_list, dim="time").max(dim="time")
#         da_yesterday = da
#         TMAX = xr.concat([da.assign_coords({"Time": days_of_max[0] - np.timedelta64(1, "D")}), da.assign_coords({"Time": days_of_max[0]})], dim="time")


# TMAX_yesterday = TMAX_da.isel(time = slice(0,3)).max(dim='time').assign_coords({"Time": days_of_max[-2]})
# TMAX_today = TMAX_da.isel(time = slice(1,4)).max(dim='time').assign_coords({"Time": days_of_max[-1]})

# TMAX = xr.concat([TMAX_yesterday, TMAX_today], dim="time")


## TODO take TMX avergae on the forecast days of int..ie 4-30 and 05-01

# # D = daily_ds.isel(time = 0).D
# TMAX = cont_ds.mean(dim = 'time').load()
# TMAX = TMAX.assign_coords({'Time':time_array[0].astype('datetime64[D]')})


# test = hourly_ds.isel(time = ind_a).T
# test2 = hourly_ds.isel(time = 0).T
# ## loop every 24 hours at noon local
# files_ds = []
# for i in index:
#     print(i)
#     ## loop each variable
#     mean_da = []
#     for var in int_ds.data_vars:
#         if var == "SNOWC":
#             var_array = int_ds[var].values
#             noon = var_array[(i + tzone), I, J]

# var_array = hourly_ds['T'].values

# noon = var_array[(index[0] + tzone) , I, J]

# if timestep == 'daily':
#     tslice = 0
# elif timestep == 'hourly':
#     tslice = slice(0,24)
# else:
#     raise ValueError(f'Invalide timesept option of {timestep}, can only take daily or hourly')

# previous_dss = []
# for i in range(3,0,-1):
#     retrieve_time_np = time_array[0] - np.timedelta64(i, "D")
#     retrieve_time = pd.to_datetime(retrieve_time_np).strftime("%Y%m%d06")
#     int_file_dir = (
#         str(iterator_dir) + f"/fwf-{timestep}-{domain}-{retrieve_time}.nc"
#     )
#     try:
#         da = xr.open_dataset(int_file_dir).isel(time = tslice).chunk('auto').T.max(dim = 'time')
#         # da = xr.open_dataset(int_file_dir).isel(time = tslice).chunk('auto').SNOWC.mean(dim = 'time')
#         da = da.assign_coords({'Time':retrieve_time_np.astype('datetime64[D]')})
#         previous_dss.append(da)
#     except:
#         pass

# cont_ds = xr.concat(previous_dss, dim = 'time')
# # D = daily_ds.isel(time = 0).D
# TMAX = cont_ds.mean(dim = 'time').load()
# TMAX = TMAX.assign_coords({'Time':time_array[0].astype('datetime64[D]')})

# try:
#     da = hourly_ds.isel(time = tslice).chunk('auto').T.max(dim = 'time')
#     da = da.assign_coords({'Time':time_array[0].astype('datetime64[D]')})
#     previous_dss.append(da)
#     cont_ds = xr.concat(previous_dss[1:], dim = 'time')
#     TMAX2 = cont_ds.mean(dim = 'time').load()
#     retrieve_time_np = time_array[0] + np.timedelta64(i, "D")
#     TMAX2 = TMAX2.assign_coords({'Time':retrieve_time_np.astype('datetime64[D]')})
#     TMAX = xr.concat([TMAX,TMAX2], dim = 'time')
# except:
#     TMAX = xr.concat([TMAX,TMAX], dim = 'time')


# FSy = np.random.randint(0, 2, size=TMAX.shape)

# nan_full = np.full(TMAX.shape, np.nan)
# FSi = xr.where(TMAX < 5, 1, nan_full)
# FSi = xr.where(TMAX > 12, 0, FSi)
# print('FSi')
# print(FSi)

# ## take dif of yesterdays FS mask minus intermediate FS mask
# dFS = FSy- FSi
# print('dFS')
# print(dFS)
# dFS = xr.DataArray(dFS, name="dFS", dims=("time", "south_north", "west_east"))


# ## create todays FS binary mask
# FSt = xr.where(dFS == -1, 1, FSy)
# FSt = xr.where(dFS == 1, 0, FSt)
# print('FSt')
# print(FSt)
# FSt = xr.DataArray(FSt, name="FSt", dims=("time", "south_north", "west_east"))


# ## 0 summer
# ## 1 winter
# FSy = np.random.randint(0, 2, size=(3,3))
# print('FSy')
# print(FSy)


# TMAX = np.random.randint(1, 16, size=(3,3))
# print('TMAX')
# print(TMAX)


# ## create intermediate mask of fire seaon based on TMAX from past 3 days
# nan_full = np.full(TMAX.shape, np.nan)
# FSi = np.where(TMAX < 5, 1, nan_full)
# FSi = np.where(TMAX > 12, 0, FSi)
# print('FSi')
# print(FSi)


# ## take dif of yesterdays FS mask minus intermediate FS mask
# dFS = FSy- FSi
# print('dFS')
# print(dFS)

# ## create todays FS binary mask
# FSt = np.where(dFS == -1, 1, FSy)
# FSt = np.where(dFS == 1, 0, FSt)
# print('FSt')
# print(FSt)


# D_w =


# if timestep == 'daily':
#     tslice = 0
# elif timestep == 'hourly':
#     tslice = slice(0,24)
# else:
#     raise ValueError(f'Invalide timesept option of {timestep}, can only take daily or hourly')
# previous_dss = []
# for i in range(6,0,-1):
#     retrieve_time = pd.to_datetime(str(int_time[0] - np.timedelta64(i, "D")))
#     retrieve_time = retrieve_time.strftime("%Y%m%d06")
#     int_file_dir = (
#         str(self.iterator_dir) + f"/fwf-{timestep}-{self.domain}-{retrieve_time}.nc"
#     )
#     try:
#         previous_dss.append(xr.open_dataset(int_file_dir).isel(time = timestep).chunk('auto'))
#     except:
#         pass

# cont_ds = xr.concat(previous_dss, dim = 'time' )
# self.SNOWC = cont_ds.SNOWC.mean(dim = 'time').load()
