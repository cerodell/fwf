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

import gstools as gs
from pykrige.ok import OrdinaryKriging
from pykrige.uk import UniversalKriging
from pykrige.rk import RegressionKriging
from sklearn.linear_model import LinearRegression
from scipy import stats

from utils.krig import plotvariogram

from datetime import datetime
from context import data_dir, root_dir

startTime = datetime.now()


##################################################################
##################### Define Inputs   ###########################

startTime = datetime.now()
model = "wrf"
domain = "d03"
var = "T"
var_range = [-6, 6]
date = pd.Timestamp("2021-02-13")
date = pd.Timestamp("2021-08-01")
trail_name = "02"
days = 6
krig_type = "uk"

##################################################################
##################### Open Data Files  ###########################

# date_range = pd.date_range("2022-07-15", "2022-07-20")
# # for date in date_range:
# test_ds = salem.open_xr_dataset(
#     f'/Volumes/WFRT-Ext24/fwf-data/{model}/{domain}/krig-bias-{krig_type}/fwf-krig-{domain}-{date.strftime("%Y%m%d")}.nc'
# )
# # fwf_ds = salem.open_xr_dataset(
# #     f"/Volumes/WFRT-Ext24/fwf-data/{model}/{domain}/{trail_name}/fwf-daily-{domain}-{date.strftime('%Y%m%d')}06.nc"
# # )
# fig = plt.figure(figsize=(12, 8))
# ax = fig.add_subplot(1, 1, 1)
# test_ds[f"{var}_bias"].salem.quick_map(
#     ax=ax,
#     cmap="coolwarm",
#     vmin=int(-3),
#     vmax=int(3),
#     extend="both",
#     prov=True,
#     states=True,
# )

# fig.savefig(
#     str(data_dir) + f'/images/{krig_type}-{date.strftime("%Y%m%d")}.png',
#     dpi=300,
#     bbox_inches="tight",
# )

# fig.savefig(
#     str(data_dir) + f'/images/{krig_type}-{date.strftime("%Y%m%d")}.png',
#     dpi=300,
#     bbox_inches="tight",
# )


# fwf_ds['T'].isel(time = 0).salem.quick_map()

# static_ds = xr.open_dataset((str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"))


# test = static_ds.ZoneDT.values
# test[test<1] = 99

ds = xr.open_dataset(
    str(data_dir) + f"/obs/observations-d02-20191231-20230521.nc",
    # chunks = 'auto'
)
# ds["time"] = ds["Time"]

for cord in ["elev", "name", "prov", "id"]:
    ds[cord] = ds[cord].astype(str)


df_wmo = {
    "wmo": ds.wmo.values,
    "lats": ds.lats.values,
    "lons": ds.lons.values,
    "elev": ds.elev.values.astype(float),
    "name": ds.name.values,
    "tz_correct": ds.tz_correct.values,
}
df_wmo = pd.DataFrame(df_wmo)

print(f"{len(df_wmo)} number of observations")
fig = px.scatter_mapbox(
    df_wmo,
    lat="lats",
    lon="lons",
    color="elev",
    # size=f"{var_lower}_bias_abs",
    color_continuous_scale="ylgnbu_r",
    hover_name="wmo",
    center={"lat": 58.0, "lon": -110.0},
    hover_data=["elev"],
    mapbox_style="carto-positron",
    # range_color=[-3, 3],
    zoom=1,
    # labels={"colorbar": '2m Temperature Bias'}
)
fig.layout.coloraxis.colorbar.title = "2m T Bias"
fig.update_layout(margin=dict(l=0, r=100, t=30, b=10))
fig.show()


ds = ds.chunk("auto")
## open modle config file with varible names and attibutes
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)
var_lower = cmaps[var]["name"].lower()


################## Time Averaged Dataset #########################
# index = np.isin(ds["prov"].values, ['BC'])

# ds = ds.isel(wmo=index)
##### Plot bias at each wxstation averaged over 7 day period #####

ds_tm = ds.sel(domain="d03")[var_lower] - ds.sel(domain="obs")[var_lower]
valid_data = date.strftime("%Y-%m-%d")
past_date = pd.to_datetime(str(date - np.timedelta64(days, "D"))).strftime("%Y-%m-%d")
ds_tm = ds_tm.sel(time=slice(past_date, valid_data)).mean(dim="time").to_dataset()

