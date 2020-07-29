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
from matplotlib.dates import DateFormatter

import seaborn as sns
import scipy.stats as stats
from utils.make_csv import intercomparison_make_csv
from context import data_dir, xr_dir, wrf_dir, root_dir
from wrf import ll_to_xy, xy_to_ll
import io
import warnings

warnings.filterwarnings("ignore", message="elementwise comparison failed")



"""######### get directory to hourly/daily .zarr files.  #############"""


todays_date = '20200726'

# filecsv = f'/Volumes/cer/fireweather/data/csv/fwf-intermoparison-{todays_date}00.csv'
filecsv = str(data_dir) + f'/csv/fwf-intercomparison-{todays_date}00.csv'
inter_df = pd.read_csv(filecsv)


## replace NULL with np.nan
for column in inter_df:
    mask = inter_df[column] == '  NULL'
    inter_df[column][mask] = np.nan


### Drop bad data
calstat = inter_df['CALCSTATUS'].to_numpy(dtype = float)
inter_df = inter_df.drop(inter_df.index[np.where(calstat<-1)])

# ### Convert specific colums to float64
# inter_df = inter_df.astype({'lon':float, 'lat':float,'TEMP':float, 'RH': float, \
#     'WS': float, 'WG': float, 'WDIR': float, 'PRES': float, 'PRECIP': float, 'FFMC': float,\
#         'DMC': float, 'DC': float, 'BUI': float, 'ISI': float, 'FWI': float, 'DSR': float})



colors =  plt.rcParams['axes.prop_cycle'].by_key()['color']

x = df['F_today']
y = df["FFMC"]
ffmc = sns.jointplot(x=x, y=y,\
         kind='kde', color=colors[0]).annotate(stats.pearsonr)
ffmc.set_axis_labels( xlabel = 'Model (FFMC)', ylabel = 'Observation (FFMC)')
ffmc.savefig(str(root_dir) + "/images/intercomparison/ffmc.png")


x = df['P_today']
y = df["DMC"]
dmc = sns.jointplot(x=x, y=y,\
         kind='kde', color=colors[1]).annotate(stats.pearsonr)
dmc.set_axis_labels( xlabel = 'Model (DMC)', ylabel = 'Observation (DMC)')
dmc.savefig(str(root_dir) + "/images/intercomparison/dmc.png")


x = df['D_today']
y = df["DC"]
dc = sns.jointplot(x=x, y=y, \
    kind='kde', color=colors[2]).annotate(stats.pearsonr)
dc.set_axis_labels( xlabel = 'Model (DC)', ylabel = 'Observation (DC)')
dc.savefig(str(root_dir) + "/images/intercomparison/dc.png")


x = df['U_today']
y = df["BUI"]
bui = sns.jointplot(x=x, y=y,\
         kind='kde', color=colors[3]).annotate(stats.pearsonr)
bui.set_axis_labels( xlabel = 'Model (BUI)', ylabel = 'Observation (BUI)')
bui.savefig(str(root_dir) + "/images/intercomparison/bui.png")


x = df['R_today']
y = df["ISI"]
isi = sns.jointplot(x=x, y=y,\
         kind='kde', color=colors[4]).annotate(stats.pearsonr)
isi.set_axis_labels( xlabel = 'Model (ISI)', ylabel = 'Observation (ISI)')
isi.savefig(str(root_dir) + "/images/intercomparison/isi.png")


x = df['S_today']
y = df["FWI"]
fwi = sns.jointplot(x=x, y=y,\
         kind='kde', color=colors[5]).annotate(stats.pearsonr)
fwi.set_axis_labels( xlabel = 'Model (fwi)', ylabel = 'Observation (fwi)')
fwi.savefig(str(root_dir) + "/images/intercomparison/fwi.png")




x = df['T_today']
y = df["TEMP"]
temp = sns.jointplot(x=x, y=y,\
         kind='kde', color="red").annotate(stats.pearsonr)
temp.set_axis_labels( xlabel = 'Model (TEMP C)', ylabel = 'Observation (TEMP C)')
temp.savefig(str(root_dir) + "/images/intercomparison/temp.png")


x = df['H_today']
y = df["RH"]
rh = sns.jointplot(x=x, y=y,\
         kind='kde', color="purple").annotate(stats.pearsonr)
rh.set_axis_labels( xlabel = 'Model (RH %)', ylabel = 'Observation (RH %)')
rh.savefig(str(root_dir) + "/images/intercomparison/rh.png")


x = df['r_o_today']
y = df["PRECIP"]
precip = sns.jointplot(x=x, y=y, \
    kind='kde', color="green").annotate(stats.pearsonr)
precip.set_axis_labels( xlabel = 'Model (PRECIP mm)', ylabel = 'Observation (PRECIP mm)')
precip.savefig(str(root_dir) + "/images/intercomparison/precip.png")


x = df['W_today']
y = df["WS"]
wsp = sns.jointplot(x=x, y=y,\
         kind='kde', color="blue").annotate(stats.pearsonr)
wsp.set_axis_labels( xlabel = 'Model (WIND SPEED m/s)', ylabel = 'Observation (WIND SPEED m/s)')
wsp.savefig(str(root_dir) + "/images/intercomparison/wsp.png")


x = df['WD_today']
y = df["WDIR"]
wdir = sns.jointplot(x=x, y=y,\
         kind='kde', color="grey").annotate(stats.pearsonr)
wdir.set_axis_labels( xlabel = 'Model (Wind Direction deg)', ylabel = 'Observation (Wind Direction deg)')
wdir.savefig(str(root_dir) + "/images/intercomparison/wdir.png")




