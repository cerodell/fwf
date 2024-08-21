#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import cartopy.crs as crs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
from utils.ml_data import MLDATA
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler


from scipy import stats
from utils.stats import MBE, RMSE
from sklearn.metrics import r2_score
from datetime import datetime
from context import data_dir

from netCDF4 import Dataset
from wrf import to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ll_to_xy, xy_to_ll


# Mark the start time for the run
startTime = datetime.now()


all_fire = True
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense"
method = "averaged-v14"
ml_pack = "tf"
target_vars = "FRP"
model_dir = str(data_dir) + f"/mlp/{ml_pack}/{method}/{target_vars}/{mlp_test_case}"

with open(f"{model_dir}/config.json", "r") as json_data:
    config = json.load(json_data)["user_config"]

fire_cases = np.loadtxt(f"{model_dir}/test_cases.txt", delimiter=",")
test_ids = fire_cases[0].astype(int)

mlD = MLDATA(config=config)
df = mlD.open_ml_ds()
df_test = df[df["id"].isin(test_ids)].reset_index()

X = df_test[config["feature_vars"]]

# Load the scaler
scaler = joblib.load(f"{model_dir}/feature-scaler.joblib")
X_new_scaled = scaler.transform(X)

# Load the model
model = load_model(f"{model_dir}/model.keras")

startFRP = datetime.now()
# print("Start prediction:", startFRP)
y_out_this_nhn = model(X_new_scaled).numpy()
if config["target_scaler_type"] != None:
    y_out_this_nhn = y_out_this_nhn * config["FRP_MAX"]
if config["transform"] == True:
    y_out_this_nhn = np.expm1(y_out_this_nhn)
    df_test["FRP"] = np.expm1(df_test["FRP"])

# FRP_FULL = y_out_this_nhn.ravel().reshape(shape)
FRP_FULL = y_out_this_nhn.ravel()
df_test["MODELED_FRP"] = FRP_FULL


# Open the NetCDF file
ncfile = Dataset(str(data_dir) + f"/wrf/wrfout_d01_2023-04-20_00:00:00")
# Get the sea level pressure
slp = getvar(ncfile, "slp")
# Get the cartopy mapping object
cart_proj = get_cartopy(slp)


## bring in state/prov boundaries
states_provinces = cfeature.NaturalEarthFeature(
    category="cultural",
    name="admin_1_states_provinces_shp",
    scale="50m",
    facecolor="none",
)


# %%
matplotlib.rcParams.update({"font.size": 22})
plt.rc("font", family="sans-serif")
plt.rc("text", usetex=True)


df_group = df_test.groupby("id").first().reset_index()
# scaler = MinMaxScaler(feature_range=(10, 400))
# burn_time = scaler.fit_transform(
#     np.array(df_group["burn_time"].values).reshape(-1, 1)
# ).flatten()
# df_group["scaled_burn_time"] = burn_time

lat, lon, pearson_r, mbe, rmse, r_square, id_list, year_list = (
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
)

ISI_pearson_r, area_ha, burn_time = [], [], []
for ID, group in df_test.groupby("id"):
    lat.append(float(group["lats"].iloc[0]))
    lon.append(float(group["lons"].iloc[0]))
    id_list.append(int(group["id"].iloc[0]))
    area_ha.append(int(group["area_ha"].iloc[0]))
    year_list.append(int(group["time"].dt.year.iloc[0]))
    burn_time.append(len(group["FRP"]))
    pearson_r.append(np.round(stats.pearsonr(group["FRP"], group["MODELED_FRP"])[0], 2))
    mbe.append(np.round(MBE(group["FRP"], group["MODELED_FRP"]), 2))
    rmse.append(np.round(RMSE(group["FRP"], group["MODELED_FRP"]), 2))
    r_square.append(np.round(r2_score(group["FRP"], group["MODELED_FRP"]), 2))
    ISI_pearson_r.append(np.round(stats.pearsonr(group["FRP"], group["R"])[0], 2))


scaler = joblib.load(f"dot-scaler.joblib")
df_group["burn_time"] = burn_time
burn_time = scaler.fit_transform(
    np.array(df_group["burn_time"].values).reshape(-1, 1)
).flatten()
df_group["scaled_burn_time"] = burn_time

############################################################################
########################     Pearson's r        ############################
############################################################################

# %%
# # Create a figure
# fig = plt.figure(figsize=(18, 12))
# # Set the GeoAxes to the projection used by WRF
# ax = fig.add_subplot(2, 2, 1, projection=cart_proj)

# ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
# ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
# ax.coastlines("50m", linewidth=0.8, zorder=5)

# ## plot wx stations locations
# sc = ax.scatter(
#     lon,
#     lat,
#     c=pearson_r,
#     cmap="PRGn",
#     vmin=-1,
#     vmax=1,
#     edgecolor="k",
#     lw=0.3,
#     zorder=10,
#     alpha=1,
#     s=burn_time,
#     transform=crs.PlateCarree(),
# )

# # Add a colorbar
# cbar = plt.colorbar(sc, ax=ax, orientation="vertical", label="Value", pad=0.01)
# cbar.set_label("r", rotation=90)

# # Add the gridlines
# # Customize the gridlines
# gl = ax.gridlines(
#     draw_labels=False, linewidth=0.1, color="gray", alpha=1, linestyle="--"
# )

# gl.top_labels = False
# gl.left_labels = False
# # gl.xlines = False
# gl.xlocator = mticker.FixedLocator([-180, -160, -140, -120, -100, -80, -60, -40])
# gl.ylocator = mticker.FixedLocator([30, 40, 50, 60, 70])

# gl.xformatter = LONGITUDE_FORMATTER
# gl.yformatter = LATITUDE_FORMATTER

# plt.tight_layout()

# ax.set_title(f"Pearson's r")


############################################################################
############################       MBE        ##############################
############################################################################

# # Create a figure
# # fig = plt.figure(figsize=(14, 8))
# # Set the GeoAxes to the projection used by WRF
# ax = fig.add_subplot(2, 2, 4, projection=cart_proj)

# ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
# ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
# ax.coastlines("50m", linewidth=0.8, zorder=5)

# vmin = np.percentile(mbe, 5)
# vmax = np.percentile(mbe, 97)
# vm = abs(vmax - abs(vmin))
# ## plot wx stations locations
# sc = ax.scatter(
#     lon,
#     lat,
#     c=mbe,
#     cmap="coolwarm",
#     vmin=-vm,
#     vmax=vm,
#     edgecolor="k",
#     lw=0.3,
#     zorder=10,
#     alpha=1,
#     s=burn_time,
#     transform=crs.PlateCarree(),
# )

# # Add a colorbar
# cbar = plt.colorbar(sc, ax=ax, orientation="vertical", label="Value", pad=0.01)
# cbar.set_label("MW", rotation=90)

# # Add the gridlines
# # Customize the gridlines
# gl = ax.gridlines(
#     draw_labels=False, linewidth=0.1, color="gray", alpha=1, linestyle="--"
# )

# gl.top_labels = False
# gl.left_labels = False
# # gl.xlines = False
# gl.xlocator = mticker.FixedLocator([-180, -160, -140, -120, -100, -80, -60, -40])
# gl.ylocator = mticker.FixedLocator([30, 40, 50, 60, 70])

# gl.xformatter = LONGITUDE_FORMATTER
# gl.yformatter = LATITUDE_FORMATTER

# plt.tight_layout()

# ax.set_title(f"Mean Bias Error")

# # # save as png
# # fig.savefig(
# #     str(data_dir) + f"/images/frp-paper/map-mbe-{method}.png",
# #     bbox_inches="tight",
# #     dpi=240,
# # )

# ############################################################################
# ############################       RMSE       ##############################
# ############################################################################
# # Create a figure
# # fig = plt.figure(figsize=(14, 8))
# # Set the GeoAxes to the projection used by WRF
# ax = fig.add_subplot(2, 2, 3, projection=cart_proj)

# ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
# ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
# ax.coastlines("50m", linewidth=0.8, zorder=5)

# vmin = np.percentile(rmse, 5)
# vmax = np.percentile(rmse, 97)
# ## plot wx stations locations
# sc = ax.scatter(
#     lon,
#     lat,
#     c=rmse,
#     vmin=0,
#     vmax=vmax,
#     cmap="OrRd",
#     edgecolor="k",
#     lw=0.3,
#     zorder=10,
#     alpha=1,
#     s=burn_time,
#     transform=crs.PlateCarree(),
# )

# # Add a colorbar
# cbar = plt.colorbar(sc, ax=ax, orientation="vertical", label="Value", pad=0.01)
# cbar.set_label("MW", rotation=90)

# # Add the gridlines
# # Customize the gridlines
# gl = ax.gridlines(
#     draw_labels=False, linewidth=0.1, color="gray", alpha=1, linestyle="--"
# )

