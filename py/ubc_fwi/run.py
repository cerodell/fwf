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

# folder = "/01_wrf_ds.zarr"

# wrf_file_dir = str(data_dir) + folder
# ds_wrf = xr.open_zarr(wrf_file_dir)
wrf_file_dir = '/Volumes/CER/WFRT/FWI/Data/20190819'


coeff = FWF(wrf_file_dir, None)
fwf_file_dir  = coeff.fwf_ds()
# fwf_file_dir  = str(xr_dir) + "/2019-08-19T00_daily_ds.zarr"
ffmc_ds = xr.open_zarr(fwf_file_dir)
print(ffmc_ds)
print(ffmc_ds.H)
# print(type(ffmc_ds.F.projection))

# from wrf import (to_np, getvar, get_cartopy, latlon_coords, g_uvmet)
# test = get_cartopy(ffmc_ds.F)


# %%

wrf_file_dir = '/Volumes/CER/WFRT/FWI/Data/20190820'

coeff02 = FWF(wrf_file_dir, fwf_file_dir)
fwf_file_dir_02  = coeff02.fwf_ds()

ffmc_ds_02 = xr.open_zarr(fwf_file_dir_02)
print(ffmc_ds_02)
print(ffmc_ds_02.F)

### Timer
print("Run Time: ", datetime.now() - startTime)

