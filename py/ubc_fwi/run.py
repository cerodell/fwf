#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python
import context
import math
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime, date, timedelta
startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))
from fwi.utils.ubc_fwi.fwf import FWF
from context import data_dir, xr_dir, wrf_dir, tzone_dir, root_dir


"""######### get directory to yesterdays hourly/daily .zarr files.  #############"""
# yesterday = date.today() - timedelta(days=1)
# zarr_filein = yesterday.strftime('%Y-%m-%dT00.zarr')
# # zarr_filein = "2020-06-02T00.zarr"
# hourly_file_dir = str(xr_dir) + str("/hourly/") + zarr_filein
# daily_file_dir = str(xr_dir) + str("/daily/") + zarr_filein
hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 

"""######### get directory to todays wrf_out .nc files.  #############"""
wrf_filein = date.today().strftime('/%y%m%d00/')
# wrf_filein = str('/20060300/')
wrf_file_dir = str(wrf_dir) + wrf_filein

tar -cvzf my_files.tar.gz /path/to/my/directory
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

