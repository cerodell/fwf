#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python
import context
import json
import bson
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
# from utils.geoutils import jsonmask, delete3D, delete2D, latlngmask
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

domains = ['d02', 'd03']

fwf = {}
for domain in domains:
    ## Get Path to most recent FWI forecast and open 
    hourly_file_dir = str(data_dir) + str(f"/test/current/fwf-hourly-current-{domain}.zarr") 
    daily_file_dir = str(data_dir) + str(f"/test/current/fwf-daily-current-{domain}.zarr") 

    # hourly_file_dir = str(xr_dir) + str("/current/fwf-hourly-current.zarr") 
    # daily_file_dir = str(xr_dir) + str("/current/fwf-daily-current.zarr")

    ### Open datasets
    hourly_ds = xr.open_zarr(hourly_file_dir)
    daily_ds = xr.open_zarr(daily_file_dir)

    ### Open color map json
    with open('/bluesky/fireweather/fwf/json/nested-index.json') as f:
        nested_index = json.load(f)

    n, y1, y2, x1, x2 = nested_index["n"], nested_index["y1_"+domain], nested_index["y2_"+domain], nested_index["x1_"+domain], nested_index["x2_"+domain] 
    unique_y, unique_x = nested_index['unique_y'], nested_index['unique_x']

    # # ### make dir for that days forecast files to be sotred...along woth index.html etc!!!!!
    # make_dir = Path("/bluesky/fireweather/fwf/web_dev/")
    # # # make_dir.mkdir(parents=True, exist_ok=True)

    xlat = np.round(daily_ds.XLAT.values,5)
    xlat= xlat[y1:-y2,x1:-x2]
    shape = xlat.shape

    xlat = np.array(xlat, dtype = '<U8')
    # xlat = xlat.ravel()

    xlong = np.round(daily_ds.XLONG.values,5)
    xlong= xlong[y1:-y2,x1:-x2]
    xlong = np.array(xlong, dtype = '<U8')
    # xlong = xlong.ravel()

    abc = list(string.ascii_lowercase)
    nfile = n
    ff = np.arange(0,nfile)
    xx = int(shape[0]/nfile)
    yy = int(shape[1]/nfile)
    empty = np.empty([shape[0],shape[1]], dtype = '<U2')

    for i in ff:
        # print(i)
        for j in ff:
            xx1, yy1 = (xx * i), (yy * j)
            xx2, yy2 = (xx * ( i + 1)), (yy * ( j + 1))
            zone = str((abc[i]+abc[j]))
            # print(zone)
            empty[xx1:xx2,yy1:yy2] = zone


    unique, index, counts = np.unique(empty, return_index = True, return_counts = True)
    test = empty

    if domain == 'd02':
        print('domain d02')
        empty[unique_y[0]:unique_y[-1]+1, unique_x[0]:unique_x[-1]+1] = 'd3'
    else:
        print('domain d03')

    fwf.update({
            'ZONE_'+ domain: empty.tolist(),
            'XLAT_'+ domain: xlat.tolist(),
            'XLONG_'+ domain: xlong.tolist(),
            })



# Write json file to defind dir 
with open(str(root_dir) + f"/json/fwf-zone-merge.json","w") as f:
    json.dump(fwf,f, default=json_util.default, separators=(',', ':'), indent=None)
print(f"{str(datetime.now())} ---> wrote json fwf zone to:  " + str(root_dir) + f"/json/fwf-zone-merge.json")

# ### Timer
print("Run Time: ", datetime.now() - startTime)




# unique_masked, index_masked, counts_masked = np.unique(empty, return_index = True, return_counts = True)
# unique_masked_list = unique_masked.tolist()
# unique_masked_list.remove('d3')

# ### Open color map json
# with open('/bluesky/fireweather/fwf/json/colormaps-dev.json') as f:
#   cmaps = json.load(f)

# var_list = list(hourly_ds)
# remove = ["SNOWC", "SNOWH", "U10", "V10", "m_o", "r_o_hourly"]
# var_list = list(set(var_list) - set(remove))
# empty = empty.flatten()
# for filename in unique_masked_list:
#     dict_file = {}
#     for var in var_list:
#         var_name = cmaps[var]['name'].lower()
#         # print(var_name)
#         var_array = hourly_ds[var].values
#         var_array = var_array[:, y1:-y2,x1:-x2]
#         time_shape = var_array.shape    
#         var_array = var_array.reshape(time_shape[0],(time_shape[1]*time_shape[2]))
#         inds = np.where(empty==filename)
#         var_array = var_array[:,inds[0]]
#         dict_file.update({var_name: var_array.tolist()})



# unique, index, counts = np.unique(inds[0], return_index = True, return_counts = True)

# blah = np.array([np.take(ffmc_,inds_,axis=0) for (ffmc_,inds_) in zip(ffmc,inds)])


# new_msaarr = np.take(ffmc, inds)

#     # i, j = np.indices(empty.shape)
#     # j_true = np.isin(j, unique_x)
#     # i_true = np.isin(i, unique_y)
#     # empty = np.where((j_true== False) & (i_true== False), empty, 'd3')

# tester = np.where(empty=='aa', ffmc)



# unique_masked

