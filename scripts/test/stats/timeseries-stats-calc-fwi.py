"""
This script compares how well the fwf model did compare to observed values.
It solves FWI from obs met and model met at obs points. Creates a time series of
all met/fwi values averaged across all wx stations in the model domain.
"""

import context
import json
import salem
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
from pylab import *

matplotlib.rcParams.update({"font.size": 14})


from scipy import stats
from sklearn.metrics import mean_squared_error, mean_absolute_error
from utils.stats import MBE

from pathlib import Path

from datetime import datetime
from context import data_dir, root_dir
from utils.fwi import (
    solve_ffmc,
    solve_dmc,
    solve_dc,
    solve_isi,
    solve_bui,
    solve_fwi,
)


import warnings

warnings.filterwarnings("ignore")
# cp -r /Volumes/Scratch/FWF-WAN00CG/d03/202104 202104

matplotlib.rcParams.update({"font.size": 14})

##################################################################
##################### Define Inputs   ###########################
## time of interest
start, stop = "2021-01-02", "2022-12-31"
## default moisture code values
F = 85.0
P = 6.0
D = 15.0

## models to compare
model = "wrf"
domains = ["d03", "d03C"]
trail_name = "02"

## define directory to save figures
save_dir = Path(str(data_dir) + f"/images/stats/test/")
save_dir.mkdir(parents=True, exist_ok=True)


##################################################################
#################### Open Data Files   ###########################

#### Open Datafiles and modify based on inputs
## open fwf attribute json file, used for axis labels in plotting
with open(str(root_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)

## open modle config file with varible names and attibutes
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)
# ## open intercomparsion data
# ds_wmo = xr.open_dataset(
#     str(data_dir) + "/intercomp/d02/WRF05060708/20210101-20221031.nc"
# )

ds_wmo = xr.open_dataset(
    str(data_dir) + f"/intercomp/{trail_name}/{model}/d03-20210101-20221231.nc",
)
ds_wmo = ds_wmo.load()
ds_wmo["time"] = ds_wmo["Time"]
all_obs_ds = ds_wmo.sel(domain="obs").sel(time=slice(start, stop))
ds_wmo = ds_wmo.sel(domain=["d03", "d02"])

## slice data acrcoss time of interest and drop any wx station with nan values.
## droping the nan values gibves a contiual data stream over the time of int
ds_wmoI = ds_wmo.sel(time="2021-01-01")
ds_wmo = ds_wmo.sel(time=slice(start, stop))

# ds_wmo = ds_wmo.dropna(dim="wmo")

krig_ds = salem.open_xr_dataset(str(data_dir) + f"/krig/fwf-krig-d03-elev.nc")
krig_ds[f"elev_bias"].attrs = krig_ds.attrs
krig_ds[f"T_bias"] = krig_ds[f"elev_bias"] * (9.8 / 1000)
krig_ds[f"T_bias"].attrs = krig_ds.attrs
krig_ds["T_bias"].salem.quick_map()
## reproject lat long of wxstation to wrf/fwf model projection (polar stereographic)


df_wmo = {
    "wmo": ds_wmo.wmo.values,
    "lats": ds_wmo.lats.values,
    "lons": ds_wmo.lons.values,
    "elev": ds_wmo.elev.values.astype(float),
    "name": ds_wmo.name.values,
    "tz_correct": ds_wmo.tz_correct.values,
}
df_wmo = pd.DataFrame(df_wmo)
obs_gdf = gpd.GeoDataFrame(
    df_wmo,
    crs="EPSG:4326",
    geometry=gpd.points_from_xy(df_wmo["lons"], df_wmo["lats"]),
).to_crs(
    "+proj=stere +lat_0=90 +lat_ts=53.25 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs"
)
obs_gdf["Easting"], obs_gdf["Northing"] = obs_gdf.geometry.x, obs_gdf.geometry.y

gridx = krig_ds.west_east.values
gridy = krig_ds.south_north.values

