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
doi = pd.Timestamp("2021-02-02T06")


static_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-{model}-{domain}.nc"
)
tzone_ds = salem.open_xr_dataset(str(data_dir) + f"/tzone/tzone-{model}-{domain}-ST.nc")


filein_dir = f"/Volumes/WFRT-Ext24/fwf-data/{model}/{domain}/01"
daily_ds = salem.open_xr_dataset(
    filein_dir + f"/fwf-daily-{domain}-{doi.strftime('%Y%m%d%H')}.nc"
)
# hourly = salem.open_xr_dataset(
#     filein_dir + f"/fwf-hourly-{domain}-{doi.strftime('%Y%m%d%H')}.nc"
# )

houlry_ds = salem.open_xr_dataset(
    f"/Volumes/Scratch/fwf-data/wrf/d02/202102/fwf-hourly-{domain}-{doi.strftime('%Y%m%d%H')}.nc"
)


tzone = static_ds.ZoneST.values
XLAT = houlry_ds["XLAT"].values
XLONG = houlry_ds["XLONG"].values

var_list = [
    "F",
    "R",
    "S",
]  # \ 'T', 'W', "H"]
# Subset the dataset
ds_subset = houlry_ds[var_list]
# ds_subset = houlry_ds.chunk("auto")

## find all index of 00Z in the continuous dataarray based on the inital time
time_array = houlry_ds.Time.values
int_time = int(pd.Timestamp(time_array[0]).hour)
length = len(time_array) + 1
num_days = [i for i in range(1, length) if i % 24 == 0]
if int_time == 0:
    num_days = [0] + num_days
else:
    pass
index = [i - int_time if 12 - int_time >= 0 else i + 24 - int_time for i in num_days]
if (len(houlry_ds.time) - index[-1]) < (24 + float(np.max(tzone))):
    if (len(houlry_ds.time) - index[-1]) < (float(np.max(tzone))):
        index = index[:-2]
    else:
        if len(index) != 1:
            index = index[:-1]
        else:
            pass
    if len(index) == 0:
        index = [int_time]
    if index[0] != 0:
        retrieve_time_np = time_array[0] - np.timedelta64(1, "D")
        retrieve_time = pd.to_datetime(retrieve_time_np).strftime("%Y%m%d%H")
        try:
            if (model == "wrf") or (model == "eccc"):
                int_file_dir = (
                    str(filein_dir) + f"/fwf-hourly-{domain}-{retrieve_time}.nc"
                )
                ds_yesterday = xr.open_dataset(int_file_dir).isel(
                    time=slice(index[0], 24)
                )[var_list]
                ds_subset = xr.concat(
                    [ds_yesterday, ds_subset],
                    dim="time",
                    coords="minimal",
                    compat="override",
                )
                index = [24]
        except:
            pass
        index = [0] + index
        if (len(ds_subset.time)) < (24 + index[-1] + float(np.max(tzone))):
            index = index[:-1]

        print(
            f"index of 00Z times {index} with initial time {int_time}Z using yesterdays forecast to backfill time"
        )
    else:
        print(f"index of 00Z times {index} with initial time {int_time}Z")

else:
    pass

days_of_max = [time_array[index[i]].astype("datetime64[D]") for i in range(len(index))]
## loop every 00Z index and find daily max temps between local midnight to midnight using an array of utc offsets
ds_j_list = []
for j in range(len(index)):
    ds_i_list = []
    for i in range(index[j], index[j] + 24):
        ind_a = xr.DataArray(i + tzone, dims=["south_north", "west_east"])
        ds_i = ds_subset.isel(time=ind_a)
        try:
            ds_i = ds_i.drop(
                [var for var in list(ds_i.coords) if var in ["XTIME", "XLAT", "XLONG"]]
            )
        except:
            pass
        ds_i["mTime"] = (
            ("south_north", "west_east"),
            ds_i.Time.values.astype("datetime64[h]").astype(int) % 24,
        )
        ds_i_list.append(ds_i.drop(["Time"]).chunk("auto"))
    ds_j = xr.concat(ds_i_list, dim="time", coords="minimal", compat="override").load()
    mds_j = ds_j.max(dim="time")
    if "H" in var_list:
        mds_j["H"] = ds_j["H"].min(dim="time")
    for var in var_list:
        if var == "H":
            min_index = ds_j[var].argmin(dim="time")
            # mVt =  ds_j['mTime'][dict(time=min_index)]
            mVt = ds_j["mTime"].isel(time=min_index)
            mds_j["m" + var + "t"] = mVt
            mds_j["m" + var + "t"].attrs = daily_ds[var].attrs
            mds_j["m" + var + "t"].attrs["description"] = (
                "TIME OF MIN " + daily_ds[var].attrs["description"]
            )
        else:
            max_index = ds_j[var].argmax(dim="time")
            # print(max_index.values[:4,:4])
            mVt = ds_j["mTime"].isel(time=max_index)
            mds_j["m" + var + "t"] = mVt
            mds_j["m" + var + "t"].attrs = daily_ds[var].attrs
            mds_j["m" + var + "t"].attrs["description"] = (
                "TIME OF MAX " + daily_ds[var].attrs["description"]
            )
    try:
        mds_j = mds_j.drop(["mTime", "XTIME"])
    except:
        mds_j = mds_j.drop(["mTime"])

    mds_j = mds_j.assign_coords(
        {
            "Time": days_of_max[j],
            "XLAT": (("south_north", "west_east"), XLAT),
            "XLONG": (("south_north", "west_east"), XLONG),
        }
    )
    ds_j_list.append(mds_j)

# max_ds = xr.concat(ds_j_list, dim="time")
# var_dict = {var_list[i]: 'm'+var_list[i] for i in range(len(var_list))}
# max_ds = max_ds.rename(var_dict)
# for var in var_list:
#     max_ds['m'+var].attrs = daily_ds[var].attrs
#     max_ds['m'+var].attrs['description'] = 'MAX ' + daily_ds[var].attrs['description']
# # print('daily_ds', daily_ds)
# # print('max_ds', max_ds)
# if len(daily_ds.time) == len(max_ds.time):
#     pass
# else:
#     max_ds_fake = max_ds
#     max_ds_fake['time'] = ('time', [1])
#     max_ds = xr.concat([max_ds, max_ds_fake], dim = 'time')
#     max_ds = max_ds.assign_coords({"Time" : ('time',[max_ds.Time.values, max_ds.Time.values + np.timedelta64(1, "D")])})

# daily_ds = xr.merge([max_ds, daily_ds])


print("Total Run Time: ", datetime.now() - startTime)
