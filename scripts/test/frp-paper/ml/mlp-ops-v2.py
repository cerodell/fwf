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


doi = pd.Timestamp("2024-05-01")
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense"
model_dir = str(data_dir) + f"/mlp/tf/averaged-v2/{mlp_test_case}"

model = load_model(f"{model_dir}/model.keras")

static_ds = salem.open_xr_dataset(str(data_dir) + f"/static/static-vars-wrf-d02.nc")
ny = (417 * 4) - 12
nx = (627 * 4) - 12
target_grid = salem.Grid(
    nxny=(nx, ny),
    dxdy=(3000.0, 3000.0),
    x0y0=(-3593999.2734108134, -6343328.220350546),
    proj=static_ds.attrs["pyproj_srs"],
).to_dataset()
lon, lat = target_grid.salem.grid.ll_coordinates
target_grid = static_ds
# smap = salem.Map(grid)
# smap.visualize(addcbar=False)
# var_list = ['S', 'R', 'SNOWC', 'r_o', 'F', 'Live_Wood' , 'Dead_Wood', 'Live_Leaf', 'Dead_Foliage']

### Open color map json
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)


def transform_ds(ds, domain):

    if domain != "fuel":
        ds["time"] = ds["Time"]
        static = salem.open_xr_dataset(
            str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
        )
        #   ds = xr.where(static['LAND']==1, np.nan, ds)
        if domain == "d03":
            static = static.isel(west_east=slice(30, 610), south_north=slice(30, 810))
            ds = ds.isel(west_east=slice(30, 610), south_north=slice(30, 810))
        ds["west_east"] = static["west_east"]
        ds["south_north"] = static["south_north"]
        for var in list(ds):
            ds[var].attrs = static.attrs
        ds.attrs = static.attrs
    ds = target_grid.salem.transform(
        ds[
            [
                "MODELED_FRP",
                # "S",
                "R",
                "r_o",
                "U",
                # "F",
                "Live_Wood",
                "Dead_Wood",
                "Live_Leaf",
                "Dead_Foliage",
                "R_hour_sin",
                "R_hour_cos",
            ]
        ],
        interp="nearest",
    )
    static = target_grid.salem.transform(static["LAND"], interp="nearest")
    ds = xr.where(static == 1, np.nan, ds)
    return ds


def open_fwf(doi, domain):

    fwf_dir = "/Volumes/WFRT-Ext24/fwf-data/wrf/"
    fwf_dir = " /Volumes/ThunderBay/CRodell/fwf-data/"
    static = salem.open_xr_dataset(
        str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
    )
    # fwf_hourly = xr.open_dataset(
    #     f"{fwf_dir}/{domain}/04/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc"
    # ).chunk("auto")
    fwf_hourly = xr.open_dataset(
        f"{fwf_dir}/{domain}/{doi.strftime('%Y')}/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc"
    ).chunk("auto")
    print(list(fwf_hourly))
    fwf_hourly = fwf_hourly  # [['S', 'R', 'SNOWC', 'r_o', 'F']]
    fwf_hourly["time"] = fwf_hourly["Time"]
    # fwf_daily = (
    #     xr.open_dataset(
    #         f"{fwf_dir}/{domain}/04/fwf-daily-{domain}-{doi.strftime('%Y%m%d06')}.nc"
    #     )["U"]
    #     .to_dataset()
    #     .chunk("auto")
    # )
    fwf_daily = (
        xr.open_dataset(
            f"{fwf_dir}/{domain}/{doi.strftime('%Y')}/fwf-daily-{domain}-{doi.strftime('%Y%m%d06')}.nc"
        )["U"]
        .to_dataset()
        .chunk("auto")
    )
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
    fuel_dir = f"/Volumes/WFRT-Ext23/fuel-characteristics/fuel-load/"
    fuels_ds = salem.open_xr_dataset(
        fuel_dir + f'{2021}/CFUEL_timemean_2021{moi.strftime("_%m")}.nc'
    ).sel(lat=slice(90, 10), lon=slice(-180, -30))
    fuels_ds.coords["time"] = moi
    return fuels_ds


