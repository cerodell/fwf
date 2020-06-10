import context
import numpy as np
import xarray as xr
import sys
sys.path.insert(0, 'folium')
sys.path.insert(0, 'branca')

import branca
import folium
from datetime import datetime, date, timedelta
startTime = datetime.now()
import branca.colormap as cm
import geojsoncontour
import json

from context import data_dir,leaflet_dir, xr_dir
from utils import contourf_to_geojson, BindColormap, contourf_cm
from branca.element import MacroElement
import matplotlib.pyplot as plt
from bson import json_util

from jinja2 import Template




"""######### get directory to hourly/daily .zarr files.  #############"""
hourly_file_dir  = "/Volumes/CER/WFRT/FWI/Data/hourly/2020-06-07T00.zarr"
hourly_ds = xr.open_zarr(hourly_file_dir)

daily_file_dir  = "/Volumes/CER/WFRT/FWI/Data/daily/2020-06-07T00.zarr"
daily_ds = xr.open_zarr(daily_file_dir)
lats, lons = np.array(hourly_ds.XLAT), np.array(hourly_ds.XLONG)


with open('/Users/rodell/fireweather/python/basemaps.json') as f:
  basemaps = json.load(f)
with open('/Users/rodell/fireweather/python/colormaps.json') as f:
  cmaps = json.load(f)

### Make countourf and cmaps
F, F_cmap = contourf_cm(cmaps, 'F', hourly_ds, 18)
P, P_cmap = contourf_cm(cmaps, 'P', daily_ds, 0)
D, D_cmap = contourf_cm(cmaps, 'D', daily_ds, 0)
R, R_cmap = contourf_cm(cmaps, 'R', hourly_ds, 18)
U, U_cmap = contourf_cm(cmaps, 'U', daily_ds, 0)
S, S_cmap = contourf_cm(cmaps, 'S', hourly_ds, 18)

plt.close()


### Convert matplotlib contourf to geojson
ffmc = contourf_to_geojson(F, cmaps['F']['name'])
dmc  = contourf_to_geojson(P, cmaps['P']['name'])
dc   = contourf_to_geojson(D, cmaps['D']['name'])
isi  = contourf_to_geojson(R, cmaps['R']['name'])
bui  = contourf_to_geojson(U, cmaps['U']['name'])
fwi  = contourf_to_geojson(S, cmaps['S']['name'])





fwimap = folium.Map(
         location=[float(daily_ds.CEN_LAT), float(daily_ds.CEN_LON)], 
         zoom_start = 3)
for key in basemaps.keys():
    folium.TileLayer(basemaps[key]["tiles"], attr = basemaps[key]["attrs"], name = key).add_to(fwimap)
    
fwimap.add_child(ffmc).add_child(dmc).add_child(dc).add_child(isi).add_child(bui).add_child(fwi)

fwimap.add_child(folium.map.LayerControl())
fwimap.add_child(F_cmap).add_child(P_cmap).add_child(D_cmap).add_child(R_cmap).add_child(U_cmap).add_child(S_cmap)
fwimap.add_child(BindColormap(ffmc, F_cmap)).add_child(BindColormap(dmc, P_cmap))
fwimap.add_child(BindColormap(dc, D_cmap)).add_child(BindColormap(isi, R_cmap))
fwimap.add_child(BindColormap(bui, U_cmap)).add_child(BindColormap(fwi, S_cmap))




# # # Plot the data
fwimap.save('/Users/rodell/fireweather/html/multi_layer_all_15colors.html')

# ### Timer
print("Run Time: ", datetime.now() - startTime)