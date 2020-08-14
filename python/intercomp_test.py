import context
import sys
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
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

### Pandas hates me and throws out so many warnings......turn on warnings to find out :) 
import warnings
warnings.filterwarnings("ignore")

"""######### get directory to hourly/daily .zarr files.  #############"""


todays_date = '20200806'
# filecsv = f'/Volumes/cer/fireweather/data/csv/fwf-intermoparison-{todays_date}00.csv'
filecsv = str(data_dir) + f'/csv/fwf-intercomparison-{todays_date}00.csv'
inter_df = pd.read_csv(filecsv)


## replace NULL with np.nan
for column in inter_df:
    mask = inter_df[column] == '  NULL'
    inter_df[column][mask] = np.nan

for column in inter_df:
    mask = inter_df[column] == ' NULL'
    inter_df[column][mask] = np.nan
### Drop bad data
calstat = inter_df['CALCSTATUS'].to_numpy(dtype = float)
inter_df = inter_df.drop(inter_df.index[np.where(calstat<-1)])

### Convert specific colums to float64
inter_df = inter_df.astype({'lon':float, 'lat':float,'TEMP':float, 'RH': float, \
    'WS': float, 'WG': float, 'WDIR': float, 'PRES': float, 'PRECIP': float, 'FFMC': float,\
        'DMC': float, 'DC': float, 'BUI': float, 'ISI': float, 'FWI': float, 'DSR': float})

df = inter_df[inter_df['FFMC'].notna()]

### Find all unique weather sations
wmo = sorted(df['WMO'].unique())
wmo.remove(71203)
wmo.remove(9114)
wmo.remove(9113)
wmo.remove(9213)
wmo.remove(9513)
wmo.remove(71520)
# wmo.remove(721525)
# wmo.remove(721430)
# wmo.remove(721303)
# wmo.remove(71682)
# wmo.remove(71669)
# wmo.remove(9419)
# wmo.remove(5536)
# wmo.remove(9418)
# wmo.remove(9314)
# wmo.remove(9408)
# wmo.remove(9418)
# wmo.remove(9423)
# wmo.remove(9516)
# wmo.remove(9518)
# wmo.remove(9107)
# wmo.remove(9109)
# wmo.remove(9212)
# wmo.remove(9301)
# wmo.remove(9419)


## Set weather sations as the index
df = df.set_index('WMO')

## Empty dictorary to append pearson's r values
wmo_r_1day = {}
## Loop thoguh csv for each individula weather station and solve
## pearson's correlation coefficient
for loc in wmo:
    print(loc)
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

very_bad_wx  = bad_wxstation(df_wmo['TEMP']>-0.99)
to_good_wx = bad_wxstation(df_wmo['TEMP']<0.99999)





bad_anon = df_wmo.loc[~df_wmo['wmo'].isin(bad_wx_wmo)]


# i = 10
# df_dc_weak = inter_df.drop(inter_df.index[np.where(inter_df['WMO']!=dc_weak_wmo[i])])
# df_dc_weak['DateTime'] = pd.to_datetime(df_dc_weak['DateTime'] ,format= '%Y%m%d%H')
# weak_r = dc_weak.loc[dc_weak['wmo'] == str(dc_weak_wmo[i])]


# test = df_wmo.drop(df_wmo.index[np.where(df_wmo['FFMC']>-0.999)])











# ## find statiosn with crap correlation
# dc_weak = df_wmo.drop(df_wmo.index[np.where(df_wmo['DC']>0.39)])
# dc_weak_wmo = sorted(dc_weak['wmo'].unique())
# dc_weak_wmo = [int(i) for i in dc_weak_wmo]

# # i = 10
# # df_dc_weak = inter_df.drop(inter_df.index[np.where(inter_df['WMO']!=dc_weak_wmo[i])])
# # df_dc_weak['DateTime'] = pd.to_datetime(df_dc_weak['DateTime'] ,format= '%Y%m%d%H')
# # weak_r = dc_weak.loc[dc_weak['wmo'] == str(dc_weak_wmo[i])]


# # test = df_wmo.drop(df_wmo.index[np.where(df_wmo['FFMC']>-0.999)])

# blah = dc_weak.loc[~dc_weak['wmo'].isin(dc_weak_wmo)]

 

