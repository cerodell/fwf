import context
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from utils.read_wrfout import readwrf

from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta


domain = "d02"
# date = pd.Timestamp("today")
date = pd.Timestamp(2018, 4, 5)
forecast_date = date.strftime("%Y%m%d06")

file_dir = str(fwf_zarr_dir) + f"/fwf-daily-{domain}-{forecast_date}.zarr"
ds = xr.open_zarr(file_dir)
ds = ds.isel(time=0)
# F = ds.U.isel(south_north = 10, west_east= 300 )
# F.plot()

for var in list(ds):
    # print(f"max of {var}: {str(ds.Time.values)}")
    print(f"max of {var}: {float(ds[var].max(skipna= True))}")
    print(f"min of {var}: {float(ds[var].min(skipna= True))}")
    print(f"mean of {var}: {float(ds[var].mean(skipna= True))}")

# var = "DC_day1"
# for i in range(len(ds.time)):
#     print(str(ds.time.values[i]))
#     print(float(ds.isel(time=i)[var].max(skipna=True)))
#     print(float(ds.isel(time=i)[var].min(skipna=True)))
#     print(float(ds.isel(time=i)[var].mean(skipna=True)))
