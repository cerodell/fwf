#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import salem
import json
import numpy as np
import pandas as pd
import xarray as xr
from utils.ml_data import MLDATA
from utils.geoutils import make_KDtree
from utils.frp import set_axis_postion_full_fwx
import matplotlib.dates as mdates


import matplotlib.pyplot as plt

from context import data_dir


domain = "d02"
doi = pd.Timestamp("2023-06-06")
mlp_test_case = "MLP_64U-Dense_64U-Dense_64U-Dense_2U-Dense"
model_dir = str(data_dir) + f"/mlp/tf/averaged-v7/FRP_FRE/{mlp_test_case}"
### Open model config
with open(f"{model_dir}/config.json", "r") as json_data:
    config = json.load(json_data)["user_config"]
mlD = MLDATA(config)


def open_fwf(doi, domain):
    fwf_dir = "/Volumes/WFRT-Ext24/fwf-data/wrf/"
    static_ds = salem.open_xr_dataset(
        str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
    )
    fwf_hourly = xr.open_dataset(
        f"{fwf_dir}/{domain}/04/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc"
    ).chunk("auto")
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
    fwf_daily["time"] = fwf_daily["Time"]
    fwf_hourly["U"] = fwf_daily["U"].reindex(time=fwf_hourly.Time, method="ffill")
    fwf_hourly["west_east"] = static_ds["west_east"]
    fwf_hourly["south_north"] = static_ds["south_north"]
    for var in list(fwf_hourly):
        fwf_hourly[var].attrs = static_ds.attrs
    fwf_hourly.attrs = static_ds.attrs
    # print("Start prediction:", startFRP)
    fwf_hourly = mlD.get_static(fwf_hourly, static=static_ds)
    fwf_hourly = mlD.get_eng_features(fwf_hourly, wrf=True)
    for var in list(fwf_hourly):
        fwf_hourly[var].attrs = static_ds.attrs
    fwf_hourly.attrs = static_ds.attrs
    return fwf_hourly, static_ds


fwf_ds, static_ds = open_fwf(doi, domain)  # .isel(time = slice(0,24))


y, x = make_KDtree(27.92145, -81.09624, static_ds)
# y, x = make_KDtree(49.01554,-76.43027, static_ds)
# y, x = make_KDtree(57.47797,-121.16833, static_ds)


ds_i = fwf_ds.isel(west_east=x, south_north=y, time=slice(0, 48))
static_i = static_ds.isel(west_east=x, south_north=y)
ds_i["time"] = ds_i["Time"] - pd.Timedelta(int(static_i["ZoneST"]), "hour")

# %%
fig = plt.figure(figsize=(12, 4))
hs = fig.add_subplot(1, 1, 1)
isi = hs.twinx()
isi_hs = hs.twinx()
ds_i["hour_sin"].plot(ax=hs, color="tab:blue")
set_axis_postion_full_fwx(hs, "left", 0, "Sin(Solar Hour)")
hs.set_title("")

ds_i["R"].plot(ax=isi, color="tab:green")
set_axis_postion_full_fwx(isi, "right", 0, "ISI")
isi.set_title("")

ds_i["R-hour_sin-Live_Wood"].plot(ax=isi_hs, color="tab:red")
set_axis_postion_full_fwx(isi_hs, "left", 120, "ISI x Sin(Solar Hour) \n x Live Wood")
# y_min, y_max = isi_hs.get_ylim()
# if abs(y_min) > abs(y_max):
#     higher_abs_value = abs(y_min)
# else:
#     higher_abs_value = abs(y_max)
# isi_hs.set_ylim(-higher_abs_value, higher_abs_value)
isi_hs.set_title("Feature Engineering")
hs.xaxis.set_major_formatter(mdates.DateFormatter("%H"))
hs.set_xlabel("Local Hour")
fig.tight_layout()

plt.savefig(
    str(data_dir) + "/images/frp-paper/feature-eng-time-isi-hour-sin-fuels.png", dpi=250
)


