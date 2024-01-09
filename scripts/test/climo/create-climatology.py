#!/Users/crodell/miniconda3/envs/fwx/bin/python
import json
import context
import salem
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime

from utils.compressor import compressor
from utils.climatology import get_daily_files, hour_qunt, rechunk, open_ds, concat_ds
from context import root_dir

## https://stackoverflow.com/questions/49620140/get-hourly-average-for-each-month-from-a-netcds-file

save_dir = Path("/Volumes/WFRT-Ext22/ecmwf/era5-land/")
save_dir.mkdir(parents=True, exist_ok=True)
var = "S"
# var_list = ['S', 'F', 'P', 'D', 'R', 'U', 'DSR', "T", "W", "H", 'r_o']
# var_list = ['S', 'R', 'F']
fwf = True
method = "hourly"
start = "1991-01-01"
stop = "2020-12-31"


## open additional fwf attributes
with open(str(root_dir) + f"/json/colormaps-dev.json", "r") as fp:
    attrs_plus = json.load(fp)


## get all files for era5-land of fwf
pathlist = get_daily_files(fwf, method, start, stop)

## open =, chunk and combine into single dask chunk dataset
open = datetime.now()
print("Start opening: ", open)
ds = concat_ds(pathlist, var)
print("Opening Time: ", datetime.now() - open)


rechunk_time = datetime.now()
print("Start rechunking: ", rechunk_time)
ds = rechunk(ds)
print("rechunk Time: ", datetime.now() - rechunk_time)

group = datetime.now()
print("Start Grouping: ", group)
if method == "daily":
    ## group data into dayofyear and solve for quantiles for each day over the 30 years
    ds = ds.groupby("time.dayofyear").quantile(
        [0, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 1.0], dim="time"
    )
elif method == "hourly":
    ## group data into hours for each month and solve for quantiles for each hour on each month over the 30 years
    ds = ds.groupby("time.month").apply(hour_qunt)
else:
    raise ValueError(f"Not a valid method: {method}")
print("Grouping Time: ", datetime.now() - group)


# Add some dataset attributes
ds.attrs["pyproj_srs"] = "+proj=longlat +datum=WGS84 +no_defs"
ds.attrs[
    "description"
] = f"30 year ({start.replace('-','')}-{stop.replace('-','')}) climatology"
ds[var].attrs["pyproj_srs"] = "+proj=longlat +datum=WGS84 +no_defs"

rechunk_time = datetime.now()
print("Start rechunking: ", rechunk_time)
ds = rechunk(ds)
print("rechunk Time: ", datetime.now() - rechunk_time)

# write ds to netcdf
# ds, encoding = compressor(ds)
write = datetime.now()
print("Start Writing: ", write)
ds.to_netcdf(
    str(save_dir)
    + f"/{attrs_plus[var]['name']}-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}.nc",
    mode="w",
    # encoding = encoding
)
print("Write Time: ", datetime.now() - write)


# group = datetime.now()
# print("Start Grouping: ", group)
# ds_dayofyear = ds.groupby('time.dayofyear').apply(hour_qunt)
# print("Day of year Time: ", datetime.now() - group)

# group = datetime.now()
# print("Start Grouping: ", group)
# ds_month = ds.groupby('time.month').apply(hour_qunt)
# print("Month Time: ", datetime.now() - group)


# rechunk_time = datetime.now()
# print("Start rechunking: ", rechunk_time)
# ds = rechunk(ds)
# print("rechunk Time: ", datetime.now() - rechunk_time)

# drop_time = datetime.now()
# print("Start dropping: ", drop_time)
# ds["time"] = ds["Time"]
# ds = ds.drop(["Time"])
# print("Dropping Time: ", datetime.now() - drop_time)


