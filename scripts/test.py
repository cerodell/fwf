<<<<<<< HEAD
#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import wrf
import json
import pickle
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime

# from wrf import omp_set_num_threads, omp_get_max_threads

# omp_set_num_threads(8)
# print(f"read files with {omp_get_max_threads()} threads")

startTime = datetime.now()

g = 9.81  # gravity
pm_ef = 21.05  # boreal wildfire emission factor Urbanski (2014)
zstep = 20.0  # vertical step to interpolate to
BLfrac = 0.75  # fraction of BL height to set zs at
interpz = np.arange(0, 4000, zstep)
interpz[0] = 2
interpz = np.insert(interpz, 1, 10)


ncfile = Dataset("/bluesky/fireweather/fwf/data/wrfout_d01_2019-05-11_17:49:11")
# ncfile = Dataset(str(vol_dir) + "/sfire/unit5/wrfout_d01_0001-01-01_00:00:00")
save_dir = "/bluesky/fireweather/fwf/data/"


# startCache= datetime.now()
# my_cache = wrf.extract_vars(ncfile, wrf.ALL_TIMES, ( "PSFC", "PH", "PHB"))
# print("Cache time: ", datetime.now() - startCache)

startInterp = datetime.now()

print(f"Start of Interoplation ---> {datetime.now()}")
startVar = datetime.now()
# tr17_1 = wrf.getvar(ncfile, "tr17_1", wrf.ALL_TIMES)
interp_tr17_1 = wrf.vinterp(
    ncfile,
    field=wrf.getvar(ncfile, "tr17_1", wrf.ALL_TIMES),
    vert_coord="ght_msl",
    interp_levels=interpz / 1000,
    extrapolate=True,
    log_p=True,
    timeidx=wrf.ALL_TIMES,
    # cache=my_cache
)
print("Interpolate tracer time: ", datetime.now() - startVar)

startVar = datetime.now()
# qvapor = wrf.getvar(ncfile, "QVAPOR", wrf.ALL_TIMES)
interp_qvapor = wrf.vinterp(
    ncfile,
    field=wrf.getvar(ncfile, "QVAPOR", wrf.ALL_TIMES),
    vert_coord="ght_msl",
    interp_levels=interpz / 1000,
    extrapolate=True,
    log_p=True,
    timeidx=wrf.ALL_TIMES,
    # cache=my_cache
)
print("Interpolate qvapor time: ", datetime.now() - startVar)

startVar = datetime.now()
# temp = wrf.getvar(ncfile, "temp", wrf.ALL_TIMES)
interp_temp = wrf.vinterp(
    ncfile,
    field=wrf.getvar(ncfile, "temp", wrf.ALL_TIMES),
    vert_coord="ght_msl",
    interp_levels=interpz / 1000,
    extrapolate=True,
    log_p=True,
    timeidx=wrf.ALL_TIMES,
    field_type="tk",
    # cache=my_cache
)
print("Interpolate temp time: ", datetime.now() - startVar)

startVar = datetime.now()
# td = wrf.getvar(ncfile, "td", wrf.ALL_TIMES)
interp_td = wrf.vinterp(
    ncfile,
    field=wrf.getvar(ncfile, "td", wrf.ALL_TIMES),
    vert_coord="ght_msl",
    interp_levels=interpz / 1000,
    extrapolate=True,
    log_p=True,
    timeidx=wrf.ALL_TIMES,
    field_type="tk",
    # cache=my_cache
)
print("Interpolate td time: ", datetime.now() - startVar)

startVar = datetime.now()
# theta_e = wrf.getvar(ncfile, "theta_e", wrf.ALL_TIMES)
interp_theta_e = wrf.vinterp(
    ncfile,
    field=wrf.getvar(ncfile, "theta_e", wrf.ALL_TIMES),
    vert_coord="ght_msl",
    interp_levels=interpz / 1000,
    extrapolate=True,
    log_p=True,
    timeidx=wrf.ALL_TIMES,
    field_type="tk",
    # cache=my_cache
)
print("Interpolate theta_e time: ", datetime.now() - startVar)

