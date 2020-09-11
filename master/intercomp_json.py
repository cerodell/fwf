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


filecsv = str(data_dir) + f'/csv/fwf-intercomparison-{file_date}00.csv'
inter_df = pd.read_csv(filecsv)

inter_df['DateTime'] = pd.to_datetime(inter_df['DateTime'] ,format= '%Y%m%d%H')
inter_df = inter_df.set_index('DateTime')

stop = stop_date.strftime("%Y-%m-%d")
last_df = inter_df.loc[stop]
last_df['wmo']  = last_df["WMO"]
drop_list = ["WMO", 'aes', 'id', 'NAME_x', 'instr', 'prov', 'lon', 'lat', 'elev', 'tz_correct', 'useindex', 'agency', 'NAME_y', 'AGENCY', 'AES', 'REPDATE', 'TD', 'WG', 'WDIR', 'PRES', 'SOG', 'DSR', 'OPTS', 'CALCSTATUS', 'x', 'y', 'D_today', 'D_yesterday', 'H_today', 'H_yesterday', 'P_today', 'P_yesterday', 'T_today', 'T_yesterday', 'U_today', 'U_yesterday', 'W_today', 'W_yesterday', 'WD_today', 'WD_yesterday', 'r_o_today', 'r_o_yesterday', 'r_o_tomorrow_today', 'r_o_tomorrow_yesterday', 'DSR_today', 'DSR_yesterday', 'F_today', 'F_yesterday', 'R_today', 'R_yesterday', 'S_today', 'S_yesterday', 'm_o_today', 'm_o_yesterday', 'r_o_hourly_today']
for colume in drop_list:
    last_df = last_df.drop(str(colume), 1)

last_df = last_df.dropna()
last_df = last_df.reset_index()
last_df = last_df.sort_values('wmo')
# last_df = last_df.drop('DateTime', 1)

last_df = last_df.astype({'TEMP':float, 'RH': float, \
    'WS': float, 'PRECIP': float, 'FFMC': float,\
        'DMC': float, 'DC': float, 'BUI': float, 'ISI': float, 'FWI': float})

