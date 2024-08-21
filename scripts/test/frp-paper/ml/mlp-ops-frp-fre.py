#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import context
import salem
import dask
import joblib
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime


from utils.ml_data import MLDATA
from utils.firep import FIREP
from utils.fwx import FWX
from utils.wrf_ import hourly_rain
from utils.solar_hour import get_solar_hours
from utils.geoutils import make_KDtree
from tensorflow.keras.models import load_model

from scipy import stats
from utils.stats import MBE, RMSE
from sklearn.metrics import r2_score

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors

from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm

from context import root_dir, data_dir

import warnings

startFWX = datetime.now()
# Suppress future warnings
warnings.simplefilter(action="ignore", category=FutureWarning)

domain = "d02"
doi = pd.Timestamp("2023-06-06")
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense"
method = "averaged-v15"
ml_pack = "tf"
target_vars = "FRP"
model_dir = str(data_dir) + f"/mlp/tf/{method}/{target_vars}/{mlp_test_case}"


### Open color map json
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)


target_grid = salem.open_xr_dataset(str(data_dir) + f"/static/static-vars-wrf-d02.nc")


def open_fwf(doi, domain):

    fwf_dir = "/Volumes/WFRT-Ext24/fwf-data/wrf/"
    # fwf_dir = " /Volumes/ThunderBay/CRodell/fwf-data/"
    static = salem.open_xr_dataset(
        str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
    )
    fwf_hourly = xr.open_dataset(
        f"{fwf_dir}/{domain}/04/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc"
    ).chunk("auto")
    # fwf_hourly = xr.open_dataset(
    #     f"{fwf_dir}/{domain}/{doi.strftime('%Y')}/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc"
    # ).chunk("auto")
    print(list(fwf_hourly))
    fwf_hourly = fwf_hourly  # [['S', 'R', 'SNOWC', 'r_o', 'F']]
    fwf_hourly["time"] = fwf_hourly["Time"]
    fwf_daily = (
        xr.open_dataset(
            f"{fwf_dir}/{domain}/04/fwf-daily-{domain}-{doi.strftime('%Y%m%d06')}.nc"
        )["U"]
        .to_dataset()
        .chunk("auto")
    )
    # fwf_daily = (
    #     xr.open_dataset(
    #         f"{fwf_dir}/{domain}/{doi.strftime('%Y')}/fwf-daily-{domain}-{doi.strftime('%Y%m%d06')}.nc"
    #     )["U"]
    #     .to_dataset()
    #     .chunk("auto")
    # )
    fwf_daily["time"] = fwf_daily["Time"]
    fwf_hourly["U"] = fwf_daily["U"].reindex(time=fwf_hourly.Time, method="ffill")
    fwf_hourly["west_east"] = static["west_east"]
    fwf_hourly["south_north"] = static["south_north"]

    for var in list(fwf_hourly):
        fwf_hourly[var].attrs = static.attrs
    fwf_hourly.attrs = static.attrs
    del static
    return fwf_hourly


def open_fuels(moi):
    moi = pd.Timestamp(moi)
    fuel_dir = f"/Volumes/ThunderBay/CRodell/ecmwf/fuel-load/"
    fuels_ds = salem.open_xr_dataset(
        fuel_dir + f'{2021}/CFUEL_timemean_2021{moi.strftime("_%m")}.nc'
    ).sel(lat=slice(75, 20), lon=slice(-170, -50))
    fuels_ds.coords["time"] = moi
    return fuels_ds


# def predict_frp(doi, domain, model_dir):
startFRP = datetime.now()
### Open model config
with open(f"{model_dir}/config.json", "r") as json_data:
    config = json.load(json_data)["user_config"]
mlD = MLDATA(config)
# print("Start prediction:", startFRP)
fwf_ds = open_fwf(doi, domain)  # .isel(time = slice(0,24))
ds = fwf_ds
curves_ds = salem.open_xr_dataset(str(data_dir) + "/static/curves-wrf-d02.nc")
fire_time = ds.time.values
hour_one = pd.Timestamp(fire_time[0]).hour
curves_ds = curves_ds.roll(time=-hour_one, roll_coords=True)
for var in list(curves_ds):
    CURVES_VAR = curves_ds[var].values
    N = len(fire_time)
    ds[var] = (
        ("time", "south_north", "west_east"),
        np.tile(CURVES_VAR, (N + 1, 1, 1))[:N, :, :],
    )
    ds[var].attrs = ds.attrs

