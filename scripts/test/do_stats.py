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
from pylab import *

from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta


domain = "d03"
# date = pd.Timestamp("today")
date = pd.Timestamp(2018, 10, 1)
intercomp_today_dir = date.strftime("%Y%m%d")

ds = xr.open_zarr(
    str(data_dir) + "/intercomp/" + f"intercomp-{domain}-{intercomp_today_dir}.zarr",
)

# wrf_in = xr.open_zarr('/Volumes/cer/fireweather/data/WAN00CP-04/wrfout-d03-2018090706.zarr')

# wrf_in = wrf_in.compute()
# wrf_in.to_zarr('/Volumes/cer/fireweather/data/WAN00CP-04/wrfout-d03-2018090706.zarr', mode = 'w')

cmap = cm.get_cmap("tab10", len(list(ds)[::3]) + 1)  # PiYG
colors = []
for i in range(cmap.N):
    rgba = cmap(i)
    colors.append(matplotlib.colors.rgb2hex(rgba))


# ds = ds.isel(time= slice(-30,))
if domain == "d02":
    res = "12 km"
else:
    res = "4 km"


def checkstats(var, color):
    time = np.array(ds.time.dt.strftime("%Y-%m-%d"), dtype="<U10")
    start_time = datetime.strptime(str(time[0]), "%Y-%m-%d").strftime("%Y%m%d")
    end_time = datetime.strptime(str(time[-1]), "%Y-%m-%d").strftime("%Y%m%d")
    var_obs = ds[var].values.flatten()
    var_modeld = ds[var + "_day1"].values.flatten()
    ind = ~np.isnan(var_obs)
    var_obs_ = var_obs[ind]
    var_modeld_ = var_modeld[ind]
    result = scipy.stats.linregress(var_modeld_, var_obs_)
    # # result = scipy.stats.linregress(var_obs_, var_modeld_)
    print(len(var_modeld_) == len(var_obs_))
    print(var.upper())
    print("slope ", result.slope)
    print("intercept ", result.intercept)
    print("rvalue ", result.rvalue)
    print("pvalue ", result.pvalue)
    print("stderr ", result.stderr)
    print("-------------------------")
    plt.close()
    fig = plt.figure()  # figsize=[8, 8]
    ax = fig.add_subplot(1, 1, 1)
    ax.set_title(
        f"WRF3 Domain {res} for {var.upper()} \n slope: {round(result.slope,3)}  intercept: {round(result.intercept,3)}  rvalue: {round(result.rvalue,3)}  pvalue: {round(result.pvalue,3)}  stderr: {round(result.stderr,3)} \n {start_time}-{end_time}"
    )
    ax.scatter(var_modeld_, var_obs_, s=0.5, color=color)
    xpoints = ypoints = ax.get_xlim()
    ax.plot(
        xpoints, ypoints, linestyle="--", color="k", lw=0.6, scalex=False, scaley=False
    )
    ax.set_xlabel("Observed")
    ax.set_ylabel("Modeled")
    fig.savefig(
        str(data_dir) + f"/images/stats/{var}-{domain}-{start_time}-{end_time}.png"
    )
    plt.close()

    return


var_list = list(ds)[::3]
for i in range(len(var_list)):
    checkstats(var_list[i], colors[i])


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
