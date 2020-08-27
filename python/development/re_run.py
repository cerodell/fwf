#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python
import context
import math
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime, date, timedelta
startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))
from utils.fwf import FWF
from context import data_dir, xr_dir, wrf_dir, tzone_dir, root_dir
import warnings

#ignore by message
warnings.filterwarnings("ignore", message="invalid value encountered in power")
warnings.filterwarnings("ignore", message="invalid value encountered in log")



"""######### get directory to yesterdays hourly/daily .zarr files.  #############"""
hourly_file_dir = str(xr_dir) + str("/fwf-hourly-2020082600.zarr") 
daily_file_dir = str(xr_dir) + str("/fwf-daily-2020082600.zarr") 

"""######### get directory to todays wrf_out .nc files.  #############"""
# wrf_filein = date.today().strftime('/%y%m%d00/')
wrf_filein = '/20082700/'
wrf_file_dir = str(wrf_dir) + wrf_filein

"""######### Open wrf_out.nc and write  new hourly/daily .zarr files #############"""
coeff = FWF(wrf_file_dir, hourly_file_dir, daily_file_dir)

daily_file_dir  = coeff.daily()
hourly_file_dir  = coeff.hourly()


"""######### Open daily_ds #############"""
# daily_ds = xr.open_zarr(daily_file_dir)
# print(daily_ds)
# print(np.nanmin(np.array(daily_ds.D)), "D final min")
# print(np.nanmax(np.array(daily_ds.D)), "D final max")

"""######### Open hourly_ds #############"""
# hourly_ds = xr.open_zarr(hourly_file_dir)
# print(hourly_ds)
# print(hourly_ds.H)
# print((hourly_ds.R))
# print(np.nanmax(np.array(hourly_ds.S)))

### Timer
print("Run Time: ", datetime.now() - startTime)

