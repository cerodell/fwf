import context
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
from netCDF4 import Dataset
import cartopy.crs as crs
import geopandas as gpd

from datetime import datetime
import matplotlib.colors
import matplotlib.pyplot as plt

from datetime import datetime, date, timedelta

from context import fwf_dir, root_dir

filein_daily = str(fwf_dir) + "/fwf-daily-d02-2019*"
filein_hourly = str(fwf_dir) + "/fwf-hourly-d02-2019*"

from glob import glob


ds = xr.open_dataset(str(fwf_dir) + "/fwf-hourlyHFI-d02-20180401-20181001.nc")
ds = ds.isel(time=3000)
ds.HFI.plot()


def combine(files, dim, ind):
    def truncate(p, ind):
        print(p)
        keep_vars = ["HFI"]
        ds = xr.open_dataset(p)
        ds = ds.isel(time=slice(0, ind))
        ds = ds.drop([var for var in list(ds) if var not in keep_vars])
        return ds

    paths = sorted(glob(files))
    # paths = paths[1:]
    datasets = [truncate(p, ind) for p in paths]
    combined = xr.concat(datasets, dim)
    return combined


# daily_ds = combine(filein_daily, dim="time", ind = 1)
# daily_ds = daily_ds.load()
# daily_ds.to_netcdf(
#     str(fwf_dir) + "/fwf-daily-20180401-20181001.nc", mode="w"
# )
# print('daily done')

hourly_ds = combine(filein_hourly, dim="time", ind=24)
hourly_ds = hourly_ds.load()
hourly_ds.to_netcdf(str(fwf_dir) + "/fwf-hourlyHFI-d02-20190401-20191001.nc", mode="w")
print("hourly done")
