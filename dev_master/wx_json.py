import context
import io
import json 
import requests
from bson import json_util

import numpy as np
import pandas as pd
import xarray as xr
from glob import glob
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from wrf import ll_to_xy, xy_to_ll
from datetime import datetime, date, timedelta
from dev_utils.make_intercomp import daily_merge_ds

from context import data_dir, root_dir, wrf_dir_new, tzone_dir
startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))


## Open color map json
with open('/bluesky/fireweather/fwf/json/colormaps-dev.json') as f:
  cmaps = json.load(f)
name_list = list(cmaps)

make_dir = Path("/bluesky/fireweather/fwf/web_dev/data/")
make_dir.mkdir(parents=True, exist_ok=True)


## Get Path to most recent FWI forecast and open 
domain = 'd03'
# for i in range(13,1,-1):
# print(i)
d = datetime.today() - timedelta(days=4)
obs_date = d.strftime('%Y%m%d')
obs_date = '20201223'
print(obs_date)

obs_d2_ds = xr.open_zarr(str(data_dir) + "/intercomp/" + f"intercomp-{obs_date}-d02.zarr")
obs_d3_ds = xr.open_zarr(str(data_dir) + "/intercomp/" + f"intercomp-{obs_date}-d03.zarr")
obs_list = list(obs_d3_ds)
obs_list = obs_list[::3]

wmo_d2 = obs_d2_ds.wmo.values
wmo_d3 = obs_d3_ds.wmo.values




















## Open datasets
forecast_date = '20201224'
hourly_file_dir = str(data_dir) + str(f"/test/fwf-hourly-{forecast_date}00-{domain}.zarr") 
daily_file_dir = str(data_dir) + str(f"/test/fwf-daily-{forecast_date}00-{domain}.zarr") 

hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)

## Get a wrf file
wrf_filein = "/wrf/"
wrf_file_dir = str(data_dir) + wrf_filein
wrf_file_dir = sorted(Path(wrf_file_dir).glob(f'wrfout_{domain}_*'))
wrf_file = Dataset(wrf_file_dir[0],'r')

## Get gridded index of wmo locations
xy_np  = ll_to_xy(wrf_file, obs_d3_ds.lats.values, obs_d3_ds.lons.values)
south_north, west_east = xy_np[1], xy_np[0]

## Index datasets by wmo locations
hourly_ds = hourly_ds.isel(south_north = south_north, west_east = west_east)
daily_ds = daily_ds.isel(south_north = south_north, west_east = west_east)

time = np.array(hourly_ds.Time.dt.strftime('%Y-%m-%dT%H'), dtype = '<U13')
day = np.array(daily_ds.Time.dt.strftime('%Y-%m-%d'), dtype = '<U10')

## Get first timestamp of forecast and make dir to store files
timestamp = datetime.strptime(str(time[0]), '%Y-%m-%dT%H').strftime('%Y%m%d%H')









## Get uniquie variables from all the datasets 
var_list = list(hourly_ds)
new_list = []
for var in var_list:
  if var in name_list:
    name = cmaps[var]['name'].upper()
    if name in obs_list:
      new_list.append(var)


coords_list = list(obs_d3_ds.coords)
dict_var = {'time_fch': time.tolist(), 'time_fcd': day.tolist()}
for coords in coords_list:
  coord_array = obs_d3_ds[coords].values
  coord_array = coord_array.tolist()
  if coords == 'time':
    coords = 'time_obs'
  else:
    pass
  dict_var.update({coords.lower() :str(coord_array)})

for var in new_list:
  var_name = cmaps[var]['name'].upper() 
  fc_array = hourly_ds[var].values.astype('float64')
  fc_array= np.round(fc_array, decimals=2)
  fc_array = fc_array.tolist()
  dict_var.update({var_name.lower() + '_fc' :str(fc_array)})

  obs_array = obs_d3_ds[var_name].values.astype('float64')
  fc_array= np.round(fc_array, decimals=2)
  fc_array = fc_array.tolist()
  dict_var.update({var_name.lower() + '_obs': str(fc_array)})


  pfc_array = obs_d3_ds[var_name + '_day1'].values.astype('float64')
  pfc_array= np.round(pfc_array, decimals=2)
  pfc_array = pfc_array.tolist()
  dict_var.update({var_name.lower() + '_pfc': str(fc_array)})


with open(str(make_dir) + f"/zwx-{timestamp}-{domain}.json","w") as f:
    json.dump(dict_var,f, default=json_util.default, separators=(',', ':'), indent=None)
print(f"{str(datetime.now())} ---> wrote json to:  " + str(make_dir) + f"/zwx-{timestamp}-{domain}.json")



# ### Timer
print("Run Time: ", datetime.now() - startTime)