import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
import scipy.stats
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.ndimage as ndimage
from scipy.ndimage.filters import gaussian_filter
from pylab import *

from context import data_dir, xr_dir, wrf_dir, tzone_dir
from datetime import datetime, date, timedelta
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from scipy import stats
from matplotlib.offsetbox import AnchoredText

import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

wrf_model = "wrf4"
models = ["_era5_nearest", "_day1_nearest"]
domain = "d02"
# date = pd.Timestamp("today")
date = pd.Timestamp(2021, 11, 1)

intercomp_today_dir = date.strftime("%Y%m%d")

with open(str(data_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)

ds = xr.open_zarr(
    str(data_dir) + "/intercomp/" + f"intercomp-{domain}-{intercomp_today_dir}.zarr",
)

ds = ds.sel(time=slice("2021-04-01", "2021-11-01"))

date_range = pd.date_range(ds.time.values[0], ds.time.values[-1])
ds = ds.chunk(chunks="auto")
ds = ds.unify_chunks()
for var in list(ds):
    ds[var].encoding = {}

if domain == "d02":
    res = "12 km"
else:
    res = "4 km"

df = ds.to_dataframe().dropna()
df = df.reset_index()
df = df[~np.isnan(df.bui)]
df = df[~np.isnan(df.bui_day1_nearest)]

unique, counts = np.unique(df.wmo.values, return_counts=True)
# wmo_of_int = unique[counts > 170]
# df = df[df.wmo.isin(wmo_of_int)]
# unique, counts = np.unique(df.wmo.values, return_counts=True)


var_list = list(ds)[::3]
time = np.array(ds.time.dt.strftime("%Y-%m-%d"), dtype="<U10")
start_time = datetime.strptime(str(time[0]), "%Y-%m-%d").strftime("%Y%m%d")
end_time = datetime.strptime(str(time[-1]), "%Y-%m-%d").strftime("%Y%m%d")
colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]


##########################################################################
##########################################################################
fwi_list = ["ffmc", "dmc", "dc", "bui", "isi", "fwi"]
length = len(fwi_list)

fig = plt.figure(figsize=[10, 10])  # figsize=[8, 8]
fig.suptitle(
    f'Comparison of FWF {res} vs NRCAN at {len(unique)} Weather Stations \n {date_range[0].strftime("%Y%m%d")} - {date_range[-1].strftime("%Y%m%d")}',
    fontsize=14,
)
for i in range(length):
    # plt.subplot(i+1, 1, 1)
    ax = fig.add_subplot(length + 1, 1, i + 1)
    # var = fwi_list[i].upper()
    var = fwi_list[i]
    # df_final = df[np.abs(df[var] - df[var].mean()) <= (3 * df[var].std())]
    df_final = df[~np.isnan(df[var])]
    r2values, rmses = [], []
    for model in models:
        # df_final = df_final[
        #     np.abs(df_final[var + model] - df_final[var + model].mean())
        #     <= (3 * df_final[var + model].std())
        # ]

        r2value = round(
            stats.pearsonr(df_final[var].values, df_final[var + model].values)[0], 2
        )
        rmse = str(
            round(
                mean_squared_error(
                    df_final[var].values, df_final[var + model].values, squared=False
                ),
                2,
            )
        )
        r2values.append(r2value)
        rmses.append(rmse)

        # df_final = df[np.abs(df[var] - df[var].mean()) <= (2 * df[var].std())]
        # df_final = df_final[
        #     np.abs(df_final[var + model] - df_final[var + model].mean())
        #     <= (2 * df_final[var + model].std())
        # ]
        df_final = df_final.groupby("time").mean()
        var_obs = df_final[var].values
        var_model = df_final[var + model].values
        if model == "_day1_nearest":
            # print('_day1_nearest')
            ax.plot(df_final.index, var_model, label="WRF", zorder=2, color=colors[3])
        elif model == "_era5_nearest":
            ax.plot(df_final.index, var_model, label="ERA5", zorder=2, color=colors[1])
            # print('_era5_nearest')
        else:
            pass

    anchored_text = AnchoredText(
        r"$ERA5 (r)$ "
        + f" \t {r2values[0]}   ERA5 (rmse): {rmses[0]} \n "
        + r"$WRF (r)$ "
        + f" \t {r2values[1]}   WRF (rmse): {rmses[1]}",
        loc="upper right",
        prop={"size": 6, "zorder": 10},
    )

    try:
        ax.set_ylabel(fr"$({var_dict[var]['units']})$", fontsize=8)
    except:
        pass
    ax.set_title(var_dict[var.lower()]["description"], fontsize=10)
    ax.plot(df_final.index, var_obs, label="Observation", zorder=2, color=colors[0])
    # ax.plot(df_final.index, var_model, label="Forecast", zorder=2, color=colors[3])
    ax.yaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
    ax.xaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
    ax.add_artist(anchored_text)
    if var == "dc":
        ax.set_ylim([0, 600])
    else:
        pass

    if i != length - 1:
        ax.tick_params(axis="x", labelbottom=False)
    else:
        pass
    if i == 0:
        # ax.legend()
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.1, 1.4),
            ncol=2,
            fancybox=True,
            shadow=True,
        )
    else:
        pass

