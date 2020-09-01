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


todays_date = '20200830'


# filecsv = f'/Volumes/cer/fireweather/data/csv/fwf-intermoparison-{todays_date}00.csv'
filecsv = str(data_dir) + f'/csv/fwf-intercomparison-{todays_date}00.csv'
inter_df = pd.read_csv(filecsv)


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

df = inter_df.dropna()
wmo = sorted(df['WMO'].unique())
wmo_array = df['WMO'].values
unique, counts = np.unique(wmo_array, return_counts=True)
unique_counts = np.asarray((unique, counts)).T
low_count = np.where(counts<16)
remove_wmo  = unique[low_count]
for i in range(len(remove_wmo)):
    # print(remove_wmo[i])
    wmo.remove(remove_wmo[i])

df = df.set_index('WMO')

# for column in inter_df:
#     inter_df = inter_df[inter_df[column] != ' NULL']
#     inter_df = inter_df[inter_df[column] != '  NULL']


# ### Drop bad data
# calstat = inter_df['CALCSTATUS'].to_numpy(dtype = float)
# inter_df = inter_df.drop(inter_df.index[np.where(calstat<-1)])

# precip = inter_df['PRECIP'].to_numpy(dtype = float)
# inter_df = inter_df.drop(inter_df.index[np.where(precip>200)])
# u, indices = np.unique(inter_df['WMO'], return_index=True)
# bad_wx_wmo = inter_df.agg(['count', 'size', 'nunique'])


# wx_count = inter_df.WMO.value_counts()
# wx_count_to_small = wx_count.index[np.where(wx_count < 2)]
# inter_df = inter_df.loc[~inter_df['WMO'].isin(wx_count_to_small)]


# ### Convert specific colums to float64
# inter_df = inter_df.astype({'lon':float, 'lat':float,'TEMP':float, 'RH': float, \
#     'WS': float, 'WG': float, 'WDIR': float, 'PRES': float, 'PRECIP': float, 'FFMC': float,\
#         'DMC': float, 'DC': float, 'BUI': float, 'ISI': float, 'FWI': float, 'DSR': float})

# df = inter_df[inter_df['FFMC'].notna()]

# ### Find all unique weather sations
# wmo = sorted(df['WMO'].unique())
# wmo.remove(71203)
# wmo.remove(9114)
# wmo.remove(9113)
# wmo.remove(9213)
# wmo.remove(9513)
# wmo.remove(71520)

# ## Set weather sations as the index
# df = df.set_index('WMO')

## Empty dictorary to append pearson's r values
wmo_r_1day = {}
## Loop thoguh csv for each individula weather station and solve
## pearson's correlation coefficient
for loc in wmo:
    # print(loc)
    df_corr = df.loc[loc]
    prearson_ffmc = df_corr['F_today'].corr(df_corr['FFMC'])
    prearson_dmc = df_corr['P_today'].corr(df_corr['DMC'])
    prearson_dc = df_corr['D_today'].corr(df_corr['DC'])
    prearson_isi = df_corr['R_today'].corr(df_corr['ISI'])
    prearson_bui = df_corr['U_today'].corr(df_corr['BUI'])
    prearson_fwi = df_corr['S_today'].corr(df_corr['FWI'])

    prearson_temp = df_corr['T_today'].corr(df_corr['TEMP'])
    prearson_rh = df_corr['H_today'].corr(df_corr['RH'])
    prearson_wsp = df_corr['W_today'].corr(df_corr['WS'])
    prearson_wdir = df_corr['WD_today'].corr(df_corr['WDIR'])
    prearson_precip = df_corr['r_o_today'].corr(df_corr['PRECIP'])
    ## Appedn pearson's r vlaues to dictorary
    wmo_r_1day[str(loc)] = {'FFMC': prearson_ffmc, "DMC": prearson_dmc, \
        "DC": prearson_dc, "ISI": prearson_isi, "BUI": prearson_bui, "FWI": prearson_fwi, \
            'lat': round(df_corr['lat'].iloc[0],3), 'lng': round(df_corr['lon'].iloc[0],3), \
                "TEMP": prearson_temp,"RH": prearson_rh,"WSP": prearson_wsp,"WDIR": prearson_wdir,\
                    "PRECIP": prearson_precip }

