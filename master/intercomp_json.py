#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import json
import sys
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from bson import json_util
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from datetime import datetime, date, timedelta
# from scipy.stats.stats import pearsonr

startTime = datetime.now()
from matplotlib.dates import DateFormatter

import seaborn as sns
import scipy.stats as stats
from utils.make_csv import intercomparison_make_csv
from context import data_dir, xr_dir, wrf_dir, root_dir
from utils.dostats import dostats


### Pandas hates me and throws out so many warnings......turn on warnings to find out :) 
import warnings
warnings.filterwarnings("ignore")

"""######### get directory to hourly/daily .zarr files.  #############"""
start_date_prearsons = date.today() - timedelta(days=61)

start_date_bias = date.today() - timedelta(days=16)
stop_date = date.today() - timedelta(days=1)

file_date = stop_date.strftime("%Y%m%d")
todays_date = date.today() 
todays_date = todays_date.strftime("%Y%m%d")


# filecsv = str(data_dir) + f'/csv/fwf-intercomparison-{file_date}00.csv'
filecsv = str(data_dir) + f'/csv/current/fwf-intercomparison-current.csv'

inter_df = pd.read_csv(filecsv)
# inter_df = inter_df.iloc[::-1]

inter_df['DateTime'] = pd.to_datetime(inter_df['DateTime'] ,format= '%Y%m%d%H')
inter_df = inter_df.set_index('DateTime')

stop = stop_date.strftime("%Y-%m-%d")
last_df = inter_df.loc[stop]
last_df['wmo']  = last_df["WMO"]
drop_list = ["WMO", 'aes', 'id', 'NAME_x', 'instr', 'prov', 'lon', 'lat', 'elev', 'tz_correct', 'useindex', 'agency', 'NAME_y', 'AGENCY', 'AES', 'REPDATE', 'TD', 'WG', 'WDIR', 'PRES', 'SOG', 'DSR', 'OPTS', 'CALCSTATUS', 'x', 'y', 'D_today', 'D_yesterday', 'H_today', 'H_yesterday', 'P_today', 'P_yesterday', 'T_today', 'T_yesterday', 'U_today', 'U_yesterday', 'W_today', 'W_yesterday', 'WD_today', 'WD_yesterday', 'r_o_today', 'r_o_yesterday', 'r_o_tomorrow_today', 'r_o_tomorrow_yesterday', 'DSR_today', 'DSR_yesterday', 'F_today', 'F_yesterday', 'R_today', 'R_yesterday', 'S_today', 'S_yesterday', 'm_o_today', 'r_o_hourly_today']
for colume in drop_list:
    last_df = last_df.drop(str(colume), 1)

last_df = last_df.dropna()
last_df = last_df.reset_index()
last_df = last_df.sort_values('wmo')
# last_df = last_df.drop('DateTime', 1)

last_df = last_df.astype({'TEMP':float, 'RH': float, \
    'WS': float, 'PRECIP': float, 'FFMC': float,\
        'DMC': float, 'DC': float, 'BUI': float, 'ISI': float, 'FWI': float})


bias_df     = dostats(inter_df,start_date_bias, stop_date, 'bias')
prearson_df = dostats(inter_df,start_date_prearsons, stop_date, 'prearsons')


wmo_df = bias_df.merge(prearson_df, on='index')
wmo_df = wmo_df.drop('wmo_y',1)
wmo_df['wmo'] = wmo_df['wmo_x']
wmo_df = wmo_df.drop('wmo_x',1)

wmo_df = pd.merge(wmo_df.astype(str),last_df.astype(str), on='wmo')

wmo_array = wmo_df['prearsons'].values
unique, counts = np.unique(wmo_array, return_counts=True)
wmo_df = wmo_df.T


wmo_r_1day = wmo_df.to_dict()


print(f"{str(datetime.now())} ---> write fwf wxstation dictonary to json" )

### Write json file to defind dir 
make_dir = Path("/bluesky/archive/fireweather/forecasts/" + str(todays_date) + "00/data")
make_dir.mkdir(parents=True, exist_ok=True)

with open(str(make_dir) + f"/fwf-wxstation-{file_date}00.json","w") as f:
    json.dump(wmo_r_1day,f, default=json_util.default, separators=(',', ':'), indent=None)

print(f"{str(datetime.now())} ---> wrote json fwf wxstation to:  " + str(make_dir) + f"/fwf-wxstation-{file_date}.json")