ax.set_xlabel("Time")
fig.tight_layout()

fig.savefig(
    str(data_dir) + f"/images/stats/fwi-vars-{domain}-{intercomp_today_dir}-mean.png"
)
plt.close()

##########################################################################
##########################################################################
met_list = ["temp", "td", "rh", "ws", "wdir", "precip"]
met_unit = ["C", "%", "km h^-1", "mm"]
length = len(met_list)

fig = plt.figure(figsize=[10, 10])  # figsize=[8, 8]
fig.suptitle(
    f'Comparison of {wrf_model.upper()} {res} vs Observations at {len(unique)} Weather Stations \n {date_range[0].strftime("%Y%m%d")} - {date_range[-1].strftime("%Y%m%d")}',
    fontsize=14,
)
for i in range(length):
    # plt.subplot(i+1, 1, 1)
    ax = fig.add_subplot(length + 1, 1, i + 1)
    var = met_list[i]
    df_final = df[~np.isnan(df[var])]

    r2values, rmses = [], []
    for model in models:
        # print(model)
        r2value = round(
            stats.pearsonr(df_final[var].values, df_final[var + model].values)[0], 2
        )
        rmse = str(
            round(
                mean_squared_error(
                    df_final[var].values, df_final[var + model].values, squared=False
                ),
                2,
            )
        )
        r2values.append(r2value)
        print(model + str(r2value))
        rmses.append(rmse)

        df_final = df_final.groupby("time").mean()
        var_obs = df_final[var].values
        var_model = df_final[var + model].values
        if model == "_day1_nearest":
            # print('_day1_nearest')
            ax.plot(df_final.index, var_model, label="WRF", zorder=2, color=colors[3])
        elif model == "_era5_nearest":
            ax.plot(df_final.index, var_model, label="ERA5", zorder=2, color=colors[1])
            # print('_era5_nearest')

        else:
            pass

    anchored_text = AnchoredText(
        r"$ERA5 (r)$ "
        + f" \t {r2values[0]}   ERA5 (rmse): {rmses[0]} \n "
        + r"$WRF (r)$ "
        + f" \t {r2values[1]}   WRF (rmse): {rmses[1]}",
        loc="upper right",
        prop={"size": 6, "zorder": 10},
    )
    try:
        ax.set_ylabel(fr"$({var_dict[var]['units']})$", fontsize=8)
    except:
        pass
    ax.set_title(var_dict[var.lower()]["description"], fontsize=10)
    ax.plot(df_final.index, var_obs, label="Observation", zorder=2, color=colors[0])
    # ax.plot(df_final.index, var_model, label="Forecast", zorder=2, color=colors[3])
    ax.yaxis.grid(linewidth=0.4, linestyle="--")
    ax.xaxis.grid(linewidth=0.4, linestyle="--")
    ax.add_artist(anchored_text)

    if i != length - 1:
        ax.tick_params(axis="x", labelbottom=False)
    else:
        pass
    if i == 0:
        ax.legend()
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.1, 1.3),
            ncol=3,
            fancybox=True,
            shadow=True,
        )
    else:
        pass

ax.set_xlabel("Time")
fig.tight_layout()
fig.savefig(
    str(data_dir) + f"/images/stats/met-vars-{domain}-{intercomp_today_dir}-mean.png"
)
plt.close()