# ds_tm[var_lower] = (ds_tm[f"{var_lower}_wrf04"] - ds_tm[var_lower]).mean(
#     dim="time"
# )
# valid_data = pd.to_datetime(ds_tm.time.values[0]).strftime("%Y-%m-%d")
# past_date = pd.to_datetime(ds_tm.time.values[-1]).strftime("%Y-%m-%d")
## drop all wxstation that are nulled values
var_bias_tm = ds_tm[var_lower].dropna(dim="wmo")


## convert dataset to dataframe, ensure no null values exist and solve for mean bias
var_bias_tm_df = var_bias_tm.to_dataframe()
var_bias_tm_df = var_bias_tm_df[~np.isnan(var_bias_tm_df[var_lower])]
var_bias_tm_df = var_bias_tm_df[
    np.abs(var_bias_tm_df[var_lower] - var_bias_tm_df[var_lower].mean())
    <= (2 * var_bias_tm_df[var_lower].std())
]
var_bias_tm_df = var_bias_tm_df.reset_index()
var_bias_tm_df[f"{var_lower}_bias_abs"] = np.abs(var_bias_tm_df[var_lower])
# print(f"{len(var_bias_tm_df)} number of observations")
# fig = px.scatter_mapbox(
#     var_bias_tm_df,
#     lat="lats",
#     lon="lons",
#     color=var_lower,
#     title=f"2m Temperature Bias at {len(var_bias_tm_df)} station locations <br> averaged from {past_date} - {valid_data}",
#     # size=f"{var_lower}_bias_abs",
#     color_continuous_scale="RdBu_r",
#     hover_name="wmo",
# center={"lat": 58.0, "lon": -110.0},
#     hover_data=[var_lower, "elev"],
#     mapbox_style="carto-positron",
#     range_color=[-3, 3],
#     zoom=2.6,
#     # labels={"colorbar": '2m Temperature Bias'}
# )
# fig.layout.coloraxis.colorbar.title = "2m T Bias"
# fig.update_layout(margin=dict(l=0, r=100, t=30, b=10))
# fig.show()
# fig.write_image(
#     str(data_dir) + f'/images/{var_lower}-{domain}-obs-{date.strftime("%Y%m%d")}.png',
#     scale=6,
# )


smap = test_ds.salem.get_map()


fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1)
test_ds[f"{var}_bias"].salem.quick_map(
    ax=ax,
    cmap="coolwarm",
    vmin=int(-3),
    vmax=int(3),
    extend="both",
    prov=True,
    states=True,
)

# def transform_locs(lons, lats):
df = pd.DataFrame(
    data={
        "lons": ds_tm.lons.values,
        "lats": ds_tm.lats.values,
    }
)
pyproj_srs = test_ds.attrs["pyproj_srs"]
print(pyproj_srs)
locs = gpd.GeoDataFrame(
    df,
    crs="EPSG:4326",
    geometry=gpd.points_from_xy(df["lons"], df["lats"]),
).to_crs(pyproj_srs)
xx, yy = smap.grid.transform(
    locs.geometry.x, locs.geometry.y, crs=test_ds.salem.grid.proj
)
# return xx, yy

# xx, yy = transform_locs(ds_tm.lons.values, ds_tm.lats.values)
## plot wx stations locations
ax.scatter(
    xx,
    yy,
    c=ds_tm[var_lower].values,
    cmap="coolwarm",
    vmin=int(-3),
    vmax=int(3),
    zorder=10,
    alpha=1,
    s=10,
    label="WxStations",
)

fig.savefig(
    str(data_dir) + f'/images/test-{krig_type}-{date.strftime("%Y%m%d")}.png',
    dpi=300,
    bbox_inches="tight",
)

# ##################################################################
# ###################### Transfrom Data ############################
# ############ meter-based Lambert projection (EPSG:3347) ##########

# obs_gdf = gpd.GeoDataFrame(
#     var_bias_tm_df,
#     crs="EPSG:4326",
#     geometry=gpd.points_from_xy(var_bias_tm_df["lons"], var_bias_tm_df["lats"]),
# ).to_crs(
#     "+proj=stere +lat_0=90 +lat_ts=53.25 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs"
# )
# obs_gdf["Easting"], obs_gdf["Northing"] = obs_gdf.geometry.x, obs_gdf.geometry.y
# obs_gdf.head()