def predict_frp(doi, domain, mlp_test_case):
    model_dir = str(data_dir) + f"/mlp/tf/averaged-v2/{mlp_test_case}"
    with open(f"{model_dir}/config.json", "r") as json_data:
        config = json.load(json_data)
    startFRP = datetime.now()
    # print("Start prediction:", startFRP)
    fwf_ds = open_fwf(doi, domain)  # .isel(time = slice(0,24))
    fuel_date_range = pd.date_range(
        fwf_ds["Time"].values[0],
        fwf_ds["Time"].values[-1],
        freq="MS",
    )
    if len(fuel_date_range) == 0:
        fuel_date_range = [pd.Timestamp(fwf_ds["Time"].values[0])]
    fuels_ds = xr.combine_nested(
        [open_fuels(moi) for moi in fuel_date_range], concat_dim="time"
    )

    fuels_ds = fwf_ds.salem.transform(fuels_ds, interp="linear").reindex(
        time=fwf_ds.Time, method="ffill"
    )
    for var in list(fuels_ds):
        fwf_ds[var] = fuels_ds[var]
    fwf_ds = get_solar_hours(fwf_ds)
    # hour_sin = np.sin(2 * np.pi * fwf_ds["solar_hour"] / 24)
    # hour_cos = np.cos(2 * np.pi * fwf_ds["solar_hour"] / 24)

    phi_sin = -np.pi
    # Compute hour_sin and hour_cos with the phase shift
    fwf_ds["hour_sin"] = np.sin((2 * np.pi * fwf_ds["solar_hour"] / 24) + phi_sin)
    fwf_ds["hour_cos"] = np.cos((2 * np.pi * fwf_ds["solar_hour"] / 24) + phi_sin)

    fwf_ds["R_hour_sin"] = fwf_ds["hour_sin"] * fwf_ds["R"]
    fwf_ds["R_hour_cos"] = fwf_ds["hour_cos"] * fwf_ds["R"]
    fwf_ds["S_hour_sin"] = fwf_ds["hour_sin"] * fwf_ds["S"]
    fwf_ds["S_hour_cos"] = fwf_ds["hour_cos"] * fwf_ds["S"]

    fwf_ds["U_Dead_Wood"] = fwf_ds["Dead_Wood"] * fwf_ds["U"]
    fwf_ds["U_Live_Wood"] = fwf_ds["Live_Wood"] * fwf_ds["U"]
    fwf_ds["U_Live_Leaf"] = fwf_ds["Live_Leaf"] * fwf_ds["U"]
    fwf_ds["U_Dead_Foliage"] = fwf_ds["Dead_Foliage"] * fwf_ds["U"]
    fwf_ds["F_Dead_Foliage"] = fwf_ds["Dead_Foliage"] * fwf_ds["F"]

    lat_sin = np.sin(np.radians(fwf_ds.XLAT.values))
    lat_cos = np.cos(np.radians(fwf_ds.XLAT.values))

    lon_sin = np.sin(np.radians(fwf_ds.XLONG.values))
    lon_cos = np.cos(np.radians(fwf_ds.XLONG.values))

    fwf_ds["S_lat_sin"] = lat_sin * fwf_ds["S"]
    fwf_ds["S_lat_cos"] = lat_cos * fwf_ds["S"]

    fwf_ds["S_lon_sin"] = lon_sin * fwf_ds["S"]
    fwf_ds["S_lon_cos"] = lon_cos * fwf_ds["S"]

    fwf_ds["R_lat_sin"] = lat_sin * fwf_ds["R"]
    fwf_ds["R_lat_cos"] = lat_cos * fwf_ds["R"]

    fwf_ds["R_lon_sin"] = lon_sin * fwf_ds["R"]
    fwf_ds["R_lon_cos"] = lon_cos * fwf_ds["R"]

    fwf_ds["U_lat_sin"] = lat_sin * fwf_ds["U"]
    fwf_ds["U_lat_cos"] = lat_cos * fwf_ds["U"]

    fwf_ds["U_lon_sin"] = lon_sin * fwf_ds["U"]
    fwf_ds["U_lon_cos"] = lon_cos * fwf_ds["U"]

    fwf_ds["R_hour_sin_Live_Wood"] = (
        fwf_ds["R"] * fwf_ds["hour_sin"] * fwf_ds["Live_Wood"]
    )
    fwf_ds["R_hour_cos_Live_Wood"] = (
        fwf_ds["R"] * fwf_ds["hour_cos"] * fwf_ds["Live_Wood"]
    )

    fwf_ds["R_hour_sin_Dead_Wood"] = (
        fwf_ds["R"] * fwf_ds["hour_sin"] * fwf_ds["Dead_Wood"]
    )
    fwf_ds["R_hour_cos_Dead_Wood"] = (
        fwf_ds["R"] * fwf_ds["hour_cos"] * fwf_ds["Dead_Wood"]
    )

    fwf_ds["R_hour_sin_Live_Leaf"] = (
        fwf_ds["R"] * fwf_ds["hour_sin"] * fwf_ds["Live_Leaf"]
    )
    fwf_ds["R_hour_cos_Live_Leaf"] = (
        fwf_ds["R"] * fwf_ds["hour_cos"] * fwf_ds["Live_Leaf"]
    )

    fwf_ds["R_hour_sin_Dead_Foliage"] = (
        fwf_ds["R"] * fwf_ds["hour_sin"] * fwf_ds["Dead_Foliage"]
    )
    fwf_ds["R_hour_cos_Dead_Foliage"] = (
        fwf_ds["R"] * fwf_ds["hour_cos"] * fwf_ds["Dead_Foliage"]
    )

    fwf_ds["U_lat_sin_Live_Wood"] = fwf_ds["U"] * lat_sin * fwf_ds["Live_Wood"]
    fwf_ds["U_lat_cos_Live_Wood"] = fwf_ds["U"] * lat_cos * fwf_ds["Live_Wood"]
    fwf_ds["U_lat_sin_Dead_Wood"] = fwf_ds["U"] * lat_sin * fwf_ds["Dead_Wood"]
    fwf_ds["U_lat_cos_Dead_Wood"] = fwf_ds["U"] * lat_cos * fwf_ds["Dead_Wood"]
    fwf_ds["U_lat_sin_Live_Leaf"] = fwf_ds["U"] * lat_sin * fwf_ds["Live_Leaf"]
    fwf_ds["U_lat_cos_Live_Leaf"] = fwf_ds["U"] * lat_cos * fwf_ds["Live_Leaf"]
    fwf_ds["U_lat_sin_Dead_Foliage"] = fwf_ds["U"] * lat_sin * fwf_ds["Dead_Foliage"]
    fwf_ds["U_lat_cos_Dead_Foliage"] = fwf_ds["U"] * lat_cos * fwf_ds["Dead_Foliage"]
    fwf_ds["F_lat_sin_Dead_Foliage"] = fwf_ds["F"] * lat_sin * fwf_ds["Dead_Foliage"]
    fwf_ds["F_lat_cos_Dead_Foliage"] = fwf_ds["F"] * lat_cos * fwf_ds["Dead_Foliage"]

    fwf_ds["U_lon_sin_Live_Wood"] = fwf_ds["U"] * lon_sin * fwf_ds["Live_Wood"]
    fwf_ds["U_lon_cos_Live_Wood"] = fwf_ds["U"] * lon_cos * fwf_ds["Live_Wood"]
    fwf_ds["U_lon_sin_Dead_Wood"] = fwf_ds["U"] * lon_sin * fwf_ds["Dead_Wood"]
    fwf_ds["U_lon_cos_Dead_Wood"] = fwf_ds["U"] * lon_cos * fwf_ds["Dead_Wood"]
    fwf_ds["U_lon_sin_Live_Leaf"] = fwf_ds["U"] * lon_sin * fwf_ds["Live_Leaf"]
    fwf_ds["U_lon_cos_Live_Leaf"] = fwf_ds["U"] * lon_cos * fwf_ds["Live_Leaf"]
    fwf_ds["U_lon_sin_Dead_Foliage"] = fwf_ds["U"] * lon_sin * fwf_ds["Dead_Foliage"]
    fwf_ds["U_lon_cos_Dead_Foliage"] = fwf_ds["U"] * lon_cos * fwf_ds["Dead_Foliage"]

    fwf_ds["F_lon_sin_Dead_Foliage"] = fwf_ds["F"] * lon_sin * fwf_ds["Dead_Foliage"]
    fwf_ds["F_lon_cos_Dead_Foliage"] = fwf_ds["F"] * lon_cos * fwf_ds["Dead_Foliage"]

    total_fuel = (
        fwf_ds["Live_Wood"]
        + fwf_ds["Dead_Wood"]
        + fwf_ds["Live_Leaf"]
        + fwf_ds["Dead_Foliage"]
    )
    fwf_ds["U_lat_sin_total_fuel"] = fwf_ds["U"] * lat_sin * total_fuel
    fwf_ds["U_lat_cos_total_fuel"] = fwf_ds["U"] * lat_cos * total_fuel

    fwf_ds["U_lon_sin_total_fuel"] = fwf_ds["U"] * lon_sin * total_fuel
    fwf_ds["U_lon_cos_total_fuel"] = fwf_ds["U"] * lon_cos * total_fuel

    shape = fwf_ds["S"].shape

    df_dict = {}
    print(config["features_used"])
    for key in config["features_used"]:
        try:
            df_dict[key] = np.ravel(fwf_ds[key].values)
        except KeyError:
            df_dict[key] = None

    df = pd.DataFrame(df_dict)
    # df["solar_hour"] = np.ravel(np.ravel(fwf_ds["solar_hour"].values))
    # df["hour_sin"] = np.sin(2 * np.pi * df["solar_hour"] / 24)
    # df["hour_cos"] = np.cos(2 * np.pi * df["solar_hour"] / 24)
    # df["S_hour_sin"] = df["hour_sin"] * df["S"]
    # df["S_hour_cos"] = df["hour_cos"] * df["S"]
    X = df[config["features_used"]]

    # Load the scaler
    scaler = joblib.load(f"{model_dir}/scaler.joblib")
    X_new_scaled = scaler.transform(X)

    # Load the model
    model = load_model(f"{model_dir}/model.keras")
    # FRP = model.predict(X_new_scaled)
    FRP = model(X_new_scaled)
    FRP_FULL = FRP.numpy().ravel().reshape(shape)
    FRPend = datetime.now() - startFRP
    print("Time to predict FRP: ", FRPend)
    fwf_ds["MODELED_FRP"] = (("time", "south_north", "west_east"), FRP_FULL)
    fwf_ds["MODELED_FRP"] = xr.where(fwf_ds["SNOWC"] > 0.5, 0, fwf_ds["MODELED_FRP"])

    startTRANSFORM = datetime.now()
    # print("Start transform:", startTRANSFORM)
    # fwf_ds = transform_ds(fwf_ds, domain)
    print("Time to transform data: ", datetime.now() - startTRANSFORM)
    del FRP_FULL, FRP, model, df, fuels_ds
    return fwf_ds


