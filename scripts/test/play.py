#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from utils.read_wrfout import readwrf

# from context import data_dir, xr_dir, wrf_dir, tzone_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()


date_range = pd.date_range("2021-02-23", "2021-03-01")

ds_new = xr.open_dataset(
    f"/bluesky/fireweather/fwf/data/FWF-WAN00CG-01/fwf-hourly-d03-2021062406.nc"
)

ds_old = xr.open_dataset(
    f"/bluesky/archive/fireweather/data/fwf-hourly-d03-2021062406.nc"
)
print(f"Min RH : {float(np.min(ds.H))}")
print(f"Mean RH : {float(np.mean(ds.H))}")

print(f"Max RH : {float(np.max(ds.H))}")
print(f"Min TD : {float(np.min(ds.TD))}")
print(f"Max TD : {float(np.max(ds.TD))}")

# def solve_rh(ds):
#   ds['TD'] = ds.TD +273.15
#   RH = (
#     (6.11 * 10 ** (7.5 * (ds.TD / (237.7 + ds.TD))))
#     / (6.11 * 10 ** (7.5 * (ds.T / (237.7 + ds.T))))
#     * 100
#   )
#   RH = xr.where(RH > 100, 100, RH)
#   RH = xr.DataArray(
#   RH, name="H", dims=("time", "south_north", "west_east")
#   )
#   ds["H"] = RH
#   return ds
# # """######### get directory to yesterdays hourly/daily .zarr files.  #############"""
# for date in date_range:
#     forecast_date = date.strftime("%Y%m%d06")
#     ds = xr.open_dataset(f'/bluesky/archive/fireweather/data/fwf-daily-d02-{forecast_date}.nc')
#     if np.max(ds.TD) < -100:
#       ds = solve_rh(ds)
#     else:
#       pass
#     print(forecast_date)
#     print(f'Min RH : {float(np.min(ds.H))}')
#     print(f'Max RH : {float(np.max(ds.H))}')
#     print(f'Min TD : {float(np.min(ds.TD))}')
#     print(f'Max TD : {float(np.max(ds.TD))}')

# test.H.plot()
# np.mean(test.H)

# domain = "d03"
# # date = pd.Timestamp("today")
# forecast_date = pd.Timestamp(2021, 4, 12).strftime("%Y%m%d06")
# # forecast_date = pd.Timestamp("today").strftime("%Y%m%d00")
# filein = str(wrf_dir) + f"/{forecast_date}/"

# hourly_ds = xr.open_zarr(
#     str(fwf_zarr_dir) + str("/fwf-hourly-") + domain + str(f"-{forecast_date}.zarr")
# )

# file_date = str(np.array(hourly_ds.Time[0], dtype="datetime64[h]"))
# file_date = datetime.strptime(str(file_date), "%Y-%m-%dT%H").strftime("%Y%m%d%H")

# # ## Write and save DataArray (.zarr) file
# make_dir = Path(
#     str(fwf_zarr_dir)
#     # + str(f"/{file_date[:-2]}00/fwf-hourly-")
#     + str("/fwf-hourly-")
#     + domain
#     + str(f"-{forecast_date}-test.nc")
# )

# ds = xr.open_dataset(make_dir)
# HFI = ds.HFI.values
# # make_dir.mkdir(parents=True, exist_ok=True)
# def rechunk(ds):
#     # ds = ds.chunk(chunks="auto")
#     # ds = ds.unify_chunks()
#     for var in list(ds):
#         ds[var].encoding = {}
#     return ds


# # comp = dict(zlib=True, complevel=9)
# # encoding = {var: comp for var in hourly_ds.data_vars}
# hourly_ds = rechunk(hourly_ds)
# # comp = dict(zlib=True, complevel=9)
# # encoding = {var: comp for var in hourly_ds.data_vars}
# loadTime = datetime.now()
# print("Start Load ", datetime.now())
# hourly_ds = hourly_ds.load()
# print("Load Time: ", datetime.now() - loadTime)

# writeTime = datetime.now()
# print("Start Write ", datetime.now())
# hourly_ds.to_netcdf(make_dir, mode="w")
# print("Write Time: ", datetime.now() - writeTime)

# print("Total Time: ", datetime.now() - startTime)


# # print(ds.P)
# # ds = ds.isel(time=0)

# # filein = str(wrf_dir) + f"/wrfout-{domain}-2021010306.zarr"
# # # pathlist = sorted(Path(filein).glob(f"wrfout_{domain}_*00"))

# # # # wrf_file = Dataset(file_dir, "r")
# # forecast_date = pd.Timestamp("today").strftime("%Y%m%d00")
# # domains = ["d02"]
# # for domain in domains:
# #     domain_startTime = datetime.now()
# #     print(f"start of domain {domain}: ", str(domain_startTime))
# #     # """######### get directory to todays wrf_out .nc files.  #############"""

# #     wrf_file_dir = str(wrf_dir) + f"/{forecast_date}/"
# #     print(wrf_file_dir)

# #     ds = readwrf(wrf_file_dir, domain, wright=False)
# #     print(float(ds.r_o.isel(time=-1).max()))

# #     ds.SNW = ds.SNW - ds.SNW.values[0]
# #     print(float(ds.SNW.isel(time=0).max()))


# # file_dir =  '/bluesky/working/wrf2arl/WAN00CG-01/2021022100/download/wrfout_d03_2021-02-21_00:00:00'
# # ds = xr.open_dataset(file_dir)

# # ds = xr.open_zarr(
# #     str(data_dir) + "/intercomp/" + f"intercomp-{domain}-{forecast_date[:-2]}.zarr"
# # )

# # qpf = ['RAINC', 'RAINSH', 'RAINNC']

# # qpf = ds.RAINC + ds.RAINSH + ds.RAINNC

# # for var in list(ds):
# #     # print(f"max of {var}: {str(ds.Time.values)}")
# #     print(f"max of {var}: {float(ds[var].max(skipna= True))}")
# #     print(f"min of {var}: {float(ds[var].min(skipna= True))}")
# #     print(f"mean of {var}: {float(ds[var].mean(skipna= True))}")

# # var = "DC_day1"
# # for i in range(len(ds.time)):
# #     print(str(ds.time.values[i]))
# #     print(float(ds.isel(time=i)[var].max(skipna=True)))
# #     print(float(ds.isel(time=i)[var].min(skipna=True)))
# #     print(float(ds.isel(time=i)[var].mean(skipna=True)))

# # air1d = ds[var].isel(wmo=200)

# # air1d.plot()
