#!/Users/crodell/miniconda3/envs/fwf/bin/python

import context
import io
import json
import requests
import salem

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from glob import glob
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from wrf import ll_to_xy, xy_to_ll
from datetime import datetime, date, timedelta
from utils.compressor import compressor, file_size

from context import data_dir, root_dir

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

filein = "/Volumes/WFRT-Ext22/fwf-data/wrf/d03/202302/fwf-hourly-d03-2023021906.nc"

ds = xr.open_dataset(filein)

ds1 = ds.isel(time=slice(24, 56))

ds1.to_netcdf(
    "/Volumes/WFRT-Ext22/fwf-data/wrf/d03/202302/fwf-hourly-d03-2023022006.nc", mode="w"
)
