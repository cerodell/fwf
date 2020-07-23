import context
import sys
import json
import numpy as np
import pandas as pd
import xarray as xr
import geojsoncontour
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
startTime = datetime.now()

from context import data_dir, xr_dir, wrf_dir, root_dir
from wrf import ll_to_xy


comparison_date = '20200717'

### Get Path to most recent FWI forecast and open 
# hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
# daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 
hourly_file_dir = str(xr_dir) + str(f"/fwf-hourly-{comparison_date}00.zarr") 
daily_file_dir = str(xr_dir) + str(f"/fwf-daily-{comparison_date}00.zarr") 

hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)


### Get Path to most recent WRF run for most uptodate snowcover info
# wrf_folder = date.today().strftime('/%y%m%d00/')
wrf_folder = f"/{comparison_date[2:]}00/"
filein = str(wrf_dir) + wrf_folder
wrf_file_dir = sorted(Path(filein).glob('wrfout_d03_*'))
wrf_file = Dataset(wrf_file_dir[0],'r')

### Get All Stations CSV
url = 'https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/cwfis_allstn2019.csv'
stations_df = pd.read_csv(url, sep = ',')
stations_df = stations_df.drop_duplicates()
stations_df = stations_df.rename({'wmo': 'WMO', 'name': 'NAME'}, axis=1)
stations_df = stations_df.drop(columns=['tmm','ua', 'the_geom', 'h_bul','s_bul','hly','syn'])
# stations_df['WMO'] = stations_df['WMO'].astype(str).astype(int)
blah = len(np.array(stations_df['WMO']))


### Get Daily observations CSV
# obs_date = date.today().strftime('%Y%m%d')
url2 = f'https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/current/cwfis_fwi_{comparison_date}.csv'
headers = list(pd.read_csv(url2,nrows=0))
daily_df = pd.read_csv(url2,  sep = ',', names=headers)
daily_df = daily_df.drop_duplicates()
daily_df = daily_df.drop(daily_df.index[[0]])
daily_df['WMO'] = daily_df['WMO'].astype(str).astype(int)



inter_df = stations_df.merge(daily_df, on='WMO', how='inner')


calstat = inter_df['CALCSTATUS'].to_numpy()
calstat = calstat.astype(int)
inter_df = inter_df.drop(inter_df.index[np.where(calstat<-1)])


xy_np  = ll_to_xy(wrf_file, np.array(inter_df['lat']), np.array(inter_df['lon']))

# stnloc = [np.array(inter_df['lat']), np.array(inter_df['lon'])]
# xlat, xlon = np.array(daily_ds.XLAT), np.array(daily_ds.XLONG)

# from scipy.spatial import cKDTree
# gridTree = cKDTree(list(zip(xlon.ravel(), xlat.ravel())))
# grid_shape = xlon.shape

# xy_kd = []
# for i in range(len(np.array(inter_df['lat']))):
#     dist, inds = gridTree.query((stnloc[0][i], stnloc[1][i]))
#     xy_kd.append(np.unravel_index(inds, grid_shape))



# inter_df['x'] = xy_np[0]
# inter_df['y'] = xy_np[1]
# shape = np.shape(daily_ds.T[0,:,:])
# inter_df = inter_df.drop(inter_df.index[np.where(inter_df['x'].to_numpy()>(shape[1]-1))])
# inter_df = inter_df.drop(inter_df.index[np.where(inter_df['y'].to_numpy()>(shape[0]-1))])
# inter_df = inter_df.drop(inter_df.index[np.where(inter_df['x'].to_numpy()<-1)])
# inter_df = inter_df.drop(inter_df.index[np.where(inter_df['y'].to_numpy()<-1)])
# # inter_df = inter_df.drop(inter_df.index[np.where(xy_np[0]<-1)])


# # daily_ds_locs = daily_ds.isel(south_north=slice([inter_df['y'],inter_df['x']])
# # daily_ds_locs = daily_ds_locs.isel(south_north=0)

# # for var in daily_ds.data_vars:


# #     # timestamp  = str(np.array(daily_ds.Time[0], dtype ='datetime64[h]'))
# #     # day = datetime.strptime(str(timestamp), '%Y-%m-%dT%H').strftime('_%Y%m%d')
# #     var_day = var 
# #     inter_df[var_day] = daily_ds[var][0,inter_df['y'],inter_df['x']]

#     # timestamp  = str(np.array(daily_ds_locs.Time[1], dtype ='datetime64[h]'))
#     # # day = datetime.strptime(str(timestamp), '%Y-%m-%dT%H').strftime('_%Y%m%d')
#     # var_day = var + '_day2'
#     # inter_df[var_day] = daily_ds_locs[var][1,:]


# # hourly_ds_locs = hourly_ds.isel(south_north=inter_df['y'], west_east=inter_df['x'])
# # houlry_ds_locs = hourly_ds_locs.isel(south_north=0, time = 18)

# # for var in hourly_ds_locs.data_vars:
# #     # timestamp  = str(np.array(hourly_ds_locs.Time[0], dtype ='datetime64[h]'))
# #     # day = datetime.strptime(str(timestamp), '%Y-%m-%dT%H').strftime('_%Y%m%d')
# #     var_day = var + '_day1'
# # inter_df['F_day1'] = hourly_ds_locs['F']

# markers = "o"
# markercolor = "y"

# test = daily_ds['P'][0,inter_df['y'].to_numpy(),inter_df['x'].to_numpy()]

# fig, ax = plt.subplots(figsize=(14,8))
# # fig.suptitle(Plot_Title + '\n CRESTON, BC (CWJR 116.5 \N{DEGREE SIGN}W, 49.083 \N{DEGREE SIGN}N)', fontsize=16)
# fig.subplots_adjust(hspace=0.1)
# ax.scatter(inter_df['lat'].to_numpy(dtype=float), test.XLAT[1], color = 'purple', 
#                     marker = markers, linewidth= 5, zorder =10, label = "Observations")
# ax.set_ylabel('Model')
# ax.set_xlabel('Observed')

# plt.show()



