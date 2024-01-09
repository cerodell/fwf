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

vars = ["F", "P", "D", "R", "U", "S", "T", "H", "W", "r_o"]
vars = ["T"]

##################################################################
##################### Open Data Files  ###########################
## open modle config file with varible names and attibutes
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

static_ds = salem.open_xr_dataset(
    (str(data_dir) + f"/static/static-vars-{model}-{domain}.nc")
)

try:
    ds = xr.open_dataset(
        str(data_dir) + f"/intercomp/{trail_name}/{model}/d03-20210101-20221231.nc",
    )
except:
    ds = xr.open_dataset(
        str(data_dir) + f"/intercomp/{trail_name}/{model}/20210101-20221231.nc",
    )
## make time dim sliceable with datetime
ds["time"] = ds["Time"]
wmo_idx = np.loadtxt(str(data_dir) + "/intercomp/02/wx_station.txt").astype(int)
ds = ds.sel(wmo=wmo_idx)

## make time dim sliceable with datetime
ds["time"] = ds["Time"]

ds_2021 = ds.sel(time=slice("2021-04-01", "2021-10-31"))
ds_2022 = ds.sel(time=slice("2022-04-01", "2022-10-31"))
null_ds = ds.sel(time=slice("2021-11-01", "2022-03-31"))
null_array = np.full(null_ds["temp"].shape, np.nan)
for var in null_ds:
    null_ds[var] = (("time", "domain", "wmo"), null_array)

ds_2021 = ds_2021.drop("Time")
ds_2022 = ds_2022.drop("Time")
null_ds = null_ds.drop("Time")

ds = xr.combine_nested([ds_2021, null_ds, ds_2022], concat_dim="time")
for var in ["elev", "name", "prov", "id", "domain"]:
    ds[var] = ds[var].astype(str)

##################################################################

for cord in ["elev", "name", "prov", "id"]:
    ds[cord] = ds[cord].astype(str)
ds["elev"] = ds["elev"].astype(float)
ds["elev"] = xr.where(ds["elev"] < 0, 0, ds["elev"])

for cord in ["elev", "name", "prov", "id"]:
    ds[cord] = ds[cord].astype(str)

ds = ds.chunk("auto")


ds_bias = ds.sel(domain="d03") - ds.sel(domain="obs")
# ds_bias = ds_bias.sel(time = slice("2021-04-01", "2021-05-01"))
ds_bias = ds_bias.mean(dim="time").compute()
ds_bias = ds_bias.dropna(dim="wmo", how="all")


df_wmo = {
    "wmo": ds_bias.wmo.values,
    "lats": ds_bias.lats.values,
    "lons": ds_bias.lons.values,
    "elev": ds_bias.elev.values.astype(float),
    "name": ds_bias.name.values,
    "tz_correct": ds_bias.tz_correct.values,
}
for name in list(ds_bias):
    df_wmo.update({name: ds_bias[name].values})

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

# Assuming 'column_name' is the name of the column you're interested in
column_name = "fwi"

# Calculate mean and standard deviation
mean_value = df_wmo[column_name].mean()
std_dev = df_wmo[column_name].std()

# Define a threshold based on two standard deviations
threshold = 2 * std_dev

# Filter rows where values are outside of two standard deviations
# df_wmo = df_wmo[(df_wmo[column_name] < mean_value - threshold) | (df_wmo[column_name] > mean_value + threshold)]
df_wmo = df_wmo[
    (df_wmo[column_name] >= mean_value - threshold)
    & (df_wmo[column_name] <= mean_value + threshold)
]

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