y = xr.DataArray(
    np.array(obs_gdf["Northing"]),
    dims="wmo",
    coords=dict(wmo=obs_gdf.wmo.values),
)
x = xr.DataArray(
    np.array(obs_gdf["Easting"]),
    dims="wmo",
    coords=dict(wmo=obs_gdf.wmo.values),
)

T_bias = krig_ds["T_bias"].interp(west_east=x, south_north=y, method="nearest")


##################################################################
######################### Solve FWI  #############################
## create datasets for each model and the observations. Used as input to solve FWI
ds_all = []
for domain in domains:
    if domain == "d03C":
        r_o = ds_wmo.sel(domain="d03")["precip"].values - 0.5
        r_f = np.where(r_o < 0, 0, r_o)

        ds_time = xr.Dataset(
            {
                "F": (["time", "wmo"], ds_wmo.sel(domain="d03")["ffmc"].values),
                "P": (["time", "wmo"], ds_wmo.sel(domain="d03")["dmc"].values),
                "D": (["time", "wmo"], ds_wmo.sel(domain="d03")["dc"].values),
                "W": (["time", "wmo"], ds_wmo.sel(domain="d03")["ws"].values),
                "WD": (["time", "wmo"], ds_wmo.sel(domain="d03")["wdir"].values),
                "T": (["time", "wmo"], ds_wmo.sel(domain="d03")["temp"].values),
                "TD": (["time", "wmo"], ds_wmo.sel(domain="d03")["td"].values),
                "r_o": (["time", "wmo"], r_f),
            }
        )
        F = ds_wmoI.sel(domain="d03")["ffmc"].values
        P = ds_wmoI.sel(domain="d03")["dmc"].values
        D = ds_wmoI.sel(domain="d03")["dc"].values
    else:
        ds_time = xr.Dataset(
            {
                "F": (["time", "wmo"], ds_wmo.sel(domain=domain)["ffmc"].values),
                "P": (["time", "wmo"], ds_wmo.sel(domain=domain)["dmc"].values),
                "D": (["time", "wmo"], ds_wmo.sel(domain=domain)["dc"].values),
                "W": (["time", "wmo"], ds_wmo.sel(domain=domain)["ws"].values),
                "WD": (["time", "wmo"], ds_wmo.sel(domain=domain)["wdir"].values),
                "T": (["time", "wmo"], ds_wmo.sel(domain=domain)["temp"].values),
                "TD": (["time", "wmo"], ds_wmo.sel(domain=domain)["td"].values),
                "r_o": (["time", "wmo"], ds_wmo.sel(domain=domain)["precip"].values),
            }
        )
        F = ds_wmoI.sel(domain=domain)["ffmc"].values
        P = ds_wmoI.sel(domain=domain)["dmc"].values
        D = ds_wmoI.sel(domain=domain)["dc"].values
    ds_time["r_o"] = xr.where(ds_time["r_o"] < 0, 0.0, ds_time["r_o"])

    ## solve RH and add to datasets
    RH = (
        (6.11 * 10 ** (7.5 * (ds_time.TD / (237.7 + ds_time.TD))))
        / (6.11 * 10 ** (7.5 * (ds_time.T / (237.7 + ds_time.T))))
        * 100
    )
    RH = xr.where(RH > 100, 100, RH)
    RH = xr.DataArray(RH, name="H", dims=("time", "wmo"))
    ds_time["H"] = RH
    if np.min(ds_time.H) > 90:
        raise ValueError("ERROR: Check TD nonphysical RH values")

    date_range = ds_wmo.time.values

    ## loop and solve fwi system for specified range of days
    datasets = []
    for i in range(len(date_range)):
        ts = pd.to_datetime(str(date_range[i]))
        ds = ds_time.isel(time=i)
        month = int(ts.strftime("%m"))
        ## Daylength factor in Duff Moisture Code
        L_e = [6.5, 7.5, 9.0, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8.0, 7.0, 6.0]
        L_e = L_e[month - 1]

        ## Daylength adjustment in Drought Code
        L_f = [-1.6, -1.6, -1.6, 0.9, 3.8, 5.8, 6.4, 5.0, 2.4, 0.4, -1.6, -1.6]
        L_f = L_f[month - 1]
        ds = solve_ffmc(ds, F)

        ds = solve_dmc(ds, P, L_e)
        ds = solve_dc(ds, D, L_f)
        ds = solve_isi(ds)
        ds = solve_bui(ds)
        ds = solve_fwi(ds)
        datasets.append(ds)
        # redefine moisture codes then drop for interation
        if domain == "_wrfbias":
            F = ds.F + 1.32
            P = ds.P + 8.66
            D = ds.D + 32.13
        else:
            F = ds.F
            P = ds.P
            D = ds.D

        ds = ds.drop_vars(["F", "P", "D"])

    ## concat all times on a new dimension time
    ds_concat = xr.concat(datasets, dim="time")
    for var in list(ds_concat):
        try:
            name_lower = cmaps[var]["name"].lower()
            ds_concat[name_lower] = ds_concat[var]
            ds_concat = ds_concat.drop([var])
        except:
            try:
                ds_concat[var.lower()] = ds_concat[var]
                if var == "r_w":
                    pass
                else:
                    ds_concat = ds_concat.drop([var])
            except:
                pass
    ds_concat["time"] = ds_wmo["Time"]
    ds_2021 = ds_concat.sel(time=slice("2021-05-01", "2021-09-30"))
    ds_2022 = ds_concat.sel(time=slice("2022-05-01", "2022-09-30"))
    null_ds = ds_concat.sel(time=slice("2021-10-01", "2022-04-30"))
    null_array = np.full(null_ds["temp"].shape, np.nan)
    for var in null_ds:
        null_ds[var] = (("time", "wmo"), null_array)

    ds_2021 = ds_2021.drop("Time")
    ds_2022 = ds_2022.drop("Time")
    null_ds = null_ds.drop("Time")

    prov_ds = xr.combine_nested(
        [ds_2021, null_ds, ds_2022], concat_dim="time"
    ).transpose()
    # for var in ["elev", "name", "prov", "id", "domain"]:
    #     prov_ds[var] = prov_ds[var].astype(str)
    ds_all.append(prov_ds)


