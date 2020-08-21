import context
import numpy as np
import xarray as xr
import sys
sys.path.insert(0, 'folium')
sys.path.insert(0, 'branca')

from pathlib import Path
import branca
import folium
from datetime import datetime, date, timedelta
startTime = datetime.now()
import branca.colormap as cm
import geojsoncontour
import json

from context import data_dir, xr_dir, wrf_dir
from  dev_geoutils import  colormaps, mask, mycontourf_to_geojson

from branca.element import MacroElement
import matplotlib.pyplot as plt

from jinja2 import Template


with open('/bluesky/fireweather/fwf/json/basemaps.json') as f:
  basemaps = json.load(f)
with open('/bluesky/fireweather/fwf/json/colormaps.json') as f:
  cmaps = json.load(f)


### Get Path to most recent FWI forecast and open 
hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 
############################################################
# hourly_file_dir = str(xr_dir) + str("/fwf-hourly-2020072500.zarr") 
# daily_file_dir = str(xr_dir) + str("/fwf-daily-2020072500.zarr")
############################################################
hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)

CEN_LAT, CEN_LON = float(daily_ds.CEN_LAT), float(daily_ds.CEN_LON)
hourly_vars = ['F','R','S','DSR']
for var in hourly_vars:
  hourly_ds[var] = xr.where(hourly_ds[var]< cmaps[var]['vmax'], hourly_ds[var], int(cmaps[var]['vmax'] + 1))

daily_vars = ['D','P','U']
for var in daily_vars:
  daily_ds[var] = xr.where(daily_ds[var]< cmaps[var]['vmax'], daily_ds[var], int(cmaps[var]['vmax'] + 1))



### Get Path to most recent WRF run for most uptodate snowcover info
# wrf_folder = date.today().strftime('/%y%m%d00/')
# wrf_folder = '/20072500/'
# filein = str(wrf_dir) + wrf_folder
# wrf_file_dir = sorted(Path(filein).glob('wrfout_d03_*'))


### Mask out oceans, lakes and snow cover
# hourly_ds = mask(hourly_ds, wrf_file_dir)
# daily_ds  = mask(daily_ds, wrf_file_dir)


## Get first timestamp of forecast and make dir to store files
timestamp  = str(np.array(hourly_ds.Time[0], dtype ='datetime64[h]'))
folderdate = datetime.strptime(str(timestamp), '%Y-%m-%dT%H').strftime('%Y%m%d%H')
make_dir = Path("/bluesky/fireweather/fwf/data/geojson/" + str(folderdate))
make_dir.mkdir(parents=True, exist_ok=True)




### Make countourf and cmaps
F_cmap = colormaps(cmaps, 'F') 
# P_cmap = colormaps(cmaps, 'P')
# D_cmap = colormaps(cmaps, 'D')
# R_cmap = colormaps(cmaps, 'R')
# U_cmap = colormaps(cmaps, 'U')
# S_cmap = colormaps(cmaps, 'S')


### Convert matplotlib contourf to geojson
# mycontourf_to_geojson(cmaps, 'F', hourly_ds, 0, folderdate, "colors15")

# dmc  = contourf_to_geojson(P, cmaps['P']['name'])
# dc   = contourf_to_geojson(D, cmaps['D']['name'])
# isi  = contourf_to_geojson(R, cmaps['R']['name'])
# bui  = contourf_to_geojson(U, cmaps['U']['name'])
# fwi  = contourf_to_geojson(S, cmaps['S']['name'])

with open('/bluesky/fireweather/fwf/data/geojson/2020081700/ffmc-2020081700.geojson') as f:
  geojson = json.load(f)


fwimap = folium.Map(
         location=[CEN_LAT, CEN_LON], 
         zoom_start = 3)


folium.GeoJson(
    geojson
    # style_function=lambda x: {
    #     # 'color':     x['properties']['stroke'],
    #     'weight':    x['properties']['stroke-width'],
    #     'fillColor': x['properties']['fill'],
    #     'opacity':   0.9,
    ).add_to(fwimap)



# for key in basemaps.keys():
#     folium.TileLayer(basemaps[key]["tiles"], attr = basemaps[key]["attrs"], name = key).add_to(fwimap)
    
# fwimap.add_child(ffmc).add_child(dmc).add_child(dc).add_child(isi).add_child(bui).add_child(fwi)
# fwimap.add_child(ffmc)
# fwimap.add_child(folium.map.LayerControl())
fwimap.add_child(F_cmap)
# fwimap.add_child(F_cmap).add_child(P_cmap).add_child(D_cmap).add_child(R_cmap).add_child(U_cmap).add_child(S_cmap)
# fwimap.add_child(BindColormap(ffmc, F_cmap)).add_child(BindColormap(dmc, P_cmap))
# fwimap.add_child(BindColormap(dc, D_cmap)).add_child(BindColormap(isi, R_cmap))
# fwimap.add_child(BindColormap(bui, U_cmap)).add_child(BindColormap(fwi, S_cmap))




# # # # Plot the data
fwimap.save('/bluesky/fireweather/fwf/html/colormaps.html')

# # ### Timer
print("Run Time: ", datetime.now() - startTime)