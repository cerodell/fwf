import context
import io
import os
import json
import salem
import requests

import numpy as np
import pandas as pd
import xarray as xr
from glob import glob
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta

from context import data_dir

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

# cont_ds = xr.concat(
#     previous_dss, dim="time", coords="minimal", compat="override"
# ).load()
# print(cont_ds)
## find all index of 00Z in the continuous dataarray based on the inital time


date_range = pd.date_range("2021-01-01T00", "2021-01-04T00", freq="H")

time_array = date_range
print(time_array[0])
int_time = int(pd.Timestamp(time_array[0]).hour)
length = len(time_array) + 1
num_days = [i for i in range(1, length) if i % 24 == 0]
if int_time == 0:
    num_days = [0] + num_days
else:
    pass
print(num_days)
index = [i - int_time if 12 - int_time >= 0 else i + 24 - int_time for i in num_days]
print(index)
# index = index[:-1]
print(index)
if (len(date_range) - index[-1]) < (24 + float(9)):
    if (len(date_range) - index[-1]) < (float(9)):
        index = index[:-2]
    else:
        index = index[:-1]
else:
    pass
# if self.iterator == "fwf":
#     pass
#     # index = index[:-1]
# elif self.iterator == "era5":
#     # index = [0] + index
#     pass
# else:
#     raise ValueError("Bad iterator")
# print(index)

print(f"index of 00Z times {index} with initial time {int_time}Z")


# def convert_bytes(num):
#     """
#     this function will convert bytes to MB.... GB... etc
#     """
#     for x in ["bytes", "KB", "MB", "GB", "TB"]:
#         if num < 1024.0:
#             return "%3.1f %s" % (num, x)
#         num /= 1024.0


# def file_size(file_path):
#     """
#     this function will return the file size
#     """
#     if os.path.isfile(file_path):
#         file_info = os.stat(file_path)
#         return convert_bytes(file_info.st_size)


# def compressor(ds):
#     """
#     this function comresses datasets
#     """
#     # ds = ds.load()
#     # ds.attrs["TITLE"] = "FWF MODEL USING OUTPUT FROM WRF V4.2.1 MODEL"
#     comp = dict(zlib=True, complevel=9)
#     encoding = {var: comp for var in ds.data_vars}
#     # for var in ds.data_vars:
#     #     ds[var].attrs = var_dict[var]

#     return ds, encoding


# date_range = pd.date_range("1991-01-01", "2021-01-01")

# filein = "/Volumes/WFRT-Ext24/era5/era5-mslp-monthly-1991-2021.nc"
# fileout = "/Volumes/WFRT-Ext24/era5/era5-mslp-monthly-1991-2021-compress.nc"

# ds = xr.open_dataset(filein)

# writeTime = datetime.now()
# ds, encoding = compressor(ds)
# ds.to_netcdf(fileout, encoding=encoding, mode="w")
# print(f"Write Time: ", datetime.now() - writeTime)
# print(
#     f"Compressed daily from {file_size(filein)} to {file_size(fileout)}"
