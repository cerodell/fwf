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
from matplotlib import gridspec
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, zoomed_inset_axes


from sklearn.linear_model import LinearRegression
from scipy import stats

from utils.krig import plotvariogram

from datetime import datetime
from context import data_dir, root_dir
import matplotlib
from pathlib import Path

startTime = datetime.now()
matplotlib.rcParams.update({"font.size": 14})
plt.rc("font", family="sans-serif")
plt.rc("text", usetex=True)

##################################################################
##################### Define Inputs   ###########################

startTime = datetime.now()
paper = True
model = "wrf"
domain = "d02"
var = "F"
trail_name = "04"

vars = ["F", "P", "D", "R", "U", "S", "T", "H", "W", "r_o"]
vars = ["W"]


if paper == True:
    save_dir = Path("/Users/crodell/ams-fwf/LaTeX/img/fwf/")
    save_dir.mkdir(parents=True, exist_ok=True)
else:
    save_dir = Path(str(data_dir) + f"/images/paper/elev_bias/")
    save_dir.mkdir(parents=True, exist_ok=True)
##################################################################
##################### Open Data Files  ###########################
## open modle config file with varible names and attibutes
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)


# try:
ds_old = xr.open_dataset(
    str(data_dir) + f"/intercomp/{trail_name}/{model}/d03-20210101-20221231.nc",
)
# except:
#     ds = xr.open_dataset(
#         str(data_dir) + f"/intercomp/{trail_name}/{model}/20210101-20221231.nc",
#     )
ds = xr.open_dataset(
    str(data_dir) + f"/intercomp/{trail_name}/{model}/d03-20210301-20231101.nc",
)

dims_order = ["time", "domain", "wmo"]
ds = ds.transpose(*dims_order)
for var in ["elev", "name", "prov", "id", "domain"]:
    ds[var] = ds[var].astype(str)
## make time dim sliceable with datetime
ds["time"] = ds["Time"]
ds = ds.chunk("auto")

## make time dim sliceable with datetime
# ds["time"] = ds["Time"]
wmo_idx = np.loadtxt(str(data_dir) + "/intercomp/02/wx_station.txt").astype(int)
ds = ds.sel(wmo=wmo_idx)

for wx in [71232, 71245]:
    ds = ds.drop_sel(wmo=wx)
## make time dim sliceable with datetime
# ds["time"] = ds["Time"]

# ds_2021 = ds.sel(time=slice("2021-04-01", "2021-10-31"))
# ds_2022 = ds.sel(time=slice("2022-04-01", "2022-10-31"))
# null_ds = ds.sel(time=slice("2021-11-01", "2022-03-31"))
# null_array = np.full(null_ds["temp"].shape, np.nan)
# for var in null_ds:
#     null_ds[var] = (("time", "domain", "wmo"), null_array)

# ds_2021 = ds_2021.drop("Time")
# ds_2022 = ds_2022.drop("Time")
# null_ds = null_ds.drop("Time")

# ds = xr.combine_nested([ds_2021, null_ds, ds_2022], concat_dim="time")

ds_2021 = ds.sel(time=slice("2021-04-01", "2021-10-31"))
ds_2022 = ds.sel(time=slice("2022-04-01", "2022-10-31"))
ds_2023 = ds.sel(time=slice("2023-04-01", "2023-10-31"))

null21_ds = ds.sel(time=slice("2021-11-01", "2022-03-30"))
null22_ds = ds.sel(time=slice("2022-11-01", "2023-03-30"))


null_array = np.full(null21_ds["fwi"].shape, np.nan)
for var in null21_ds:
    null21_ds[var] = (("time", "domain", "wmo"), null_array)
    null22_ds[var] = (("time", "domain", "wmo"), null_array)

ds_2021 = ds_2021.drop("Time")
ds_2022 = ds_2022.drop("Time")
ds_2023 = ds_2023.drop("Time")
null21_ds = null21_ds.drop("Time")
null22_ds = null22_ds.drop("Time")

ds = xr.combine_nested(
    [ds_2021, null21_ds, ds_2022, null22_ds, ds_2023], concat_dim="time"
)


# for var in ["elev", "name", "prov", "id", "domain"]:
#     ds[var] = ds[var].astype(str)

##################################################################

for cord in ["elev", "name", "prov", "id"]:
    ds[cord] = ds[cord].astype(str)