fwf_d02 = predict_frp(doi, "d02", mlp_test_case=mlp_test_case)
# fwf_d03 = predict_frp(doi, 'd03',  mlp_test_case = mlp_test_case)

# fwf_d02_hour = predict_frp(doi, 'd02',  mlp_test_case = 'MLP_32U-Dense_32U-Dense_1U-Dense-BEST-MODEL')
# fwf_d03_hour = predict_frp(doi, 'd03',  mlp_test_case = 'MLP_32U-Dense_32U-Dense_1U-Dense-BEST-MODEL')


# frp_da_fwi = xr.where(~np.isnan(fwf_d03_fwi),fwf_d03_fwi, fwf_d02_fwi)
# frp_da_hour = xr.where(~np.isnan(fwf_d03_hour),fwf_d03_hour, fwf_d02_hour)
# frp_da = xr.where(~np.isnan(fwf_d03),fwf_d03, fwf_d02)
frp_da = fwf_d02
# frp_da.name = 'MODELED_FRP'
# frp_da = frp_da.to_dataset()
# frp_da = (frp_da_fwi + frp_da_hour) / 2
for var in list(frp_da):
    frp_da[var].attrs = target_grid.attrs
frp_da.attrs = target_grid.attrs


print(float(frp_da["MODELED_FRP"].max()))

