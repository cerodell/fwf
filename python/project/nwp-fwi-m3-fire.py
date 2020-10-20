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

from datetime import datetime
import matplotlib.colors
import matplotlib.pyplot as plt

from datetime import datetime, date, timedelta
from context import data_dir, root_dir
from utils.fireutils import firestats, read_zarr, extract_poly_coords
from wrf import getvar, xy_to_ll, ll_to_xy

ncfile = Dataset("/Volumes/cer/fireweather/data/wrf/wrfout_d03_2020-07-17_16:00:00")
wrf_file = getvar(ncfile, "T2")

filein_daily = '/Volumes/cer/fireweather/data/xr/fwf-daily-*'
filein_hourly = '/Volumes/cer/fireweather/data/xr/fwf-hourly-*'

# daily_ds = read_zarr(filein_daily, dim='time')
hourly_ds = read_zarr(filein_hourly, dim='time')

timelist = hourly_ds.Time.values

filein = str(data_dir) + '/shp/' + "perimeters.shp"
df_per = gpd.read_file(filein)
df_per = df_per.to_crs(epsg=4326)
df_per = firestats(df_per)


test_dict = {}
data_vars = list(hourly_ds.data_vars)
for var in data_vars:
    test_dict.update({var:[]})




# x_list, y_list = [], []
# for i in range(len(df_per['geometry'])):

first = np.datetime64(datetime.fromisoformat(df_per['FIRSTDATE'][0][:13]))
last = np.datetime64(datetime.fromisoformat(df_per['LASTDATE'][0][:13]))
first = np.where(timelist == first)
last = np.where(timelist == last)


ds = hourly_ds.sel(time=slice(int(first[0]),int(last[0]))) 

geom = df_per['geometry'][0]
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
y = xy[:,1]

for var in data_vars:
    test_dict.update({var: ds[var][:,y,x].values})







balh = test_dict['r_o_hourly']






