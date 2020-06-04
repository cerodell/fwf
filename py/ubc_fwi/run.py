import context
import math
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime, date, timedelta
startTime = datetime.now()

from fwi.utils.ubc_fwi.fwf import FWF
from context import data_dir, xr_dir, wrf_dir, tzone_dir, root_dir

# yesterday = date.today() - timedelta(days=1)
# zarr_filein = yesterday.strftime('%Y-%m-%dT00')
# hourly_file_dir = str(xr_dir) + str("/hourly/") + zarr_filein
# daily_file_dir = str(xr_dir) + str("/daily/") + zarr_filein

# %%
"""######### Open wrf_out.nc and write  hourly/daily zarr #############"""
# wrf_filein = date.today().strftime('%y%m%d00')
wrf_filein = str('/20052400/')

wrf_file_dir = str(wrf_dir) + wrf_filein
coeff = FWF(wrf_file_dir, None, None)

daily_file_dir  = coeff.daily()
hourly_file_dir  = coeff.hourly()


"""######### Open daily_ds #############"""
daily_ds = xr.open_zarr(daily_file_dir)
print(daily_ds)
# print(np.nanmin(np.array(daily_ds.D)), "D final min")
# print(np.nanmax(np.array(daily_ds.D)), "D final max")


"""######### Open hourly_ds #############"""
hourly_ds = xr.open_zarr(hourly_file_dir)
print(hourly_ds)
# print(hourly_ds.H)
# print((hourly_ds.R))
# print(np.nanmax(np.array(hourly_ds.S)))

### Timer
print("Run Time: ", datetime.now() - startTime)

# %%



# wrf_file_dir = '/Volumes/CER/WFRT/FWI/Data/20190820'
# coeff = FWF(wrf_file_dir, hourly_file_dir, daily_file_dir )

# daily_file_dir  = coeff.daily()
# hourly_file_dir  = coeff.hourly()

# """######### Open daily_ds #############"""
# daily_ds = xr.open_zarr(daily_file_dir)
# print(daily_ds)
# print(np.nanmin(np.array(daily_ds.D)), "D final min")
# print(np.nanmax(np.array(daily_ds.D)), "D final max")
# print((daily_ds.H.projection))


# """######### Open hourly_ds #############"""
# hourly_ds = xr.open_zarr(hourly_file_dir)
# print(hourly_ds)
# print(np.nanmax(np.array(hourly_ds.S)))





# ### Timer
# print("Run Time: ", datetime.now() - startTime)

