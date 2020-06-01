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


"""######### This Solves for hourly_ds #############"""
# hourly_file_dir  = coeff.hourly()

# hourly_ds = xr.open_zarr(hourly_file_dir)
# print(hourly_ds)
# print(hourly_ds.H)
# print((hourly_ds.F.projection))

"""######### This Solves for daily_ds #############"""
daily_file_dir  = coeff.daily()
daily_ds = xr.open_zarr(daily_file_dir)
print(daily_ds)
print(daily_ds.P)
print((daily_ds.H.projection))
daily_ds.T[1]
# u, indices = np.unique(np.array(daily_ds.T[1]), return_index=True)
# %%



wrf_file_dir = '/Volumes/CER/WFRT/FWI/Data/20190820'
coeff = FWF(wrf_file_dir, None, daily_file_dir )


# """######### This Solves for hourly_ds #############"""
# hourly_file_dir  = coeff.fwf_ds()
# hourly_ds = xr.open_zarr(hourly_file_dir)
# print(hourly_ds)
# print(hourly_ds.F)


# """######### This Solves for daily_ds #############"""
daily_file_dir  = coeff.daily()
daily_ds = xr.open_zarr(daily_file_dir)
print(daily_ds)
print(daily_ds.r_o)
# print((daily_ds.H.projection))
# daily_ds.r_o





### Timer
print("Run Time: ", datetime.now() - startTime)