# %%
# fig = plt.figure(figsize=(12, 4))
# hs = fig.add_subplot(1, 1, 1)
# isi = hs.twinx()
# isi_hs = hs.twinx()

# ds_i["hour_cos"].plot(ax=hs, color="tab:blue")
# set_axis_postion_full_fwx(hs, "left", 0, "Cos(Solar Hour)")
# hs.set_title("")

# ds_i["R"].plot(ax=isi, color="tab:green")
# set_axis_postion_full_fwx(isi, "right", 0, "ISI")
# isi.set_title("")

# ds_i["R_hour_cos_Live_Wood"].plot(ax=isi_hs, color="tab:red")
# set_axis_postion_full_fwx(isi_hs, "left", 120, "ISI x Cos(Solar Hour) \n x Live Wood")
# y_min, y_max = isi_hs.get_ylim()
# if abs(y_min) > abs(y_max):
#     higher_abs_value = abs(y_min)
# else:
#     higher_abs_value = abs(y_max)
# isi_hs.set_ylim(-higher_abs_value, higher_abs_value)
# isi_hs.set_title("Feature Engineering")
# hs.xaxis.set_major_formatter(mdates.DateFormatter("%H"))
# hs.set_xlabel("Local Hour")
# fig.tight_layout()
# plt.savefig(
#     str(data_dir) + "/images/frp-paper/feature-eng-time-isi-hour-cos-fuels.png", dpi=250
# )

# %%


ds_space = fwf_ds.isel(time=18)

fig = plt.figure(figsize=(16, 10))
cmap = "jet"
ax = fig.add_subplot(2, 2, 1)
ds_space["U-lat_sin-Live_Wood"].salem.quick_map(
    oceans=True, lakes=True, ax=ax, vmax=800, cmap=cmap
)
ax.set_title("BUI x Sin(Latitude) x Live Wood Fuel Load")

ax = fig.add_subplot(2, 2, 2)
ds_space["U"].salem.quick_map(oceans=True, lakes=True, ax=ax, vmax=200, cmap=cmap)
ax.set_title("BUI")

ax = fig.add_subplot(2, 2, 3)
ds_space["lat_sin"].salem.quick_map(oceans=True, lakes=True, ax=ax, cmap=cmap)
ax.set_title("Sin(Latitude)")

ax = fig.add_subplot(2, 2, 4)
ds_space["Live_Wood"].salem.quick_map(
    oceans=True, lakes=True, ax=ax, vmax=20, cmap=cmap
)
ax.set_title(r"Live Wood Fuel Load ($kg$ $m^{-2}$)")
fig.tight_layout()
plt.savefig(
    str(data_dir) + "/images/frp-paper/feature-eng-map-bui-lat-sin-load.png", dpi=250
)


# # # %%
# # fig = plt.figure(figsize=(16, 10))
# # cmap = 'jet'
# # ax = fig.add_subplot(2, 2, 1)
# # ds_space['U_lat_cos_Live_Wood'].salem.quick_map(oceans = True, lakes = True, ax=ax, vmax = 800, cmap =cmap)
# # ax.set_title("BUI x Cos(Latitude) x Live Wood Fuel Load")

# # ax = fig.add_subplot(2, 2, 2)
# # ds_space['U'].salem.quick_map(oceans = True, lakes = True, ax=ax, vmax = 200, cmap =cmap)
# # ax.set_title("BUI")

# # ax = fig.add_subplot(2, 2, 3)
# # ds_space['lat_cos'].salem.quick_map(oceans = True, lakes = True, ax=ax, cmap =cmap)
# # ax.set_title("Cos(Latitude)")

# # ax = fig.add_subplot(2, 2, 4)
# # ds_space['Live_Wood'].salem.quick_map(oceans = True, lakes = True, ax=ax, vmax = 20, cmap =cmap)
# # ax.set_title(r"Live Wood Fuel Load ($kg$ $m^{-2}$)")
# # fig.tight_layout()
# # # plt.savefig(str(data_dir) + '/images/frp-paper/feature-eng-map-bui-lat-cos-load.png', dpi = 250)

# # # %%

# %%
