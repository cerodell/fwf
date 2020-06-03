import context
import math
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime
startTime = datetime.now()

from fwi.utils.ubc_fwi.fwf import FWF
from context import data_dir, xr_dir, wrf_dir, tzone_dir, root_dir







# %%
"""######### Open wrf_out.nc and write to zarr #############"""
# wrf_file_dir = str(data_dir) + folder
# ds_wrf = xr.open_zarr(wrf_file_dir)
wrf_file_dir = '/Volumes/CER/WFRT/FWI/Data/20190819'
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
# print(hourly_ds)
# print(hourly_ds.H)
# print((hourly_ds.R))
print(np.nanmax(np.array(hourly_ds.S)))




# %%



wrf_file_dir = '/Volumes/CER/WFRT/FWI/Data/20190820'
coeff = FWF(wrf_file_dir, hourly_file_dir, daily_file_dir )

daily_file_dir  = coeff.daily()
hourly_file_dir  = coeff.hourly()

"""######### Open daily_ds #############"""
daily_ds = xr.open_zarr(daily_file_dir)
print(daily_ds)
print(np.nanmin(np.array(daily_ds.D)), "D final min")
print(np.nanmax(np.array(daily_ds.D)), "D final max")
print((daily_ds.H.projection))


"""######### Open hourly_ds #############"""
hourly_ds = xr.open_zarr(hourly_file_dir)
print(hourly_ds)
print(np.nanmax(np.array(hourly_ds.S)))





### Timer
print("Run Time: ", datetime.now() - startTime)