## define directory to save figures
save_dir = Path(str(data_dir) + f"/images/stats/{trail_name}/{model}/timeseries/")
save_dir.mkdir(parents=True, exist_ok=True)


domains_ds = ds_all
ds_2021 = all_obs_ds.sel(time=slice("2021-05-01", "2021-09-30"))
ds_2022 = all_obs_ds.sel(time=slice("2022-05-01", "2022-09-30"))
null_ds = all_obs_ds.sel(time=slice("2021-10-01", "2022-04-30"))
null_array = np.full(null_ds["temp"].shape, np.nan)
for var in null_ds:
    null_ds[var] = (("time", "wmo"), null_array)

ds_2021 = ds_2021.drop("Time")
ds_2022 = ds_2022.drop("Time")
null_ds = null_ds.drop("Time")

all_obs_ds = xr.combine_nested([ds_2021, null_ds, ds_2022], concat_dim="time")

date_range = pd.date_range(all_obs_ds.time.values[0], all_obs_ds.time.values[-1])
time = np.array(ds_wmo.time.dt.strftime("%Y-%m-%d"), dtype="<U10")
start_time = datetime.strptime(str(time[0]), "%Y-%m-%d").strftime("%Y%m%d")
end_time = datetime.strptime(str(time[-1]), "%Y-%m-%d").strftime("%Y%m%d")
colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

domains_ds[0].isel(wmo=100)["temp"].plot()
all_obs_ds.isel(wmo=100)["temp"].plot()


def hex(name):
    hex_list = []
    cmap = cm.get_cmap(name, 20)  # PiYG
    for i in range(cmap.N):
        rgba = cmap(i)
        hex_list.append(matplotlib.colors.rgb2hex(rgba))
    return hex_list


