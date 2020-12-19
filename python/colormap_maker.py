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
from datetime import datetime, date, timedelta
startTime = datetime.now()
from context import data_dir, xr_dir, wrf_dir, root_dir
from pylab import *


cmap = cm.get_cmap('BuPu', 20)    # PiYG

hex_list = []
for i in range(cmap.N):
    rgb = cmap(i)[:3] # will return rgba, we take only first 3 so we get rgb
    hex_list.append(str(matplotlib.colors.rgb2hex(rgb)))


    
# hex_color = matplotlib.colors.to_hex([ 0.47, 
#                                       0.0,  
#                                       1.0,  
#                                       0.5 ], 
#                                      keep_alpha = True) 
  
# print(plt.rcParams['axes.prop_cycle'].by_key()['color'])
# # create discrete colormap 
# cmap = colors.ListedColormap([hex_color,  
#                               'red']) 
# # cm = mpl.colors.ListedColormap(C/255.0)
# # plt.imshow(..., cmap=cm) 


# import seaborn as sns
# colors = ["blue", "green", "yellow", "red"]
# pal = sns.color_palette(colors, n_colors=50)
# pal.as_hex()