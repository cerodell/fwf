#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from context import data_dir, xr_dir, wrf_dir

from wrf import (
    getvar,
    g_uvmet,
    get_cartopy,
    ll_to_xy,
    interplevel,
    omp_set_num_threads,
    omp_get_max_threads,
)

wrf_model = "wrf4"
domain = "d02"
# forecast_date = pd.Timestamp(2021, 4, 12).strftime("%Y%m%d06")
forecast_date = pd.Timestamp("today").strftime("%Y%m%d00")
filein = str(wrf_dir) + f"/{forecast_date}/"


omp_set_num_threads(8)
startTime = datetime.now()
pathlist = sorted(Path(filein).glob(f"wrfout_{domain}_*00"))
if domain == "d02":
    pathlist = pathlist[6:61]
else:
    pathlist = pathlist[6:]

ds_list = []
for path in pathlist:
    path_in_str = str(path)
    print(path_in_str)
    wrf_file = Dataset(path_in_str, "r")

    T = getvar(wrf_file, "T2", meta=True) - 273.15
    TD = getvar(wrf_file, "td2", meta=True) - 273.15
    H = getvar(wrf_file, "rh2", meta=True)

    wsp_wdir = g_uvmet.get_uvmet10_wspd_wdir(wrf_file, units="km h-1")
    wsp_array = np.array(wsp_wdir[0])
    wdir_array = np.array(wsp_wdir[1])
    W = xr.DataArray(wsp_array, name="W", dims=("south_north", "west_east"))
    WD = xr.DataArray(wdir_array, name="WD", dims=("south_north", "west_east"))
    U10 = getvar(wrf_file, "U10", meta=True)
    V10 = getvar(wrf_file, "V10", meta=True)

    ##varied parameterization scheme to forecast rain..note this is a sum of rain from the starts of the model run
    rain_c = getvar(wrf_file, "RAINC", meta=True)
    rain_sh = getvar(wrf_file, "RAINSH", meta=True)
    rain_nc = getvar(wrf_file, "RAINNC", meta=True)
    r_o_i = rain_c + rain_sh + rain_nc
    r_o = xr.DataArray(r_o_i, name="r_o", dims=("south_north", "west_east"))

    SNW = getvar(wrf_file, "SNOWNC", meta=True)
    SNOWC = getvar(wrf_file, "SNOWC", meta=True)
    SNOWH = getvar(wrf_file, "SNOWH", meta=True)

    var_list = [T, TD, H, W, WD, r_o, SNW, SNOWC, SNOWH, U10, V10]
    ds = xr.merge(var_list)
    ds_list.append(ds)

### Combine xarray and rename to match van wangers defs
wrf_ds = xr.combine_nested(ds_list, "time")
wrf_ds = wrf_ds.rename_vars({"T2": "T", "td2": "TD", "rh2": "H", "SNOWNC": "SNW"})
wrf_ds["SNW"] = wrf_ds.SNW - wrf_ds.SNW.isel(time=0)
wrf_ds["r_o"] = wrf_ds.r_o - wrf_ds.r_o.isel(time=0)

wrf_file = Dataset(str(pathlist[0]), "r")
nc_attrs = wrf_file.ncattrs()
for nc_attr in nc_attrs:
    wrf_ds.attrs[nc_attr] = repr(wrf_file.getncattr(nc_attr))

wrf_ds = wrf_ds.load()
for var in list(wrf_ds):
    wrf_ds[var].encoding = {}

print("readwrf run time: ", datetime.now() - startTime)