startVar = datetime.now()
# rh = wrf.getvar(ncfile, "rh", wrf.ALL_TIMES)
interp_rh = wrf.vinterp(
    ncfile,
    field=wrf.getvar(ncfile, "rh", wrf.ALL_TIMES),
    vert_coord="ght_msl",
    interp_levels=interpz / 1000,
    extrapolate=True,
    log_p=True,
    timeidx=wrf.ALL_TIMES,
    # cache=my_cache
)
print("Interpolate rh time: ", datetime.now() - startVar)

startVar = datetime.now()
# U = wrf.getvar(ncfile, "ua", wrf.ALL_TIMES)
interp_U = wrf.vinterp(
    ncfile,
    field=wrf.getvar(ncfile, "ua", wrf.ALL_TIMES),
    vert_coord="ght_msl",
    interp_levels=interpz / 1000,
    extrapolate=True,
    log_p=True,
    timeidx=wrf.ALL_TIMES,
    # cache=my_cache
)
print("Interpolate U time: ", datetime.now() - startVar)


startVar = datetime.now()
# V = wrf.getvar(ncfile, "va", wrf.ALL_TIMES)
interp_V = wrf.vinterp(
    ncfile,
    field=wrf.getvar(ncfile, "va", wrf.ALL_TIMES),
    vert_coord="ght_msl",
    interp_levels=interpz / 1000,
    extrapolate=True,
    log_p=True,
    timeidx=wrf.ALL_TIMES,
    # cache=my_cache
)
print("Interpolate V time: ", datetime.now() - startVar)


startVar = datetime.now()
# W = wrf.getvar(ncfile, "wa", wrf.ALL_TIMES)
interp_W = wrf.vinterp(
    ncfile,
    field=wrf.getvar(ncfile, "wa", wrf.ALL_TIMES),
    vert_coord="ght_msl",
    interp_levels=interpz / 1000,
    extrapolate=True,
    log_p=True,
    timeidx=wrf.ALL_TIMES,
    # cache=my_cache
)
print("Interpolate W time: ", datetime.now() - startVar)


startVar = datetime.now()
# pressure = wrf.getvar(ncfile, "pressure", wrf.ALL_TIMES)
interp_pressure = wrf.vinterp(
    ncfile,
    field=wrf.getvar(ncfile, "pressure", wrf.ALL_TIMES),
    vert_coord="ght_msl",
    interp_levels=interpz / 1000,
    extrapolate=True,
    log_p=True,
    timeidx=wrf.ALL_TIMES,
    # cache=my_cache
)
print("Interpolate pressure time: ", datetime.now() - startVar)


def compressor(ds):
    """
    this function comresses datasets
    """
    # print('loading')
    # ds = ds.load()
    print("zipping")
    comp = dict(zlib=True, complevel=9)
    print("encoding")
    encoding = {var: comp for var in ds.data_vars}
    return ds, encoding


interp_ds = xr.merge(
    [
        interp_tr17_1,
        interp_qvapor,
        interp_temp,
        interp_td,
        interp_theta_e,
        interp_rh,
        interp_U,
        interp_V,
        interp_W,
        interp_pressure,
    ]
)
interp_ds.attrs = {
    "description": "WRF SFIRE UNIT 5 MOISTURE OFF",
    "dx": "25 m",
    "dy": "25 m",
    "dz": "20 m",
}
for var in interp_ds.data_vars:
    interp_ds[var].attrs["projection"] = str(interp_ds[var].attrs["projection"])
print("Interpolate time: ", datetime.now() - startInterp)

startCompress = datetime.now()
comp_ds, encoding = compressor(interp_ds)
print("Compress time: ", datetime.now() - startCompress)

