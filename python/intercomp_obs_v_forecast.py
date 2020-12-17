import context
import sys
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from sklearn import preprocessing
from scipy.stats import kde
import seaborn as sns

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from datetime import datetime, date, timedelta
from scipy.stats.stats import pearsonr

startTime = datetime.now()
from matplotlib.dates import DateFormatter

import seaborn as sns
import scipy.stats as stats
from utils.make_csv import intercomparison_make_csv
from context import data_dir, xr_dir, wrf_dir, root_dir

import warnings
warnings.filterwarnings("ignore")

datastuff = pd.date_range(start="2020-06-01",end="2020-10-01")


### Open color map json
with open('/bluesky/fireweather/fwf/json/colormaps-dev.json') as f:
  cmaps = json.load(f)

var_list = list(cmaps)
remove = ["r_o_06", "r_o_3hour", "SNW"]
var_list = list(set(var_list) - set(remove))
var_list = ['T', 'H',  'W', 'WD', 'r_o', 'F', 'P', 'D', 'R', 'U', 'S', 'DSR']


"""######### get directory to hourly/daily .zarr files.  #############"""
start_date = date(2020, 6, 1)
stop_date  = date(2020, 10, 1)

todays_date = stop_date.strftime("%Y%m%d")

filecsv = str(data_dir) + f'/csv/current/fwf-intercomparison-current.csv'
inter_df = pd.read_csv(filecsv)

inter_df['DateTime'] = pd.to_datetime(inter_df['DateTime'] ,format= '%Y%m%d%H')
inter_df = inter_df.set_index('DateTime')

start = start_date.strftime("%Y-%m-%d")
stop = stop_date.strftime("%Y-%m-%d")
inter_df = inter_df.loc[stop:start]
inter_df = inter_df.reset_index()

make_dir = Path(str(root_dir) + f"/images/intercomparison/obs_v_forecast/{start}-{stop}/")
make_dir.mkdir(parents=True, exist_ok=True)


# ## replace NULL with np.nan
# for column in inter_df:
#     mask = inter_df[column] == '  NULL'
#     inter_df[column][mask] = np.nan

# for column in inter_df:
#     mask = inter_df[column] == ' NULL'
#     inter_df[column][mask] = np.nan

### replace NULL with np.nan
for column in inter_df:
    inter_df = inter_df[inter_df[column] != ' NULL']
    inter_df = inter_df[inter_df[column] != '  NULL']

### Drop bad data
calstat = inter_df['CALCSTATUS'].to_numpy(dtype = float)
inter_df = inter_df.drop(inter_df.index[np.where(calstat<-1)])

### Convert specific colums to float64
inter_df = inter_df.astype({'lon':float, 'lat':float,'TEMP':float, 'RH': float, \
    'WS': float, 'WG': float, 'WDIR': float, 'PRES': float, 'PRECIP': float, 'FFMC': float,\
        'DMC': float, 'DC': float, 'BUI': float, 'ISI': float, 'FWI': float, 'DSR': float})

df = inter_df
df = df[df['FFMC'].notna()]


def rmse(target, prediction):
    return np.sqrt(((target - prediction) ** 2).sum() / len(target))

fig = plt.figure(figsize=[18,14])

for i in range(len(var_list)):
    plt.subplot(3, 4, i * 1 + 1)
    var = var_list[i]        
    var_obs = cmaps[var]['name'].upper()
    color = cmaps[var]['color']
    var_forecast = var+'_today'
    var_min =  cmaps[var]['vmin']
    var_max =  cmaps[var]['vmax']
    observations, forecast = df[var_obs], df[var_forecast]
    r = np.corrcoef(observations, forecast)[0, 1]
    rmse_val = rmse(observations, forecast)
    plt.scatter(observations, forecast, s = 0.5, color = color)
    plt.title(
        f"Forecast {var_obs} \n r:{round(r,2)} RMSE:{round(rmse_val,2)}", fontsize=10
        )
    plt.xlim(0,var_max)
    plt.ylim(0,var_max)




plt.tight_layout()
fig.savefig(str(make_dir) + f"/all-obs-v-forecast.png")
plt.close()

