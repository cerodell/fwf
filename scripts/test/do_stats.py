import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
import scipy.stats
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.ndimage as ndimage
from scipy.ndimage.filters import gaussian_filter

from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta


domain = "d03"
# date = pd.Timestamp("today")
date = pd.Timestamp(2018, 6, 28)
intercomp_today_dir = date.strftime("%Y%m%d")

ds = xr.open_zarr(
    str(data_dir) + "/intercomp/" + f"intercomp-{domain}-{intercomp_today_dir}.zarr",
)


def checkstats(var):
    var_obs = ds[var].values.flatten()
    var_modeld = ds[var + "_day1"].values.flatten()
    ind = ~np.isnan(var_obs)
    var_obs_ = var_obs[ind]
    var_modeld_ = var_modeld[ind]
    result = scipy.stats.linregress(var_obs_, var_modeld_)
    print(var)
    print("slope ", result.slope)
    print("intercept ", result.intercept)
    print("rvalue ", result.rvalue)
    print("pvalue ", result.pvalue)
    print("stderr ", result.stderr)
    print("-------------------------")

    return


# var_list = list(ds)[::3]
for var in list(ds)[::3]:
    checkstats(var)


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