# gridx = fwf_ds.west_east.values
# gridy = fwf_ds.south_north.values


# #################################################################
# ##################### Regression Kriging #########################

# # lr_model = LinearRegression(normalize=True, copy_X=True, fit_intercept=False)

# y = xr.DataArray(
#     np.array(obs_gdf["Northing"]),
#     dims="ids",
#     coords=dict(ids=obs_gdf.id.values),
# )
# x = xr.DataArray(
#     np.array(obs_gdf["Easting"]),
#     dims="ids",
#     coords=dict(ids=obs_gdf.id.values),
# )
# static_ds["west_east"], static_ds["south_north"] = (
#     fwf_ds["west_east"],
#     fwf_ds["south_north"],
# )

# var_points = static_ds["HGT"].interp(west_east=x, south_north=y, method="nearest")
# # print(var_points)
# if len(obs_gdf.index) == len(var_points.values):
#     var_points = var_points.values
# else:
#     raise ValueError("Lengths dont match")


# # var_bias = obs_gdf[var_lower].values.astype(float)
# obs_points = obs_gdf[f"elev"].values.astype(float)
# # lats, lons = obs_gdf[f"lats"], obs_gdf[f"lons"]
# # regress = stats.linregress(var_points, var_bias)
# # trend = lambda x, y: regress.intercept + regress.slope * x
# fig = plt.figure(figsize=(8, 6))
# ax = fig.add_subplot(1, 1, 1)
# sc = ax.scatter(
#     var_points,
#     obs_points,
#     c=obs_gdf[var_lower],
#     vmin=-3,
#     vmax=3,
#     cmap="coolwarm",
# )
# xpoints = ypoints = plt.xlim()
# ax.plot(xpoints, ypoints, linestyle="--", color="k", lw=0.8, scalex=False, scaley=False)
# cbar = plt.colorbar(sc, ax=ax, pad=0.04)
# cbar.ax.tick_params(labelsize=10)
# cbar.set_label(
#     "2m Temperature Bias"
#     + r"($\mathrm{C})$"
#     + " \n averaged from 01 Jan 2021 - 01 Jan 2023 ",
#     rotation=90,
#     fontsize=10,
#     labelpad=15,
# )
# ax.set_xlabel("Model Elevation (m)")
# ax.set_ylabel("Station Elevation (m)")
# ax.set_title(
#     f"Weather Station Elevation vs Modeled Elevation \n at {len(x)} station locations"
# )
# plt.savefig(
#     str(data_dir) + f"/images/{var_lower}-{domain}-model-v-obs-elevation.png",
#     dpi=250,
#     bbox_inches="tight",
# )

# ##################################################################
# ###################### Universal Kriging #########################
# # nlags = 23
# # variogram_model = "spherical"
# # startTime = datetime.now()
# # krig = UniversalKriging(
# #     x=obs_gdf["Easting"],
# #     y=obs_gdf["Northing"],
# #     z=obs_gdf[var_lower],
# #     drift_terms=["specified"],
# #     variogram_model=variogram_model,
# #     # enable_statistics=True,
# #     # verbose=True,
# #     specified_drift=[obs_gdf["elev"]],
# #     nlags=nlags,
# # )
# # print(f"UK build time {datetime.now() - startTime}")
# # startTime = datetime.now()
# # z, ss = krig.execute(
# #     "grid", gridx, gridy, specified_drift_arrays=[static_ds.HGT.values]
# # )
# # print(f"UK execution time {datetime.now() - startTime}")

# # fwf_ds[f"{var}_bias_uk_obs_elev"] = (("south_north", "west_east"), z)
# # fwf_ds[f"{var}_bias_uk_obs_elev"].attrs["pyproj_srs"] = fwf_ds[var].attrs["pyproj_srs"]
# # fwf_ds[f"{var}_bias_uk_obs_elev"].salem.quick_map(
# #     cmap="coolwarm",
# #     vmin=int(var_range[0] / 2),
# #     vmax=int(var_range[-1] / 2),
# #     extend="both",
# # )


