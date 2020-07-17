import context
import numpy as np
import pandas as pd
import geopandas as gpd
from context import data_dir, xr_dir, wrf_dir, tzone_dir







shapedir = str(data_dir) + "/gpr_000b11a_e.shp"

shapefile = gpd.read_file(shapedir)
print(shapefile)