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


save_fig = False
paper_fig = True
domain = "d02"
method = "averaged-v19"


### Open color map json
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

bad_fwf = salem.open_xr_dataset(str(data_dir) + f"/frp/bad_sample_{domain}_{method}.nc")
fwf_ds = salem.open_xr_dataset(str(data_dir) + f"/frp/sample_{domain}_{method}.nc")
zero_full = np.zeros(fwf_ds["XLONG"].shape, dtype=float)

if "r_o_hourly" not in list(fwf_ds):
    r_oi = np.array(fwf_ds.r_o)
    r_o_plus1 = np.dstack((zero_full.T, r_oi.T)).T
    r_hourly_list = []
    for i in range(len(fwf_ds.Time)):
        r_hour = fwf_ds.r_o[i] - r_o_plus1[i]
        r_hourly_list.append(r_hour)
    r_hourly = np.stack(r_hourly_list)
    r_hourly = xr.DataArray(
        r_hourly, name="r_o_hourly", dims=("time", "south_north", "west_east")
    )
    fwf_ds["r_o_hourly"] = r_hourly
    fwf_ds["r_o_hourly"].attrs = fwf_ds.attrs

frp_i = fwf_ds.isel(time=18)
bad_frp_i = bad_fwf.isel(time=18)

# np.expm1(frp_i["Total_Fuel_Load"]).salem.quick_map(oceans=True, lakes=True)
# # frp_i["S"].salem.quick_map(oceans=True, lakes=True)

# frp_i["r_o_hourly"].salem.quick_map(vmax = 5, oceans=True, lakes=True)
# frp_i["FRP"].salem.quick_map(vmax=900, vmin=10, oceans=True, lakes=True)
# frp_i["S-hour_cos-Total_Fuel_Load"].salem.quick_map(oceans=True, lakes=True)

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
    ax.set_title(f"Init: {itime.strftime('%HZ %a %d %b %Y')}", loc="left", fontsize=12)
    ax.set_title(
        f"{setBold('Valid')}: {vtimes.strftime('%HZ %a %d %b %Y')}",
        fontsize=12,
        loc="right",
    )
    return


plt.rcParams.update({"font.size": 15})

# %%
fig = plt.figure(figsize=(20, 12))
# Set the main title
fig.suptitle("Fire Weather Forecast", fontsize=22, y=0.96)

# Add the Init text on the left
fig.text(
    0.35,
    0.92,
    f"Init: {itime.strftime('%HZ %a %d %b %Y')}",
    ha="left",
    fontsize=14,
    transform=fig.transFigure,
)

# Add the Valid text on the right
fig.text(
    0.65,
    0.92,
    f"{setBold('Valid')}: {vtimes.strftime('%HZ %a %d %b %Y')}",
    ha="right",
    fontsize=14,
    transform=fig.transFigure,
)
################  FRP  #####################
ax = fig.add_subplot(3, 3, 1)
var = "FRP"
vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
title, colors = str(cmaps[var]["title"]), cmaps[var]["colors"]
custom_cmap = LinearSegmentedColormap.from_list(
    "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
)
norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
frp_i[var].attrs["units"] = "MW"
frp_i[var].salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True)
ax.set_title(f"Fire Radiative Power (MW) (MLP-FE)")
ax.set_xticks([])


################  FWI  #####################
ax = fig.add_subplot(3, 3, 2)
var = "S"
vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
title, colors = str(cmaps[var]["title"]), cmaps[var]["colors18"]
custom_cmap = LinearSegmentedColormap.from_list(
    "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
)
norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
frp_i[var].attrs["units"] = ""
frp_i[var].salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True)
ax.set_title(title)
ax.set_xticks([])
ax.set_yticks([])

################  FUELS  #####################
ax = fig.add_subplot(3, 3, 3)
var = "Live_Wood"
frp_i[var].attrs["units"] = r"kg $m^{-2}$"
frp_i[var].salem.quick_map(cmap="Greens", ax=ax, oceans=True, lakes=True)
# ax.set_title("Total Fuel Load (kg m^-2)" + "\n")
# add_time_label(ax)
ax.set_title(r"Live Wood Fuel Load (kg $m^{-2}$)")
ax.set_xticks([])
ax.set_yticks([])


################ Bad FRP  #####################
ax = fig.add_subplot(3, 3, 4)
var = "FRP"
vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
title, colors = str(cmaps[var]["title"]), cmaps[var]["colors"]
custom_cmap = LinearSegmentedColormap.from_list(
    "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
)
norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
bad_frp_i[var].attrs["units"] = "MW"
bad_frp_i[var].salem.quick_map(
    cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True
)
ax.set_title(f"Fire Radiative Power (MW) (MLP-NoFE)")
ax.set_xticks([])


################ SOLAR HOUR #####################
ax = fig.add_subplot(3, 3, 5)
var = "hour_sin"
frp_i[var].attrs["units"] = ""
frp_i[var].salem.quick_map(cmap="rainbow", ax=ax, oceans=True, lakes=True)
ax.set_title("Sine of Solar Hour")
ax.set_xticks([])
ax.set_yticks([])

################ TEMP #####################
ax = fig.add_subplot(3, 3, 6)
var = "T"
vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
title, colors = str(cmaps[var]["title"]), cmaps[var]["colors"]
custom_cmap = LinearSegmentedColormap.from_list(
    "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
)
norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
frp_i[var].attrs["units"] = "°C"
frp_i[var].salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True)
ax.set_title(title)
ax.set_yticks([])
ax.set_xticks([])

################ RAIN #####################
ax = fig.add_subplot(3, 3, 7)
var = "r_o"
vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
title, colors = str(cmaps[var]["title"]), cmaps[var]["colors18"]
custom_cmap = LinearSegmentedColormap.from_list(
    "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
)
norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
frp_i[var].attrs["units"] = "mm"
frp_i[var].salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True)
ax.set_title(title)


################ WIND #####################
ax = fig.add_subplot(3, 3, 8)
var = "W"
vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
title, colors = str(cmaps[var]["title"]), cmaps[var]["colors18"]
custom_cmap = LinearSegmentedColormap.from_list(
    "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
)
norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
frp_i[var].attrs["units"] = r"km $hr^{-2}$"
frp_i[var].salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True)
ax.set_title(r"Wind Speed (km $hr^{-2}$)")
ax.set_yticks([])


################ RH #####################
ax = fig.add_subplot(3, 3, 9)
var = "H"
vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
title, colors = str(cmaps[var]["title"]), cmaps[var]["colors18"]
custom_cmap = LinearSegmentedColormap.from_list(
    "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
)
norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)
frp_i[var].attrs["units"] = "%"
frp_i[var].salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True)
ax.set_title(title)
ax.set_yticks([])


# fig.tight_layout()
if save_fig == True:
    fig.savefig(
        str(data_dir) + f"/images/frp-paper/map-fwx-{method[-3:]}.png",
        bbox_inches="tight",
        dpi=240,
    )
if paper_fig == True:
    fig.savefig(
        f"/Users/crodell/ams-frp/map-fwx-{method[-3:]}.pdf",
        bbox_inches="tight",
    )
    fig.savefig(
        f"/Users/crodell/ams-frp/map-fwx-{method[-3:]}.png",
        bbox_inches="tight",
        dpi=240,
    )

# %%
