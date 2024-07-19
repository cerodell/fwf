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
method = "averaged-v12"
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
scaler = MinMaxScaler(feature_range=(10, 400))
burn_time = scaler.fit_transform(
    np.array(df_group["burn_time"].values).reshape(-1, 1)
).flatten()
df_group["scaled_burn_time"] = burn_time

lat, lon, pearson_r, mbe, rmse, r_square, id_list, = (
    [],
    [],
    [],
    [],
    [],
    [],
    [],
)

ISI_pearson_r, area_ha = [], []
for ID, group in df_test.groupby("id"):
    lat.append(float(group["lats"].iloc[0]))
    lon.append(float(group["lons"].iloc[0]))
    id_list.append(int(group["id"].iloc[0]))
    area_ha.append(int(group["area_ha"].iloc[0]))
    pearson_r.append(np.round(stats.pearsonr(group["FRP"], group["MODELED_FRP"])[0], 2))
    mbe.append(np.round(MBE(group["FRP"], group["MODELED_FRP"]), 2))
    rmse.append(np.round(RMSE(group["FRP"], group["MODELED_FRP"]), 2))
    r_square.append(np.round(r2_score(group["FRP"], group["MODELED_FRP"]), 2))
    ISI_pearson_r.append(np.round(stats.pearsonr(group["FRP"], group["R"])[0], 2))

scaler = MinMaxScaler(feature_range=(10, 400))
area_ha_scaled = scaler.fit_transform(
    np.array(df_group["area_ha"].values).reshape(-1, 1)
).flatten()


############################################################################
########################     Pearson's r        ############################
############################################################################

# Create a figure
fig = plt.figure(figsize=(14, 8))
# Set the GeoAxes to the projection used by WRF
ax = plt.axes(projection=cart_proj)

ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
ax.coastlines("50m", linewidth=0.8, zorder=5)

## plot wx stations locations
sc = ax.scatter(
    lon,
    lat,
    c=pearson_r,
    cmap="PRGn",
    vmin=-1,
    vmax=1,
    edgecolor="k",
    lw=0.5,
    zorder=10,
    alpha=1,
    s=burn_time,
    transform=crs.PlateCarree(),
)

# Add a colorbar
cbar = plt.colorbar(sc, ax=ax, orientation="vertical", label="Value", pad=0.01)
cbar.set_label("r", rotation=90)

# Add the gridlines
# Customize the gridlines
gl = ax.gridlines(
    draw_labels=False, linewidth=0.1, color="gray", alpha=1, linestyle="--"
)

gl.top_labels = False
gl.left_labels = False
# gl.xlines = False
gl.xlocator = mticker.FixedLocator([-180, -160, -140, -120, -100, -80, -60, -40])
gl.ylocator = mticker.FixedLocator([30, 40, 50, 60, 70])

gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER

plt.tight_layout()

ax.set_title(f"Pearson's r \n {len(lon)} Wildfire Test Cases")

# save as png
fig.savefig(
    str(data_dir) + f"/images/frp-paper/map-pearsonr-{method}.png",
    bbox_inches="tight",
    dpi=240,
)

############################################################################
############################       MBE        ##############################
############################################################################

# Create a figure
fig = plt.figure(figsize=(14, 8))
# Set the GeoAxes to the projection used by WRF
ax = plt.axes(projection=cart_proj)

ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
ax.coastlines("50m", linewidth=0.8, zorder=5)

vmin = np.percentile(mbe, 5)
vmax = np.percentile(mbe, 95)
vm = abs(vmax - abs(vmin))
## plot wx stations locations
sc = ax.scatter(
    lon,
    lat,
    c=mbe,
    cmap="coolwarm",
    vmin=-vm,
    vmax=vm,
    edgecolor="k",
    lw=0.5,
    zorder=10,
    alpha=1,
    s=burn_time,
    transform=crs.PlateCarree(),
)

# Add a colorbar
cbar = plt.colorbar(sc, ax=ax, orientation="vertical", label="Value", pad=0.01)
cbar.set_label("MW", rotation=90)

# Add the gridlines
# Customize the gridlines
gl = ax.gridlines(
    draw_labels=False, linewidth=0.1, color="gray", alpha=1, linestyle="--"
)

gl.top_labels = False
gl.left_labels = False
# gl.xlines = False
gl.xlocator = mticker.FixedLocator([-180, -160, -140, -120, -100, -80, -60, -40])
gl.ylocator = mticker.FixedLocator([30, 40, 50, 60, 70])

gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER

plt.tight_layout()

ax.set_title(f"Mean Bias Error \n {len(lon)} Wildfire Test Cases")

# save as png
fig.savefig(
    str(data_dir) + f"/images/frp-paper/map-mbe-{method}.png",
    bbox_inches="tight",
    dpi=240,
)

############################################################################
############################       RMSE       ##############################
############################################################################
# Create a figure
fig = plt.figure(figsize=(14, 8))
# Set the GeoAxes to the projection used by WRF
ax = plt.axes(projection=cart_proj)

ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
ax.coastlines("50m", linewidth=0.8, zorder=5)

vmin = np.percentile(rmse, 5)
vmax = np.percentile(rmse, 95)
## plot wx stations locations
sc = ax.scatter(
    lon,
    lat,
    c=rmse,
    vmin=0,
    vmax=vmax,
    cmap="OrRd",
    edgecolor="k",
    lw=0.5,
    zorder=10,
    alpha=1,
    s=burn_time,
    transform=crs.PlateCarree(),
)

# Add a colorbar
cbar = plt.colorbar(sc, ax=ax, orientation="vertical", label="Value", pad=0.01)
cbar.set_label("MW", rotation=90)

# Add the gridlines
# Customize the gridlines
gl = ax.gridlines(
    draw_labels=False, linewidth=0.1, color="gray", alpha=1, linestyle="--"
)

gl.top_labels = False
gl.left_labels = False
# gl.xlines = False
gl.xlocator = mticker.FixedLocator([-180, -160, -140, -120, -100, -80, -60, -40])
gl.ylocator = mticker.FixedLocator([30, 40, 50, 60, 70])

gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER

plt.tight_layout()

ax.set_title(f"Root Mean Square Error \n {len(lon)} Wildfire Test Cases")

# save as png
fig.savefig(
    str(data_dir) + f"/images/frp-paper/map-rmse-{method}.png",
    bbox_inches="tight",
    dpi=240,
)


############################################################################
##########################     R Square        #############################
############################################################################

# Create a figure
fig = plt.figure(figsize=(14, 8))
# Set the GeoAxes to the projection used by WRF
ax = plt.axes(projection=cart_proj)

ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
ax.coastlines("50m", linewidth=0.8, zorder=5)

vmin = np.percentile(r_square, 5)
vmax = np.percentile(r_square, 95)
## plot wx stations locations
sc = ax.scatter(
    lon,
    lat,
    c=r_square,
    vmin=0,
    vmax=1,
    cmap="YlGn",
    edgecolor="k",
    lw=0.5,
    zorder=10,
    alpha=1,
    s=burn_time,
    transform=crs.PlateCarree(),
)

# Add a colorbar
cbar = plt.colorbar(sc, ax=ax, orientation="vertical", label="Value", pad=0.01)
# cbar.set_label("MW", rotation=90)

# Add the gridlines
# Customize the gridlines
gl = ax.gridlines(
    draw_labels=False, linewidth=0.1, color="gray", alpha=1, linestyle="--"
)

gl.top_labels = False
gl.left_labels = False
# gl.xlines = False
gl.xlocator = mticker.FixedLocator([-180, -160, -140, -120, -100, -80, -60, -40])
gl.ylocator = mticker.FixedLocator([30, 40, 50, 60, 70])

gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER

plt.tight_layout()

ax.set_title(f"R Squared \n {len(lon)} Wildfire Test Cases")

# save as png
fig.savefig(
    str(data_dir) + f"/images/frp-paper/map-r_square-{method}.png",
    bbox_inches="tight",
    dpi=240,
)


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
        area_ha_scaled=area_ha_scaled,
    )
)


plt.scatter(burn_time, pearson_r)

pearson_r = np.array(pearson_r)
import plotly.express as px

fig = px.scatter_mapbox(
    df_plotly,
    lat="lat",
    lon="lon",
    color="ISI_pearson_r",
    size=f"area_ha_scaled",
    color_continuous_scale="RdBu_r",
    hover_name="id",
    center={"lat": 58.0, "lon": -110.0},
    hover_data=["id", "pearson_r", "mbe", "rmse", "r_square", "burn_time", "area_ha"],
    mapbox_style="carto-positron",
    range_color=[-1, 1],
    zoom=1,
    # labels={"colorbar": '2m Temperature Bias'}
)
fig.layout.coloraxis.colorbar.title = "pearson_r"
fig.update_layout(margin=dict(l=0, r=100, t=30, b=10))
fig.show()
