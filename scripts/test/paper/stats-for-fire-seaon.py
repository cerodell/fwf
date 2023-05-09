import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
import scipy.stats
import re

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import matplotlib.pyplot as plt
from pylab import *

from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.ndimage as ndimage
from scipy.ndimage import gaussian_filter
from pylab import *

from context import data_dir, root_dir
from datetime import datetime, date, timedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.metrics import r2_score
from utils.stats import MBE
from scipy import stats
from matplotlib.offsetbox import AnchoredText
import matplotlib
from pathlib import Path

matplotlib.rcParams.update({"font.size": 14})


import matplotlib.pyplot as plt

# # Create the main plot
# fig, ax = plt.subplots()
# ax.plot([1, 2, 3], [4, 5, 6])

# # Create the table data
# data = [['', 'Col1', 'Col2'],
#         ['Row1', '1', '2'],
#         ['Row2', '3', '4']]

# # Create the fill colors for the table cells
# cell_colors = [['lightgray', 'lightgray', 'lightgray'],
#                ['lightblue', 'lightgreen', 'lightblue'],
#                ['lightgreen', 'lightblue', 'lightgreen']]

# # Create the second set of axes for the table
# ax_table = fig.add_axes([0.65, 0.7, 0.3, 0.2])

# # Create the table and add it to the second set of axes
# table = ax_table.table(cellText=data, cellColours=cell_colors, loc='center')

# # Hide the table axis ticks and labels
# ax_table.axis('off')

# # Show the plot
# plt.show()


__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

########################### INPUTS ###########################

config = {"wrf": ["d02", "d03"], "eccc": ["rdps", "hrdps"]}

model = "nwp"
# domains = ["d02", "d03"]
domains = ["d02", "d03", "rdps", "hrdps"]
trail_name = "02"
fwf_dir = f"/Volumes/WFRT-Ext24/fwf-data/"

######################### END INPUTS #########################

#################### Open static datasets ####################