colors_d02 = hex("Blues_r")
colors_d03 = hex("Greens_r")
colors_d03C = hex("Oranges_r")
colors_hrdps = hex("Reds_r")
colors_rdps = hex("Purples_r")

test = domains_ds[0]
test["wmo"] = all_obs_ds["wmo"]
(test.sel(wmo=71413)["temp"] - all_obs_ds.sel(wmo=71413)["temp"]).plot()


# %%
def fct_plot(
    j, idx, var, obs_ds, obs_flat, obs_flat_null, stats_text, ax, ax2, ls, name
):

    domain = domains[j]
    if domain == "d02":
        dom_name = "WRF 12km"
        # colors = colors_d02
    elif domain == "d03":
        dom_name = "WRF 4km"
    elif domain == "d03C":
        dom_name = "WRFC 4km "
    elif domain == "hrdps":
        dom_name = "HRDPS 2.5km"
    elif domain == "rdps":
        dom_name = "RDPS 10km"
    elif domain == "era5":
        dom_name = "ERA5 30km"
    else:
        pass
    # colors = colors
    if (name == "max   ") or (name == "min   "):
        i = 1
    elif name == "hourly":
        i = 2
    else:
        i = 0

    fct_ds = xr.where(obs_ds.isnull(), np.nan, domains_ds[j][var])
    fct_flat = fct_ds.values.ravel()
    fct_flat = fct_flat[~np.isnan(obs_flat_null)]
    fct_flat = np.delete(fct_flat, idx)

    if var == "precip":
        fct_flat = fct_flat[obs_flat > 0.0]
        obs_flat = obs_flat[obs_flat > 0.0]
    else:
        pass
    # print(np.unique(obs_ds.isnull(), return_counts=True))
    # print(np.unique(fct_ds.isnull(), return_counts=True))
    r2value = "{:.2f}".format(round(stats.pearsonr(obs_flat, fct_flat)[0], 2))
    rmse = "{:.2f}".format(
        round(
            mean_squared_error(
                obs_flat,
                fct_flat,
                squared=False,
            ),
            2,
        )
    )
    mbe = round(MBE(obs_flat, fct_flat), 2)
    if mbe < 0:
        mbe = "{:.2f}".format(mbe)
    else:
        mbe = " " + "{:.2f}".format(mbe)

    mae = "{:.2f}".format(
        round(
            mean_absolute_error(obs_flat, fct_flat),
            2,
        )
    )
    fct_mean = fct_ds.mean(dim="wmo")  # .dropna(dim = 'time')
    print(fct_mean)

    ax.plot(
        fct_mean.time,
        fct_mean,
        label=dom_name,  # + "-" + name,
        zorder=10,
        color=colors[j + i],
        lw=0.8,
        ls=ls,
        # alpha = 0.8
    )
    ax2.plot(
        date_range,
        fct_mean,
        label=dom_name,  # + "-" + name,
        zorder=10,
        color=colors[j + i],
        lw=0.8,
        ls=ls,
        # alpha = 0.8
    )

    stats_text += (
        f"{dom_name}, (r): {r2value}, (mbe): {mbe}, (rmse): {rmse}, (mae): {mae},"
    )

    return stats_text, colors[j + i]


# %%
# fig = plt.figure(figsize=[10, 14])
# var_list = ["temp", "td", "rh", "ws", "wdir", "precip"]
# var_list = ["ffmc", "dmc", "dc", "bui", "isi", "fwi"]
var_list = [
    "temp",
    "td",
    "rh",
    "ws",
    "wdir",
    "precip",
    "ffmc",
    "dmc",
    "dc",
    "bui",
    "isi",
    "fwi",
]
# var_list = ["precip"]