fwf_ds = mlD.get_static(fwf_ds, static=target_grid)
fwf_ds = mlD.get_eng_features(fwf_ds, wrf=True)

shape = fwf_ds["S"].shape
df_dict = {}
print(config["feature_vars"])
for key in config["feature_vars"]:
    try:
        df_dict[key] = np.ravel(fwf_ds[key].values)
    except KeyError:
        df_dict[key] = None

df = pd.DataFrame(df_dict)
X = df[config["feature_vars"]]

# Load the scaler
feature_scaler = joblib.load(f"{model_dir}/feature-scaler.joblib")
X_new_scaled = feature_scaler.transform(X)
df_scaled = pd.DataFrame(X_new_scaled, columns=config["feature_vars"])
for var in config["feature_vars"]:
    fwf_ds[var] = (
        ("time", "south_north", "west_east"),
        df_scaled[var].values.reshape(shape),
    )
    fwf_ds[var].attrs = fwf_ds.attrs

# Load the model
model = load_model(f"{model_dir}/model.keras")
y_out_this_nhn = model(X_new_scaled).numpy()


if config["target_scaler_type"] == True:
    # print("self.target_scaler_type is: ", self.target_scaler_type)
    # y_out_this_nhn = self.target_scaler.inverse_transform(y_out_this_nhn)
    y_out_this_nhn = y_out_this_nhn * config["FRP_MAX"]


if config["transform"] == True:
    y_out_this_nhn = np.expm1(y_out_this_nhn)

FRP_FULL = y_out_this_nhn.ravel().reshape(shape)
fwf_ds["FRP"] = (("time", "south_north", "west_east"), FRP_FULL)

static = salem.open_xr_dataset(str(data_dir) + f"/static/static-vars-wrf-{domain}.nc")

fwf_ds["FRP"] = xr.where(static["LAND"] == 1, 0, fwf_ds["FRP"])
fwf_ds["FRP"] = xr.where(np.isnan(fwf_ds["FRP"]) == True, 0, fwf_ds["FRP"])

for var in list(fwf_ds):
    if var == "FRP":
        fwf_ds[var].attrs = {
            "description": "MEAN FIRE RADIATIVE POWER",
            "pyproj_srs": target_grid.attrs["pyproj_srs"],
            "units": "(MW)",
        }
    else:
        fwf_ds[var].attrs["pyproj_srs"] = target_grid.attrs["pyproj_srs"]
fwf_ds.attrs = target_grid.attrs
FRPend = datetime.now() - startFRP
print("Time to predict FRP: ", FRPend)
# return fwf_ds

# fwf_ds['R-diurnal_curve-Total_Fuel_Load'] = fwf_ds['R']  * fwf_ds['diurnal_curve']  * fwf_ds['Total_Fuel_Load']

# np.expm1(fwf_ds["Total_Fuel_Load"]).isel(time=18).salem.quick_map()
# fwf_ds["FRP"].isel(time=18).salem.quick_map()


# fwf_ds.to_netcdf(str(data_dir) + f"/frp/sample_{domain}_{method}.nc")


# fwf_ds = predict_frp(doi, domain, model_dir)

# test = pd.DatetimeIndex(fwf_ds["Time"].values)
# # print(float(fwf_ds["FRP"].max()))

# # y, x = make_KDtree(49.01554, -76.43027, target_grid)
# # y, x = make_KDtree(57.47797,-121.16833, target_grid)
y, x = make_KDtree(27.92145, -81.09624, target_grid)
# # y, x = make_KDtree(62.21035,-113.32549, target_grid)
# # y, x = make_KDtree(37.307,-113.571, target_grid)
# # y, x = make_KDtree(40,-140, target_grid)

# y, x = make_KDtree(57.47797,-121.16833, target_grid)


ds_i = fwf_ds.isel(west_east=x, south_north=y, time=slice(0, 48))

