import context
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
from netCDF4 import Dataset
import cartopy.crs as crs
import geopandas as gpd
import seaborn as sns
from glob import glob
import json
from bson import json_util


from datetime import datetime
import matplotlib.colors
import matplotlib.pyplot as plt

from datetime import datetime, date, timedelta
from context import data_dir, root_dir
from utils.fireutils import firestats, read_zarr, extract_poly_coords
from wrf import getvar, xy_to_ll, ll_to_xy

datarane = np.arange(np.datetime64('1974-01-01'), np.datetime64('2020-10-25'))


ncfile = Dataset("/Volumes/cer/fireweather/data/wrf/wrfout_d03_2020-07-17_16:00:00")
wrf_file = getvar(ncfile, "T2")

filein_daily = '/Volumes/cer/fireweather/data/xr/fwf-daily-*'
filein_hourly = '/Volumes/cer/fireweather/data/xr/fwf-hourly-*'

daily_ds = read_zarr(filein_daily, dim='time')
hourly_ds = read_zarr(filein_hourly, dim='time')
domain = hourly_ds.XLAT.shape
timelist = hourly_ds.Time.values

filein = str(data_dir) + '/shp/' + "perimeters.shp"
df_per = gpd.read_file(filein)
df_per = df_per.to_crs(epsg=4326)
df_per = firestats(df_per)
fire_id = df_per['UID'].values


# for i in range(5):
for i in df_per.index:
    first = np.datetime64(datetime.fromisoformat(df_per['FIRSTDATE'][i][:13]))
    last = np.datetime64(datetime.fromisoformat(df_per['LASTDATE'][i][:13]))
    print(f"First: {first}")
    print(f"Last: {last}")
    if first > timelist[0]:
        first = np.where(timelist == first)
        last = np.where(timelist == last)
        print(f"First: {first}")
        print(f"Last: {last}")
        ds = hourly_ds.sel(time=slice(int(first[0]),int(last[0])+1)) 

        geom = df_per['geometry'][i]
        poly_ll = extract_poly_coords(geom)
        if len(poly_ll['interior_coords']) == 0:
            lats = list(poly_ll['exterior_coords'][:,1])
            lngs = list(poly_ll['exterior_coords'][:,0])
            xy_np_ex  = ll_to_xy(ncfile, lats, lngs)   
            combined = np.vstack((xy_np_ex[0], xy_np_ex[1])).T
            xy = np.unique(combined, axis=0)
        else:
            lats = list(poly_ll['interior_coords'][:,1])
            lngs = list(poly_ll['interior_coords'][:,0])
            xy_np_int  = ll_to_xy(ncfile, lats, lngs)
            lats = list(poly_ll['exterior_coords'][:,1])
            lngs = list(poly_ll['exterior_coords'][:,0])
            xy_np_ex  = ll_to_xy(ncfile, lats, lngs)
            x = np.concatenate((xy_np_ex[0], xy_np_int[0]))
            y = np.concatenate((xy_np_ex[1], xy_np_int[1]))
            combined = np.vstack((x, y)).T
            xy = np.unique(combined, axis=0)

        x = xy[:,0]
        print(x)
        y = xy[:,1]
        print(y)
        if (np.max(x) > domain[1]) or (np.max(y) > domain[0]) or (np.min(x) < 0) or (np.min(y) < 0):
            pass
        else:
            var_list = []
            for var in hourly_ds:
                var_array = ds[var][:,y,x]
                var_list.append(var_array)
            fire_ds = xr.merge(var_list)
            fire_ds_dir = str(data_dir) + str(f'/xr/fwf-fireid-{fire_id[i]}.zarr')
            fire_ds = fire_ds.compute()
            fire_ds.attrs['fireID'] = fire_id[i]
            fire_ds.to_zarr(fire_ds_dir, "w")
            print(f"wrote working {fire_ds_dir}")

            # fire_ds_list.append(fire_ds)
    else:
        pass



# for i in range(len(fire_ds_list)):
#     print(i)
#     fire_ds_dir = str(data_dir) + str(f'/xr/fwf-fireid-{fire_id[i]}.zarr')
#     fire_ds = fire_ds_list[i]
#     fire_ds = fire_ds.compute()
#     fire_ds.to_zarr(fire_ds_dir, "w")
#     print(f"wrote working {fire_ds_dir}")




# filein = str(data_dir) + "/json/fwf-fire-dictionary.json"


# with open(str(data_dir) + "/json/fwf-fire-dictionary.json","r") as f:
#   blah = json.load(f)


# df_per['xlat']= hourly_ds.XLAT.values

# fire_dict = {}
# data_vars = list(hourly_ds.data_vars)
# df_per.index
# for var in data_vars:
#     fire_dict.update({var:[]})


# for i in df_per.index:
#     for var in hourly_ds:
#         df_per.at[i,var] = 

# fire_ds_list = []



