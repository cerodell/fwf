#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import sys
import json
import numpy as np
import xarray as xr
import geojsoncontour
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from dev_geoutils import mask, mycontourf_to_geojson
from datetime import datetime, date, timedelta
startTime = datetime.now()

from context import data_dir, xr_dir, wrf_dir, root_dir

import warnings
warnings.filterwarnings("ignore", message="invalid value encountered in true_divide")


### Open color map json
with open('/bluesky/fireweather/fwf/json/dev_colormaps.json') as f:
  cmaps = json.load(f)


### Get Path to most recent FWI forecast and open 
hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 
############################################################
# hourly_file_dir = str(xr_dir) + str("/fwf-hourly-2020082300.zarr") 
# daily_file_dir = str(xr_dir) + str("/fwf-daily-2020082300.zarr")
############################################################
hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)

ffmc = [0, 0.5, 1, 2, 3, 6, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 100, 140, 141]
# blah = np.linspace(-1,1,0.2, dtype =int)
# blah = np.arange(-1,1,0.2, dtype =int)

tester = np.zeros(18)
tester = tester +5.5
from pylab import *

# 0.00-0.19: very weak
# 0.20-0.39: weak
# 0.40-0.59: moderate 
# 0.60-0.79: strong
# 0.80-1.00: very strong.

cmap = cm.get_cmap('PiYG', 10)    # PiYG

hex_list = []
for i in range(cmap.N):
    rgb = cmap(i)[:3] # will return rgba, we take only first 3 so we get rgb
    hex_list.append(str(matplotlib.colors.rgb2hex(rgb)))
hex_color = matplotlib.colors.to_hex([ 0.47, 
                                      0.0,  
                                      1.0,  
                                      0.5 ], 
                                     keep_alpha = True) 
  
# print(plt.rcParams['axes.prop_cycle'].by_key()['color'])

# # create discrete colormap 
# cmap = colors.ListedColormap([hex_color,  
#                               'red']) 
# # cm = mpl.colors.ListedColormap(C/255.0)
# # plt.imshow(..., cmap=cm) 


# # import seaborn as sns
# colors = ["blue", "green", "yellow", "red"]
# pal = sns.color_palette(colors, n_colors=50)
# pal.as_hex()




# var color_map_wx = L.control({position: "bottomleft"});
# color_map_wx.onAdd = function(map) {
#     var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
#     div.innerHTML =
# '<table id="values">\
# <tr id="colours">\
# <td style="background:#000080; height:10px; border-left:none;"></td>\
# <td style="background:#0000c4;"></td>\
# <td style="background:#0000ff;"></td>\
# <td style="background:#0034ff;"></td>\
# <td style="background:#0070ff;"></td>\
# <td style="background:#00acff;"></td>\
# <td style="background:#02e8f4;"></td>\
# <td style="background:#33ffc4;"></td>\
# <td style="background:#63ff94;"></td>\
# <td style="background:#94ff63;"></td>\
# <td style="background:#c4ff33;"></td>\
# <td style="background:#f4f802;"></td>\
# <td style="background:#ffc100;"></td>\
# <td style="background:#ff8900;"></td>\
# <td style="background:#ff5200;"></td>\
# <td style="background:#ff1a00;"></td>\
# <td style="background:#c40000;"></td>\
# <td style="background:#800000;"></td>\
# </tr>\
# <tr id="ticks">\
# <td style="height:10px; border-left:none;"></td>\
# <td></td>\
# <td></td>\
# <td></td>\
# <td></td>\
# <td></td>\
# <td></td>\
# <td></td>\
# <td></td>\
# <td></td>\
# <td></td>\
# <td></td>\
# <td></td>\
# <td></td>\
# <td></td>\
# <td></td>\
# <td></td>\
# <td></td>\
# </tr>\
# </table>\
# <table id="labels">\
# <tr>\
# <td height="2px">0</td>\
# <td height="10px"></td>\
# <td height="10px">60</td>\
# <td height="10px"></td>\
# <td height="10px">75</td>\
# <td height="10px"></td>\
# <td height="14px">81</td>\
# <td height="10px"></td>\
# <td height="10px">83</td>\
# <td height="10px"></td>\
# <td height="10px">85</td>\
# <td height="10px"></td>\
# <td height="14px">87</td>\
# <td height="10px"></td>\
# <td height="10px">89</td>\
# <td height="10px"></td>\
# <td height="10px">95</td>\
# <td height="2px"></td>\
# <td height="2px">100+</td>\
# </tr>\
# </table>\
# <div class="legend-title">Fine Fuel Moisture Code</div>';
#     return div;
# }
# color_map_wx.addTo(map);