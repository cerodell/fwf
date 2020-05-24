import context
import math
import numpy as np
import xarray as xr
from fwi.utils.wrf.read_wrfout import readwrf
from fwi.utils.ubc_fwi.fwf import FWF
from context import data_dir, xr_dir, wrf_dir

folder = "/20190805/"
ds_wrf_file = readwrf(str(wrf_dir) + folder)
ds_wrf = xr.open_zarr(ds_wrf_file)

coeff = FWF(ds_wrf_file, None)
ds_list = coeff.loop_ds()
ds_ffmc_file  = coeff.ds_fwf()

ds_ffmc = xr.open_zarr(ds_ffmc_file)





folder02 = "/20190806/"
ds_wrf_file = readwrf(str(wrf_dir) + folder02)

coeff02 = FWF(ds_wrf_file, ds_ffmc_file)
ds_ffmc_file02  = coeff02.ds_fwf()

ds_ffmc02 = xr.open_zarr(ds_ffmc_file02)


