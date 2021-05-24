import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from utils.read_wrfout import readwrf

from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()

wrf_model = "wrf4"
domain = "d03"
forecast_date = pd.Timestamp(2021, 4, 11).strftime("%Y%m%d06")
intercomp_today_dir = pd.Timestamp(2021, 4, 10).strftime("%Y%m%d")
# forecast_date = pd.Timestamp("today").strftime("%Y%m%d00")
filein = str(wrf_dir) + f"/{forecast_date}/"

# hourly_ds = xr.open_zarr(
#     str(fwf_dir) + str("/fwf-hourly-") + domain + str(f"-{forecast_date}.zarr")
# )

# daily_ds = xr.open_zarr(
#     str(fwf_dir) + str("/fwf-daily-") + domain + str(f"-{forecast_date}.zarr")
# )

# inter_ds = xr.open_zarr(
#     str(data_dir) + "/intercomp/" + f"intercomp-{domain}-{intercomp_today_dir}.zarr"
# )


static_ds = xr.open_zarr(
    str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}-dev.zarr"
)


def prepare_ds(ds):
    loadTime = datetime.now()
    print("Start Load ", datetime.now())
    ds = ds.load()
    print("Load Time: ", datetime.now() - loadTime)
    # comp = dict(zlib=True, complevel=9)
    # encoding = {var: comp for var in hourly_ds.data_vars}
    for var in list(ds):
        ds[var].encoding = {}
    return ds


# inter_ds = prepare_ds(inter_ds)
# writeTime = datetime.now()
# print("Start Write Hourly", datetime.now())
# inter_ds.to_netcdf(
#     str(data_dir) + "/intercomp/" + f"intercomp-{domain}-{intercomp_today_dir}.nc",
#     mode="w",
# )
# print("Write Time Hourly: ", datetime.now() - writeTime)


static_ds = prepare_ds(static_ds)
writeTime = datetime.now()
print("Start Write Hourly", datetime.now())
static_ds.to_netcdf(
    str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}.nc", mode="w"
)
print("Write Time Hourly: ", datetime.now() - writeTime)

# daily_dir = Path(
#     str(fwf_dir)
#     + str("/fwf-daily-")
#     + domain
#     + str(f"-{forecast_date}.nc")
# )
# daily_ds = prepare_ds(daily_ds)
# writeTime = datetime.now()
# print("Start Write Hourly", datetime.now())
# daily_ds.to_netcdf(daily_dir, mode="w")
# print("Write Time Hourly: ", datetime.now() - writeTime)


# hourly_dir = Path(
#     str(fwf_dir)
#     + str("/fwf-hourly-")
#     + domain
#     + str(f"-{forecast_date}.nc")
# )
# hourly_ds = prepare_ds(hourly_ds)
# writeTime = datetime.now()
# print("Start Write Hourly", datetime.now())
# hourly_ds.to_netcdf(hourly_dir, mode="w")
# print("Write Time Hourly: ", datetime.now() - writeTime)
# print("Total Time: ", datetime.now() - startTime)
