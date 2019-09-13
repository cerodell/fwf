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
user = "crodell"


file    = 'knn2011_feb14_2017.tif'
filein  = '/Users/'+user+'/Google Drive File Stream/Shared drives/Research/CRodell/Model/Data/fuel/'




src = rasterio.open(filein+file)
fuel = src.read(1)

#fuel = np.array(fuel)
