ds["elev"] = ds["elev"].astype(float)
ds["elev"] = xr.where(ds["elev"] < 0, 0, ds["elev"])

# for cord in ["elev", "name", "prov", "id"]:
#     ds[cord] = ds[cord].astype(str)

# ds = ds.chunk("auto")


def make_mean_bias(ds, domain):
    static_ds = salem.open_xr_dataset(
        (str(data_dir) + f"/static/static-vars-{model}-{domain}.nc")
    )
    ds_bias = ds.sel(domain=domain) - ds.sel(domain="obs")
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
    column_name = "precip"

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
    df_wmo["elev"] = df_wmo[f"elev"].values.astype(float)
    df_wmo["elev_model"] = elev_model
    df_wmo["elev_bias"] = df_wmo["elev_model"] - df_wmo["elev"]
    df_wmo["elev_bias_abs"] = df_wmo["elev_bias"].abs()
    print(f"{len(df_wmo)} number of observations")
    return df_wmo


df_wmo_d03 = make_mean_bias(ds, "d03")
df_wmo_d02 = make_mean_bias(ds, "d02")

# for var in vars:


def plot_bias(var, df_wmo, ax):
    var_lower = cmaps[var]["name"].lower()
    paper = cmaps[var]["paper"]

    vmin = paper["vmin"]
    vmax = paper["vmax"]
    cmap = paper["cmap"]
    df_wmo["var_lower_abs"] = df_wmo[var_lower].abs()

    sc = ax.scatter(
        df_wmo["elev_model"],
        df_wmo["elev"],
        c=df_wmo[var_lower],
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
    )
    xpoints = ypoints = plt.xlim()
    ax.plot(
        xpoints, ypoints, linestyle="--", color="k", lw=0.8, scalex=False, scaley=False
    )

    # this is an inset axes over the main axes
    axins = inset_axes(
        ax,
        width="30%",  # width = 30% of parent_bbox
        height="25%",  # height : 1 inch
        loc="upper left",
    )
    n, bins, patches = plt.hist(df_wmo[var_lower])
    axins.yaxis.set_label_position("right")
    axins.yaxis.tick_right()  # Move y-axis ticks and labels to the right
    axins.set_xlabel(var_lower.title(), fontsize=16)
    axins.set_ylabel("Count", fontsize=16)
    axins.tick_params(axis="both", which="minor", labelsize=14)

    return sc


# %%
varsum = ""
var = "T"
varsum += cmaps[var]["name"].lower()
fig = plt.figure(figsize=(12, 18))
gs = gridspec.GridSpec(4, 3, width_ratios=[1, 1, 0.05])

#################        TEMP       ###################
########################
ax = plt.subplot(gs[0])
ax.set_title("WRF 4-km", fontsize=18)
ax.annotate(
    "A)", xy=(-0.05, 1.04), xycoords="axes fraction", fontsize=22, fontweight="bold"
)
ax.set_xticklabels([])
sc = plot_bias(var, df_wmo_d03, ax)
ax.set_ylabel("Station Elevation (m)", fontsize=18)
ax.tick_params(axis="both", labelsize=18)

########################
ax = plt.subplot(gs[1])
ax.set_title("WRF 12-km", fontsize=18)
ax.annotate(
    "B)", xy=(-0.05, 1.04), xycoords="axes fraction", fontsize=22, fontweight="bold"
)
sc = plot_bias(var, df_wmo_d02, ax)
ax.set_yticklabels([])
ax.set_xticklabels([])
ax.tick_params(axis="both", labelsize=18)

########################
ax = plt.subplot(gs[2])
ax.set_yticks([])
ax.set_xticks([])
cbar = plt.colorbar(sc, cax=ax, orientation="vertical", fraction=1, pad=0.04)
cbar.ax.tick_params(labelsize=18)
cbar.set_label(
    r"2-m Temperature (C)" + "\n Mean Bias",
    # + " \n  01 April - 31 Oct (2021"
    # + r"\&"
    # + "2022) ",
    rotation=90,
    fontsize=18,
    labelpad=15,
)
#####################################################


#################        RH       ###################
var = "H"
varsum += cmaps[var]["name"].lower()
########################
ax = plt.subplot(gs[3])
ax.annotate(
    "C)", xy=(-0.05, 1.04), xycoords="axes fraction", fontsize=22, fontweight="bold"
)
ax.set_xticklabels([])
sc = plot_bias(var, df_wmo_d03, ax)
ax.set_ylabel("Station Elevation (m)", fontsize=18)
ax.tick_params(axis="both", labelsize=18)