# gl.top_labels = False
# gl.left_labels = False
# # gl.xlines = False
# gl.xlocator = mticker.FixedLocator([-180, -160, -140, -120, -100, -80, -60, -40])
# gl.ylocator = mticker.FixedLocator([30, 40, 50, 60, 70])

# gl.xformatter = LONGITUDE_FORMATTER
# gl.yformatter = LATITUDE_FORMATTER

# plt.tight_layout()

# ax.set_title(f"Root Mean Square Error")

# # save as png
# # fig.savefig(
# #     str(data_dir) + f"/images/frp-paper/map-rmse-{method}.png",
# #     bbox_inches="tight",
# #     dpi=240,
# # )


# ############################################################################
# ##########################     R Square        #############################
# ############################################################################

# # Create a figure
# # fig = plt.figure(figsize=(14, 8))
# # Set the GeoAxes to the projection used by WRF
# ax = fig.add_subplot(2, 2, 2, projection=cart_proj)

# ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
# ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
# ax.coastlines("50m", linewidth=0.8, zorder=5)

# ## plot wx stations locations
# sc = ax.scatter(
#     lon,
#     lat,
#     c=r_square,
#     vmin=0,
#     vmax=1,
#     cmap="YlGn",
#     edgecolor="k",
#     lw=0.3,
#     zorder=10,
#     alpha=1,
#     s=burn_time,
#     transform=crs.PlateCarree(),
# )

# # Add a colorbar
# cbar = plt.colorbar(sc, ax=ax, orientation="vertical", label=r"$R^{2}$", pad=0.01)
# # cbar.set_label("MW", rotation=90)

# # Add the gridlines
# # Customize the gridlines
# gl = ax.gridlines(
#     draw_labels=False, linewidth=0.1, color="gray", alpha=1, linestyle="--"
# )

# gl.top_labels = False
# gl.left_labels = False
# # gl.xlines = False
# gl.xlocator = mticker.FixedLocator([-180, -160, -140, -120, -100, -80, -60, -40])
# gl.ylocator = mticker.FixedLocator([30, 40, 50, 60, 70])

# gl.xformatter = LONGITUDE_FORMATTER
# gl.yformatter = LATITUDE_FORMATTER

# ax.set_title(f"R Squared")

# # Create a second legend for the sizes
# size_values_invers = np.array([  30. ,  503. , 1003.5])
# # Calculate the range for obs_hours
# min_obs_hours = int(size_values_invers[0])
# median_obs_hours = int(size_values_invers[1])
# max_obs_hours = int(size_values_invers[2])

# # Create a second legend for the sizes
# size_values = [10, 96, 187]
# size_labels = ['30 - 499 h', '500 - 999 h', r'$>=$ 1000 h']
# size_legend = [plt.scatter([], [], s=size, lw=0.4, color='gray', edgecolor='k') for size in size_values]

# # Add the global legend
# fig.legend(size_legend, size_labels, title='Observation Hours', loc='upper center', bbox_to_anchor=(0.5, 1.08), ncol=3)


# plt.tight_layout()

# #
# ## save as png
# fig.savefig(
#     str(data_dir) + f"/images/frp-paper/map-stats-{method}.png",
#     bbox_inches="tight",
#     dpi=240,
# )

# %%
df_plotly = pd.DataFrame(
    dict(
        lat=lat,
        lon=lon,
        pearson_r=pearson_r,
        mbe=mbe,
        rmse=rmse,
        r_square=r_square,
        id=id_list,
        burn_time=burn_time,
        ISI_pearson_r=ISI_pearson_r,
        area_ha=area_ha,
        # area_ha_scaled=area_ha_scaled,
        year=year_list,
    )
)


plt.scatter(burn_time, pearson_r)

pearson_r = np.array(pearson_r)
import plotly.express as px

fig = px.scatter_mapbox(
    df_plotly,
    lat="lat",
    lon="lon",
    color="r_square",
    size=f"burn_time",
    color_continuous_scale="RdBu_r",
    hover_name="id",
    center={"lat": 58.0, "lon": -110.0},
    hover_data=[
        "id",
        "pearson_r",
        "mbe",
        "rmse",
        "r_square",
        "burn_time",
        "area_ha",
        "year",
    ],
    mapbox_style="carto-positron",
    range_color=[-1, 1],
    zoom=1,
    # labels={"colorbar": '2m Temperature Bias'}
)
fig.layout.coloraxis.colorbar.title = "pearson_r"
fig.update_layout(margin=dict(l=0, r=100, t=30, b=10))
fig.show()

# %%
