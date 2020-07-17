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


### Get All Stations CSV
url = 'https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/cwfis_allstn2019.csv'
stations_df = pd.read_csv(url, sep = ',')
stations_df = stations_df.drop_duplicates()

### Get Daily observations CSV
obs_date = date.today().strftime('%Y%m%d')
obs_date = '20200715'
url2 = f'https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/current/cwfis_fwi_{obs_date}.csv'
headers = list(pd.read_csv(url2,nrows=0))
daily_df = pd.read_csv(url2,  sep = ',', names=headers)
daily_df = daily_df.drop_duplicates()
# if daily_df.iloc[0,0] == "NAME":
#     daily_df.drop(index=0)


# daily_df['lat'] = df.lookup(df.index, df.names, skiprows=1)


### Get Path to most recent FWI forecast and open 
hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 
hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)


### Get Path to most recent WRF run for most uptodate snowcover info
# wrf_folder = date.today().strftime('/%y%m%d00/')
wrf_folder = "/200714/"
filein = str(wrf_dir) + wrf_folder
wrf_file_dir = sorted(Path(filein).glob('wrfout_d03_*'))




