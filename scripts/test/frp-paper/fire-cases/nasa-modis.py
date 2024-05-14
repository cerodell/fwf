#!/Users/crodell/miniconda3/envs/fwx/bin/python


import json
import context
import salem
import dask
import numpy as np
import pandas as pd
import xarray as xr

from salem import wgs84

from context import root_dir, data_dir

import geopandas as gpd
from shapely.geometry import Polygon


static_d02 = salem.open_xr_dataset(str(data_dir) + "/static/static-vars-wrf-d02.nc")
# Reading the Shapefile
# fire_i = gpd.read_file(str(data_dir) + '/fires/GLOBFIRE_burned_area_full_dataset_2002-2022/GLOBFIRE_vs1_2022.shp')
fire_i = gpd.read_file(
    str(data_dir) + "/fires/nbac_m3_2023_Feb22/nbac_m3_2023_Feb22.shp"
)
# Displaying the first few rows of the GeoDataFrame
print(fire_i.head())