########################
ax = plt.subplot(gs[4])
ax.annotate(
    "D)", xy=(-0.05, 1.04), xycoords="axes fraction", fontsize=22, fontweight="bold"
)
sc = plot_bias(var, df_wmo_d02, ax)
ax.set_yticklabels([])
ax.set_xticklabels([])
ax.tick_params(axis="both", labelsize=18)

########################
ax = plt.subplot(gs[5])
ax.set_yticks([])
ax.set_xticks([])
cbar = plt.colorbar(sc, cax=ax, orientation="vertical", fraction=1, pad=0.04)
cbar.ax.tick_params(labelsize=18)
cbar.set_label(
    r"2-m Relative Humidity (\%)" + "\n Mean Bias",
    # + " \n  01 April - 31 Oct (2021"
    # + r"\&"
    # + "2022) ",
    rotation=90,
    fontsize=18,
    labelpad=15,
)
#####################################################


#################        WS       ###################
var = "W"
varsum += cmaps[var]["name"].lower()
########################
ax = plt.subplot(gs[6])
ax.annotate(
    "E)", xy=(-0.05, 1.04), xycoords="axes fraction", fontsize=22, fontweight="bold"
)
sc = plot_bias(var, df_wmo_d03, ax)
ax.set_ylabel("Station Elevation (m)", fontsize=18)
ax.set_xticklabels([])
ax.tick_params(axis="both", labelsize=18)

########################
ax = plt.subplot(gs[7])
ax.annotate(
    "F)", xy=(-0.05, 1.04), xycoords="axes fraction", fontsize=22, fontweight="bold"
)
sc = plot_bias(var, df_wmo_d02, ax)
ax.set_yticklabels([])
ax.set_xticklabels([])
ax.tick_params(axis="both", labelsize=18)

########################
ax = plt.subplot(gs[8])
ax.set_yticks([])
ax.set_xticks([])
cbar = plt.colorbar(sc, cax=ax, orientation="vertical", fraction=1, pad=0.04)
cbar.ax.tick_params(labelsize=18)
cbar.set_label(
    r"10-m Wind Speed (km/hr)" + "\n Mean Bias",
    # + " \n  01 April - 31 Oct (2021"
    # + r"\&"
    # + "2022) ",
    rotation=90,
    fontsize=18,
    labelpad=15,
)
#####################################################


#################        r_o       ###################
var = "r_o"
varsum += cmaps[var]["name"].lower()
########################
ax = plt.subplot(gs[9])
ax.annotate(
    "G)", xy=(-0.05, 1.04), xycoords="axes fraction", fontsize=22, fontweight="bold"
)
sc = plot_bias(var, df_wmo_d03, ax)
ax.set_xlabel("Model Elevation (m)", fontsize=18)
ax.set_ylabel("Station Elevation (m)", fontsize=18)
ax.tick_params(axis="both", labelsize=18)

########################
ax = plt.subplot(gs[10])
ax.annotate(
    "H)", xy=(-0.05, 1.04), xycoords="axes fraction", fontsize=22, fontweight="bold"
)
sc = plot_bias(var, df_wmo_d02, ax)
ax.set_yticklabels([])
ax.set_xlabel("Model Elevation (m)", fontsize=18)
ax.tick_params(axis="both", labelsize=18)

########################
ax = plt.subplot(gs[11])
ax.set_yticks([])
ax.set_xticks([])
cbar = plt.colorbar(sc, cax=ax, orientation="vertical", fraction=1, pad=0.04)
cbar.ax.tick_params(labelsize=18)
cbar.set_label(
    r"Precipiation (mm)" + "\n Mean Bias",
    # + " \n  01 April - 31 Oct (2021"
    # + r"\&"
    # + "2022) ",
    rotation=90,
    fontsize=18,
    labelpad=15,
)
#####################################################
fig.suptitle(
    f"Weather Station Elevation vs Modeled Elevation at 917 station locations",
    fontsize=22,
    y=0.99,
    x=0.45,
)

plt.tight_layout()
plt.savefig(
    str(save_dir) + f"/{varsum}-model-v-obs-elevation.png",
    dpi=250,
    bbox_inches="tight",
)
plt.savefig(
    str(save_dir) + f"/{varsum}-model-v-obs-elevation.pdf",
    # bbox_inches="tight",
)
# %%
