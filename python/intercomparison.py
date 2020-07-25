import context
import sys
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
startTime = datetime.now()

from utils.make_csv import intercomparison_make_csv
from context import data_dir, xr_dir, wrf_dir, root_dir
from wrf import ll_to_xy, xy_to_ll

import warnings

warnings.filterwarnings("ignore", message="elementwise comparison failed")



"""######### get directory to yesterdays hourly/daily .zarr files.  #############"""


todays_date = '20200723'
yesterday_date = '20200722'
intercomparison_make_csv(None, todays_date, yesterday_date)

# filecsv = '/Volumes/cer/fireweather/data/csv/fwf-intermoparison-2020071900.csv'
# filecsv = str(data_dir) + '/csv/fwf-intercomparison-2020071900.csv'
# inter_df = pd.read_csv(filecsv)


# hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
# daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 
# xr_dir = '/Volumes/cer/fireweather/data/xr'
# hourly_file_dir = str(xr_dir) + str(f"/fwf-hourly-{todays_date}00.zarr") 
# daily_file_dir = str(xr_dir) + str(f"/fwf-daily-{todays_date}00.zarr") 

# hourly_ds = xr.open_zarr(hourly_file_dir)


# df.insert(0,'HOUR','')
# daily_ds = xr.open_zarr(daily_file_dir)

### Get Path to YESTERDAYS FWI forecast and open 
# yesterday_date = '20200716'
# hourly_file_dir_yesterday = str(xr_dir) + str(f"/fwf-hourly-{yesterday_date}00.zarr") 
# daily_file_dir_yesterday = str(xr_dir) + str(f"/fwf-daily-{yesterday_date}00.zarr") 

# hourly_ds_yesterday = xr.open_zarr(hourly_file_dir_yesterday)
# daily_ds_yesterday = xr.open_zarr(daily_file_dir_yesterday)


### Get Path to most recent WRF run for most uptodate snowcover info
# wrf_folder = date.today().strftime('/%y%m%d00/')
# wrf_folder = f"/{todays_date[2:]}00/"
# filein = str(wrf_dir) + wrf_folder
# filein = '/Volumes/cer/fireweather/data/wrf/'
# wrf_file_dir = sorted(Path(filein).glob('wrfout_d03_*'))
# wrf_file = Dataset(wrf_file_dir[0],'r')



# ### Convert specific colums to float64
# inter_df = inter_df.astype({'lon':float, 'lat':float,'TEMP':float, 'RH': float, \
#     'WS': float, 'WG': float, 'WDIR': float, 'PRES': float, 'PRECIP': float, 'FFMC': float,\
#         'DMC': float, 'DC': float, 'BUI': float, 'ISI': float, 'FWI': float, 'DSR': float})

# ### Drop bad data
# calstat = inter_df['CALCSTATUS'].to_numpy(dtype = float)
# inter_df = inter_df.drop(inter_df.index[np.where(calstat<-1)])


# import seaborn as sns
# import scipy.stats as stats


# # plt.scatter(inter_df["FFMC"],inter_df['F_today'])
# # plt.scatter(inter_df["FFMC"],inter_df['F_yesterday'])

# # sns.jointplot(x=inter_df["FFMC"], y=inter_df['F_today'], kind='scatter').annotate(stats.pearsonr)
# sns.jointplot(x=inter_df["FFMC"], y=inter_df['F_today'], kind='hex').annotate(stats.pearsonr)
# sns.jointplot(x=inter_df["TEMP"], y=inter_df['T_today'], kind='kde', data=inter_df).annotate(stats.pearsonr)



# plt.show()



