#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import salem
import json
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib
from utils.ml_data import MLDATA
from utils.geoutils import make_KDtree
from utils.frp import set_axis_postion_full_fwx
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from context import data_dir, root_dir


save_fig = False
paper_fig = True
domain = "d02"
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense-Main"
method = "averaged-v19"
### Open color map json
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

static_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
)
fwf_ds = salem.open_xr_dataset(str(data_dir) + f"/frp/sample_{domain}_{method}.nc")

phi_sin = -10 * (2 * np.pi / 24)
fwf_ds["hour_sin"] = (
    0.1 + (np.sin((2 * np.pi * fwf_ds["solar_hour"] / 24) + phi_sin) + 1) * 0.45
)
fwf_ds["hour_cos"] = (
    0.1 + (np.cos((2 * np.pi * fwf_ds["solar_hour"] / 24) + phi_sin) + 1) * 0.45
)


fwf_ds["Live_Wood"] = (
    ("time", "south_north", "west_east"),
    np.full(fwf_ds["F"].shape, fwf_ds["Live_Wood"].values),
)

# frp_i = fwf_ds.isel(time=18)
# frp_i['FRP'].salem.quick_map(vmax =500, oceans=True, lakes=True)
# frp_i['r_o'].salem.quick_map(vmax =10, oceans=True, lakes=True)


y, x = make_KDtree(27.92145, -81.09624, static_ds)
# y, x = make_KDtree(49.01554,-76.43027, static_ds)
# y, x = make_KDtree(57.47797,-121.16833, static_ds)


ds_i = fwf_ds.isel(west_east=x, south_north=y, time=slice(0, 48))

static_i = static_ds.isel(west_east=x, south_north=y)
ds_i["time"] = ds_i["Time"] - pd.Timedelta(int(static_i["ZoneST"]), "hour")

# %%
matplotlib.rcParams.update({"font.size": 18})
fig = plt.figure(figsize=(14, 5))
hs = fig.add_subplot(1, 1, 1)
isi = hs.twinx()
fuel = hs.twinx()
isi_hs = hs.twinx()
ds_i["hour_sin"].plot(ax=hs, color="tab:blue", zorder=10)
set_axis_postion_full_fwx(hs, "left", 0, "Sin(Solar Hour)")
hs.set_title("")

ds_i["S"].plot(ax=isi, color="tab:green", zorder=10)
set_axis_postion_full_fwx(isi, "right", 0, "Fire Weather Index")
isi.set_title("")

ds_i["Live_Wood"].plot(ax=fuel, color="tab:orange", zorder=1)
set_axis_postion_full_fwx(
    fuel, "right", 90, "Live Wood Fuel Load \n" + r"($kg$ $m^{-2}$)"
)
fuel.set_title("")

ds_i["S-hour_sin-Live_Wood"].plot(ax=isi_hs, color="tab:red", zorder=10)
set_axis_postion_full_fwx(
    isi_hs,
    "left",
    90,
    "Normalized [\n Sin(Solar Hour) \n x Fire Weather Index \n x Live Wood Fuel Load]",
)

isi_hs.set_title("")
hs.xaxis.set_major_formatter(mdates.DateFormatter("%H"))
hs.set_xlabel("Local Hour", fontsize=18)
fig.suptitle("Feature Engineering", fontsize=30)
fig.tight_layout()
if save_fig == True:
    fig.savefig(
        str(data_dir) + "/images/frp-paper/feature-eng-time-fwi-hour-sin-fuels.png",
        bbox_inches="tight",
        dpi=240,
    )
if paper_fig == True:
    fig.savefig(
        f"/Users/crodell/ams-frp/feature-eng-time-fwi-hour-sin-fuels.pdf",
        bbox_inches="tight",
    )

# %%


fig = plt.figure(figsize=(14, 5))
hs = fig.add_subplot(1, 1, 1)
isi = hs.twinx()
fuel = hs.twinx()
isi_hs = hs.twinx()
ds_i["hour_cos"].plot(ax=hs, color="tab:blue", zorder=10)
set_axis_postion_full_fwx(hs, "left", 0, "Sin(Solar Hour)")
hs.set_title("")

