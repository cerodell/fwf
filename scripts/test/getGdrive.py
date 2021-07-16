import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime, timedelta

from wrf import getvar, ll_to_xy, omp_set_num_threads, omp_get_max_threads, g_uvmet

wrf_dir = "/Users/rodell/Google Drive/Shared drives/WAN00CG-01/"
# path to save data
save_dir = "/Users/rodell/fwf/data/FWF-WAN00CG-01/"

# range of dates to extract data for
date_range = pd.date_range("2021-03-17", "2021-03-17")
print(wrf_dir)


def readwrf(filein, domain, save_dir, *args):
    """
    This function reads wrfout files and grabs required met variables for fire weather index calculations.  Writes/outputs as a xarray

        - wind speed (km h-1)
        - temp (degC)
        - rh (%)
        - qpf (mm)
        - snw (mm)

    Parameters
    ----------

    files: str
        - File directory to NetCDF files

    Returns
    -------

    ds_wrf: DataSet
        xarray DataSet
    """
    startTime = datetime.now()
    print("begin readwrf: ", str(startTime))
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

    if args:
        xy_np = np.array(ll_to_xy(wrf_file, float(args[0]), float(args[1])))
    else:
        xy_np = None

    time = np.array(wrf_ds.Time.dt.strftime("%Y-%m-%dT%H"))
    timestamp = datetime.strptime(str(time[0]), "%Y-%m-%dT%H").strftime("%Y%m%d%H")

    print(list(wrf_ds))

    wrf_ds_dir = str(save_dir) + str(f"fwf-hourly-{domain}-{timestamp}.zarr")
    wrf_ds.to_zarr(wrf_ds_dir, mode="w")
    print(f"wrote {wrf_ds_dir}")
    print("readwrf run time: ", datetime.now() - startTime)

    return wrf_ds, xy_np


for domain in ["d03"]:
    for date in date_range:
        wrf_filein = date.strftime("%y%m%d00/")
        wrf_file_dir = str(wrf_dir) + wrf_filein
        print(wrf_file_dir)
        readwrf(wrf_file_dir, domain, save_dir)