with open(str(root_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)

wx_ds = xr.open_dataset(str(data_dir) + f"/obs/observations-all-20191231-20221231.nc")
# wx_ds = wx_ds.drop_sel(wmo=2275)

try:
    prov_ds = xr.open_dataset(
        str(data_dir) + f"/intercomp/{trail_name}/{model}/20210401-20221101-null.nc"
    )
except:
    ds = xr.open_dataset(
        str(data_dir) + f"/intercomp/{trail_name}/{model}/20210101-20221231.nc",
    )
    ## make time dim sliceable with datetime
    ds["time"] = ds["Time"]

    ## index between fire season
    ds = ds.sel(time=slice("2021-04-01", "2022-10-31"))

    ds_2021 = ds.sel(time=slice("2021-04-01", "2021-10-31"))
    ds_2022 = ds.sel(time=slice("2022-04-01", "2022-10-31"))
    null_ds = ds.sel(time=slice("2021-11-01", "2022-03-31"))
    null_array = np.full(null_ds["temp"].shape, np.nan)
    for var in null_ds:
        null_ds[var] = (("time", "domain", "wmo"), null_array)

    ds_2021 = ds_2021.drop("Time")
    ds_2022 = ds_2022.drop("Time")
    null_ds = null_ds.drop("Time")

    prov_ds = xr.combine_nested([ds_2021, null_ds, ds_2022], concat_dim="time")
    for var in ["elev", "name", "prov", "id", "domain"]:
        prov_ds[var] = prov_ds[var].astype(str)
    prov_ds.to_netcdf(
        str(data_dir) + f"/intercomp/{trail_name}/{model}/20210401-20221101-null.nc",
        mode="w",
    )


######################## Set up plotting stuff ###########################

## define directory to save figures
save_dir = Path(str(data_dir) + f"/images/stats/{trail_name}/{model}/timeseries/")
save_dir.mkdir(parents=True, exist_ok=True)

date_range = pd.date_range(prov_ds.time.values[0], prov_ds.time.values[-1])
time = np.array(prov_ds.time.dt.strftime("%Y-%m-%d"), dtype="<U10")
start_time = datetime.strptime(str(time[0]), "%Y-%m-%d").strftime("%Y%m%d")
end_time = datetime.strptime(str(time[-1]), "%Y-%m-%d").strftime("%Y%m%d")
colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

all_obs_ds = prov_ds.sel(domain="obs")
domains_ds = [prov_ds.sel(domain=domain) for domain in domains]


########################################################################


def hex(name):
    hex_list = []
    cmap = cm.get_cmap(name, 20)  # PiYG
    for i in range(cmap.N):
        rgba = cmap(i)
        hex_list.append(matplotlib.colors.rgb2hex(rgba))
    return hex_list


colors_d02 = hex("Blues_r")
colors_d03 = hex("Greens_r")
colors_hrdps = hex("Reds_r")
colors_rdps = hex("Purples_r")


def fct_plot(
    j, idx, var, obs_ds, obs_flat, obs_flat_null, stats_text, ax, ax2, ls, name
):

    domain = domains[j]
    if domain == "d02":
        dom_name = "WRF 12km"
        # colors = colors_d02
    elif domain == "d03":
        dom_name = "WRF 4km"
    elif domain == "hrdps":
        dom_name = "HRDPS 2.5km"
    elif domain == "rdps":
        dom_name = "RDPS 10km"
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
    "ffmc",
    "dmc",
    "dc",
    "bui",
    "isi",
    "fwi",
    "temp",
    "td",
    "rh",
    "ws",
    "wdir",
    "precip",
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

    ax.set_xlim([pd.Timestamp("2021-03-15"), pd.Timestamp("2021-11-15")])
    ax2.set_xlim([pd.Timestamp("2022-03-15"), pd.Timestamp("2022-11-15")])
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

    numbers_only = np.array(numbers_only).reshape(y, x).astype(float)

    cell_colors = np.empty((y, x), dtype="U10")
    cell_colors.fill("white")
    good_color, bad_color = "lightblue", "lightpink"
    color_table = np.stack(color_table)
    # cell_colors[:,0] = color_table

    cell_colors[
        np.where(numbers_only[:, 1] == np.min(numbers_only[:, 1]))[0], 1
    ] = bad_color
    cell_colors[
        np.where(np.abs(numbers_only[:, 2]) == np.max(np.abs(numbers_only[:, 2])))[0], 2
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
        np.where(np.abs(numbers_only[:, 2]) == np.min(np.abs(numbers_only[:, 2])))[0], 2
    ] = good_color
    cell_colors[
        np.where(numbers_only[:, 3] == np.min(numbers_only[:, 3]))[0], 3
    ] = good_color
    cell_colors[
        np.where(numbers_only[:, 4] == np.min(numbers_only[:, 4]))[0], 4
    ] = good_color

    # mbe_best
    # cell_colors[np.abs(numbers_only[:,2]).argmin(),2] = 'blue'
    # rmse_best = np.argmin(numbers_only[:,3])
    # mae_best = np.argmin(numbers_only[:,4])

    # Create the fill colors for the table cells
    # cell_colors = [['lightgray', 'lightgray', 'lightgray'],
    #             ['lightblue', 'lightgreen', 'lightblue'],
    #             ['lightgreen', 'lightblue', 'lightgreen']]

    # Create the second set of axes for the table
    ax_table = fig.add_axes([0.55, 0.87, 0.33, 0.2])

    # Create the table and add it to the second set of axes
    table = ax_table.table(cellText=data, loc="center", cellColours=cell_colors)
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
    fig.savefig(str(save_dir) + f"/{var}-fireseason.png", bbox_inches="tight", dpi=250)


# %%

########################## Plot Stuff  ###############################

# ds_2021 = prov_ds.sel(time=slice("2021-04-01", "2021-10-31"), domain = 'obs')#.chunk('auto')
# ds_2022 = prov_ds.sel(time=slice("2022-04-01", "2022-10-31"), domain = 'obs')#.chunk('auto')
# null_ds = prov_ds.sel(time=slice("2021-11-01", "2022-03-31"), domain = 'obs')#.chunk('auto')
# null_array = np.full(null_ds['temp'].shape, np.nan)
# for var in null_ds:
#     null_ds[var] = (('time', 'wmo'), null_array)

# ds_2021 = ds_2021.drop('Time')
# ds_2022 = ds_2022.drop('Time')
# null_ds = null_ds.drop('Time')

# for var in ["elev", "name", "prov", "id", 'domain']:
#     ds[var] = ds[var].astype(str)

# cont_ds = xr.concat([ds_2021, null_ds, ds_2022], dim="time")
# prov_dss = prov_ds.sel(domain = ['d02', 'd03', 'rdps', 'hrdps'])
# cont_ds
# test = xr.merge([cont_ds.expand_dims(dim={"domain": ["obs"]}), prov_dss])
# test.to_netcdf(str(data_dir) + f'/intercomp/{trail_name}/20210101-20221231-null.nc', mode = 'w')

# # start_date = date_range[0].strftime("%Y%m%d")
# # stop_date = date_range[-1].strftime("%Y%m%d")


# # fwi_list = ["ffmc", "dmc", "dc", "bui", "isi", "fwi"]
# # fwi_list = ["ffmc","dmc", "dc"]

# # fig = plt.figure(figsize=[10, 14])
# # fig.suptitle(
# #     f'Comparison of domain Derived FWI vs Observations at {len(unique)} Weather Stations \n {date_range[0].strftime("%Y%m%d")} - {date_range[-1].strftime("%Y%m%d")}',
# #     fontsize=14,
# # )

# # plotstats(fig, fwi_list)
# # fig.tight_layout()

# # fig.savefig(str(save_dir) + f"/fwi-vars-{domain}-{start_date}-{stop_date}.png")
# # fig.savefig(
# #     str(save_dir) + f"/fwi-vars-{domain}-{start_date}-{stop_date}.pdf",
# #     bbox_inches="tight",
# # )

# # plt.close()

# ##########################################################################
# ##########################################################################
# # met_list = ["temp", "td", "rh", "ws", "wdir", "precip"]
# # # met_unit = ["C", "%", "km h^-1", "mm"]
# # # length = len(met_list)
# # # domain_config = ["_era5", "_wrf05"]

# # fig = plt.figure(figsize=[10, 14])
# # # fig.suptitle(
# # #     f'Comparison of domain Derived Met vs Observations at {len(unique)} Weather Stations \n {date_range[0].strftime("%Y%m%d")} - {date_range[-1].strftime("%Y%m%d")}',
# # #     fontsize=14,
# # )
# # plotstats(fig, met_list)


# # fig.tight_layout()
# # fig.savefig(str(save_dir) + f"/met-vars-{domain}-{start_date}-{stop_date}.png")
# # fig.savefig(
# #     str(save_dir) + f"/met-vars-{domain}-{start_date}-{stop_date}.pdf",
# #     bbox_inches="tight",
# # )

# # plt.close()