# nlags = 23
# variogram_model = "spherical"
# startTime = datetime.now()
# krig = UniversalKriging(
#     x=obs_gdf["Easting"],
#     y=obs_gdf["Northing"],
#     z=obs_gdf[var_lower],
#     drift_terms=["specified"],
#     variogram_model=variogram_model,
#     # enable_statistics=True,
#     # verbose=True,
#     specified_drift=[var_points],
#     nlags=nlags,
# )
# print(f"UK build time {datetime.now() - startTime}")
# startTime = datetime.now()
# z, ss = krig.execute(
#     "grid", gridx, gridy, specified_drift_arrays=[static_ds.HGT.values]
# )
# print(f"UK execution time {datetime.now() - startTime}")

# fwf_ds[f"{var}_bias_uk_mod_elev"] = (("south_north", "west_east"), z)
# fwf_ds[f"{var}_bias_uk_mod_elev"].attrs["pyproj_srs"] = fwf_ds[var].attrs["pyproj_srs"]
# fig = plt.figure(figsize=(8, 6))
# ax = fig.add_subplot(1, 1, 1)
# fwf_ds[f"{var}_bias_uk_mod_elev"].salem.quick_map(
#     cmap="coolwarm",
#     vmin=int(var_range[0] / 2),
#     vmax=int(var_range[-1] / 2),
#     extend="both",
#     ax=ax,
# )
# plt.savefig(
#     str(data_dir) + f"/images/{var_lower}-{domain}-uk-krig-model-elve.png",
#     dpi=250,
#     bbox_inches="tight",
# )


# # fwf_ds[f"{var}_bias_diff"] = fwf_ds[f"{var}_bias_uk_mod_elev"] - fwf_ds[f"{var}_bias_uk_obs_elev"]
# # fwf_ds[f"{var}_bias_diff"].attrs['pyproj_srs'] = fwf_ds[var].attrs['pyproj_srs']
# # fwf_ds[f"{var}_bias_diff"].salem.quick_map(cmap='coolwarm',vmin = int(-1), vmax = int(1), extend = 'both')


# # bias_diff = fwf_ds[f"{var}_bias_uk_mod_elev"].values.ravel()
# # terrain = static_ds.HGT.values.ravel()

# # fig = plt.figure(figsize=(8, 6))
# # ax = fig.add_subplot(1,1,1)
# # # sc = ax.scatter(bias_diff, terrain)
# # sc = ax.scatter(obs_points-var_points, obs_gdf['temp_bias'])

# # xpoints = ypoints = plt.xlim()
# # ax.plot(xpoints, ypoints, linestyle='--', color='k', lw=0.8, scalex=False, scaley=False)
# # cbar = plt.colorbar(sc, ax=ax, pad=0.04)
# # cbar.ax.tick_params(labelsize=10)
# # cbar.set_label(
# #     "2m Temperature Bias" + r"($\mathrm{C})$" + " \n averaged from 01 Jan 2021 - 01 Jan 2023 ",
# #     rotation=90,
# #     fontsize=10,
# #     labelpad=15,
# # )
# # ax.set_xlabel('Model Elevation (m)')
# # ax.set_ylabel('Station Elevation (m)')
# # ax.set_title(f"Weather Station Elevation vs Modeled Elevation \n at {len(x)} station locations")
# # plt.savefig(
# #     str(data_dir) + f'/images/{domain}-model-v-obs-elevation.png',
# #     dpi=250,
# #     bbox_inches="tight",
# # )

# ##################################################################
# ##################### Estimate Variogram #########################

# # y, x, field= obs_gdf['Northing'], obs_gdf['Easting'], obs_gdf[var_lower]

# # bins = gs.standard_bins((y,x), latlon=False)
# # bin_c, vario = gs.vario_estimate((y,x),field, bin_edges=bins, latlon=False)


# # model = gs.Spherical(latlon=False, dim = 2)
# # para, pcov, r2 = model.fit_variogram(bin_c, vario, nugget=False, return_r2=True)
# # # ax = model.plot(x_max=bin_c[-1])
# # # ax.scatter(bin_c, vario)
# # # ax.set_xlabel("great circle distance / radians")
# # # ax.set_ylabel("semi-variogram")
# # # fig = ax.get_figure()
# # # print(r2)
# # nlags = len(bin_c)
# # variogram_model = model