static_i = target_grid.isel(west_east=x, south_north=y)
ds_i["time"] = ds_i["Time"] - pd.Timedelta(int(static_i["ZoneST"]), "hour")
ds_i["S-hour_sin-Total_Fuel_Load"].plot(color="tab:blue", zorder=10)


# # frp_interp = fwf_ds.isel(x= x, y =y)
# frp_interp = fwf_ds.isel(west_east=x, south_north=y)

# fig = plt.figure(figsize=(10, 3))
# ax = fig.add_subplot(1, 1, 1)
# frp_interp["FRP"].plot(ax=ax)
# # # plt.savefig('FRP.png')
# fig = plt.figure(figsize=(10, 3))
# ax = fig.add_subplot(1, 1, 1)
# np.expm1(frp_interp["R"]).plot(ax=ax)

# for var in config["feature_vars"]:
#     fig = plt.figure(figsize=(10, 3))
#     ax = fig.add_subplot(1, 1, 1)
#     frp_interp[var].plot(ax=ax)

# # # fig = plt.figure(figsize=(10,3))
# # # ax = fig.add_subplot(1,1,1)
# # # frp_interp['U'].plot(ax =ax)

# fig = plt.figure(figsize=(10, 3))
# ax = fig.add_subplot(1, 1, 1)
# frp_interp["r_o"].plot(ax=ax)
# # plt.savefig('S.png')


# %%


frp_i = fwf_ds.isel(time=18)
np.expm1(frp_i["Total_Fuel_Load"]).salem.quick_map(oceans=True, lakes=True)
frp_i["Total_Fuel_Load"].salem.quick_map(oceans=True, lakes=True)

frp_i["FRP"].salem.quick_map(vmax=600, vmin=10, oceans=True, lakes=True)
frp_i["S-hour_sin-Total_Fuel_Load"].salem.quick_map(oceans=True, lakes=True)

import matplotlib.colors as mcolors


def get_hex_colors_from_colormap(colormap_name, num_colors):
    cmap = plt.get_cmap(colormap_name)
    colors = [cmap(i / num_colors) for i in range(num_colors)]
    hex_colors = [mcolors.to_hex(color) for color in colors]
    return hex_colors


vtimes = pd.Timestamp(frp_i.time.values)
itime = pd.Timestamp(fwf_ds.time.values[0]) - pd.Timedelta("6h")


def setBold(txt):
    return r"$\bf{" + str(txt) + "}$"


def add_time_label(ax):
    ax.set_title(f"Init: {itime.strftime('%HZ %a %d %b %Y')}", loc="left", fontsize=8)
    ax.set_title(
        f"{setBold('Valid')}: {vtimes.strftime('%HZ %a %d %b %Y')}",
        fontsize=8,
        loc="right",
    )
    return


plt.rcParams.update({"font.size": 10})

fig = plt.figure(figsize=(24, 12))
ax = fig.add_subplot(3, 4, 1)
frp_i["FRP"].attrs["units"] = "(MW)"
colors = np.vstack(
    ([1, 1, 1, 1], plt.get_cmap("YlOrRd")(np.linspace(0, 1, 256)))
)  # Add white at the start
custom_cmap = LinearSegmentedColormap.from_list("custom_YlOrRd", colors)
frp_i["FRP"].salem.quick_map(
    cmap=custom_cmap, vmin=0, vmax=1000, ax=ax, oceans=True, lakes=True
)
# ax.set_title(f'Fire Radiative Power (MW) \n {str(frp_i.time.values)[:13]}')
ax.set_title(f"Fire Radiative Power (MW) \n")
add_time_label(ax)

ax = fig.add_subplot(3, 4, 2)
var = "R"
vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
title, colors = str(cmaps[var]["title"]), cmaps[var]["colors18"]
custom_cmap = LinearSegmentedColormap.from_list(
    "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
)
norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
frp_i[var].attrs["units"] = ""
np.expm1(frp_i[var]).salem.quick_map(
    cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True
)
ax.set_title(title + "\n")
add_time_label(ax)

