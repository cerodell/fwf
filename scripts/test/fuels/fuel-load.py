import os
import context
import salem
import dask
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
from datetime import datetime


from context import data_dir


file_dir = "/Volumes/WFRT-Ext23/fuel-characteristics/fuel-load/2021/"
ds = salem.open_xr_dataset(file_dir + "CFUEL_timemean_2021_06.nc").sel(
    lat=slice(75, 20), lon=slice(-170, -50)
)
