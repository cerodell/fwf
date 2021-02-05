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

from context import data_dir, root_dir

filein_daily = "/Volumes/cer/fireweather/data/xr/fwf-daily-*"
filein_hourly = "/Volumes/cer/fireweather/data/xr/fwf-hourly-*"

from glob import glob


def read_zarr(files, dim):
    paths = sorted(glob(files))
    datasets = [xr.open_zarr(p) for p in paths]
    combined = xr.concat(datasets, dim)
    return combined


daily_ds = read_zarr(filein_daily, dim="time")
hourly_ds = read_zarr(filein_hourly, dim="time")

daily_ds = daily_ds.compute()
daily_ds.to_zarr(
    "/Volumes/cer/fireweather/data/fwf-daily-20200524-20201016.zarr", mode="w"
)

hourly_ds = hourly_ds.compute()
hourly_ds.to_zarr(
    "/Volumes/cer/fireweather/data/fwf-hourly-20200524-20201016.zarr", mode="w"
)
