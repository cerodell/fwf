#!/Users/crodell/miniconda3/envs/fwf/bin/python

import context
import salem
import json

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

# import gstools as gs
# from pykrige.ok import OrdinaryKriging
# from pykrige.uk import UniversalKriging
# from pykrige.rk import RegressionKriging
from sklearn.linear_model import LinearRegression
from scipy import stats

from utils.krig import plotvariogram

from datetime import datetime
from context import data_dir, root_dir
import matplotlib

startTime = datetime.now()
matplotlib.rcParams.update({"font.size": 14})
plt.rc("font", family="sans-serif")
plt.rc("text", usetex=True)

##################################################################
##################### Define Inputs   ###########################

startTime = datetime.now()
model = "wrf"
domain = "d02"
var = "F"
trail_name = "02"


##################################################################
##################### Open Data Files  ###########################
## open modle config file with varible names and attibutes
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

static_ds = salem.open_xr_dataset(
    (str(data_dir) + f"/static/static-vars-{model}-{domain}.nc")
)

ds_old = xr.open_dataset(
    str(data_dir) + f"/intercomp/04/wrf/d03-20210101-20221231.nc",
)

ds_old = xr.open_dataset(
    str(data_dir) + f"/intercomp/04/wrf/d03-20210301-20231101.nc",
)


## make time dim sliceable with datetime
ds_old["time"] = ds_old["Time"]
wmo_idx = np.loadtxt(str(data_dir) + "/intercomp/02/wx_station.txt").astype(int)
ds_old = ds_old.sel(wmo=wmo_idx)

## make time dim sliceable with datetime
ds_old["time"] = ds_old["Time"]


df_wmo = {
    "wmo": ds_old.wmo.values,
    "lats": ds_old.lats.values,
    "lons": ds_old.lons.values,
    "elev": ds_old.elev.values.astype(float),
    "name": ds_old.name.values,
    "tz_correct": ds_old.tz_correct.values,
}


df_wmo = pd.DataFrame(df_wmo)
df_wmo = gpd.GeoDataFrame(
    df_wmo,
    crs="EPSG:4326",
    geometry=gpd.points_from_xy(df_wmo["lons"], df_wmo["lats"]),
).to_crs(
    "+proj=stere +lat_0=90 +lat_ts=53.25 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs"
)
df_wmo["Easting"], df_wmo["Northing"] = df_wmo.geometry.x, df_wmo.geometry.y
df_wmo.head()


# df_wmo['wmo'].to_csv('your_data.txt', index=False, header=False)

gridx = static_ds.west_east.values
gridy = static_ds.south_north.values

y = xr.DataArray(
    np.array(df_wmo["Northing"]),
    dims="ids",
    coords=dict(ids=df_wmo.wmo.values),
)
x = xr.DataArray(
    np.array(df_wmo["Easting"]),
    dims="ids",
    coords=dict(ids=df_wmo.wmo.values),
)

elev_model = static_ds["HGT"].interp(west_east=x, south_north=y, method="nearest")
if len(df_wmo.index) == len(elev_model.values):
    elev_model = elev_model.values
else:
    raise ValueError("Lengths dont match")
obs_points = df_wmo[f"elev"].values.astype(float)
df_wmo["elev_model"] = elev_model
df_wmo["elev_bias"] = df_wmo["elev_model"] - df_wmo["elev"]
df_wmo["elev_bias_abs"] = df_wmo["elev_bias"].abs()
print(f"{len(df_wmo)} number of observations")


fig = px.scatter_mapbox(
    df_wmo,
    lat="lats",
    lon="lons",
    # color=var_lower,
    # size=f"elev_bias_abs",
    # color_continuous_scale=cmap_plotly,
    hover_name="wmo",
    center={"lat": 59.0, "lon": -120.0},
    hover_data=["elev_bias", "elev", "elev_model", "name", "tz_correct", "wmo"],
    mapbox_style="carto-positron",
    # range_color=[vmin, vmax],
    zoom=2.5,
    # labels={"colorbar": '2m Temperature Bias'}
)
fig.layout.coloraxis.colorbar.title = "Bias"

fig.show()
