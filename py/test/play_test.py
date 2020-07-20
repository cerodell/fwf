import context
import sys
import json
import numpy as np
import pandas as pd
import xarray as xr
import geojsoncontour
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
startTime = datetime.now()

from context import data_dir, xr_dir, wrf_dir, root_dir
from wrf import ll_to_xy


comparison_date = '20200716'

### Get Path to most recent FWI forecast and open 
# hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
# daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 

re_run = '/Volumes/cer/fireweather/data/'

wrf_file_dir = re_run + 'wrf/wrfout_d03_2020-07-17_02:00:00'
wrf_file = Dataset(wrf_file_dir,'r')
                                 
hourly_file_dir = str(re_run) + str(f"xr/fwf-hourly-{comparison_date}00.zarr") 
new_hourly_file_dir = str(re_run) + str(f"new_xr/fwf-hourly-{comparison_date}00.zarr") 

old_hourly_ds = xr.open_zarr(hourly_file_dir)
new_hourly_ds = xr.open_zarr(new_hourly_file_dir)



xy  = ll_to_xy(wrf_file,53.8660, -123.0840 )

print(float(new_hourly_ds.F[34,xy[1],xy[0]]))