# ##################################################################
# ############### Ordinary Kriging with gs cov #####################
# # startTime = datetime.now()
# # krig = OrdinaryKriging(
# #     x=obs_gdf["Easting"],
# #     y=obs_gdf["Northing"],
# #     z=obs_gdf[var_lower],
# #     variogram_model=variogram_model,
# #     # enable_statistics=True,
# #     # verbose=True,
# #     nlags=nlags,
# # )
# # print(f"OK build time {datetime.now() - startTime}")
# # startTime = datetime.now()
# # z, ss = krig.execute("grid", gridx, gridy)
# # print(f"OK execution time {datetime.now() - startTime}")


# # fwf_ds[f"{var}_bias_ok_cov"] = (("south_north", "west_east"), z)
# # fwf_ds[f"{var}_bias_ok_cov"].attrs['pyproj_srs'] = fwf_ds[var].attrs['pyproj_srs']
# # fwf_ds[f"{var}_bias_ok_cov"].salem.quick_map(cmap='coolwarm',vmin = int(var_range[0]/2), vmax = int(var_range[-1]/2), extend = 'both')


# ##################################################################
# ###################### Ordinary Kriging #########################
# # nlags = 15
# # variogram_model = "spherical"

# # startTime = datetime.now()
# # krig = OrdinaryKriging(
# #     x=obs_gdf["Easting"],
# #     y=obs_gdf["Northing"],
# #     z=obs_gdf[var_lower],
# #     variogram_model=variogram_model,
# #     # enable_statistics=True,
# #     # verbose=True,
# #     nlags=nlags,
# # )
# # print(f"OK build time {datetime.now() - startTime}")
# # startTime = datetime.now()
# # z, ss = krig.execute("grid", gridx, gridy)
# # print(f"OK execution time {datetime.now() - startTime}")


# # fwf_ds[f"{var}_bias_ok"] = (("south_north", "west_east"), z)
# # fwf_ds[f"{var}_bias_ok"].attrs["pyproj_srs"] = fwf_ds[var].attrs["pyproj_srs"]
# # fwf_ds[f"{var}_bias_ok"].salem.quick_map(
# #     cmap="coolwarm",
# #     vmin=int(var_range[0] / 2),
# #     vmax=int(var_range[-1] / 2),
# #     extend="both",
# # )


# # fwf_ds[f"{var}_bias_ok_ok"] = fwf_ds[f"{var}_bias_ok_cov"] - fwf_ds[f"{var}_bias_ok"]
# # fwf_ds[f"{var}_bias_ok_ok"].attrs['pyproj_srs'] = fwf_ds[var].attrs['pyproj_srs']
# # fwf_ds[f"{var}_bias_ok_ok"].salem.quick_map(cmap='coolwarm',vmin = int(-1), vmax = int(1), extend = 'both')


# # fwf_ds["HGT"] = static_ds.HGT
# # fwf_ds["HGT"].attrs['pyproj_srs'] = fwf_ds[var].attrs['pyproj_srs']
# # fwf_ds["HGT"].salem.quick_map(cmap='terrain',extend = 'both')


# ##################################################################
# ################## Space Averaged Dataset ########################

# # ds_wm = ds.copy()[[var_lower,f'{var_lower}_wrf04']]

# # ds_wm = xr.open_dataset(
# #     str(data_dir) + f"/obs/observations-{domain}-20191231-20221231-old.nc",
# #     # chunks = 'auto'
# # )[[var_lower]]
# # wmo_count, wmo_bias = [], []

# # for i in range(len(ds_wm.time)):
# #     ds_i = ds_wm.isel(time = i).dropna(dim="wmo")
# #     # ds_i[f'{var_lower}_bias'] = (ds_i[var_lower] - ds_i[f'{var_lower}_wrf04']).mean(dim = 'wmo')
# #     # wmo_bias.append(float(ds_i[f'{var_lower}_bias'].values))
# #     wmo_count.append(len(ds_i.wmo))

# # # Create figure with secondary y-axis
# # fig = make_subplots(specs=[[{"secondary_y": True}]])
# # # Add traces
# # fig.add_trace(
# #     go.Scatter(x=ds_wm.time.values, y=wmo_count, name="WxStation Count"),
# #     secondary_y=False,
# # )
# # # fig.add_trace(
# # #     go.Scatter(x=ds_wm.Time.values, y=wmo_bias, name="Mean Bias"),
# # #     secondary_y=True,
# # # )
# # # Set x-axis title
# # fig.update_xaxes(title_text="DateTime")
# # # Set y-axes titles
# # fig.update_yaxes(title_text="<b>WxStation Count</b>", secondary_y=False)
# # fig.update_yaxes(title_text="<b>Mean Bias</b> (C)", secondary_y=True)
# # fig.show()


