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
forecast_date = pd.Timestamp("today").strftime("%Y%m%d06")
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