y, x = make_KDtree(49.01554, -76.43027, target_grid)
# y, x = make_KDtree(57.47797,-121.16833, target_grid)
# y, x = make_KDtree(27.92145, -81.09624, target_grid)
# y, x = make_KDtree(62.21035,-113.32549, target_grid)
# y, x = make_KDtree(37.307,-113.571, target_grid)
# y, x = make_KDtree(40,-140, target_grid)


# frp_interp = frp_da.isel(x= x, y =y)
frp_interp = frp_da.isel(west_east=x, south_north=y)

fig = plt.figure(figsize=(10, 3))
ax = fig.add_subplot(1, 1, 1)
frp_interp["MODELED_FRP"].plot(ax=ax)
# plt.savefig('MODELED_FRP.png')
fig = plt.figure(figsize=(10, 3))
ax = fig.add_subplot(1, 1, 1)
frp_interp["R"].plot(ax=ax)

# fig = plt.figure(figsize=(10,3))
# ax = fig.add_subplot(1,1,1)
# frp_interp['U'].plot(ax =ax)

fig = plt.figure(figsize=(10, 3))
ax = fig.add_subplot(1, 1, 1)
frp_interp["r_o"].plot(ax=ax)
# plt.savefig('S.png')

# %%
frp_da_small = frp_da.isel(time=slice(0, 24))
frp_i = hourly_rain(frp_da_small)

