import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from utils.read_wrfout import readwrf

from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta


domain = "d03"
# date = pd.Timestamp("today")
forecast_date = pd.Timestamp(2021, 4, 10).strftime("%Y%m%d06")
# forecast_date = pd.Timestamp("today").strftime("%Y%m%d00")
filein = str(wrf_dir) + f"/{forecast_date}/"

hourly_ds = xr.open_zarr(
    str(fwf_zarr_dir) + str("/fwf-hourly-") + domain + str(f"-{forecast_date}.zarr")
)

file_date = str(np.array(hourly_ds.Time[0], dtype="datetime64[h]"))
file_date = datetime.strptime(str(file_date), "%Y-%m-%dT%H").strftime("%Y%m%d%H")

# # ## Write and save DataArray (.zarr) file
make_dir = Path(
    str(fwf_zarr_dir)
    # + str(f"/{file_date[:-2]}00/fwf-hourly-")
    + str("/fwf-hourly-")
    + domain
    + str(f"-{file_date}-test.nc")
)
# make_dir.mkdir(parents=True, exist_ok=True)
def rechunk(ds):
    ds = ds.chunk(chunks="auto")
    ds = ds.unify_chunks()
    for var in list(ds):
        ds[var].encoding = {}
    return ds


# comp = dict(zlib=True, complevel=9)
# encoding = {var: comp for var in hourly_ds.data_vars}
hourly_ds = rechunk(hourly_ds)
startTime = datetime.now()
hourly_ds = hourly_ds.load()
hourly_ds.to_netcdf(make_dir, mode="w")
print("Write Time: ", datetime.now() - startTime)
print(f"wrote working {make_dir}")


# print(ds.P)
# ds = ds.isel(time=0)

# filein = str(wrf_dir) + f"/wrfout-{domain}-2021010306.zarr"
# # pathlist = sorted(Path(filein).glob(f"wrfout_{domain}_*00"))

# # # wrf_file = Dataset(file_dir, "r")
# forecast_date = pd.Timestamp("today").strftime("%Y%m%d00")
# domains = ["d02"]
# for domain in domains:
#     domain_startTime = datetime.now()
#     print(f"start of domain {domain}: ", str(domain_startTime))
#     # """######### get directory to todays wrf_out .nc files.  #############"""

#     wrf_file_dir = str(wrf_dir) + f"/{forecast_date}/"
#     print(wrf_file_dir)

#     wrf_ds = readwrf(wrf_file_dir, domain, wright=False)
#     print(float(wrf_ds.r_o.isel(time=-1).max()))

#     wrf_ds.SNW = wrf_ds.SNW - wrf_ds.SNW.values[0]
#     print(float(wrf_ds.SNW.isel(time=0).max()))


# file_dir =  '/bluesky/working/wrf2arl/WAN00CG-01/2021022100/download/wrfout_d03_2021-02-21_00:00:00'
# wrf_ds = xr.open_dataset(file_dir)

# ds = xr.open_zarr(
#     str(data_dir) + "/intercomp/" + f"intercomp-{domain}-{forecast_date[:-2]}.zarr"
# )

# qpf = ['RAINC', 'RAINSH', 'RAINNC']

# qpf = wrf_ds.RAINC + wrf_ds.RAINSH + wrf_ds.RAINNC

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

# air1d = ds[var].isel(wmo=200)

# air1d.plot()