startWrite = datetime.now()
## write the new dataset
comp_ds.to_netcdf(
    str(save_dir) + "/interp_unit5.nc",
    encoding=encoding,
    mode="w",
)
print("Write time: ", datetime.now() - startWrite)

print("Total run time: ", datetime.now() - startTime)
=======

import context
import io
import json
import requests

import numpy as np
import pandas as pd
import xarray as xr
from glob import glob
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from wrf import ll_to_xy, xy_to_ll
from datetime import datetime, date, timedelta
from utils.make_intercomp import daily_merge_ds

from context import data_dir, tzone_dir

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"



domain = 'd03'
intercomp_date = '20210810'

ds = xr.open_zarr(
                str(data_dir)
                + "/intercomp/"
                + f"intercomp-{domain}-{intercomp_date}.zarr"
                )



ds1 = ds.isel(time =221)

print(np.unique(np.isnan(ds1.fwi.values), return_counts=True))

# ## choose wrf model and date range of interest
# wrf_model = "wrf4"
# date_range = pd.date_range("2021-05-01", "2021-05-03")
# domains = ["d02"]

# ## make dir for that intercomp files if it doest not all ready exist
# make_dir = Path(str(data_dir) + "/intercomp/")
# make_dir.mkdir(parents=True, exist_ok=True)

# ### Open color map json
# with open(str(data_dir) + "/json/colormaps-dev.json") as f:
#     cmaps = json.load(f)

# ## Get All Stations CSV
# url = "https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/cwfis_allstn2019.csv"
# stations_df_og = pd.read_csv(url, sep=",")
# stations_df_og = stations_df_og.drop_duplicates(subset="wmo", keep="last")
# stations_df_og = stations_df_og.drop(
#     columns=["tmm", "ua", "the_geom", "h_bul", "s_bul", "hly", "syn"]
# )
# # ### Get Daily observations CSV
# # filein_obs = str(data_dir) + f"/fwi-obs/cwfis_fwi2010sopEC.csv"
# filein_obs = "https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/cwfis_fwi2020sopEC.csv"
# obs_df = pd.read_csv(filein_obs, sep=",", skiprows=0)


# for date in date_range:
#     dateLoop = datetime.now()
#     stations_df = stations_df_og
#     day1_obs_date = date.strftime("%Y%m%d06")
#     day2_obs_date = (date - np.timedelta64(1, "D")).strftime("%Y%m%d06")
#     for domain in domains:
#         domainLoop = datetime.now()
#         stations_df = stations_df_og

#         print(day1_obs_date)
#         day1_ds = daily_merge_ds(day1_obs_date, domain, wrf_model)
#         day1_ds.H.attrs = {
#             "FieldType": 104,
#             "MemoryOrder": "XY ",
#             "description": "2m RELATIVE HUMIDITY",
#             "projection": "PolarStereographic(stand_lon=-110.0, moad_cen_lat=53.99999237060547, truelat1=57.0, truelat2=90.0, pole_lat=90.0, pole_lon=0.0)",
#             "stagger": "",
#             "units": "(%)",
#         }
#         day2_ds = daily_merge_ds(day2_obs_date, domain, wrf_model)
#         try:
#             day2_ds.H.attrs = {
#                 "FieldType": 104,
#                 "MemoryOrder": "XY ",
#                 "description": "2m RELATIVE HUMIDITY",
#                 "projection": "PolarStereographic(stand_lon=-110.0, moad_cen_lat=53.99999237060547, truelat1=57.0, truelat2=90.0, pole_lat=90.0, pole_lon=0.0)",
#                 "stagger": "",
#                 "units": "(%)",
#             }
#         except:
#             pass

#         ### Get a wrf file
#         if wrf_model == "wrf3":
#             wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CP-04/18072000/wrfout_{domain}_2018-07-20_11:00:00"
#         else:
#             wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CG-01/21022000/wrfout_{domain}_2021-02-20_11:00:00"
#         wrf_file = Dataset(wrf_filein, "r")

