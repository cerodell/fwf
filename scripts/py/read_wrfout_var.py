#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 13:57:18 2019

@author: crodell
"""

from netCDF4 import Dataset
import numpy as np
from wrf import (getvar, to_np, ALL_TIMES)


filein = '/Volumes/Scratch/ALBERTA_2019080500/'
#filein = '/scratch/summit/rodell/WRFTEST/WRF/test/em_real/'


file =	"wrfout_d03_2019-08-06_18:00:00"

wrf_file = Dataset(filein+file,'r')
print(wrf_file.variables)

