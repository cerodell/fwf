#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import sys
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime, date, timedelta

from context import data_dir, wrf_dir, root_dir, xr_dir
from wrf import ll_to_xy, xy_to_ll




def intercomparison_make_csv(local, todays_date, yesterday_date):

    # ### Get Path to TODAYS FWI forecast and open 
    # if local == True:
    #     # xr_dir = '/Volumes/cer/fireweather/data/xr'
    #     filein = '/Volumes/cer/fireweather/data/wrf/'
    #     write_to_dir = '/Volumes/cer/fireweather/data/csv/'

    # else:

    wrf_folder = date.today().strftime(f'/{todays_date[2:]}00/')
    filein = str(wrf_dir) + wrf_folder
    write_to_dir = str(data_dir) + '/csv/'

    hourly_file_dir = str(xr_dir) + str(f"/fwf-hourly-{todays_date}00.zarr") 
    daily_file_dir = str(xr_dir) + str(f"/fwf-daily-{todays_date}00.zarr") 
    hourly_ds = xr.open_zarr(hourly_file_dir)
    daily_ds = xr.open_zarr(daily_file_dir)

    ### Get Path to YESTERDAYS FWI forecast and open
    if yesterday_date == None:
        print('No houlry or daily ds from yesterday')
    else:
        hourly_file_dir_yesterday = str(xr_dir) + str(f"/fwf-hourly-{yesterday_date}00.zarr") 
        daily_file_dir_yesterday = str(xr_dir) + str(f"/fwf-daily-{yesterday_date}00.zarr") 
        hourly_ds_yesterday = xr.open_zarr(hourly_file_dir_yesterday)
        daily_ds_yesterday = xr.open_zarr(daily_file_dir_yesterday)

    ### Get Path to most recent WRF run for most uptodate snowcover info
    
    wrf_file_dir = sorted(Path(filein).glob('wrfout_d03_*'))
    wrf_file = Dataset(wrf_file_dir[0],'r')

    ### Get All Stations CSV
    url = 'https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/cwfis_allstn2019.csv'
    stations_df = pd.read_csv(url, sep = ',')
    stations_df = stations_df.drop_duplicates()
    stations_df = stations_df.rename({'wmo': 'WMO', 'name': 'NAME'}, axis=1)
    stations_df = stations_df.drop(columns=['tmm','ua', 'the_geom', 'h_bul','s_bul','hly','syn'])

    ### Get Daily observations CSV
    url2 = f'https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/current/cwfis_fwi_{todays_date}.csv'
    headers = list(pd.read_csv(url2,nrows=0))
    daily_df = pd.read_csv(url2,  sep = ',', names=headers)
    daily_df = daily_df.drop_duplicates()
    daily_df = daily_df.drop(daily_df.index[[0]])
    daily_df['WMO'] = daily_df['WMO'].astype(str).astype(int)


    ### Merge daily_df and stations_df and drop stations with no data
    inter_df = stations_df.merge(daily_df, on='WMO', how='outer')

    ### replace NULL with np.nan
    for column in inter_df:
        inter_df = inter_df[inter_df[column] != ' NULL']
        inter_df = inter_df[inter_df[column] != '  NULL']


    ### Drop stations out sie of model domain
    xy_np  = ll_to_xy(wrf_file, inter_df['lat'], inter_df['lon'])
    inter_df['x'] = xy_np[0]
    inter_df['y'] = xy_np[1]
    shape = np.shape(daily_ds.T[0,:,:])
    inter_df = inter_df.drop(inter_df.index[np.where(inter_df['x']>(shape[1]-1))])
    inter_df = inter_df.drop(inter_df.index[np.where(inter_df['y']>(shape[0]-1))])
    inter_df = inter_df.drop(inter_df.index[np.where(inter_df['x']<-1)])
    inter_df = inter_df.drop(inter_df.index[np.where(inter_df['y']<-1)])
    date_time  = str(np.array(hourly_ds.Time[0], dtype ='datetime64[h]'))
    date_time = datetime.strptime(str(date_time), '%Y-%m-%dT%H').strftime('%Y%m%d%H')
    inter_df.insert(0,'DateTime', date_time)


    ### Get point forecasts for Wxstation locations from model domain...then add to inter_df
    for var in daily_ds.data_vars:
        today = np.array(daily_ds[var][0])
        today = today[inter_df['y'],inter_df['x']]
        var_today = var + '_today'
        inter_df[var_today] = today

        if yesterday_date == None:
            print('No daily_ds from yesterday')
        else:
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





        if yesterday_date == None:
            print('No hourly_ds from yesterday')
        else:
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

    file_name_today  = str(np.array(hourly_ds.Time[0], dtype ='datetime64[h]'))
    file_name_today = datetime.strptime(str(file_name_today), '%Y-%m-%dT%H').strftime('%Y%m%d%H')
    csv_dir_today = write_to_dir + f'fwf-intercomparison-{file_name_today}.csv'
    csv_dir_current = write_to_dir + f'current/fwf-intercomparison-current.csv'


        
    if yesterday_date == None:
        print('No inter_df from yesterday')
        inter_df.to_csv(csv_dir_today, sep=',', encoding='utf-8', index=False)
        print(f"{str(datetime.now())} ---> wrote {csv_dir_today}" )

    else:
        # file_name_yesterday  = str(np.array(hourly_ds_yesterday.Time[0], dtype ='datetime64[h]'))
        # file_name_yesterday = datetime.strptime(str(file_name_yesterday), '%Y-%m-%dT%H').strftime('%Y%m%d%H')
        # csv_dir_yesterday = write_to_dir + f'fwf-intercomparison-{file_name_yesterday}.csv'
        csv_dir_yesterday = write_to_dir + f'current/fwf-intercomparison-current.csv'
        
        inter_df_yesterday = pd.read_csv(csv_dir_yesterday)
        final_inter_df = pd.concat([inter_df,inter_df_yesterday])
        final_inter_df.drop(final_inter_df.columns[-1],axis=1,inplace=True)  
        final_inter_df.to_csv(csv_dir_today, sep=',', encoding='utf-8', index=False)
        final_inter_df.to_csv(csv_dir_current, sep=',', encoding='utf-8', index=False)
        print(f"{str(datetime.now())} ---> wrote {csv_dir_today}" )
        print(f"{str(datetime.now())} ---> wrote {csv_dir_current}" )