# # ds_wm[f'{var_lower}_bias'] = (ds_wm[var_lower] - ds_wm[f'{var_lower}_wrf04']).mean(dim = 'wmo')

# ## drop all wxstation that are nulled values
# # var_bias_wm = ds_wm[f'{var_lower}_bias'].dropna(dim="time")


# # var_bias_wm_df = var_bias_wm.to_dataframe()
# # var_bias_wm_df = var_bias_wm_df.reset_index()
# # fig = px.line(var_bias_wm_df, x="time", y=["temp_bias"])
# # fig.show()


# ##################################################################


# # ### OLD CODE IS BELOW THAT HAS UNIVERSAL KRIGING

# # # y, x, field= obs_gdf['Northing'], obs_gdf['Easting'], obs_gdf[var_lower]
# # y, x, field= obs_gdf['lats'], obs_gdf['lons'], obs_gdf[var_lower]


# # bins = np.arange(20)
# # bin_center, gamma = gs.vario_estimate((x, y), field, bins, latlon=True)

# # models = {
# #     "Gaussian": gs.Gaussian,
# #     "Exponential": gs.Exponential,
# #     "Matern": gs.Matern,
# #     "Stable": gs.Stable,
# #     "Rational": gs.Rational,
# #     "Circular": gs.Circular,
# #     "Spherical": gs.Spherical,
# #     "SuperSpherical": gs.SuperSpherical,
# #     "JBessel": gs.JBessel,
# # }
# # scores = {}

# # # plot the estimated variogram
# # plt.scatter(bin_center, gamma, color="k", label="data")
# # ax = plt.gca()

# # # fit all models to the estimated variogram
# # for model in models:
# #     fit_model = models[model](dim=2)
# #     para, pcov, r2 = fit_model.fit_variogram(bin_center, gamma, return_r2=True)
# #     fit_model.plot(x_max=40, ax=ax)
# #     scores[model] = r2


# # ranking = sorted(scores.items(), key=lambda item: item[1], reverse=True)
# # print("RANKING by Pseudo-r2 score")
# # for i, (model, score) in enumerate(ranking, 1):
# #     print(f"{i:>6}. {model:>15}: {score:.5}")

# # plt.show()


# # polygons, values = pixel2poly(gridx, gridy, z, 12_000)
# # pm25_model = gpd.GeoDataFrame(
# #     {"Modelled PM2.5": values}, geometry=polygons, crs="+proj=stere +lat_0=90 +lat_ts=53.25 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs"
# # ).to_crs("EPSG:4326")

# # fig = px.choropleth_mapbox(
# #     pm25_model,
# #     geojson=pm25_model.geometry,
# #     locations=pm25_model.index,
# #     color="Modelled PM2.5",
# #     color_continuous_scale="jet",
# #     center={"lat": 50.0, "lon": -110.0},
# #     zoom=2.5,
# #     mapbox_style="carto-positron",
# #     opacity=0.6,
# # )
# # fig.update_layout(margin=dict(l=0, r=0, t=30, b=10))
# # fig.update_traces(marker_line_width=0)
# # fig.show()


# ## define the desired grid resolution in meters
# # resolution = 12_000  # grid cell size in meters

# ## make grid based on dataset bounds and resolution
# # gridx = np.arange(obs_gdf.bounds.minx.min(), obs_gdf.bounds.maxx.max(), resolution)
# # gridy = np.arange(obs_gdf.bounds.miny.min(), obs_gdf.bounds.maxy.max(), resolution)
# # gridx = np.arange(fwf_ds.west_east.min(), fwf_ds.west_east.max(), resolution)
# # gridy = np.arange(fwf_ds.south_north.min(), fwf_ds.south_north.max(), resolution)

