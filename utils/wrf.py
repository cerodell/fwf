#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import salem
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


def read_wrf(filein, domain, wright=False):
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
            - Flag Indicating Percentage of Snow Coverage in Grid (1 For Snow Cover 100% Snow Coverage)
        SNOWH: DataArray
            - Physical Snow Depth (m)
        U10: DataArray
            - 10 meter U Component of Wind
        V10: DataArray
            - 10 meter V Component of Wind

    wright: boolean
        - True: write wrfout to zarr
        - True: do not write wrfout to zarr

    """
    if filein.endswith(".nc"):
        print("Run FWF using previously configured WRF files")
        grid_ds = salem.open_xr_dataset(str(data_dir) + f"/wrf/{domain}-grid.nc")
        wrf_ds = xr.open_dataset(filein)
        wrf_ds.attrs["pyproj_srs"] = grid_ds.attrs["pyproj_srs"]

    else:
        omp_set_num_threads(8)
        print(f"read files with {omp_get_max_threads()} threads")
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
            TD = getvar(wrf_file, "td2", meta=True, units="degC")
            # H = getvar(wrf_file, "rh2", meta=True)

            wsp_wdir = g_uvmet.get_uvmet10_wspd_wdir(wrf_file, units="km h-1")
            wsp_array = np.array(wsp_wdir[0])
            wdir_array = np.array(wsp_wdir[1])
            W = xr.DataArray(wsp_array, name="W", dims=("south_north", "west_east"))
            WD = xr.DataArray(wdir_array, name="WD", dims=("south_north", "west_east"))
            U10 = getvar(wrf_file, "U10", meta=True)
            V10 = getvar(wrf_file, "V10", meta=True)

            ##varied parameterization scheme to forecast rain..NOTE this is a sum of rain from the starts of the model run
            rain_c = getvar(wrf_file, "RAINC", meta=True)
            rain_sh = getvar(wrf_file, "RAINSH", meta=True)
            rain_nc = getvar(wrf_file, "RAINNC", meta=True)
            r_o_i = rain_c + rain_sh + rain_nc
            r_o = xr.DataArray(r_o_i, name="r_o", dims=("south_north", "west_east"))

            SNW = getvar(wrf_file, "SNOWNC", meta=True)
            SNOWC = getvar(wrf_file, "SNOWC", meta=True)
            SNOWH = getvar(wrf_file, "SNOWH", meta=True)

            # var_list = [T, TD, H, W, WD, r_o, SNW, SNOWC, SNOWH, U10, V10]
            var_list = [T, TD, W, WD, r_o, SNW, SNOWC, SNOWH, U10, V10]
            ds = xr.merge(var_list)
            ds_list.append(ds)

        ### Combine xarray and rename to match van wangers defs
        wrf_ds = xr.combine_nested(ds_list, "time")
        wrf_ds = wrf_ds.rename_vars({"T2": "T", "td2": "TD", "SNOWNC": "SNW"})
        wrf_ds["SNW"] = wrf_ds.SNW - wrf_ds.SNW.isel(time=0)
        wrf_ds["r_o"] = wrf_ds.r_o - wrf_ds.r_o.isel(time=0)

        RH = (
            (6.11 * 10 ** (7.5 * (wrf_ds.TD / (237.7 + wrf_ds.TD))))
            / (6.11 * 10 ** (7.5 * (wrf_ds.T / (237.7 + wrf_ds.T))))
            * 100
        )
        RH = xr.where(RH > 100, 100, RH)
        RH = xr.DataArray(RH, name="H", dims=("time", "south_north", "west_east"))
        wrf_ds["H"] = RH
        if np.min(wrf_ds.H) > 90:
            raise ValueError("ERROR: Check TD unphysical RH values")

        wrf_file = Dataset(str(pathlist[0]), "r")
        nc_attrs = wrf_file.ncattrs()
        for nc_attr in nc_attrs:
            wrf_ds.attrs[nc_attr] = repr(wrf_file.getncattr(nc_attr))

        print(list(wrf_ds))
        if wright == True:
            print(wrf_ds)
            time = np.array(wrf_ds.Time.dt.strftime("%Y-%m-%dT%H"))
            timestamp = datetime.strptime(str(time[0]), "%Y-%m-%dT%H").strftime(
                "%Y%m%d%H"
            )
            wrf_ds = wrf_ds.load()
            for var in list(wrf_ds):
                wrf_ds[var].encoding = {}

            wrf_ds_dir = str(save_dir) + str(f"wrfout-{domain}-{timestamp}.nc")
            wrf_ds.to_netcdf(wrf_ds_dir, mode="w")
            print(f"wrote {wrf_ds_dir}")
        else:
            pass

        grid_ds = salem.open_xr_dataset(str(data_dir) + f"/wrf/{domain}-grid.nc")
        wrf_ds.attrs["pyproj_srs"] = grid_ds.attrs["pyproj_srs"]
        print("readwrf run time: ", datetime.now() - startTime)

    return wrf_ds
