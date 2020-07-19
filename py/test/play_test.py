#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

#Hack to fix missing PROJ4 env var
# import os
# import conda

# conda_file_dir = conda.__file__
# conda_dir = conda_file_dir.split('lib')[0]
# proj_lib = os.path.join(os.path.join(conda_dir, 'share'), 'proj')
# os.environ["PROJ_LIB"] = proj_lib

import context
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from context import data_dir, xr_dir, wrf_dir
import matplotlib.pyplot as plt


from wrf import (getvar, g_uvmet, ll_to_xy)
# 
### BRing in zarr FWF forecast data 
hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 

hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)