# for i in range(len(dc_weak_wmo)):
#     df_dc_weak = inter_df.drop(inter_df.index[np.where(inter_df['WMO']!=dc_weak_wmo[i])])
#     df_dc_weak['DateTime'] = pd.to_datetime(df_dc_weak['DateTime'] ,format= '%Y%m%d%H')
#     weak_r = dc_weak.loc[dc_weak['wmo'] == str(dc_weak_wmo[i])]


#     fig, ax = plt.subplots(5,1,figsize=(16,10))
#     fig.autofmt_xdate()
#     start = df_dc_weak['DateTime'].iloc[-1].strftime("%Y-%m-%d")
#     stop = df_dc_weak['DateTime'].iloc[0].strftime("%Y-%m-%d")

#     fig.suptitle(f"Drought Code with Pearsons r vlaue of {round(float(weak_r['DC']),3)}\
#     at WMO: {str(dc_weak_wmo[i])} \n {start} to {stop}", fontsize=16)

#     ax[0].plot(df_dc_weak['DateTime'], df_dc_weak['DC'], label = 'Observed')
#     ax[0].plot(df_dc_weak['DateTime'], df_dc_weak['D_today'], label = 'Modeled')
#     ax[0].set_ylabel('DC')

#     ax[1].plot(df_dc_weak['DateTime'], df_dc_weak['TEMP'])
#     ax[1].plot(df_dc_weak['DateTime'], df_dc_weak['T_today'])
#     ax[1].set_ylabel('Temp')

#     ax[2].plot(df_dc_weak['DateTime'], df_dc_weak['RH'])
#     ax[2].plot(df_dc_weak['DateTime'], df_dc_weak['H_today'])
#     ax[2].set_ylabel('RH')

#     ax[3].plot(df_dc_weak['DateTime'], df_dc_weak['WS'])
#     ax[3].plot(df_dc_weak['DateTime'], df_dc_weak['W_today'])
#     ax[3].set_ylabel('WSP')

#     ax[4].plot(df_dc_weak['DateTime'], df_dc_weak['PRECIP'])
#     ax[4].plot(df_dc_weak['DateTime'], df_dc_weak['r_o_today'])
#     ax[4].set_ylabel('PRECIP')

#     ax[0].legend(loc='upper center', bbox_to_anchor=(.50,1.4), shadow=True, ncol=2)
#     fig.savefig(str(root_dir) + f"/images/intercomparison/time_series/weak_dc/wmo_{str(dc_weak_wmo[i])}_time_series.png")

# # wmo_r_2day = {}
# for loc in wmo:
#     df_corr = df.loc[loc]
#     prearson_ffmc = df_corr['F_yesterday'].corr(df_corr['FFMC'])
#     prearson_dmc = df_corr['P_yesterday'].corr(df_corr['DMC'])
#     prearson_dc = df_corr['D_yesterday'].corr(df_corr['DC'])
#     prearson_isi = df_corr['R_yesterday'].corr(df_corr['ISI'])
#     prearson_bui = df_corr['U_yesterday'].corr(df_corr['BUI'])
#     prearson_fwi = df_corr['S_yesterday'].corr(df_corr['FWI'])

#     prearson_temp = df_corr['T_yesterday'].corr(df_corr['TEMP'])
#     prearson_rh = df_corr['H_yesterday'].corr(df_corr['RH'])
#     prearson_wsp = df_corr['W_yesterday'].corr(df_corr['WS'])
#     prearson_wdir = df_corr['WD_yesterday'].corr(df_corr['WDIR'])
#     prearson_precip = df_corr['r_o_yesterday'].corr(df_corr['PRECIP'])

#     wmo_r_2day[str(loc)] = {'FFMC': prearson_ffmc, "DMC": prearson_dmc, \
#         "DC": prearson_dc, "ISI": prearson_isi, "BUI": prearson_bui, "FWI": prearson_fwi, \
#             'lat': round(df_corr['lat'].iloc[0],3), 'lng': round(df_corr['lon'].iloc[0],3), \
#                 "TEMP": prearson_temp,"RH": prearson_rh,"WSP": prearson_wsp,"WDIR": prearson_wdir,\
#                     "PRECIP": prearson_precip }