def dostats(inter_df,start_date, stop_date, statstodo):

    start = start_date.strftime("%Y-%m-%d")
    stop = stop_date.strftime("%Y-%m-%d")
    inter_df = inter_df.loc[stop:start]
    inter_df = inter_df.reset_index()


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
    if statstodo == 'prearsons':
        low_count = np.where(counts<16)
    elif statstodo == 'bias':
        low_count = np.where(counts<4)

    remove_wmo  = unique[low_count]
    for i in range(len(remove_wmo)):
        # print(remove_wmo[i])
        wmo.remove(remove_wmo[i])

    df = df.set_index('WMO')

    wmo_r_1day = {}
    for loc in wmo:
        # print(loc)
        df_stats = df.loc[loc]

        if statstodo == 'bias':
            bias_ffmc = round(df_stats['F_today'].mean() / df_stats['FFMC'].mean(),2)
            bias_dmc = round(df_stats['P_today'].mean() / df_stats['DMC'].mean(),2)
            bias_dc = round(df_stats['D_today'].mean() / df_stats['DC'].mean(),2)
            bias_bui = round(df_stats['U_today'].mean() / df_stats['BUI'].mean(),2)
            bias_rh = round(df_stats['H_today'].mean() / df_stats['RH'].mean(),2)
            bias_wsp = round(df_stats['W_today'].mean() / df_stats['WS'].mean(),2)

            ### ISI
            if (df_stats['ISI'].mean() == 0.0 and df_stats['R_today'].mean() == 0.0):   
                bias_isi = round(1 / 1,2)
            elif df_stats['ISI'].mean() == 0.0:
                bias_isi = round(df_stats['R_today'].mean() / 1,2)
            elif df_stats['R_today'].mean() == 0.0:
                bias_isi = round(1 / df_stats['ISI'].mean(),2)
            else: 
                bias_isi = round(df_stats['R_today'].mean() / df_stats['ISI'].mean(),2)
            ### FWI
            if (df_stats['FWI'].mean() == 0.0 and df_stats['S_today'].mean() == 0.0):   
                bias_fwi = round(1 / 1,2)
            elif df_stats['FWI'].mean() == 0.0:    
                bias_fwi = round(df_stats['S_today'].mean() / 1,2)
            elif df_stats['S_today'].mean() == 0.0:
                bias_fwi = round(1 / df_stats['FWI'].mean(),2)
            else: 
                bias_fwi = round(df_stats['S_today'].mean() / df_stats['FWI'].mean(),2)
            ### TEMP
            if (df_stats['TEMP'].mean() == 0.0 and df_stats['T_today'].mean() == 0.0):   
                bias_temp = round(1 / 1,2)
            elif df_stats['TEMP'].mean() == 0.0:    
                bias_temp = round(df_stats['T_today'].mean() / 1,2)
            elif df_stats['T_today'].mean() == 0.0:
                bias_temp = round(1 / df_stats['TEMP'].mean(),2)
            else: 
                bias_temp = round(df_stats['T_today'].mean() / df_stats['TEMP'].mean(),2)
            ### QPF
            if (df_stats['PRECIP'].mean() == 0.0 and df_stats['r_o_today'].mean() == 0.0):   
                bias_qpf = round(1 / 1,2)
            elif df_stats['PRECIP'].mean() == 0.0:    
                bias_qpf = round(df_stats['r_o_today'].mean() / 1,2)
            elif df_stats['r_o_today'].mean() ==0.0:
                bias_qpf = round(1 / df_stats['PRECIP'].mean(),2)
            else:
                bias_qpf = round(df_stats['r_o_today'].mean() / df_stats['PRECIP'].mean(),2)


            all_bias = round(np.mean([bias_ffmc, bias_dmc, bias_dc, bias_isi, bias_bui, bias_fwi, \
                        bias_temp, bias_rh, bias_wsp, bias_qpf]),2)

            wmo_r_1day[str(loc)] = {'FFMC_b': bias_ffmc, "DMC_b": bias_dmc, \
                    "DC_b": bias_dc, "ISI_b": bias_isi, "BUI_b": bias_bui, "FWI_b": bias_fwi, \
                    'lat': round(df_stats['lat'].iloc[0],3), 'lng': round(df_stats['lon'].iloc[0],3), \
                    "TEMP_b": bias_temp,"RH_b": bias_rh,"WSP_b": bias_wsp,"QPF_b": bias_qpf, \
                        "bias": all_bias}
        elif statstodo == 'prearsons':

            prearson_ffmc = round(df_stats['F_today'].corr(df_stats['FFMC']),2)
            prearson_dmc = round(df_stats['P_today'].corr(df_stats['DMC']),2)
            prearson_dc = round(df_stats['D_today'].corr(df_stats['DC']),2)
            prearson_isi = round(df_stats['R_today'].corr(df_stats['ISI']),2)
            prearson_bui = round(df_stats['U_today'].corr(df_stats['BUI']),2)
            prearson_fwi = round(df_stats['S_today'].corr(df_stats['FWI']),2)

            prearson_temp = round(df_stats['T_today'].corr(df_stats['TEMP']),2)
            prearson_rh = round(df_stats['H_today'].corr(df_stats['RH']),2)
            prearson_wsp = round(df_stats['W_today'].corr(df_stats['WS']),2)
            prearson_qpf = round(df_stats['r_o_today'].corr(df_stats['PRECIP']),2)


            all_prearson = round(np.mean([prearson_ffmc, prearson_dmc, prearson_dc, prearson_isi, prearson_bui, prearson_fwi, \
                        prearson_temp, prearson_rh, prearson_wsp, prearson_qpf]),2)


            wmo_r_1day[str(loc)] = {'FFMC_c': prearson_ffmc, "DMC_c": prearson_dmc, "DC_c": prearson_dc, "ISI_c": prearson_isi,\
                            "BUI_c": prearson_bui, "FWI_c": prearson_fwi, "TEMP_c": prearson_temp,"RH_c": prearson_rh,\
                            "WSP_c": prearson_wsp,"QPF_c": prearson_qpf, "prearsons": all_prearson}
        else:
            pass

    df_wmo = pd.DataFrame.from_dict(wmo_r_1day)
    df_wmo = df_wmo.T
    df_wmo = df_wmo.dropna()
    for column in df_wmo:
        df_wmo = df_wmo[df_wmo[column] != float("inf")]
    df_wmo['wmo'] = df_wmo.index
    df_wmo = df_wmo.reset_index()
    # df_wmo = df_wmo.T

    return df_wmo


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