#         ## get i and j index of the gridded doamin based on lats and longs from station
#         xy_np = ll_to_xy(wrf_file, stations_df["lat"], stations_df["lon"])
#         ## add index to dataframe
#         stations_df["x"] = xy_np[0]
#         stations_df["y"] = xy_np[1]

#         ## set to remove boundary conditions
#         xy = 6
#         ### Drop stations out sie of model domain
#         shape = np.shape(day1_ds.XLAT)
#         stations_df = stations_df.drop(
#             stations_df.index[np.where(stations_df["x"] > (shape[1] - xy - 1))]
#         )
#         stations_df = stations_df.drop(
#             stations_df.index[np.where(stations_df["y"] > (shape[0] - xy - 1))]
#         )
#         stations_df = stations_df.drop(
#             stations_df.index[np.where(stations_df["x"] < xy - 1)]
#         )
#         stations_df = stations_df.drop(
#             stations_df.index[np.where(stations_df["y"] < xy - 1)]
#         )

#         ## index obs dateframe to get date of interest
#         obs_df_on_date = obs_df[
#             obs_df["rep_date"] == date.strftime("%Y-%m-%d 12:00:00")
#         ]
#         ## merge with stations data information
#         final_df = stations_df.merge(obs_df_on_date, on="wmo", how="left")
#         ## remove nulled data
#         final_df = final_df.replace("NULL", np.nan)
#         final_df = final_df.replace(" NULL", np.nan)
#         final_df = final_df.replace("  NULL", np.nan)
#         ## drop duplicates
#         final_df = final_df.drop_duplicates(subset=["wmo"], keep="last")

#         ## convert to float 32 for smaller storage
#         final_df = final_df.astype(
#             {
#                 "temp",
#                 "td",
#                 "rh",
#                 "ws",
#                 "wdir",
#                 "precip",
#                 "ffmc",
#                 "dmc",
#                 "dc",
#                 "bui",
#                 "isi",
#                 "fwi",
#                 "dsr",
#             }
#         )

#         ## get i and j index of array
#         south_north, west_east = final_df["y"].values, final_df["x"].values

#         ## get list of variables to loop
#         var_list = list(day1_ds)
#         ## remove none observed variabels
#         remove = ["r_o_tomorrow", "SNOWC", "RH"]
#         var_list = list(set(var_list) - set(remove))
#         ## loop and append variabel to list
#         final_var_list = []
#         for var in var_list:
#             ## get variable by name
#             name = cmaps[var]["name"]
#             ## get day 1 model values based on i and j index
#             var_columns = day1_ds[var].values[:, south_north, west_east]
#             ## convert to array and set as float32
#             var_columns = np.array(var_columns, dtyp,
#             ## add day 1 model values to dataframe
#             final_df[name + "_day1"] = var_columns[0, :]

#             ## if no day 2 forecasts set to None
#             if day2_ds is None:
#                 # print('day2_ds is none')
#                 a = np.empty(len(south_north))
#                 a[:] = np.nan
#                 a = np.array(a, dtyp,
#                 final_df[name + "_day2"] = a
#             else:
#                 ## get day 2 model values based on i and j index and add to add frame
#                 var_columns = day2_ds[var].values[:, south_north, west_east]
#                 var_columns = np.array(var_columns, dtyp,
#                 try:
#                     final_df[name + "_day2"] = var_columns[1, :]
#                 except:
#                     a = np.empty(len(south_north))
#                     a[:] = np.nan
#                     a = np.array(a, dtyp,
#                     final_df[name + "_day2"] = a

#             final_var_list.append(name)
#             final_var_list.append(name + "_day1")
#             final_var_list.append(name + "_day2")

