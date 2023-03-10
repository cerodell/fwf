import context
import salem
import json

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
import matplotlib.pyplot as plt


from context import data_dir


"""
HR, TD, HU UU/VV, PR
HR      Relative humidity                                                       fraction
TT      Temperature                                                             °C
TD      Dew point temperature                                                   °C
HU      Specific humidity                                                       kg/kg
UU      U-component of the wind (along the X-axis of the grid)                  kts
VV      V-component of the wind (along the Y-axis of the grid)                  kts
PR      Quantity of precipitation                                               m
"""


ds = salem.open_metum_dataset(str(data_dir) + "/eccc/2022050100_006.nc")
# ds = xr.open_dataset(str(data_dir)+ "/eccc/test.grib2", engine="cfgrib")

proj = ds.attrs["pyproj_srs"]

x = [ds.lon.values[0, 0]]
y = [ds.lat.values[0, 0]]

d = {"lats": y, "lons": x}
df = pd.DataFrame(data=d)

gdf = gpd.GeoDataFrame(
    df,
    crs="EPSG:4326",
    geometry=gpd.points_from_xy(df["lons"], df["lats"]),
).to_crs(proj)
gdf["Easting"], gdf["Northing"] = gdf.geometry.x, gdf.geometry.y
gdf.head()


hrdps_grid = salem.Grid(
    nxny=(2540, 1290),
    dxdy=(0.0225, 0.0225),
    x0y0=(gdf["Easting"].values[0], gdf["Northing"].values[0]),
    proj=proj,
).to_dataset()

lon, lat = hrdps_grid.salem.grid.ll_coordinates


var = ds.TT.isel(time1=1, level=0)
hrdps_grid["2t"] = (("y", "x"), var.values)

hrdps_grid["2t"].attrs["pyproj_srs"] = hrdps_grid.attrs["pyproj_srs"]
hrdps_grid["2t"].salem.quick_map(cmap="coolwarm", extend="both")

hrdps_grid["lon"] = (("y", "x"), lon)
hrdps_grid["lat"] = (("y", "x"), lat)
hrdps_grid = hrdps_grid.set_coords(["lat", "lon"])


hrdps_grid.to_netcdf(str(data_dir) + "/eccc/hrdps_grid.nc")

# ds_check = salem.open_xr_dataset(str(data_dir)+ "/eccc/hrdps_grid.nc")
# ds_check["2t"].salem.quick_map(cmap='coolwarm',extend = 'both')
