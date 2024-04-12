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
    str(data_dir) + "/fires/North_America/North_America_vs1_2021.shp"
)
# Displaying the first few rows of the GeoDataFrame
print(fire_i.head())

# # Define the bounds of North America
# na_bounds = {
#     'min_lon': -168.43,
#     'max_lon': -52.62,
#     'min_lat': 23.5,
#     'max_lat': 71.5
# }

# # Create a Polygon from the North America bounds
# na_polygon = Polygon([
#     (na_bounds['min_lon'], na_bounds['min_lat']),
#     (na_bounds['min_lon'], na_bounds['max_lat']),
#     (na_bounds['max_lon'], na_bounds['max_lat']),
#     (na_bounds['max_lon'], na_bounds['min_lat']),
#     (na_bounds['min_lon'], na_bounds['min_lat'])
# ])

# # Filter rows where the geometry is within the North American bounds
# fire_i_na = fire_i[fire_i['geometry'].apply(lambda geom: geom.within(na_polygon))]
df = fire_i
for i in range(len(fire_i)):
    try:
        static_d02["HGT"].salem.subset(
            shape=fire_i[i : i + 1], margin=20, all_touched=True
        )
    except:
        print(df.iloc[i])
        df = df.drop(index=i)

static_d02["HGT"].salem.subset(shape=df[-2:-1], margin=20, all_touched=True)

# fire_i now contains only rows with geometries inside North America
print(df)
df.to_file(
    str(data_dir) + "/fires/North_America/North_America_vs2_2021.shp",
    driver="ESRI Shapefile",
)
