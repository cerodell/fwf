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
from wrf import ll_to_xy, xy_to_ll



### Get Path to TODAYS FWI forecast and open 
comparison_date = '20200717'
# hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
# daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 
xr_dir = '/Volumes/cer/fireweather/data/xr'
hourly_file_dir = str(xr_dir) + str(f"/fwf-hourly-{comparison_date}00.zarr") 
daily_file_dir = str(xr_dir) + str(f"/fwf-daily-{comparison_date}00.zarr") 

hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)

### Get Path to YESTERDAYS FWI forecast and open 
yesterday_date = '20200716'
hourly_file_dir_yesterday = str(xr_dir) + str(f"/fwf-hourly-{yesterday_date}00.zarr") 
daily_file_dir_yesterday = str(xr_dir) + str(f"/fwf-daily-{yesterday_date}00.zarr") 

hourly_ds_yesterday = xr.open_zarr(hourly_file_dir_yesterday)
daily_ds_yesterday = xr.open_zarr(daily_file_dir_yesterday)


### Get Path to most recent WRF run for most uptodate snowcover info
# wrf_folder = date.today().strftime('/%y%m%d00/')
# wrf_folder = f"/{comparison_date[2:]}00/"
# filein = str(wrf_dir) + wrf_folder
filein = '/Volumes/cer/fireweather/data/wrf/'
wrf_file_dir = sorted(Path(filein).glob('wrfout_d03_*'))
wrf_file = Dataset(wrf_file_dir[0],'r')

### Get All Stations CSV
url = 'https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/cwfis_allstn2019.csv'
stations_df = pd.read_csv(url, sep = ',')
stations_df = stations_df.drop_duplicates()
stations_df = stations_df.rename({'wmo': 'WMO', 'name': 'NAME'}, axis=1)
stations_df = stations_df.drop(columns=['tmm','ua', 'the_geom', 'h_bul','s_bul','hly','syn'])
# stations_df['WMO'] = stations_df['WMO'].astype(str).astype(int)
blah = len(np.array(stations_df['WMO']))


### Get Daily observations CSV
# obs_date = date.today().strftime('%Y%m%d')
url2 = f'https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/current/cwfis_fwi_{comparison_date}.csv'
headers = list(pd.read_csv(url2,nrows=0))
daily_df = pd.read_csv(url2,  sep = ',', names=headers)
daily_df = daily_df.drop_duplicates()
daily_df = daily_df.drop(daily_df.index[[0]])
daily_df['WMO'] = daily_df['WMO'].astype(str).astype(int)


### Merge daily_df and stations_df and drop stations with no data
inter_df = stations_df.merge(daily_df, on='WMO', how='outer')

### replace NULL with np.nan
for column in inter_df:
    mask = inter_df[column] == ' NULL'
    inter_df[column][mask] = np.nan


### Drop stations out sie of model domain
xy_np  = ll_to_xy(wrf_file, inter_df['lat'], inter_df['lon'])
inter_df['x'] = xy_np[0]
inter_df['y'] = xy_np[1]
shape = np.shape(daily_ds.T[0,:,:])
inter_df = inter_df.drop(inter_df.index[np.where(inter_df['x']>(shape[1]-1))])
inter_df = inter_df.drop(inter_df.index[np.where(inter_df['y']>(shape[0]-1))])
inter_df = inter_df.drop(inter_df.index[np.where(inter_df['x']<-1)])
inter_df = inter_df.drop(inter_df.index[np.where(inter_df['y']<-1)])


### Get point forecasts for Wxstation locations from model domain...then add to inter_df
for var in daily_ds.data_vars:
    today = np.array(daily_ds[var][0])
    today = today[inter_df['y'],inter_df['x']]
    var_today = var + '_today'
    inter_df[var_today] = today

    yesterday = np.array(daily_ds_yesterday[var][1])
    yesterday = yesterday[inter_df['y'],inter_df['x']]
    var_yesterday = var + '_yesterday'
    inter_df[var_yesterday] = yesterday


### Get point forecasts for Wxstation locations from model domain...then add to inter_df
for var in hourly_ds.data_vars:
    ### Loop each var and get avg of 11-13 local avg time from todays forecast
    today = np.array(hourly_ds[var])
    noon_today = np.array(12+abs(inter_df['tz_correct']), dtype = int)
    before_noon = today[noon_today-1,inter_df['y'],inter_df['x']]
    after_noon = today[noon_today,inter_df['y'],inter_df['x']]
    noon = today[noon_today+1,inter_df['y'],inter_df['x']]
    today = (before_noon + after_noon + noon) / 3
    var_today = var + '_today'
    inter_df[var_today] = today
    # time_check = np.array(hourly_ds.Time[noon_today])
    # inter_df['time_check'] = time_check

    ### Loop each var and get avg of 11-13 local avg time from yesterdays forecast
    yesterday = np.array(hourly_ds_yesterday[var])
    noon_yesterday = np.array(36+abs(inter_df['tz_correct']), dtype = int)
    before_noon = yesterday[noon_yesterday-1,inter_df['y'],inter_df['x']]
    after_noon = yesterday[noon_yesterday,inter_df['y'],inter_df['x']]
    noon = yesterday[noon_yesterday+1,inter_df['y'],inter_df['x']]
    yesterday = (before_noon + after_noon + noon) / 3
    var_yesterday = var + '_yesterday'
    inter_df[var_yesterday] = yesterday
    # time_check_yesterday = np.array(hourly_ds_yesterday.Time[noon_yesterday])
    # inter_df['time_check_yesterday'] = time_check_yesterday















### Convert specific colums to float64
inter_df = inter_df.astype({'lon':float, 'lat':float,'TEMP':float, 'RH': float, \
    'WS': float, 'WG': float, 'WDIR': float, 'PRES': float, 'PRECIP': float, 'FFMC': float,\
        'DMC': float, 'DC': float, 'BUI': float, 'ISI': float, 'FWI': float, 'DSR': float})

### Drop bad data
calstat = inter_df['CALCSTATUS'].to_numpy(dtype = float)
inter_df = inter_df.drop(inter_df.index[np.where(calstat<-1)])


import seaborn as sns
import scipy.stats as stats


# plt.scatter(inter_df["FFMC"],inter_df['F_today'])
# plt.scatter(inter_df["FFMC"],inter_df['F_yesterday'])

sns.jointplot(x=inter_df["FFMC"], y=inter_df['F_today'], kind='scatter')
sns.jointplot(x=inter_df["FFMC"], y=inter_df['F_today'], kind='hex')
sns.jointplot(x=inter_df["TEMP"], y=inter_df['T_today'], kind='kde', data=inter_df).annotate(stats.pearsonr)
# j.annotate(stats.pearsonr)

# fig, ax = plt.subplots(figsize=(14,8))
# # fig.suptitle(Plot_Title + '\n CRESTON, BC (CWJR 116.5 \N{DEGREE SIGN}W, 49.083 \N{DEGREE SIGN}N)', fontsize=16)
# fig.subplots_adjust(hspace=0.1)
# ax.scatter(inter_df['lat'].to_numpy(dtype=float), test.XLAT[1], color = 'purple', 
#                     marker = markers, linewidth= 5, zorder =10, label = "Observations")
# ax.set_ylabel('Model')
# ax.set_xlabel('Observed')

# plt.show()



