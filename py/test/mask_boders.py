import context 
import geopandas as gpd

import pandas as pd

from context import data_dir, xr_dir, wrf_dir, root_dir



shapedir = str(data_dir) + "/gpr_000b11a_e.shp"

shapefile = gpd.read_file(shapedir)
# print(shapefile)