# di, dj = 517, 237
# for i in range(0,3):
#     for j in range(0,3):
#         make_climo(ds_full, i, j, di, dj)
# file_name = str(save_dir) + f"/{attrs_plus[var]['name']}-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}-i{i}j{j}.nc"
# slicing = datetime.now()
# print("Start Slicing: ", slicing)
# ds = ds_full.isel(south_north = slice(j*dj, jj*dj), west_east = slice(i*di, ii*di)).copy(deep=True)
# print("Slicing Time: ", datetime.now() - slicing)

# rechunk_time = datetime.now()
# print("Start rechunking: ", rechunk_time)
# ds = rechunk(ds)
# print("rechunk Time: ", datetime.now() - rechunk_time)

# if method == 'daily':
#     ## group data into dayofyear and solve for quantiles for each day over the 30 years
#     group = datetime.now()
#     print("Start Grouping: ", group)
#     ds = ds.groupby("time.dayofyear").quantile([0, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 1.0], dim='time')
#     print("Grouping Time: ", datetime.now() - group)
# elif method == 'hourly':
#     ## group data into hours for each dayofyear adn solve for quantiles for each hour on each day over the 30 years
#     group = datetime.now()
#     print("Start Grouping: ", group)
#     ds = ds.groupby('time.dayofyear').apply(hour_qunt)
#     print("Grouping Time: ", datetime.now() - group)
# else:
#     raise ValueError(f'Not a valid method: {method}')

# # Add some dataset attributes
# ds.attrs["pyproj_srs"] = "+proj=longlat +datum=WGS84 +no_defs"
# ds.attrs[
#     "description"
# ] = f"30 year ({start.replace('-','')}-{stop.replace('-','')}) climatology"

# # ds[var].attrs = attrs[var]
# # ds[var].attrs['abbr'] = attrs_plus[var]['name']
# ds[var].attrs["pyproj_srs"] = "+proj=longlat +datum=WGS84 +no_defs"


# rechunk_time = datetime.now()
# ds = rechunk(ds)
# print("rechunk Time: ", datetime.now() - rechunk_time)

# ## invoke compute to take dask to numpy (ie lazy objects to numerics)
# computeTime = datetime.now()
# ds = ds.compute()
# print("Compute Time: ", datetime.now() - computeTime)

# # write ds to netcdf
# # ds, encoding = compressor(ds)
# write = datetime.now()
# print("Start Writing: ", write)
# ds.to_netcdf(
#     file_name,
#     mode="w",
#     # encoding = encoding
# )
# print("Write Time: ", datetime.now() - write)


# ds = salem.open_xr_dataset(str(pathlist[0]))['S']
# # (24, 711, 1551)
# # (24, 711/3, 1551/3) = (24, 237, 517)
# # (24, 711/9, 1551/11) = (24, 79, 141)
# file_names = []
# di, dj = 517, 237
# ds_final = ds.salem.transform(ds.isel(south_north = slice(0*dj, 1*dj), west_east = slice(0*di, 1*di)).isel(time=0))
# for i in range(0,3):
#     ii = i +1
#     for j in range(0,3):
#         jj = j+1
#         ds_slice = ds.isel(south_north = slice(j*dj, jj*dj), west_east = slice(i*di, ii*di))
#         ds_final[j*dj: jj*dj, i*di: ii*di] = ds_slice.isel(time=0)

#         file_names.append(str(save_dir) + f"/{attrs_plus[var]['name']}-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}-i{i}j{j}.nc")
# ds_final.salem.quick_map()


# def make_climo(ds_full, i, j, di, dj):
#         ii = i +1
#         jj = j+1
#         file_name = str(save_dir) + f"/{attrs_plus[var]['name']}-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}-i{i}j{j}.nc"
#         slicing = datetime.now()
#         print("Start Slicing: ", slicing)
#         ds = ds_full.isel(south_north = slice(j*dj, jj*dj), west_east = slice(i*di, ii*di)).copy(deep=True)
#         print("Slicing Time: ", datetime.now() - slicing)

#         rechunk_time = datetime.now()
#         print("Start rechunking: ", rechunk_time)
#         ds = rechunk(ds)
#         print("rechunk Time: ", datetime.now() - rechunk_time)

