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
start_date = date(2020, 6, 4)
stop_date  = date(2020, 8, 10)

todays_date = stop_date.strftime("%Y%m%d")


# filecsv = f'/Volumes/cer/fireweather/data/csv/fwf-intermoparison-{todays_date}00.csv'
filecsv = str(data_dir) + f'/csv/fwf-intercomparison-{todays_date}00.csv'
inter_df = pd.read_csv(filecsv)

inter_df['DateTime'] = pd.to_datetime(inter_df['DateTime'] ,format= '%Y%m%d%H')
inter_df = inter_df.set_index('DateTime')

start = start_date.strftime("%Y-%m-%d")
stop = stop_date.strftime("%Y-%m-%d")
inter_df = inter_df.loc[stop:start]
inter_df = inter_df.reset_index()


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


wmo = sorted(df['WMO'].unique())
wmo.remove(9114)
wmo.remove(9113)
wmo.remove(9213)
wmo.remove(9513)
wmo.remove(71520)
wmo.remove(721525)
wmo.remove(721430)
wmo.remove(721303)
wmo.remove(71682)
wmo.remove(71669)
wmo.remove(9419)
wmo.remove(5536)
df = df.set_index('WMO')

wmo_r_1day = {}
for loc in wmo:
    # print(loc)
    df_corr = df.loc[loc]
    prearson_ffmc = round(df_corr['F_today'].corr(df_corr['FFMC']),3)
    prearson_dmc = round(df_corr['P_today'].corr(df_corr['DMC']),3)
    prearson_dc = round(df_corr['D_today'].corr(df_corr['DC']),3)
    prearson_isi = round(df_corr['R_today'].corr(df_corr['ISI']),3)
    prearson_bui = round(df_corr['U_today'].corr(df_corr['BUI']),3)
    prearson_fwi = round(df_corr['S_today'].corr(df_corr['FWI']),3)

    prearson_temp = round(df_corr['T_today'].corr(df_corr['TEMP']),3)
    prearson_rh = round(df_corr['H_today'].corr(df_corr['RH']),3)
    prearson_wsp = round(df_corr['W_today'].corr(df_corr['WS']),3)
    # prearson_wdir = round(df_corr['WD_today'].corr(df_corr['WDIR']),3)
    prearson_precip = round(df_corr['r_o_today'].corr(df_corr['PRECIP']),3)

    wmo_r_1day[str(loc)] = {'FFMC': prearson_ffmc, "DMC": prearson_dmc, \
        "DC": prearson_dc, "ISI": prearson_isi, "BUI": prearson_bui, "FWI": prearson_fwi, \
            'lat': round(df_corr['lat'].iloc[0],3), 'lng': round(df_corr['lon'].iloc[0],3), \
                "TEMP": prearson_temp,"RH": prearson_rh,"WSP": prearson_wsp,\
                    "PRECIP": prearson_precip }

wmo_r_2day = {}
for loc in wmo:
    df_corr = df.loc[loc]
    prearson_ffmc = df_corr['F_yesterday'].corr(df_corr['FFMC'])
    prearson_dmc = df_corr['P_yesterday'].corr(df_corr['DMC'])
    prearson_dc = df_corr['D_yesterday'].corr(df_corr['DC'])
    prearson_isi = df_corr['R_yesterday'].corr(df_corr['ISI'])
    prearson_bui = df_corr['U_yesterday'].corr(df_corr['BUI'])
    prearson_fwi = df_corr['S_yesterday'].corr(df_corr['FWI'])

    prearson_temp = df_corr['T_yesterday'].corr(df_corr['TEMP'])
    prearson_rh = df_corr['H_yesterday'].corr(df_corr['RH'])
    prearson_wsp = df_corr['W_yesterday'].corr(df_corr['WS'])
    # prearson_wdir = df_corr['WD_yesterday'].corr(df_corr['WDIR'])
    prearson_precip = df_corr['r_o_yesterday'].corr(df_corr['PRECIP'])

    wmo_r_2day[str(loc)] = {'FFMC': prearson_ffmc, "DMC": prearson_dmc, \
        "DC": prearson_dc, "ISI": prearson_isi, "BUI": prearson_bui, "FWI": prearson_fwi, \
            'lat': round(df_corr['lat'].iloc[0],3), 'lng': round(df_corr['lon'].iloc[0],3), \
                "TEMP": prearson_temp,"RH": prearson_rh,"WSP": prearson_wsp,\
                    "PRECIP": prearson_precip }


# def drop_bad_wx(wmo_dict):
    # Convert dictorary to dataframe
df_wmo = pd.DataFrame.from_dict(wmo_r_1day)
df_wmo = df_wmo.T
df_wmo['wmo'] = df_wmo.index
df_wmo = df_wmo.reset_index()
# print(df_wmo)

## find stations with crap correlation
def bad_wxstation(condtion):
    bad_wx = df_wmo.drop(df_wmo.index[np.where(condtion)])
    bad_wx_wmo = sorted(bad_wx['wmo'].unique())
    bad_wx_wmo = [int(i) for i in bad_wx_wmo]
    return bad_wx_wmo
    
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

# print(bad_ws_all)
# print(len(df_wmo))

df = df_wmo.loc[~df_wmo['wmo'].isin(bad_ws_all)]
# print(len(df))
df = df.T
test = df.fillna(-99)

wmo_r_1day = df.to_dict()
# wmo_r_2day = drop_bad_wx(wmo_r_2day)

# print(f"{str(datetime.now())} ---> write fwfskip 32 dictonary to json" )
### Write json file to defind dir 

timestamp = stop_date.strftime("%Y%m%d00")
with open(str(data_dir) + f"/json/fwf-wxstation-{timestamp}.json","w") as f:
    json.dump(wmo_r_1day,f, default=json_util.default, separators=(',', ':'), indent=None)

# print(f"{str(datetime.now())} ---> wrote json fwfskip 32 to:  " + str(make_dir) + f"/fwf-32km-{timestamp}.json")
