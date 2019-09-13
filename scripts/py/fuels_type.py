#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 14:20:29 2019

@author: crodell
"""

import numpy as np
  
import matplotlib.pyplot as plt
import matplotlib.colors
import rasterio
from rasterio.merge import merge
from pathlib import Path
from mpl_toolkits.axes_grid1 import make_axes_locatable

"######################  Adjust for user/times of interest/plot customization ######################"
##User and file location
user = "rodell"


file    = 'knn2011_feb14_2017.tif'
filein  = '/Users/'+user+'/Google Drive File Stream/Shared drives/Research/CRodell/Model/Data/fuel/'




src = rasterio.open(filein+file)
fuel = src.read(1)
fuel[fuel == -1.7e+308] = np.nan

#C1 = fuel
Water = fuel 
#C1[fuel != 101] = np.nan
Water[fuel != 118] = np.nan


#C3[fuel <= 100] = np.nan



#fuel = np.array(fuel)

#code = {"C1":101, "C2":102, "C3":103, "C4":104, "C5":105, "C6":106, "C7":107, "D1":108, \
#        "M1":109, "M2":110, "M3":111, "M4":112, "S1":113, "S2":114, "S3":115, "O1a":116, \
#        "O1B":117, "Water":118, "Non-fuel":119}
#
#
#colors = ["#D1FF73", "#216633", "#83C695", "#6FA800", "#DFB7E6", "#AB66ED", "#700BF2", \
#          "#C4BD97", "#FFD37F", "#FEFFBE", "#73DFFF", "#828282"]
#cmap= matplotlib.colors.ListedColormap(colors)
##cmap.set_under("crimson")
##cmap.set_over("w")
#levels = np.arange(100, 120,1)   
#norm= matplotlib.colors.Normalize(vmin=100.,vmax=121.)
#
#levels = np.arange(101, 119,1)   
#
#
#
fig, ax = plt.subplots(figsize=(10,10))
##fig.tight_layout(pad = 8)
plt.imshow(Water)
#plt.imshow(C1)

##clb = plt.contourf(fuel, cmap = cmap, level = levels)
#
#fig.colorbar(clb)
#
#print(fuel.min())








































