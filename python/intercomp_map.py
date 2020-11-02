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
start_date = date(2020, 6, 4)
stop_date  = date(2020, 9, 20)

todays_date = stop_date.strftime("%Y%m%d")


# filecsv = f'/Volumes/cer/fireweather/data/csv/fwf-intermoparison-{todays_date}00.csv'
# filecsv = str(data_dir) + f'/csv/fwf-intercomparison-{todays_date}00.csv'
filecsv = str(data_dir) + f'/csv/current/fwf-intercomparison-current.csv'
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
# wmo.remove(71520)
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

    wmo_r_1day[str(loc)] = {'FFMC': prearson_ffmc, "DMC": prearson_dmc, \
        "DC": prearson_dc, "ISI": prearson_isi, "BUI": prearson_bui, "FWI": prearson_fwi, \
            'lat': round(df_corr['lat'].iloc[0],3), 'lng': round(df_corr['lon'].iloc[0],3), \
                "TEMP": prearson_temp,"RH": prearson_rh,"WSP": prearson_wsp,"WDIR": prearson_wdir,\
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
    prearson_wdir = df_corr['WD_yesterday'].corr(df_corr['WDIR'])
    prearson_precip = df_corr['r_o_yesterday'].corr(df_corr['PRECIP'])

    wmo_r_2day[str(loc)] = {'FFMC': prearson_ffmc, "DMC": prearson_dmc, \
        "DC": prearson_dc, "ISI": prearson_isi, "BUI": prearson_bui, "FWI": prearson_fwi, \
            'lat': round(df_corr['lat'].iloc[0],3), 'lng': round(df_corr['lon'].iloc[0],3), \
                "TEMP": prearson_temp,"RH": prearson_rh,"WSP": prearson_wsp,"WDIR": prearson_wdir,\
                    "PRECIP": prearson_precip }


def drop_bad_wx(wmo_dict):
    # Convert dictorary to dataframe
    df_wmo = pd.DataFrame.from_dict(wmo_dict)
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

    print(bad_ws_all)
    print(len(df_wmo))

    df = df_wmo.loc[~df_wmo['wmo'].isin(bad_ws_all)]
    print(len(df))
    df = df.T

    return df.to_dict()

wmo_r_1day = drop_bad_wx(wmo_r_1day)
wmo_r_2day = drop_bad_wx(wmo_r_2day)


def stations_map(var, start, stop, day):
    if day == 1:
        wmo_r = wmo_r_1day
        title = 'One'
    elif day == 2:
        wmo_r = wmo_r_2day
        title = 'Two'
    else:
        exit

        # An arbitrary choice.
    canada_east, canada_west = -60, -138
    canada_north, canada_south = 64, 37

    standard_parallels = (49, 77)
    central_longitude = -(91 + 52 / 60)

    states_provinces = cfeature.NaturalEarthFeature(category='cultural',
        name='admin_1_states_provinces_lines',scale='50m',facecolor='none')

    fig = plt.figure(figsize=[16,8])
    fig.suptitle(f"Station Observations vs {title} Day Model Forecast at noon local of  {var} \n {start} to {stop}", fontsize=16)
    # fig.subplots_adjust(hspace=0.001)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    ax.set_extent([canada_west, canada_east, canada_south, canada_north])
    cm = plt.cm.get_cmap('jet_r')

    for key in wmo_r:
        C = ax.scatter(wmo_r[key]['lng'],wmo_r[key]['lat'], zorder =10, s= 12,\
            cmap=cm, vmin=-1, vmax=1, c=wmo_r[key][var], transform=ccrs.PlateCarree())
    ax.gridlines()
    clb = fig.colorbar(C, ax = ax, fraction=0.02, pad=0.02)
    clb.set_label(f"{var} (Pearson's r)", fontsize = 8)
    clb.ax.tick_params(labelsize= 8) 
    ax.add_feature(cfeature.LAND, zorder =1)
    ax.add_feature(cfeature.LAKES, zorder =1)
    ax.add_feature(cfeature.OCEAN, zorder =1)
    ax.add_feature(cfeature.BORDERS, zorder =1)
    ax.add_feature(cfeature.COASTLINE, zorder =1)
    # ax.add_feature(cfeature.RIVERS)
    ax.add_feature(states_provinces,edgecolor='gray', zorder =2)
    plt.tight_layout()
    var = var.lower()
    fig.savefig(str(root_dir) + f"/images/intercomparison/map/pearsons_map_{var}_{str(day)}day.png", dpi =200)




print(f"{str(datetime.now())} ---> start loop of fwi vars" )
stations_map('FFMC', start, stop, 1)
stations_map('DMC', start, stop, 1)
stations_map('DC', start, stop, 1)
stations_map('ISI', start, stop, 1)
stations_map('BUI', start, stop, 1)
stations_map('FWI', start, stop, 1)
print(f"{str(datetime.now())} ---> End loop of fwi vars" )

print(f"{str(datetime.now())} ---> start loop of met vars :)" )
stations_map('TEMP', start, stop, 1)
stations_map('RH', start, stop, 1)
stations_map('WSP', start, stop, 1)
stations_map('WDIR', start, stop, 1)
stations_map('PRECIP', start, stop, 1)
print(f"{str(datetime.now())} ---> End loop of met vars" )



print(f"{str(datetime.now())} ---> start loop of fwi vars" )
stations_map('FFMC', start, stop, 2)
stations_map('DMC', start, stop, 2)
stations_map('DC', start, stop, 2)
stations_map('ISI', start, stop, 2)
stations_map('BUI', start, stop, 2)
stations_map('FWI', start, stop, 2)
print(f"{str(datetime.now())} ---> End loop of fwi vars" )

print(f"{str(datetime.now())} ---> start loop of met vars :)" )
stations_map('TEMP', start, stop, 2)
stations_map('RH', start, stop, 2)
stations_map('WSP', start, stop, 2)
stations_map('WDIR', start, stop, 2)
stations_map('PRECIP', start, stop, 2)
print(f"{str(datetime.now())} ---> End loop of met vars" )


### Timer
print("Run Time: ", datetime.now() - startTime)