# frp_i = frp_da_small.max('time')


# ['MODELED_FRP', 'S', 'R', 'r_o', 'U', 'F', 'Live_Wood' , 'Dead_Wood', 'Live_Leaf', 'Dead_Foliage', 'R_hour_sin', 'R_hour_cos']], interp="nearest")


# %%

frp_i = frp_da_small.isel(time=18)
# frp_i["MODELED_FRP"] = xr.where(frp_i["Live_Wood"]<0.05,0, frp_i["MODELED_FRP"])

for var in list(frp_i):
    frp_i[var].attrs = target_grid.attrs
frp_i.attrs = target_grid.attrs

# %%

# fig = plt.figure(figsize=(12, 8))
# ax = fig.add_subplot(1, 1, 1)
# frp_i["MODELED_FRP"].attrs["units"] = "(MW)"
# colors = np.vstack(
#     ([1, 1, 1, 1], plt.get_cmap("YlOrRd")(np.linspace(0, 1, 256)))
# )  # Add white at the start
# custom_cmap = LinearSegmentedColormap.from_list("custom_YlOrRd", colors)
# frp_i["MODELED_FRP"].salem.quick_map(
#     cmap=custom_cmap, vmin=10, vmax=1000, ax=ax, oceans=True, lakes=True
# )
# # ax.set_title(f'Fire Radiative Power (MW) \n {str(frp_i.time.values)[:13]}')
# ax.set_title(f"Fire Radiative Power (MW) \n")
# test = xr.where(frp_da['MODELED_FRP']<100,np.nan,frp_da['MODELED_FRP'])

# # Calculate the quantiles for 18 intervals
# quantiles = np.linspace(0, 1, 19)
# quantile_values = test.quantile(quantiles).values.astype(int)
# print(quantile_values)

# fig = plt.figure(figsize=(12, 8))
# ax = fig.add_subplot(1, 1, 1)
# test.plot(bins=200, ax=ax)
# ax.set_xlim(0,500)


frp_i = frp_da_small.isel(time=18)

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1)
var = "MODELED_FRP"
# vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
# levels = cmaps[var]["levels"]
vmin, vmax = 0, 3000
levels = [
    0,
    15,
    50,
    100,
    150,
    200,
    250,
    300,
    400,
    500,
    600,
    700,
    1000,
    1400,
    1800,
    2200,
    2500,
    3000,
]
# title, colors = str(cmaps[var]["title"]), cmaps[var]["colors"]
# custom_cmap = LinearSegmentedColormap.from_list(
#     "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
# )
colors = np.vstack(
    ([1, 1, 1, 1], plt.get_cmap("YlOrRd")(np.linspace(0, 1, 256)))
)  # Add white at the start
custom_cmap = LinearSegmentedColormap.from_list("custom_YlOrRd", colors)
norm = BoundaryNorm(levels, custom_cmap.N)
frp_i[var].attrs["units"] = ""
frp_i[var].salem.quick_map(
    cmap=custom_cmap, ax=ax, norm=norm, oceans=False, lakes=True, extend="max"
)
ax.set_title(f"Fire Radiative Power (MW) \n")

# import matplotlib.colors as mcolors


