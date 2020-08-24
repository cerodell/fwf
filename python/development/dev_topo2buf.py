#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import sys
import json
import geobuf
from pathlib import Path
from datetime import datetime, date, timedelta
startTime = datetime.now()
import numpy as np

from context import data_dir, xr_dir, wrf_dir, root_dir



# # ### Open color map json
# with open('/bluesky/fireweather/fwf/data/geojson/2020082300/ffmc-2020082300.geojson') as f:
#   my_json = json.load(f)


# pbf = geobuf.encode(my_json) # GeoJSON or TopoJSON -> Geobuf string

# import matplotlib as mpl
# # import matplotlib.colors
# import matplotlib.pyplot as plt
# from matplotlib import colors 


blah = np.round(np.linspace(0,80,18),2)

# from pylab import *

# cmap = cm.get_cmap('jet', 42)    # PiYG

# hex_list = []
# for i in range(cmap.N):
#     rgb = cmap(i)[:3] # will return rgba, we take only first 3 so we get rgb
#     hex_list.append(str(matplotlib.colors.rgb2hex(rgb)))
# hex_color = matplotlib.colors.to_hex([ 0.47, 
#                                       0.0,  
#                                       1.0,  
#                                       0.5 ], 
#                                      keep_alpha = True) 
  
# # create discrete colormap 
# cmap = colors.ListedColormap([hex_color,  
#                               'red']) 
# # cm = mpl.colors.ListedColormap(C/255.0)
# # plt.imshow(..., cmap=cm) 


# # import seaborn as sns
# colors = ["blue", "green", "yellow", "red"]
# pal = sns.color_palette(colors, n_colors=50)
# pal.as_hex()