ax = fig.add_subplot(3, 4, 3)
var = "U"
vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
title, colors = str(cmaps[var]["title"]), cmaps[var]["colors18"]
custom_cmap = LinearSegmentedColormap.from_list(
    "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
)
norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
frp_i[var].attrs["units"] = ""
np.expm1(frp_i[var]).salem.quick_map(
    cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True
)
ax.set_title(title + "\n")
add_time_label(ax)


ax = fig.add_subplot(3, 4, 4)
var = "S"
vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
title, colors = str(cmaps[var]["title"]), cmaps[var]["colors18"]
custom_cmap = LinearSegmentedColormap.from_list(
    "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
)
norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
frp_i[var].attrs["units"] = ""
np.expm1(frp_i[var]).salem.quick_map(
    cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True
)
ax.set_title(title + "\n")
add_time_label(ax)


ax = fig.add_subplot(3, 4, 5)
var = "T"
vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
title, colors = str(cmaps[var]["title"]), cmaps[var]["colors"]
custom_cmap = LinearSegmentedColormap.from_list(
    "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
)
norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
frp_i[var].attrs["units"] = ""
frp_i[var].salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True)
ax.set_title(title + "\n")
add_time_label(ax)

ax = fig.add_subplot(3, 4, 6)
var = "H"
vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
title, colors = str(cmaps[var]["title"]), cmaps[var]["colors18"]
custom_cmap = LinearSegmentedColormap.from_list(
    "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
)
norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
frp_i[var].attrs["units"] = ""
frp_i[var].salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True)
ax.set_title(title + "\n")
add_time_label(ax)

ax = fig.add_subplot(3, 4, 7)
var = "W"
vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
title, colors = str(cmaps[var]["title"]), cmaps[var]["colors18"]
custom_cmap = LinearSegmentedColormap.from_list(
    "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
)
norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
frp_i[var].attrs["units"] = ""
frp_i[var].salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True)
ax.set_title(title + "\n")
add_time_label(ax)

ax = fig.add_subplot(3, 4, 8)
var = "r_o"
vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
title, colors = str(cmaps[var]["title"]), cmaps[var]["colors18"]
custom_cmap = LinearSegmentedColormap.from_list(
    "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
)
norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
frp_i[var].attrs["units"] = ""
frp_i[var].salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True)
ax.set_title(title + "\n")
add_time_label(ax)


ax = fig.add_subplot(3, 4, 9)
var = "Total_Fuel_Load"
frp_i[var].attrs["units"] = "kg m^-2"
np.expm1(frp_i[var]).salem.quick_map(cmap="Greens", ax=ax, oceans=True, lakes=True)
ax.set_title("Total Fuel Load (kg m^-2)" + "\n")
add_time_label(ax)


ax = fig.add_subplot(3, 4, 10)
var = "R-hour_sin-Total_Fuel_Load"
frp_i[var].attrs["units"] = ""
frp_i[var].salem.quick_map(cmap="jet", ax=ax, oceans=True, lakes=True, vmin=0, vmax=1)
ax.set_title("log(ISI) x Sine(Solar Hour) x log(Total Fuel Load)" + "\n")
add_time_label(ax)


ax = fig.add_subplot(3, 4, 11)
var = "U-Total_Fuel_Load"
frp_i[var].attrs["units"] = ""
frp_i[var].salem.quick_map(cmap="jet", ax=ax, oceans=True, lakes=True, vmin=0, vmax=1)
ax.set_title("Live Leaf Fuel Load" + "\n")
ax.set_title("log(BUI) x Sine(Latitude) x log(Total Fuel Load)" + "\n")
add_time_label(ax)


ax = fig.add_subplot(3, 4, 12)
# var = "SAZ_sin-Total_Fuel_Load"
# frp_i[var].attrs["units"] = ""
# frp_i[var].salem.quick_map(cmap="gist_ncar", ax=ax, oceans=True, lakes=True, vmin=0,vmax =1)
# ax.set_title("Sine(Solar Azimuthal) x log(Total Fuel Load)" + "\n")
# add_time_label(ax)

fig.tight_layout()
fig.savefig(
    str(model_dir) + "/img/test-all-vars.pdf",
    bbox_inches="tight",
    pad_inches=0.1,
    orientation="landscape",
)


# %%
