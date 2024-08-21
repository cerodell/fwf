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

domain = "d02"
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense"
method = "averaged-v15"
### Open color map json
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

static_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
)
fwf_ds = salem.open_xr_dataset(str(data_dir) + f"/frp/sample_{domain}_{method}.nc")

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

np.expm1(ds_i["S"]).plot(ax=isi, color="tab:green", zorder=10)
set_axis_postion_full_fwx(isi, "right", 0, "Fire Weather Index")
isi.set_title("")

ds_i["OG_Total_Fuel_Load"].plot(ax=fuel, color="tab:orange", zorder=1)
set_axis_postion_full_fwx(fuel, "right", 90, "Total Fuel Load \n" + r"($kg$ $m^{-2}$)")
fuel.set_title("")

ds_i["S-hour_sin-Total_Fuel_Load"].plot(ax=isi_hs, color="tab:red", zorder=10)
set_axis_postion_full_fwx(
    isi_hs,
    "left",
    90,
    "Normalized [\n Sin(Solar Hour) \n x Log(Fire Weather Index) \n x Log(Total Fuel Load)]",
)

isi_hs.set_title("")
hs.xaxis.set_major_formatter(mdates.DateFormatter("%H"))
hs.set_xlabel("Local Hour", fontsize=18)
fig.suptitle("Feature Engineering", fontsize=30)
fig.tight_layout()
plt.savefig(
    str(data_dir) + "/images/frp-paper/feature-eng-time-fwi-hour-sin-fuels.png", dpi=250
)


# %%

ds_space = fwf_ds.isel(time=18)
fig = plt.figure(figsize=(18, 12))
cmap = "jet"
ax = fig.add_subplot(2, 2, 1)
ds_space["U-lat_sin-Total_Fuel_Load"].salem.quick_map(
    oceans=True, lakes=True, ax=ax, vmax=1, cmap=cmap
)
ax.set_title("Normalized \n Log(BUI) x Sin(Latitude) \n x Log(Total Fuel Load)")
ax = fig.add_subplot(2, 2, 2)
np.expm1(ds_space["U"]).salem.quick_map(
    oceans=True, lakes=True, ax=ax, vmax=140, cmap=cmap
)
ax.set_title("Build Up Index")

ax = fig.add_subplot(2, 2, 3)
np.expm1(ds_space["Total_Fuel_Load"]).salem.quick_map(
    oceans=True, lakes=True, ax=ax, vmax=20, cmap=cmap
)
ax.set_title(r"Total Fuel Load ($kg$ $m^{-2}$)")


doi = pd.Timestamp(fwf_ds.time.values[0]).strftime("%Y-%m-%d")
fig.suptitle("Feature Engineering Example \n" + doi, fontsize=30)
fig.tight_layout()
plt.savefig(str(data_dir) + "/images/frp-paper/feature-eng-map-bui-load.png", dpi=250)


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
