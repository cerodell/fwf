#!/Users/crodell/miniconda3/envs/fwx/bin/python

"""
This script processes a dataset of global wildfire perimeters, focusing specifically on North America.
It removes any rows with null values, subsets the data for North America, and saves the cleaned subset.

Datasource: https://gwis.jrc.ec.europa.eu/apps/country.profile/downloads
Reference: https://doi.org/10.1038/s41597-019-0312-2

"""
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

year = "2022"
# df_2021 = gpd.read_file(
#     str(data_dir) + "/fires/North_America/North_America_vs2_2021.shp",
#     driver="ESRI Shapefile",
# )

# df_2022 = gpd.read_file(
#     str(data_dir) + "/fires/North_America/North_America_vs2_2022.shp",
#     driver="ESRI Shapefile",
# )

# df_2023 = gpd.read_file(
#     str(data_dir) + "/fires/North_America/North_America_vs2_2023.shp",
#     driver="ESRI Shapefile",
# )


static_d02 = salem.open_xr_dataset(str(data_dir) + "/static/static-vars-wrf-d02.nc")
# Reading the Shapefile
if year == "2023":
    fire_i = gpd.read_file(
        str(data_dir) + f"/fires/GLOBFIRE_2023/original_globfire_filtered_{year}.shp"
    )
else:
    fire_i = gpd.read_file(
        str(data_dir)
        + f"/fires/GLOBFIRE_burned_area_full_dataset_2002-2022/GLOBFIRE_vs1_{year}.shp"
    )
# fire_i = gpd.read_file(
#     str(data_dir) + "/fires/North_America/North_America_vs1_2021.shp"
# )
# Displaying the first few rows of the GeoDataFrame
print(fire_i.head())

d02_domain = static_d02.salem.grid.to_geometry()
# d02_domain = d02_domain.to_crs(fire_i.crs)
# Finding the maximum x coordinate for each polygon
d02_domain["max_x"] = d02_domain["geometry"].apply(
    lambda poly: max([coord[0] for coord in poly.exterior.coords])
)

# Finding the maximum y coordinate for each polygon
d02_domain["max_y"] = d02_domain["geometry"].apply(
    lambda poly: max([coord[1] for coord in poly.exterior.coords])
)

# Define the bounds of North America
na_bounds = {
    "min_lon": d02_domain["max_x"].min(),
    "max_lon": d02_domain["max_x"].max(),
    "min_lat": d02_domain["max_y"].min(),
    "max_lat": d02_domain["max_y"].max(),
}


# Create a Polygon from the North America bounds
na_polygon = Polygon(
    [
        (na_bounds["min_lon"], na_bounds["min_lat"]),
        (na_bounds["min_lon"], na_bounds["max_lat"]),
        (na_bounds["max_lon"], na_bounds["max_lat"]),
        (na_bounds["max_lon"], na_bounds["min_lat"]),
        (na_bounds["min_lon"], na_bounds["min_lat"]),
    ]
)

fire_i_na = fire_i.to_crs(d02_domain.crs)

# Filter rows where the geometry is within the North American bounds
fire_i_na = fire_i_na[fire_i_na["geometry"].apply(lambda geom: geom.within(na_polygon))]


df = fire_i_na
df = df.reset_index()
# drop_index = []
# for i in range(len(fire_i)):
#     try:
#         static_d02["HGT"].salem.subset(
#             shape=df[i : i + 1], margin=1, all_touched=True
#         )
#     except:
#         print(df.iloc[i])
#         drop_index[i]
# df1 = df.drop(index=drop_index)

# static_d02["HGT"].salem.subset(shape=df[-2:-1], margin=20, all_touched=True)

# fire_i now contains only rows with geometries inside North America
print(df)
# df = df.to_crs(fire_i.crs)

# df.to_file(
#     str(data_dir) + f"/fires/North_America/North_America_vs1_{year}.shp",
#     driver="ESRI Shapefile",
# )
