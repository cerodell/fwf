import context
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset

from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta


domain = "d02"
date = pd.Timestamp("today")
# date = pd.Timestamp(2021, 2, 15)
forecast_date = date.strftime("%Y%m%d06")

file_dir = str(fwf_zarr_dir) + f"/fwf-hourly-{domain}-{forecast_date}.zarr"
ds = xr.open_zarr(file_dir)

# ds = ds.isel(time=0)

# filein = str(wrf_dir) + f"/wrfout-{domain}-2021010306.zarr"
# # pathlist = sorted(Path(filein).glob(f"wrfout_{domain}_*00"))

# # wrf_file = Dataset(file_dir, "r")
# wrf_ds = xr.open_zarr(file_dir)


# ds = xr.open_zarr(
#     str(data_dir) + "/intercomp/" + f"intercomp-{domain}-{file_date}.zarr"
# )

# for var in list(ds):
#     # print(f"max of {var}: {str(ds.Time.values)}")
#     print(f"max of {var}: {float(ds[var].max(skipna= True))}")
#     print(f"min of {var}: {float(ds[var].min(skipna= True))}")
#     print(f"mean of {var}: {float(ds[var].mean(skipna= True))}")

# var = "DC_day1"
# for i in range(len(ds.time)):
#     print(str(ds.time.values[i]))
#     print(float(ds.isel(time=i)[var].max(skipna=True)))
#     print(float(ds.isel(time=i)[var].min(skipna=True)))
#     print(float(ds.isel(time=i)[var].mean(skipna=True)))

# air1d = ds[var].isel(wmo=200)

# air1d.plot()
