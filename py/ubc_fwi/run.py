import context
import math
import numpy as np
import pandas as pd
import xarray as xr
import cartopy.crs as ccrs
import timezonefinder, pytz
from datetime import datetime
import matplotlib as mpl
import matplotlib.colors
import matplotlib.pyplot as plt


from fwi.utils.ubc_fwi.fwf import FWF
from fwi.utils.wrf.read_wrfout import readwrf
from context import data_dir, xr_dir, wrf_dir, tzone_dir, root_dir



# folder = "/01_wrf_ds.zarr"

# wrf_file_dir = str(data_dir) + folder
# ds_wrf = xr.open_zarr(wrf_file_dir)
wrf_file_dir = '/Volumes/CER/WFRT/FWI/Data/20190819_05'


coeff = FWF(wrf_file_dir, None)
# ds_list = coeff.loop_ds()
fwf_file_dir  = coeff.fwf_ds()
ds_ffmc = xr.open_zarr(fwf_file_dir)



# %%

# folder02 = "/20190806/"
# ds_wrf_file = readwrf(str(wrf_dir) + folder02)

# coeff02 = FWF(ds_wrf_file, ds_ffmc_file)
# ds_ffmc_file02  = coeff02.ds_fwf()

# ds_ffmc02 = xr.open_zarr(ds_ffmc_file02)



# %%

# cmap = matplotlib.colors.ListedColormap(['b','g','y','r'])
# cmap = plt.cm.jet
# level = np.arange(0,60.5,0.5)
# # v_line = np.arange(0,61,0.5)
# # bounds = [0, 21, 27, 40, 60, 100]
# # norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
# test = ds_list[1]
# test.plot(cmap = cmap, levels = level)
# day  = str(np.array(ds_wrf.Time[0], dtype ='datetime64[D]'))
# plt.savefig(str(root_dir) + '/Images/' + day + '_P.png')

# # test = ds_wrf.sel(time=slice(0 ,2))


# %%
