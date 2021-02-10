#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import numpy as np
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


""" ####################################################################### """
""" ######################### Grab WRF Variables ########################## """


def readwrf(filein, domain, wright):
    """
    This function reads wrfout files and grabs required met variables for fire weather index calculations.  Writes/outputs as a xarray

    Parameters
    ----------

    filein: str
        - File directory to NetCDF files
    domain: str
        - Domain tag of wrf model
    *args: list
        - [Degrees Latitude, Degrees Longitude]

    Returns
    -------

    ds_wrf: DataSet
       xarray DataSet containing
        H: DataArray
            - 2 meter Relative Humidity (%)
        T: DataArray
            - 2 meter Temperature (C)
        TD: DataArray
            - 2 meter Dew Point Temperature (C)
        W: DataArray
            - 10 meter Wind Speed (km/h)
        WD: DataArray
            - 10 meter Wind Direction (deg)
        r_o: DataArray
            - Total Accumulated Precipitation (mm)
        SNW: DataArray
            - Total Accumulated Snowfall (cm)
        SNOWC: DataArray
            - Flag Indincating Presentage of Snow Coverage in Grid (1 For Snow Cover 100% Snow Coverage)
        SNOWH: DataArray
            - Physical Snow Depth (m)
        U10: DataArray
            - 10 meter U Compentent of Wind
        V10: DataArray
            - 10 meter V Compentent of Wind

    wright: boolean
        - True: write wrfout to zarr
        - False: do not write wrfout to zarr

    """
    omp_set_num_threads(8)
    print(f"read files with {omp_get_max_threads()} threads")
    startTime = datetime.now()
    print("begin readwrf: ", str(startTime))
    ds_list = []
    pathlist = sorted(Path(filein).glob(f"wrfout_{domain}_*00"))
    if domain == "d02":
        pathlist = pathlist[6:61]
    else:
        pathlist = pathlist[6:]

    for path in pathlist:
        path_in_str = str(path)
        print(path_in_str)
        wrf_file = Dataset(path_in_str, "r")

        T = getvar(wrf_file, "T2")
        T = T.rename("T") - 273.15

        TDi = getvar(wrf_file, "td2", units="degC", meta=False)
        TD = xr.DataArray(TDi, name="TD", dims=("south_north", "west_east"))

        Hi = getvar(wrf_file, "rh2", meta=False)
        H = xr.DataArray(Hi, name="H", dims=("south_north", "west_east"))

        wsp_wdir = g_uvmet.get_uvmet10_wspd_wdir(wrf_file, units="km h-1")
        wsp_array = np.array(wsp_wdir[0])
        wdir_array = np.array(wsp_wdir[1])
        W = xr.DataArray(wsp_array, name="W", dims=("south_north", "west_east"))
        WD = xr.DataArray(wdir_array, name="WD", dims=("south_north", "west_east"))

        U10i = getvar(wrf_file, "U10", meta=False)
        U10 = xr.DataArray(U10i, name="U10", dims=("south_north", "west_east"))

        V10i = getvar(wrf_file, "V10", meta=False)
        V10 = xr.DataArray(V10i, name="V10", dims=("south_north", "west_east"))

        ##varied parameterization scheme to forecast rain..note this is a sum of rain from the starts of the model run
        rain_c = getvar(wrf_file, "RAINC", meta=False)
        rain_sh = getvar(wrf_file, "RAINSH", meta=False)
        rain_nc = getvar(wrf_file, "RAINNC", meta=False)
        r_o_i = rain_c + rain_sh + rain_nc
        r_o = xr.DataArray(r_o_i, name="r_o", dims=("south_north", "west_east"))

        SNWi = getvar(wrf_file, "SNOWNC", meta=False)
        SNW = xr.DataArray(SNWi, name="SNW", dims=("south_north", "west_east"))

        SNOWCi = getvar(wrf_file, "SNOWC", meta=False)
        SNOWC = xr.DataArray(SNOWCi, name="SNOWC", dims=("south_north", "west_east"))

        SNOWHi = getvar(wrf_file, "SNOWH", meta=False)
        SNOWH = xr.DataArray(SNOWHi, name="SNOWH", dims=("south_north", "west_east"))

        var_list = [H, T, TD, W, WD, r_o, SNW, SNOWC, SNOWH, U10, V10]

        ds = xr.merge(var_list)
        ds_list.append(ds)

    ### Combine xarray and rename to match van wangers defs
    wrf_ds = xr.combine_nested(ds_list, "time")

    wrf_file = Dataset(str(pathlist[0]), "r")

    Ti = getvar(wrf_file, "T2")
    attrs = Ti.attrs
    attrs["projection"] = str(attrs["projection"])
    wrf_ds.T.attrs = attrs
    wrf_ds.T.attrs["description"] = "2m TEMP"
    wrf_ds.T.attrs["units"] = "C"

    wrf_ds.TD.attrs = attrs
    wrf_ds.TD.attrs["description"] = "2m DEW POINT TEMP"
    wrf_ds.TD.attrs["units"] = "C"

    wrf_ds.W.attrs = attrs
    wrf_ds.WD.attrs["units"] = "km hr^-1"
    wrf_ds.W.attrs["description"] = "10m WIND SPEED"
    wrf_ds.WD.attrs = attrs
    wrf_ds.WD.attrs["description"] = "10m WIND DIRECTION"
    wrf_ds.WD.attrs["units"] = "degrees"

    wrf_ds.H.attrs = attrs
    wrf_ds.H.attrs["units"] = "(%)"
    wrf_ds.H.attrs["description"] = "2m RELATIVE HUMIDITY"

    wrf_ds.U10.attrs = attrs
    wrf_ds.U10.attrs["units"] = "m s-1"
    wrf_ds.U10.attrs["description"] = "U at 10 M"

    wrf_ds.V10.attrs = attrs
    wrf_ds.V10.attrs["units"] = "m s-1"
    wrf_ds.V10.attrs["description"] = "V at 10 M"

    wrf_ds.r_o.attrs["units"] = "mm"
    r_o.attrs["description"] = "ACCUMULATED TOTAL PRECIPITATION"

    wrf_ds.SNW.attrs["units"] = "cm"
    wrf_ds.SNW.attrs["description"] = "ACCUMULATED TOTAL GRID SCALE SNOW AND ICE"

    wrf_ds.SNOWC.attrs["units"] = ""
    wrf_ds.SNOWC.attrs[
        "description"
    ] = "FLAG INDICATING SNOW COVERAGE (1 FOR SNOW COVER)"

    wrf_ds.SNOWH.attrs["units"] = "m"
    wrf_ds.SNOWH.attrs["description"] = "PHYSICAL SNOW DEPTH"

    nc_attrs = wrf_file.ncattrs()
    for nc_attr in nc_attrs:
        wrf_ds.attrs[nc_attr] = repr(wrf_file.getncattr(nc_attr))

    if wright == True:
        print(wrf_ds)
        time = np.array(wrf_ds.Time.dt.strftime("%Y-%m-%dT%H"))
        timestamp = datetime.strptime(str(time[0]), "%Y-%m-%dT%H").strftime("%Y%m%d%H")

        wrf_ds_dir = str(save_dir) + str(f"wrfout-{domain}-{timestamp}.zarr")
        wrf_ds.to_zarr(wrf_ds_dir, mode="w")
        print(f"wrote {wrf_ds_dir}")
    else:
        pass
    print("readwrf run time: ", datetime.now() - startTime)

    return wrf_ds
