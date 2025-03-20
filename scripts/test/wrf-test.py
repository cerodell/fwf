import context
import json

import salem
import numpy as np
import xarray as xr
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
import matplotlib.colors
from datetime import datetime

from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from context import data_dir, root_dir, wrf_dir

with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

from wrf import (
    getvar,
    g_uvmet,
    get_cartopy,
    ll_to_xy,
    interplevel,
    omp_set_num_threads,
    omp_get_max_threads,
)

doi = pd.Timestamp("2012-08-01")
domain = "d03"
company = 'fa'
year = doi.strftime('%Y')
month = doi.strftime('%m')
day = doi.strftime('%d')
filein = f"{wrf_dir}/{year}/{month}/{day}/" 
omp_set_num_threads(4)
print(f"read files with {omp_get_max_threads()} threads")
startTime = datetime.now()
print("begin readwrf: ", str(startTime))
pathlist = sorted(Path(filein).glob(f"wrfsfc_{domain}_*"))

try:
    doi_yesterday = doi - pd.Timedelta('1d')
    domain = "d03"
    company = 'fa'
    year = doi_yesterday.strftime('%Y')
    month = doi_yesterday.strftime('%m')
    day = doi_yesterday.strftime('%d')
    filein = f"{wrf_dir}/{year}/{month}/{day}/" 
    pathlist_yesterday = sorted(Path(filein).glob(f"wrfsfc_{domain}_*"))
    pathlist.insert(0, pathlist_yesterday[-1])
    yesterday  = True
except:
    print("No anaylis prior")
    yesterday  = False


ds_list = []
for path in pathlist:
    path_in_str = str(path)
    # print(path_in_str)
    wrf_file = Dataset(path_in_str, "r")

    T = getvar(wrf_file, "T2", meta=True) - 273.15

    # TD = getvar(wrf_file, "td2", meta=True, units="degC")
    H = getvar(wrf_file, "rh2", meta=True)

    wsp_wdir = g_uvmet.get_uvmet10_wspd_wdir(wrf_file, units="km h-1")
    wsp_array = np.array(wsp_wdir[0])
    wdir_array = np.array(wsp_wdir[1])
    W = xr.DataArray(wsp_array, name="W", dims=("south_north", "west_east"))
    WD = xr.DataArray(wdir_array, name="WD", dims=("south_north", "west_east"))

    ##varied parameterization scheme to forecast rain..NOTE this is a sum of rain from the starts of the model run
    r_o = getvar(wrf_file, "RAINNC", meta=True)

    var_list = [T, H, W, WD, r_o]
    ds = xr.merge(var_list)
    ds_list.append(ds)

### Combine xarray and rename to match van wangers defs
fwf_ds = xr.combine_nested(ds_list, "time")
fwf_ds = fwf_ds.rename_vars({"T2": "T", "rh2": "H", "RAINNC": "r_o"})

if yesterday == True:
    if (doi.month == 8) and (doi.day == 1):
        print('Yesterday and Aug 1')
        fwf_ds["r_o"][1,:,:] = fwf_ds["r_o"].isel(time=1)  - fwf_ds["r_o"].isel(time=0)
        fwf_ds = fwf_ds.isel(time =slice(1,25))
    else:
        print('Yesterday')
        fwf_ds["r_o"] = fwf_ds.r_o - fwf_ds.r_o.isel(time=0)
        fwf_ds = fwf_ds.isel(time =slice(1,25))

if len(fwf_ds['time'])!=24:
    raise ValueError('TIme lenght is wrong')

if len(fwf_ds['r_o'])<0:
    raise ValueError('Precip is less than zero')

# if (doi.month == 8) and (doi.day == 1):
#     print("Aug 1, precipt resets")
#     yesterday  = False
# else:
#     doi_yesterday = doi - pd.Timedelta('1d')
#     domain = "d03"
#     company = 'fa'
#     year = doi_yesterday.strftime('%Y')
#     month = doi_yesterday.strftime('%m')
#     day = doi_yesterday.strftime('%d')
#     filein = f"{wrf_dir}/{year}/{month}/{day}/" 
#     pathlist_yesterday = sorted(Path(filein).glob(f"wrfsfc_{domain}_*"))
#     pathlist.insert(0, pathlist_yesterday[-1])
#     yesterday  = True

wrf_file = Dataset(str(pathlist[0]), "r")
nc_attrs = wrf_file.ncattrs()
for nc_attr in nc_attrs:
    fwf_ds.attrs[nc_attr] = repr(wrf_file.getncattr(nc_attr))


print(list(fwf_ds))
grid_ds = salem.open_xr_dataset(str(data_dir) + f"/wrf/{company}/{domain}-grid.nc")
fwf_ds.attrs["pyproj_srs"] = grid_ds.attrs["pyproj_srs"]
print("readwrf run time: ", datetime.now() - startTime)

fwf_ds.isel(south_north = 300, west_east = 10)['r_o'].plot()

fwf_ds.isel(south_north = 200, west_east = 100)['r_o'].plot()
if len(fwf_ds['time'])!=24:
    raise ValueError('TIme lenght is wrong')

if len(fwf_ds['r_o'])<0:
    raise ValueError('Precip is less than zero')
print(fwf_ds['r_o'].shape)
fwf_ds_1 = fwf_ds
