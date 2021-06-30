#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python


import context
import os
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset

from context import data_dir, fwf_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()

domains = ["d02", "d03"]
date_range = pd.date_range("2021-05-01", "2021-06-22")
make_dir = Path(f"/bluesky/archive/fireweather/data/")


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)


def compressor(ds, var_dict):
    """
    this function comresses datasets
    """
    ds = ds.load()
    ds.attrs["TITLE"] = "FWF MODEL USING OUTPUT FROM WRF V4.2.1 MODEL"
    comp = dict(zlib=True, complevel=9)
    encoding = {var: comp for var in ds.data_vars}
    for var in ds.data_vars:
        ds[var].attrs = var_dict[var]

    return ds, encoding


with open(str(data_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)


for date in date_range:
    forecast_date = date.strftime("%Y%m%d06")
    for domain in domains:

        working_daily_dir = (
            str(fwf_dir) + str("/fwf-daily-") + domain + str(f"-{forecast_date}.nc")
        )
        daily_ds = xr.open_dataset(working_daily_dir)

        writeTime = datetime.now()
        daily_ds, encoding = compressor(daily_ds, var_dict)
        print(f"Start Write on daily {domain}  {forecast_date}")
        archive_daily_dir = (
            str(make_dir) + str("/fwf-daily-") + domain + str(f"-{forecast_date}.nc")
        )
        daily_ds.to_netcdf(archive_daily_dir, encoding=encoding, mode="w")
        print(
            f"Write Time for daily {domain}  {forecast_date}: ",
            datetime.now() - writeTime,
        )
        print(
            f"Compressed daily from {file_size(working_daily_dir)} to {file_size(archive_daily_dir)}"
        )

        working_hourly_dir = (
            str(fwf_dir) + str("/fwf-hourly-") + domain + str(f"-{forecast_date}.nc")
        )
        hourly_ds = xr.open_dataset(working_hourly_dir)

        writeTime = datetime.now()
        hourly_ds, encoding = compressor(hourly_ds, var_dict)
        print(f"Start Write on hourly {domain}  {forecast_date}")
        archive_hourly_dir = (
            str(make_dir) + str("/fwf-hourly-") + domain + str(f"-{forecast_date}.nc")
        )
        hourly_ds.to_netcdf(archive_hourly_dir, encoding=encoding, mode="w")
        print(
            f"Write Time for hourly {domain}  {forecast_date}: ",
            datetime.now() - writeTime,
        )
        print(
            f"Compressed hourly from {file_size(working_hourly_dir)} to {file_size(archive_hourly_dir)}"
        )