ds_i["S"].plot(ax=isi, color="tab:green", zorder=10)
set_axis_postion_full_fwx(isi, "right", 0, "Fire Weather Index")
isi.set_title("")

ds_i["Live_Wood"].plot(ax=fuel, color="tab:orange", zorder=1)
set_axis_postion_full_fwx(
    fuel, "right", 90, "Live Wood Fuel Load \n" + r"($kg$ $m^{-2}$)"
)
fuel.set_title("")

ds_i["S-hour_cos-Live_Wood"].plot(ax=isi_hs, color="tab:red", zorder=10)
set_axis_postion_full_fwx(
    isi_hs,
    "left",
    90,
    "Normalized [\n Cos(Solar Hour) \n x Fire Weather Index \n x Live Wood Fuel Load]",
)

isi_hs.set_title("")
hs.xaxis.set_major_formatter(mdates.DateFormatter("%H"))
hs.set_xlabel("Local Hour", fontsize=18)
fig.suptitle("Feature Engineering", fontsize=30)
fig.tight_layout()


# ds_space = fwf_ds.isel(time=18)
# fig = plt.figure(figsize=(18, 12))
# cmap = "jet"
# ax = fig.add_subplot(2, 2, 1)
# ds_space["U-lat_sin-Total_Fuel_Load"].salem.quick_map(
#     oceans=True, lakes=True, ax=ax, vmax=1, cmap=cmap
# )
# ax.set_title("Normalized \n Log(BUI) x Sin(Latitude) \n x Log(Total Fuel Load)")
# ax = fig.add_subplot(2, 2, 2)
# np.expm1(ds_space["U"]).salem.quick_map(
#     oceans=True, lakes=True, ax=ax, vmax=140, cmap=cmap
# )
# ax.set_title("Build Up Index")

# ax = fig.add_subplot(2, 2, 3)
# np.expm1(ds_space["Total_Fuel_Load"]).salem.quick_map(
#     oceans=True, lakes=True, ax=ax, vmax=20, cmap=cmap
# )
# ax.set_title(r"Total Fuel Load ($kg$ $m^{-2}$)")


# doi = pd.Timestamp(fwf_ds.time.values[0]).strftime("%Y-%m-%d")
# fig.suptitle("Feature Engineering Example \n" + doi, fontsize=30)
# fig.tight_layout()
# plt.savefig(str(data_dir) + "/images/frp-paper/feature-eng-map-bui-load.png", dpi=250)


# ds_space = fwf_ds.isel(time=18)
# fig = plt.figure(figsize=(18, 12))
# cmap = "jet"
# ax = fig.add_subplot(2, 2, 1)
# ds_space["U-lat_sin-Total_Fuel_Load"].salem.quick_map(
#     oceans=True, lakes=True, ax=ax, vmax=1, cmap=cmap
# )
# ax.set_title("Normalized \n Log(BUI) x Sin(Latitude) \n x Log(Total Fuel Load)")
# ax = fig.add_subplot(2, 2, 2)
# np.expm1(ds_space["U"]).salem.quick_map(oceans=True, lakes=True, ax=ax, vmax=115, cmap=cmap)
# ax.set_title("Build Up Index")

# ax = fig.add_subplot(2, 2, 3)
# ds_space["lat_sin"].salem.quick_map(oceans=True, lakes=True, ax=ax, cmap=cmap)
# ax.set_title("Sin(Latitude)")

# ax = fig.add_subplot(2, 2, 4)
# np.expm1(ds_space["Total_Fuel_Load"]).salem.quick_map(
#     oceans=True, lakes=True, ax=ax, vmax=20, cmap=cmap
# )
# ax.set_title(r"Total Fuel Load ($kg$ $m^{-2}$)")
# fig.suptitle("Feature Engineering", fontsize =30)
# fig.tight_layout()
# plt.savefig(
#     str(data_dir) + "/images/frp-paper/feature-eng-map-bui-lat-sin-load.png", dpi=250
# )


# %%