# def get_hex_colors_from_colormap(colormap_name, num_colors):
#     cmap = plt.get_cmap(colormap_name)
#     colors = [cmap(i / num_colors) for i in range(num_colors)]
#     hex_colors = [mcolors.to_hex(color) for color in colors]
#     return hex_colors


# # Example: Get 18 colors from the 'viridis' colormap
# hex_colors = get_hex_colors_from_colormap(custom_cmap, 18)


# vtimes = pd.Timestamp(frp_i.time.values)
# itime = pd.Timestamp(frp_da_small.time.values[0]) - pd.Timedelta("6h")


# def setBold(txt):
#     return r"$\bf{" + str(txt) + "}$"

# def add_time_label(ax):
#     ax.set_title(f"Init: {itime.strftime('%HZ %a %d %b %Y')}", loc="left", fontsize=8)
#     ax.set_title(
#         f"{setBold('Valid')}: {vtimes.strftime('%HZ %a %d %b %Y')}",
#         fontsize=8,
#         loc="right",
#     )
#     return


# # %%
# plt.rcParams.update({"font.size": 10})

# fig = plt.figure(figsize=(24, 12))
# ax = fig.add_subplot(3, 4, 1)
# frp_i["MODELED_FRP"].attrs["units"] = "(MW)"
# colors = np.vstack(
#     ([1, 1, 1, 1], plt.get_cmap("YlOrRd")(np.linspace(0, 1, 256)))
# )  # Add white at the start
# custom_cmap = LinearSegmentedColormap.from_list("custom_YlOrRd", colors)
# frp_i["MODELED_FRP"].salem.quick_map(
#     cmap=custom_cmap, vmin=10, vmax=1000, ax=ax, oceans=True, lakes=True
# )
# # ax.set_title(f'Fire Radiative Power (MW) \n {str(frp_i.time.values)[:13]}')
# ax.set_title(f"Fire Radiative Power (MW) \n")
# add_time_label(ax)

# ax = fig.add_subplot(3, 4, 2)
# var = "R"
# vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
# title, colors = str(cmaps[var]["title"]), cmaps[var]["colors18"]
# custom_cmap = LinearSegmentedColormap.from_list(
#     "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
# )
# norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
# frp_i[var].attrs["units"] = ""
# frp_i[var].salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True)
# ax.set_title(title + "\n")
# add_time_label(ax)

# ax = fig.add_subplot(3, 4, 3)
# var = "U"
# vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
# title, colors = str(cmaps[var]["title"]), cmaps[var]["colors18"]
# custom_cmap = LinearSegmentedColormap.from_list(
#     "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
# )
# norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
# frp_i[var].attrs["units"] = ""
# frp_i[var].salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True)
# ax.set_title(title + "\n")
# add_time_label(ax)


# ax = fig.add_subplot(3, 4, 4)
# var = "S"
# vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
# title, colors = str(cmaps[var]["title"]), cmaps[var]["colors18"]
# custom_cmap = LinearSegmentedColormap.from_list(
#     "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
# )
# norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
# frp_i[var].attrs["units"] = ""
# frp_i[var].salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True)
# ax.set_title(title + "\n")
# add_time_label(ax)


# ax = fig.add_subplot(3, 4, 5)
# var = "T"
# vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
# title, colors = str(cmaps[var]["title"]), cmaps[var]["colors"]
# custom_cmap = LinearSegmentedColormap.from_list(
#     "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
# )
# norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
# frp_i[var].attrs["units"] = ""
# frp_i[var].salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True)
# ax.set_title(title + "\n")
# add_time_label(ax)

# ax = fig.add_subplot(3, 4, 6)
# var = "H"
# vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
# title, colors = str(cmaps[var]["title"]), cmaps[var]["colors18"]
# custom_cmap = LinearSegmentedColormap.from_list(
#     "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
# )
# norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
# frp_i[var].attrs["units"] = ""
# frp_i[var].salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True)
# ax.set_title(title + "\n")
# add_time_label(ax)

# ax = fig.add_subplot(3, 4, 7)
# var = "W"
# vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
# title, colors = str(cmaps[var]["title"]), cmaps[var]["colors18"]
# custom_cmap = LinearSegmentedColormap.from_list(
#     "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
# )
# norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
# frp_i[var].attrs["units"] = ""
# frp_i[var].salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True)
# ax.set_title(title + "\n")
# add_time_label(ax)

