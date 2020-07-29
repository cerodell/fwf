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

df = inter_df[inter_df['FFMC'].notna()]
df['DateTime'] = pd.to_datetime(df['DateTime'] ,format= '%Y%m%d%H')
df = df.set_index('DateTime')




def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = date(2020, 5, 24)
end_date = date(2020, 7, 27)


ffmc_r, dmc_r, dc_r, isi_r, bui_r, fwi_r = [],[],[],[],[],[]
time = []
for single_date in daterange(start_date, end_date):
    print(single_date.strftime("%Y-%m-%d"))
    time.append(single_date)
    df_corr = df.loc[single_date.strftime("%Y-%m-%d")]
    prearson_ffmc = df_corr['F_today'].corr(df_corr['FFMC'])
    ffmc_r.append(prearson_ffmc)

    prearson_dmc = df_corr['P_today'].corr(df_corr['DMC'])
    dmc_r.append(prearson_dmc)

    prearson_dc = df_corr['D_today'].corr(df_corr['DC'])
    dc_r.append(prearson_dc)

    prearson_isi = df_corr['R_today'].corr(df_corr['ISI'])
    isi_r.append(prearson_isi)

    prearson_bui = df_corr['U_today'].corr(df_corr['BUI'])
    bui_r.append(prearson_bui)

    prearson_fwi = df_corr['S_today'].corr(df_corr['FWI'])
    fwi_r.append(prearson_fwi)
    


# %%
colors =  plt.rcParams['axes.prop_cycle'].by_key()['color']
from scipy.signal import savgol_filter
# from statsmodels.nonparametric.smoothers_lowess import lowess
def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

ffmc = smooth(ffmc_r, 6)
dmc = smooth(dmc_r, 6)
dc = smooth(dc_r, 6)
isi = smooth(isi_r, 6)
bui = smooth(bui_r, 6)
fwi = smooth(fwi_r, 6)

fig, ax = plt.subplots(figsize=(16,10))
fig.autofmt_xdate()
start = time[0].strftime("%Y-%m-%d")
stop = time[-1].strftime("%Y-%m-%d")

fig.suptitle(f"Pearsons Correlation Coefficient \n {start} to {stop}", fontsize=16)
fig.subplots_adjust(hspace=0.8)
ax.plot(time,ffmc, label ='FFMC', linewidth = 4, color = colors[0])
ax.plot(time,dmc, label ='DMC',linewidth = 4, color = colors[1])
ax.plot(time,dc, label ='DC', linewidth = 4, color = colors[2])
ax.plot(time,isi, label ='ISI', linewidth = 4, color = colors[3])
ax.plot(time,bui, label ='BUI', linewidth = 4, color = colors[4])
ax.plot(time,fwi, label ='FWI', linewidth = 4, color = colors[5])

ax.plot(time,ffmc_r, color = colors[0], zorder=1, alpha = 0.2)
ax.plot(time,dmc_r, color = colors[1],zorder=1, alpha = 0.2)
ax.plot(time,dc_r, color = colors[2], zorder=1, alpha = 0.2)
ax.plot(time,isi_r, color = colors[3], zorder=1, alpha = 0.2)
ax.plot(time,bui_r, color = colors[4], zorder=1, alpha = 0.2)
ax.plot(time,fwi_r, color = colors[5], zorder=1, alpha = 0.2)

xfmt = DateFormatter('%Y-%m-%d')
ax.xaxis.set_major_formatter(xfmt)
ax.set_xlabel("Date", fontsize=14)
ax.set_ylabel("r", fontsize=14)

ax.legend(loc='upper center', bbox_to_anchor=(.50,1.), shadow=True, ncol=6)

fig.savefig(str(root_dir) + "/images/intercomparison/pearsons_time_series.png")