#         if method == 'daily':
#             ## group data into dayofyear and solve for quantiles for each day over the 30 years
#             group = datetime.now()
#             print("Start Grouping: ", group)
#             ds = ds.groupby("time.dayofyear").quantile([0, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 1.0], dim='time')
#             print("Grouping Time: ", datetime.now() - group)
#         elif method == 'hourly':
#             ## group data into hours for each dayofyear adn solve for quantiles for each hour on each day over the 30 years
#             group = datetime.now()
#             print("Start Grouping: ", group)
#             ds = ds.groupby('time.dayofyear').apply(hour_qunt)
#             print("Grouping Time: ", datetime.now() - group)
#         else:
#             raise ValueError(f'Not a valid method: {method}')

#         # Add some dataset attributes
#         ds.attrs["pyproj_srs"] = "+proj=longlat +datum=WGS84 +no_defs"
#         ds.attrs[
#             "description"
#         ] = f"30 year ({start.replace('-','')}-{stop.replace('-','')}) climatology"

#         # ds[var].attrs = attrs[var]
#         # ds[var].attrs['abbr'] = attrs_plus[var]['name']
#         ds[var].attrs["pyproj_srs"] = "+proj=longlat +datum=WGS84 +no_defs"

#         rechunk_time = datetime.now()
#         print("Start rechunking: ", rechunk_time)
#         ds = rechunk(ds)
#         print("rechunk Time: ", datetime.now() - rechunk_time)

#         # write ds to netcdf
#         # ds, encoding = compressor(ds)
#         write = datetime.now()
#         print("Start Writing: ", write)
#         ds.to_netcdf(
#             file_name,
#             mode="w",
#             # encoding = encoding
#         )
#         print("Write Time: ", datetime.now() - write)
#         return


# # def hour_mean(x):
# #     """
# #     function groups time to hourly and solves hourly mean

# #     """
# #     return x.groupby("time.hour").mean("time")


# # def day_max(x):
# #     """
# #     function groups time to daily and take daily max

# #     """
# #     return x.groupby('time.day').max('time')


# # # ## group data into months and days solve for mean daily max over the month for the full the 30 years
# # group = datetime.now()
# # ds = ds.groupby("time.month").apply(day_max).mean("day")
# # print("Grouping Time: ", datetime.now() - group)

# # # ## group data into months and solve for monthly average over the 30 years
# # # group = datetime.now()
# # # ds = ds.groupby("time.month").mean("time")
# # # print("Grouping Time: ", datetime.now() - group)

# # # loadTime = datetime.now()
# # # ds = ds.load()
# # # print("Loading Time: ", datetime.now() - loadTime)


# # ## group data into month day hour and solve the hourly means
# # # group = datetime.now()
# # # ds = ds.groupby("time.month").apply(hour_mean)
# # # ds = xr.apply_ufunc(hour_mean, ds, dask='parallelized',output_dtypes=[float], vectorize=True,)
# # # print("Grouping Time: ", datetime.now() - group)

# # # open = datetime.now()
# # # ds = xr.concat([xr.open_dataset(path, chunks="auto") for path in pathlist],dim = 'time')
# # # print("Opening Time: ", datetime.now() - open)


# # # rechunk_time = datetime.now()
# # # ds = rechunk(ds)
# # # print("rechunk Time: ", datetime.now() - rechunk_time)


# # # def hour_mean(x):
# # #     """
# # #     function groups time to hourly and solves hourly mean

# # #     """
# # #     return x.groupby('time.hour').mean('time')

# # # def day_mean(x):
# # #     """
# # #     function groups time to daily and feeds into hourly_mean

# # #     """
# # #     x = x.groupby('time.day').mean('time') #.apply(hour_mean)
# # #     # rechunk_time = datetime.now()
# # #     # x = rechunk(x)
# # #     # print("Rechunk Time: ", datetime.now() - rechunk_time)
# # #     return x