length = len(var_list)
for i in range(length):
    # ax = fig.add_subplot(length + 1, 1, i + 1)
    fig, (ax, ax2) = plt.subplots(1, 2, sharey=True, facecolor="w", figsize=[14, 3])
    var = var_list[i]
    stats_text = ""
    obs_ds = all_obs_ds[var]
    obs_mean = obs_ds.mean(dim="wmo")  # .dropna(dim = 'time')
    # obs_mean = obs_ds.sel(wmo = 71673)  # .dropna(dim = 'time')
    t_mesh = np.arange(0, len((obs_ds.time)))
    ww, tt = np.meshgrid(obs_ds.wmo.values, t_mesh)
    obs_flat_null = obs_ds.values.ravel()
    wx_station = ww.ravel()
    obs_flat = obs_flat_null[~np.isnan(obs_flat_null)]
    wx_station = wx_station[~np.isnan(obs_flat_null)]
    # find indexes two outside standard deviation
    idx = np.where(np.abs(obs_flat - np.mean(obs_flat)) > 2 * np.std(obs_flat))
    obs_flat = np.delete(obs_flat, idx)
    wx_station, wx_count = np.unique(np.delete(wx_station, idx), return_counts=True)
    print(var)
    print(list(wx_station[np.where(wx_count < 30)[0]]))
    print(len(list(wx_station[np.where(wx_count < 30)[0]])))
    print("=============================================")
    color_table = []
    for j in range(len(domains)):
        stats_text, color_t = fct_plot(
            j,
            idx,
            var,
            obs_ds,
            obs_flat,
            obs_flat_null,
            stats_text,
            ax,
            ax2,
            ls="-",
            name="noon  ",
        )
        color_table.append(color_t)
        # if (var == "dc") | (var == "dmc") | (var == "bui"):
        #     pass
        # else:
        # try:
        #     if var == "rh":
        #         name = "min   "
        #     else:
        #         name = "max   "
        #     stats_text, color_t = fct_plot(
        #         j,
        #         idx,
        #         "m" + var,
        #         obs_ds,
        #         obs_flat,
        #         obs_flat_null,
        #         stats_text,
        #         ax,
        #         ax2,
        #         ls="--",
        #         name=name,
        #     )
        #     color_table.append(color_t)
        # except:
        #     pass
        # try:
        #     stats_text,color_t = fct_plot(
        #         j,
        #         idx,
        #         "h" + var,
        #         obs_ds,
        #         obs_flat,
        #         obs_flat_null,
        #         stats_text,
        #         ax,
        #         ax2,
        #         ls="dotted",
        #         name="hourly",
        #     )
        #     color_table.append(color_t)
        # except:
        #     pass

    # anchored_text = AnchoredText(
    #     stats_text[:-3],
    #     loc="upper right",
    #     prop={"size": 8, "zorder": 10},
    #     bbox_to_anchor=(2.015, 1.32),
    #     bbox_transform=ax.transAxes,
    # )
    try:
        ax.set_ylabel(fr"$({var_dict[var]['units']})$", fontsize=14)
    except:
        pass
    ax.tick_params(axis="x", rotation=45)
    ax2.tick_params(axis="x", rotation=45)
    ax.plot(
        obs_mean.time,
        obs_mean,
        label="Observation",
        zorder=2,
        color="k",
        lw=2,
    )
    ax2.plot(
        date_range,
        obs_mean,
        label="Observation",
        zorder=2,
        color="k",
        lw=2,
    )
    ax.yaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
    ax.xaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
    ax2.yaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
    ax2.xaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
    # ax2.add_artist(anchored_text)

    ax.set_xlim([pd.Timestamp("2021-04-15"), pd.Timestamp("2021-10-15")])
    ax2.set_xlim([pd.Timestamp("2022-04-15"), pd.Timestamp("2022-10-15")])
    # ax.set_xlim([pd.Timestamp("2021-03-15"), pd.Timestamp("2021-11-15")])
    # ax2.set_xlim([pd.Timestamp("2022-03-15"), pd.Timestamp("2022-11-15")])
    # ax.set_xlim([pd.Timestamp("2021-01-01"), pd.Timestamp("2021-12-31")])
    # ax2.set_xlim([pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")])
    # ax.set_xlim([pd.Timestamp("2021-01-01"), pd.Timestamp("2021-05-01")])
    # ax2.set_xlim([pd.Timestamp("2022-01-01"), pd.Timestamp("2022-05-01")])
    # hide the spines between ax and ax2
    ax.spines["right"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.yaxis.tick_right()
    ax2.tick_params(labelright="on")
    plt.subplots_adjust(wspace=0.08)

    d = 0.015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color="k", clip_on=False)
    ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)
    ax.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)
    ax2.plot((-d, +d), (-d, +d), **kwargs)

    # Create the table data
    lst = stats_text.split(",")[:-1]
    x = 5
    y = int(len(lst) / x)
    data = np.array(lst).reshape(y, x)

    numbers_only = []
    for string in lst:
        numbers = re.findall(r"-?\d+\.\d+|-?\d+", string)
        if numbers:
            numbers_only.extend(numbers)
        else:
            numbers_only.extend("1")
    try:
        numbers_only = np.array(numbers_only).reshape(y, x).astype(float)
    except:
        numbers_only = np.array(numbers_only).astype(float)[1:]

    cell_colors = np.empty((y, x), dtype="U10")
    cell_colors.fill("white")
    good_color, bad_color = "lightblue", "lightpink"
    color_table = np.stack(color_table)

    try:
        cell_colors[
            np.where(numbers_only[:, 1] == np.min(numbers_only[:, 1]))[0], 1
        ] = bad_color
        cell_colors[
            np.where(np.abs(numbers_only[:, 2]) == np.max(np.abs(numbers_only[:, 2])))[
                0
            ],
            2,
        ] = bad_color
        cell_colors[
            np.where(numbers_only[:, 3] == np.max(numbers_only[:, 3]))[0], 3
        ] = bad_color
        cell_colors[
            np.where(numbers_only[:, 4] == np.max(numbers_only[:, 4]))[0], 4
        ] = bad_color

        cell_colors[
            np.where(numbers_only[:, 1] == np.max(numbers_only[:, 1]))[0], 1
        ] = good_color
        cell_colors[
            np.where(np.abs(numbers_only[:, 2]) == np.min(np.abs(numbers_only[:, 2])))[
                0
            ],
            2,
        ] = good_color
        cell_colors[
            np.where(numbers_only[:, 3] == np.min(numbers_only[:, 3]))[0], 3
        ] = good_color
        cell_colors[
            np.where(numbers_only[:, 4] == np.min(numbers_only[:, 4]))[0], 4
        ] = good_color

        # Create the second set of axes for the table
        ax_table = fig.add_axes([0.55, 0.87, 0.33, 0.2])

        # Create the table and add it to the second set of axes

        table = ax_table.table(
            cellText=data, loc="center", cellColours=cell_colors, fontsize=14
        )
        for i in range(len(color_table)):
            # Get the cell object at row 0, column 1
            cell = table.get_celld()[(i, 0)]

            # Set the font color of the cell to red
            cell.set_text_props(color=color_table[i], weight="bold")
    except:
        # Create the second set of axes for the table
        ax_table = fig.add_axes([0.55, 0.87, 0.33, 0.2])

        # Create the table and add it to the second set of axes

        table = ax_table.table(cellText=data, loc="center")
        for i in range(len(color_table)):
            # Get the cell object at row 0, column 1
            cell = table.get_celld()[(i, 0)]

            # Set the font color of the cell to red
            cell.set_text_props(color=color_table[i], weight="bold")
    # Hide the table axis ticks and labels
    ax_table.axis("off")

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.48, 1.24),
        ncol=4,
        fancybox=True,
        shadow=True,
        prop={"size": 9},
    )
    fig.suptitle(var_dict[var.lower()]["description"], fontsize=20, y=1.25)
    # plt.close()
    fig.savefig(
        str(save_dir) + f"/{var}-fireseason-calc.png", bbox_inches="tight", dpi=250
    )