# 0.00-0.19: very weak
# 0.20-0.39: weak
# 0.40-0.59: moderate 
# 0.60-0.79: strong
# 0.80-1.00: very strong.

## Convert dictorary to dataframe
df_wmo = pd.DataFrame.from_dict(wmo_r_1day)
df_wmo = df_wmo.T
df_wmo['wmo'] = df_wmo.index
df_wmo = df_wmo.reset_index()


## find stations with crap correlation
def bad_wxstation(condtion):
    bad_wx = df_wmo.drop(df_wmo.index[np.where(condtion)])
    bad_wx_wmo = sorted(bad_wx['wmo'].unique())
    bad_wx_wmo = [int(i) for i in bad_wx_wmo]
    return bad_wx_wmo


df = df.reset_index()

bad_wx_temp  = bad_wxstation(df_wmo['TEMP']>-0.99)
bad_wx_rh    = bad_wxstation(df_wmo['RH']>-0.99)
bad_wx_wsp    = bad_wxstation(df_wmo['WSP']>-0.99)
bad_wx_precip = bad_wxstation(df_wmo['PRECIP']>-0.99)

bad_wx_ffmc  = bad_wxstation(df_wmo['FFMC']>-0.9)
bad_wx_fwi  = bad_wxstation(df_wmo['FWI']>-0.9)
bad_wx_isi  = bad_wxstation(df_wmo['ISI']>-0.9)
bad_wx_bui  = bad_wxstation(df_wmo['BUI']>-0.9)
bad_wx_dc  = bad_wxstation(df_wmo['DC']>-0.9)
bad_wx_dmc  = bad_wxstation(df_wmo['DMC']>-0.9)

# other = [721525, 721430, 721303, 71682, 71669, 5536, 9418]
bad_ws_all = bad_wx_temp + bad_wx_rh + bad_wx_wsp + bad_wx_precip
bad_ws_all = bad_ws_all + bad_wx_ffmc + bad_wx_fwi + bad_wx_isi + bad_wx_bui + bad_wx_dc + bad_wx_dmc
bad_ws_all = [str(i) for i in bad_ws_all]


df = df.loc[~df['WMO'].isin(bad_ws_all)]
df['DateTime'] = pd.to_datetime(df['DateTime'] ,format= '%Y%m%d%H')
df = df.set_index('DateTime')



def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = date(2020, 5, 24)
end_date = date(int(todays_date[:-4]), int(todays_date[-5:-2]), int(todays_date[-2:]))


ffmc_r, dmc_r, dc_r, isi_r, bui_r, fwi_r = [],[],[],[],[],[]
time = []
for single_date in daterange(start_date, end_date):
    # print(single_date.strftime("%Y-%m-%d"))
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
ax.plot(time[:-2],ffmc[:-2], label ='FFMC', linewidth = 4, color = colors[0])
ax.plot(time[:-2],dmc[:-2], label ='DMC',linewidth = 4, color = colors[1])
ax.plot(time[:-2],dc[:-2], label ='DC', linewidth = 4, color = colors[2])
ax.plot(time[:-2],isi[:-2], label ='ISI', linewidth = 4, color = colors[3])
ax.plot(time[:-2],bui[:-2], label ='BUI', linewidth = 4, color = colors[4])
ax.plot(time[:-2],fwi[:-2], label ='FWI', linewidth = 4, color = colors[5])

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

fig.savefig(str(root_dir) + f"/images/intercomparison/pearsons_time_series-{todays_date}.png")


print("Run Time: ", datetime.now() - startTime)
