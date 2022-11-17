import context

import numpy as np
import xarray as xr
import geopandas as gpd
import pandas as pd


import salem

from netCDF4 import Dataset
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import plotly.express as px
from context import data_dir
from pykrige.ok import OrdinaryKriging
from pykrige.uk import UniversalKriging

from datetime import datetime

from utils.fwi import solve_ffmc


startTime = datetime.now()
domain = "d02"
var = "precip"
date = pd.Timestamp(2022, 7, 2)
doi = date.strftime("%Y%m%d")


fwf_ds = salem.open_xr_dataset(
    f"/Volumes/WFRT-Data02/FWF-WAN00CG/d02/WRF01/fwf/fwf-daily-d02-{doi}06.nc"
)

obs_ds = xr.open_zarr(
    str(data_dir) + "/intercomp/" + f"intercomp-{domain}-20220730.zarr",
)

fwf_ds = fwf_ds.isel(time=0)
obs_ds = obs_ds.sel(time=doi)
obs_df = obs_ds.to_dataframe()
obs_df = obs_df[~np.isnan(obs_df[var])]
obs_df = obs_df[np.abs(obs_df[var] - obs_df[var].mean()) <= (4 * obs_df[var].std())]
obs_df = obs_df.reset_index()
print(f"{len(obs_df)} number of observations")
fig = px.scatter_mapbox(
    obs_df,
    lat="lats",
    lon="lons",
    color="precip",
    size="precip",
    color_continuous_scale="jet",
    hover_name="wmo",
    # center={"lat": 50.0, "lon": -110.0},
    hover_data=["precip"],
    mapbox_style="carto-positron",
    zoom=3.0,
)
fig.update_layout(margin=dict(l=0, r=100, t=30, b=10))
fig.show()


fwf_ds.r_o.salem.quick_map()


obs_gdf = gpd.GeoDataFrame(
    obs_df,
    crs="EPSG:4326",
    geometry=gpd.points_from_xy(obs_df["lons"], obs_df["lats"]),
).to_crs(
    "+proj=stere +lat_0=90 +lat_ts=53.25 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs"
)
obs_gdf["Easting"], obs_gdf["Northing"] = obs_gdf.geometry.x, obs_gdf.geometry.y
obs_gdf.head()


y = xr.DataArray(
    np.array(obs_gdf["Northing"]),
    dims="wmo",
    coords=dict(wmo=obs_gdf.wmo.values),
)
x = xr.DataArray(
    np.array(obs_gdf["Easting"]),
    dims="wmo",
    coords=dict(wmo=obs_gdf.wmo.values),
)

var_points = fwf_ds["r_o"].interp(west_east=x, south_north=y, method="linear")
# print(var_points)
if len(obs_gdf.index) == len(var_points.values):
    var_points = var_points.values
else:
    raise ValueError("Lengths dont match")


nlags = 15
variogram_model = "spherical"
startTime = datetime.now()
krig = UniversalKriging(
    x=obs_gdf["Easting"],  ## x location of aq monitors in lambert conformal
    y=obs_gdf["Northing"],  ## y location of aq monitors in lambert conformal
    z=obs_gdf[var],  ## measured PM 2.5 concentrations at locations
    drift_terms=["specified"],
    variogram_model=variogram_model,
    nlags=nlags,
    specified_drift=[var_points],  ## BlueSky PM2.5 at aq monitors
)
print(f"UK build time {datetime.now() - startTime}")


startTime = datetime.now()
z, ss = krig.execute(
    "grid",
    fwf_ds.west_east.values,
    fwf_ds.south_north.values,
    specified_drift_arrays=[fwf_ds.r_o.values],
)
print(f"UK execution time {datetime.now() - startTime}")

r_o_k = np.where(z < 0, 0, z)

fwf_ds["r_o_k"] = (("south_north", "west_east"), r_o_k)
fwf_ds["r_o_diff"] = fwf_ds["r_o_k"] - fwf_ds["r_o"]
