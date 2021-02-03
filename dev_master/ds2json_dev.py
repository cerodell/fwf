#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

"""
__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

"""

import context
import json
import bson
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from dev_utils.make_intercomp import daily_merge_ds
import string

from context import data_dir, xr_dir, wrf_dir, root_dir
from datetime import datetime, date, timedelta
startTime = datetime.now()

from bson import json_util
import matplotlib as mpl
import matplotlib.colors
import cartopy.crs as crs
import matplotlib.pyplot as plt
from wrf import (getvar, g_uvmet, geo_bounds)


### Open color map json
with open(str(root_dir) + '/json/colormaps-dev.json') as f:
    cmaps = json.load(f)

### Open nested grid json
with open(str(root_dir) + '/json/nested-index.json') as f:
    nested_index = json.load(f)

# # ### make dir for that days forecast files to be sotred...along woth index.html etc!!!!!
# make_dir = Path("/bluesky/fireweather/fwf/web_dev/data/plot/")
# make_dir.mkdir(parents=True, exist_ok=True)


## loop both domains
domains = ['d02','d03']
for domain in domains:
    ## Get Path to most recent FWI forecast and open 
    hourly_file_dir = str(data_dir) + str(f"/test/current/fwf-hourly-current-{domain}.zarr") 
    daily_file_dir = str(data_dir) + str(f"/test/current/fwf-daily-current-{domain}.zarr") 
    forecast_date = datetime.today().strftime('%Y%m%d')
    forecast_date = '20201224'
    # hourly_file_dir = str(xr_dir) + str("/current/fwf-hourly-current.zarr") 
    # daily_file_dir = str(xr_dir) + str("/current/fwf-daily-current.zarr")

    ### Open datasets
    hourly_ds = xr.open_zarr(hourly_file_dir)
    daily_ds = daily_merge_ds(forecast_date, domain)

    ## ROund all var is the dataset
    hourly_ds = hourly_ds.round(2)
    daily_ds = daily_ds.round(2)

    ## get array of time and day
    time = np.array(hourly_ds.Time.dt.strftime('%Y-%m-%dT%H'), dtype = '<U13')
    day = np.array(daily_ds.Time.dt.strftime('%Y-%m-%d'), dtype = '<U10')

    ## Get first timestamp of forecast and make dir to store files
    timestamp = datetime.strptime(str(time[0]), '%Y-%m-%dT%H').strftime('%Y%m%d%H')


    ### Open web grid json
    with open(str(root_dir) + f"/json/fwf-zone-{domain}.json") as f:
        filezone = json.load(f)

    ## get index to remove boundary conditions 
    n, y1, y2, x1, x2 = nested_index["n"], nested_index["y1_"+domain], nested_index["y2_"+domain], nested_index["x1_"+domain], nested_index["x2_"+domain] 
    # unique_y, unique_x = nested_index['unique_y'], nested_index['unique_x']

    ## get unique time zone ids and remove nested d03 domain from d02.
    empty = np.array(filezone['ZONE'])
    unique_masked, index_masked, counts_masked = np.unique(empty, return_index = True, return_counts = True)
    unique_masked_list = unique_masked.tolist()
    if domain == 'd02':
        unique_masked_list.remove('d3')
    else:
        pass

    ## remove some unwanted variables from dataset
    hourly_var_list = list(hourly_ds)
    remove = ["SNOWC", "SNOWH", "U10", "V10", "m_o", "r_o_hourly"]
    hourly_var_list = list(set(hourly_var_list) - set(remove))

    ## remove some unwanted variables from dataset
    daily_var_list = list(daily_ds)
    remove = ["SNOWC", "F", "H", "T", "R", "W", "WD", "r_o", "r_o_hourly", "r_o_tomorrow"]
    daily_var_list = list(set(daily_var_list) - set(remove))

    ## get array of lats and longs remove bad boundary conditions and flatten
    xlat = daily_ds.XLAT.values[y1:-y2,x1:-x2]
    xlon = daily_ds.XLONG.values[y1:-y2,x1:-x2]

    xlat = np.round(xlat.flatten(),5)
    xlon = np.round(xlon.flatten(),5)

    ## build dictionary with removed bad boundary conditions fro each variable in dataset
    ## also reshape into (time, (flatten XLAT/XLONG))
    dict_var = {}
    for var in hourly_var_list:
        var_name = cmaps[var]['name'].lower()
        var_array = hourly_ds[var].values
        var_array = var_array[:, y1:-y2,x1:-x2]
        time_shape = var_array.shape    
        var_array = var_array.reshape(time_shape[0],(time_shape[1]*time_shape[2]))
        dict_var.update({var_name:var_array})

    ## build dictionary with removed bad boundary conditions fro each variable in dataset
    ## also reshape into (time, (flatten XLAT/XLONG))
    for var in daily_var_list:
        var_name = cmaps[var]['name'].lower()
        var_array = daily_ds[var].values
        var_array = var_array[:, y1:-y2,x1:-x2]
        time_shape = var_array.shape    
        var_array = var_array.reshape(time_shape[0],(time_shape[1]*time_shape[2]))
        dict_var.update({var_name:var_array})

    ## flatten empty array 
    empty = empty.flatten()
    # unique_masked_list = ['gk']
    ## added to dictionary all variables with in there unique group
    for filename in unique_masked_list:
        print(filename)
        dict_file = {                
                    'Time': time.tolist(),
                    'Day':  day.tolist()
                    }
        inds = np.where(empty==filename)
        for var in dict_var:
            var_name = var
            # print(var_name)
            var_array = dict_var[var]
            var_array = var_array[:,inds[0]]
            var_array = var_array.astype('float64')
            var_array= np.round(var_array, decimals=2)
            var_array = var_array.tolist()
            dict_file.update({var_name: str(var_array)})
            # Write json file to defind dir 
        xlat_array = xlat[inds[0]] 
        xlat_array = xlat_array.astype('<U8')
        xlon_array = xlon[inds[0]]     
        xlon_array = xlon_array.astype('<U8')

        dict_file.update({                
                          'XLAT': xlat_array.tolist(),
                          'XLONG': xlon_array.tolist(),
                         })

        ## write json files :) 
        with open(str(make_dir) + f"/fwf-{filename}-{timestamp}-{domain}.json","w") as f:
            json.dump(dict_file,f, default=json_util.default, separators=(',', ':'), indent=None)
        print(f"{str(datetime.now())} ---> wrote json to:  " + str(make_dir) + f"/fwf-{filename}-{timestamp}-{domain}.json")
    
# ### Timer
print("Run Time: ", datetime.now() - startTime)