for var in vars:
    var_lower = cmaps[var]["name"].lower()
    title = cmaps[var]["title"]
    paper = cmaps[var]["paper"]

    vmin = paper["vmin"]
    vmax = paper["vmax"]
    cmap = paper["cmap"]
    df_wmo["var_lower_abs"] = df_wmo[var_lower].abs()
    if cmap == "coolwarm":
        cmap_plotly = "RdBu_r"
    else:
        cmap_plotly = cmap
    fig = px.scatter_mapbox(
        df_wmo,
        lat="lats",
        lon="lons",
        color=var_lower,
        size=f"elev_bias_abs",
        color_continuous_scale=cmap_plotly,
        hover_name="wmo",
        center={"lat": 59.0, "lon": -120.0},
        hover_data=["elev_bias", "elev", "elev_model", "name", "tz_correct", "wmo"],
        mapbox_style="carto-positron",
        range_color=[vmin, vmax],
        zoom=2.5,
        # labels={"colorbar": '2m Temperature Bias'}
    )
    fig.layout.coloraxis.colorbar.title = "Bias"
    # fig.update_layout(
    #     margin=dict(l=0, r=100, t=30, b=10),
    #     autosize=False,
    #     # width=700,
    #     # height=500,
    #     showlegend=False,
    # )
    fig.show()
    # fig.write_image(
    #     str(data_dir) + f"/images/paper/elev_bias/{var_lower}-{domain}-obs-map.pdf",
    #     scale=10,
    #     height=500,
    #     width=700,
    # )

    # # # ############ meter-based Lambert projection (EPSG:3347) ##########

    # var_bias = df_wmo[var_lower].values.astype(float)

    # # %%
    # fig = plt.figure(figsize=(8, 6))
    # ax = fig.add_subplot(1, 1, 1)
    # sc = ax.scatter(
    #     elev_model,
    #     obs_points,
    #     c=df_wmo[var_lower],
    #     vmin=vmin,
    #     vmax=vmax,
    #     cmap=cmap,
    # )
    # xpoints = ypoints = plt.xlim()
    # ax.plot(
    #     xpoints, ypoints, linestyle="--", color="k", lw=0.8, scalex=False, scaley=False
    # )
    # cbar = plt.colorbar(sc, ax=ax, pad=0.04)
    # # cbar.ax.tick_params(labelsize=10)
    # if var == "H":
    #     cbar.set_label(
    #         r"2-m Relative Humidity (\%)"
    #         + " Bias"
    #         + " \n Averaged from 01 April - 31 Oct (2021"
    #         + r"\&"
    #         + "2022) ",
    #         rotation=90,
    #         # fontsize=10,
    #         labelpad=15,
    #     )
    # if var == "T":
    #     cbar.set_label(
    #         r"2-m Temperature (C)"
    #         + " Bias"
    #         + " \n Averaged from 01 April - 31 Oct (2021"
    #         + r"\&"
    #         + "2022) ",
    #         rotation=90,
    #         # fontsize=10,
    #         labelpad=15,
    #     )
    # else:
    #     cbar.set_label(
    #         title
    #         + " Bias"
    #         + " \n Averaged from 01 April - 31 Oct (2021"
    #         + r"\&"
    #         + "2022) ",
    #         rotation=90,
    #         # fontsize=10,
    #         labelpad=15,
    #     )
    # ax.set_xlabel("Model Elevation (m)")
    # ax.set_ylabel("Station Elevation (m)")
    # # ax.set_title(
    # #     f"Weather Station Elevation vs Modeled Elevation \n at {len(x)} station locations"
    # # )
    # ax.set_title(
    #     f"Weather Station Elevation vs Modeled Elevation \n at 917 station locations"
    # )
    # from mpl_toolkits.axes_grid1.inset_locator import inset_axes, zoomed_inset_axes

    # # this is an inset axes over the main axes
    # axins = inset_axes(
    #     ax,
    #     width="30%",  # width = 30% of parent_bbox
    #     height="25%",  # height : 1 inch
    #     loc="upper left",
    # )
    # n, bins, patches = plt.hist(df_wmo[var_lower])
    # axins.yaxis.set_label_position("right")
    # axins.yaxis.tick_right()  # Move y-axis ticks and labels to the right
    # axins.set_xlabel(var_lower.upper(), fontsize=10)
    # axins.set_ylabel("Count", fontsize=10)
    # axins.tick_params(axis="both", which="minor", labelsize=10)

    # # plt.title('Probability')
    # # plt.xticks([])
    # # plt.yticks([])

    # plt.savefig(
    #     str(data_dir)
    #     + f"/images/paper/elev_bias/{var_lower}-{domain}-model-v-obs-elevation.png",
    #     dpi=250,
    #     bbox_inches="tight",
    # )
    # plt.savefig(
    #     str(data_dir)
    #     + f"/images/paper/elev_bias/{var_lower}-{domain}-model-v-obs-elevation.pdf",
    #     dpi=250,
    #     bbox_inches="tight",
    # )
    # # %%