# # ## use salem to create a dataset with the grid.
# # krig_ds = salem.Grid(
# #     nxny=(len(gridx), len(gridy)),
# #     dxdy=(resolution, resolution),
# #     x0y0=(fwf_ds.west_east.min()-resolution, fwf_ds.south_north.min()-resolution),
# #     proj="+proj=stere +lat_0=90 +lat_ts=53.25 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs",
# #     pixel_ref="corner",
# # ).to_dataset()
# # ## print dataset
# # krig_ds


# # y = xr.DataArray(
# #     np.array(obs_gdf["Northing"]),
# #     dims="wmo",
# #     coords=dict(wmo=obs_gdf.wmo.values),
# # )
# # x = xr.DataArray(
# #     np.array(obs_gdf["Easting"]),
# #     dims="wmo",
# #     coords=dict(wmo=obs_gdf.wmo.values),
# # )

# # var_points = fwf_ds["r_o"].interp(west_east=x, south_north=y, method="linear")
# # # print(var_points)
# # if len(obs_gdf.index) == len(var_points.values):
# #     var_points = var_points.values
# # else:
# #     raise ValueError("Lengths dont match")


# # nlags = 15
# # variogram_model = "spherical"
# # startTime = datetime.now()
# # krig = UniversalKriging(
# #     x=obs_gdf["Easting"],  ## x location of aq monitors in lambert conformal
# #     y=obs_gdf["Northing"],  ## y location of aq monitors in lambert conformal
# #     z=obs_gdf[var],  ## measured PM 2.5 concentrations at locations
# #     drift_terms=["specified"],
# #     variogram_model=variogram_model,
# #     nlags=nlags,
# #     # specified_drift=[var_points],
# # )
# # print(f"UK build time {datetime.now() - startTime}")


# # startTime = datetime.now()
# # z, ss = krig.execute(
# #     "grid",
# #     fwf_ds.west_east.values,
# #     fwf_ds.south_north.values,
# #     specified_drift_arrays=[fwf_ds.r_o.values],
# # )
# # print(f"UK execution time {datetime.now() - startTime}")

# # r_o_k = np.where(z < 0, 0, z)

# # fwf_ds["r_o_k"] = (("south_north", "west_east"), r_o_k)
# # fwf_ds["r_o_diff"] = fwf_ds["r_o_k"] - fwf_ds["r_o"]


# ##### REGRESION KRIGING

# # fig = plt.figure(figsize=(8, 6))
# # ax = fig.add_subplot(1,1,1)
# # ax.scatter(var_points-obs_points, obs_gdf['temp_bias'])
# # r2value = np.round(
# #     stats.pearsonr(var_points-obs_points, obs_gdf['temp_bias']), 2
# #     )

# # ax.set_xlabel('Model Elevation (m)')
# # ax.set_ylabel('Station Elevation (m)')
# # ax.set_title(f"Weather Station Elevation vs Modeled Elevation \n at {len(x)} station locations")


# # plt.plot(
# #     var_points, regress.intercept + regress.slope * var_points, "r", label="fitted line"
# # )
# # plt.legend()
# # plt.show()


# # bins = gs.standard_bins((lats, lons), max_dist=np.deg2rad(8), latlon=True)
# # bin_c, vario = gs.vario_estimate((lats, lons), var_bias, bin_edges=bins, latlon=True)

# # model = gs.Spherical(latlon=True, rescale=gs.EARTH_RADIUS)
# # para, pcov, r2 = model.fit_variogram(bin_c, vario, nugget=False, return_r2=True)
# # ax = model.plot(x_max=bin_c[-1])
# # ax.scatter(bin_c, vario)
# # ax.set_xlabel("great circle distance / radians")
# # ax.set_ylabel("semi-variogram")
# # fig = ax.get_figure()
# # # fig.savefig(os.path.join("..", "results", "variogram.pdf"), dpi=300)
# # print(r2)

# # startTime = datetime.now()
# # krig = RegressionKriging(
# #     x=obs_gdf["Easting"],
# #     y=obs_gdf["Northing"],
# #     z=obs_gdf[var_lower],
# #     variogram_model=variogram_model,
# #     # enable_statistics=True,
# #     # verbose=True,
# #     nlags=nlags,
# # )
# # print(f"OK build time {datetime.now() - startTime}")
# # startTime = datetime.now()
# # z, ss = krig.execute("grid", gridx, gridy)
# # print(f"OK execution time {datetime.now() - startTime}")
