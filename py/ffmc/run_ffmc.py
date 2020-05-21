import context
import math
import numpy as np
import xarray as xr
from fwi.utils.wrf.read_wrfout import readwrf
from fwi.utils.ffmc.fun_ffmc import FFMC
from context import data_dir, xr_dir, wrf_dir

ds_file = readwrf(wrf_dir)

ds_wrf = xr.open_zarr(ds_file)

coeff = FFMC(ds_file)

list_ffmc  = coeff.xr_ffmc()

# ffmc = list_ffmc[0]