# ax = fig.add_subplot(3, 4, 8)
# var = "r_o"
# vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
# title, colors = str(cmaps[var]["title"]), cmaps[var]["colors18"]
# custom_cmap = LinearSegmentedColormap.from_list(
#     "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
# )
# norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
# frp_i[var].attrs["units"] = ""
# frp_i[var].salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True)
# ax.set_title(title + "\n")
# add_time_label(ax)


# ax = fig.add_subplot(3, 4, 9)
# var = "Live_Wood"
# frp_i[var].attrs["units"] = ""
# frp_i[var].salem.quick_map(cmap="Greens", ax=ax, oceans=True, lakes=True)
# ax.set_title("Live Wood Fuel Load" + "\n")
# add_time_label(ax)


# ax = fig.add_subplot(3, 4, 10)
# var = "Dead_Wood"
# frp_i[var].attrs["units"] = ""
# frp_i[var].salem.quick_map(cmap="Oranges", ax=ax, oceans=True, lakes=True)
# ax.set_title("Dead Wood Fuel Load" + "\n")
# add_time_label(ax)


# ax = fig.add_subplot(3, 4, 11)
# var = "Live_Leaf"
# frp_i[var].attrs["units"] = ""
# frp_i[var].salem.quick_map(cmap="Greens", ax=ax, oceans=True, lakes=True)
# ax.set_title("Live Leaf Fuel Load" + "\n")
# add_time_label(ax)


# ax = fig.add_subplot(3, 4, 12)
# var = "Dead_Foliage"
# frp_i[var].attrs["units"] = ""
# frp_i[var].salem.quick_map(cmap="Oranges", ax=ax, oceans=True, lakes=True)
# ax.set_title("Dead Leaf Fuel Load" + "\n")
# add_time_label(ax)

# fig.tight_layout()
# fig.savefig(
#     str(model_dir) + "/img/frp-rain.pdf",
#     bbox_inches="tight",
#     pad_inches=0.1,
#     orientation="landscape",
# )


# # %%
# # # Parameters for the plot
# # ncol = 6
# # nrow = (len(frp_da_small.time) + ncol - 1) // ncol

# # fig, axes = plt.subplots(nrow, ncol, figsize=(18, 9))

# # # Flatten axes for easy iteration
# # axes = axes.flatten()

# # # Generate subplots
# # for i, t in enumerate(frp_da_small.time):
# #     ax = axes[i]
# #     smap = frp_da_small['MODELED_FRP'].sel(time=t).salem.get_map(cmap="YlOrRd", vmin=0, vmax=600)
# #     smap.set_data(frp_da_small['MODELED_FRP'].sel(time=t).values)
# #     smap.visualize(ax=ax, addcbar=False)  # Do not add color bar here
# #     ax.set_title(f'{str(t.values)[:13]}')

# #     # Hide x and y labels for all but the leftmost and bottommost subplots
# #     if i % ncol != 0:  # Not the leftmost column
# #         ax.set_yticklabels([])
# #     if i // ncol != nrow - 1:  # Not the bottommost row
# #         ax.set_xticklabels([])
# #     # else:
# #     #     ax.set_xticklabels(fontsize =14)

# # # Turn off unused subplots
# # for j in range(i + 1, len(axes)):
# #     fig.delaxes(axes[j])

# # # Add borders to each subplot
# # for ax in axes:
# #     for spine in ax.spines.values():
# #         spine.set_edgecolor('black')
# #         spine.set_linewidth(1.5)

# # # Adjust layout
# # fig.tight_layout(rect=[0, 0, 0.94, 1])  # Leave space for colorbar on the right

# # # Add a single color bar
# # cbar_ax = fig.add_axes([0.938, 0.1, 0.02, 0.8])  # [left, bottom, width, height]
# # sm = plt.cm.ScalarMappable(cmap="YlOrRd", norm=plt.Normalize(vmin=0, vmax=600))
# # cbar = fig.colorbar(sm, cax=cbar_ax, extend = 'max' )
# # cbar.set_label('FRP (MW)', fontsize =18)
# # # fig.savefig('frp_times.png')