#         wmos = final_df["wmo"].values
#         _, index, count = np.unique(wmos, return_index=True, return_counts=True)
#         ids = final_df["id"].values.astype(str)
#         names = final_df["name"].values.astype(str)
#         provs = final_df["prov"].values.astype(str)
#         lons = final_df["lon"].values.astyp,
#         lats = final_df["lat"].values.astyp,
#         elevs = final_df["elev"].values.astyp,
#         tz_correct = final_df["tz_correct"].values.astype(int)
#         try:
#             day = np.array(day1_ds.Time[0], dtype="datetime64[D]")
#         except:
#             day = np.array(day1_ds.Time, dtype="datetime64[D]")

#         xr_list = []
#         for var in final_var_list:
#             var_array = np.array(final_df[var], dtyp,
#             x = np.stack((final_df[var].values, final_df[var].values))
#             xr_var = xr.DataArray(
#                 x,
#                 name=f"{var}",
#                 coords={
#                     "wmo": wmos,
#                     "time": [day, day],
#                     "lats": ("wmo", lats),
#                     "lons": ("wmo", lons),
#                     "elev": ("wmo", elevs),
#                     "name": ("wmo", names),
#                     "prov": ("wmo", provs),
#                     "id": ("wmo", ids),
#                     "tz_correct": ("wmo", tz_correct),
#                 },
#                 dims=("time", "wmo"),
#             )

#             xr_list.append(xr_var)

#         intercomp_today_ds = xr.merge(xr_list)
#         intercomp_today_ds = intercomp_today_ds.isel(time=0)

#         intercomp_today_ds.attrs["TITLE"] = str(
#             "wrfout/fwf model versus wmo weather station observations"
#         ).upper()
#         for var in var_list:
#             name = cmaps[var]["name"]
#             attrs = day1_ds[var].attrs
#             intercomp_today_ds[name].attrs["description"] = attrs
#             intercomp_today_ds[name].attrs["description"] = (
#                 "OBSERVED " + attrs["description"]
#             )
#             intercomp_today_ds[name + "_day1"].attrs["description"] = attrs
#             intercomp_today_ds[name + "_day1"].attrs["description"] = (
#                 "ONE DAY FORECASTED " + attrs["description"]
#             )
#             intercomp_today_ds[name + "_day2"].attrs["description"] = attrs
#             intercomp_today_ds[name + "_day2"].attrs["description"] = (
#                 "TWO DAY FORECASTED " + attrs["description"]
#             )

#         intercomp_today_dir = day1_obs_date[:-2]
#         intercomp_yesterday_dir = day2_obs_date[:-2]

#         my_dir = Path(
#             str(data_dir)
#             + "/intercomp/"
#             + f"intercomp-{domain}-{intercomp_yesterday_dir}.zarr"
#         )
#         if my_dir.is_dir():
#             intercomp_yesterday_ds = xr.open_zarr(
#                 str(data_dir)
#                 + "/intercomp/"
#                 + f"intercomp-{domain}-{intercomp_yesterday_dir}.zarr"
#             )
#             final_ds = xr.combine_nested(
#                 [intercomp_yesterday_ds, intercomp_today_ds], "time"
#             )
#             final_ds.to_zarr(
#                 str(data_dir)
#                 + "/intercomp/"
#                 + f"intercomp-{domain}-{intercomp_today_dir}.zarr",
#                 mode="w",
#             )
#         else:
#             final_ds = intercomp_today_ds
#             final_ds.to_zarr(
#                 str(data_dir)
#                 + "/intercomp/"
#                 + f"intercomp-{domain}-{intercomp_today_dir}.zarr",
#                 mode="w",
#             )
#         print("Domain Loop Time: ", datetime.now() - domainLoop)
#     print("Date Loop Time: ", datetime.now() - dateLoop)

# ### Timer
# print("Total Run Time: ", datetime.now() - startTime)
>>>>>>> 3c28d48b1a2763dfffb98e341c9180cd3ec5be1d
