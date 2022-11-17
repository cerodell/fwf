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
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.metrics import r2_score
from scipy import stats
from matplotlib.offsetbox import AnchoredText
import matplotlib
from pathlib import Path

matplotlib.rcParams.update({"font.size": 14})

import warnings

warnings.filterwarnings("ignore")

warnings.filterwarnings("ignore", category=FutureWarning)

wrf_model = "wrf4"
# models = ["_era5", "_wrf01",  "_wrf02",  "_wrf03",  "_wrf04"]
models = ["_era5", "_wrf01", "_wrfera5"]


save_dir = Path(str(data_dir) + f"/images/stats/era5wrf03/")
save_dir.mkdir(parents=True, exist_ok=True)

domain = "d02"
# date = pd.Timestamp("today")
date = pd.Timestamp(2021, 11, 1)

intercomp_today_dir = date.strftime("%Y%m%d")

with open(str(data_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)

# ds = xr.open_zarr(
#     str(data_dir) + "/intercomp/d02/ERA5WRF01/" + f"intercomp-d02-20220730.zarr",
# )

ds = xr.open_zarr(
    str(data_dir) + "/intercomp/" + f"intercomp-{domain}-{intercomp_today_dir}.zarr",
)
ds = ds.sel(time=slice("2021-05-01", "2021-10-01"))
ds = ds.load()

ds = ds.dropna(dim="wmo")
# ds.plot.scatter('ws', 'ws_wrf01')

date_range = pd.date_range(ds.time.values[0], ds.time.values[-1])
# ds = ds.chunk(chunks="auto")
# ds = ds.unify_chunks()
# for var in list(ds):
#     ds[var].encoding = {}

if domain == "d02":
    res = "12 km"
else:
    res = "4 km"

df = ds.to_dataframe().dropna()
df = df.reset_index()
for i in range(len(date_range)):
    print(date_range[i].strftime("%Y-%m-%d"))
    obs_df = df[df["time"] == date_range[i].strftime("%Y-%m-%d")]
    print(np.unique(obs_df.temp.isnull(), return_counts=True))

# df = df[~np.isnan(df.bui)]
# df = df[~np.isnan(df[f"bui_day1_{method}"])]

unique, counts = np.unique(df.wmo.values, return_counts=True)
# wmo_of_int = unique[counts > 170]
# df = df[df.wmo.isin(wmo_of_int)]
# unique, counts = np.unique(df.wmo.values, return_counts=True)


var_list = list(ds)[::3]
time = np.array(ds.time.dt.strftime("%Y-%m-%d"), dtype="<U10")
start_time = datetime.strptime(str(time[0]), "%Y-%m-%d").strftime("%Y%m%d")
end_time = datetime.strptime(str(time[-1]), "%Y-%m-%d").strftime("%Y%m%d")
colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]


def MBE(y_true, y_pred):
    """
    Parameters:
        y_true (array): Array of observed values
        y_pred (array): Array of prediction values

    Returns:
        mbe (float): Biais score
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    y_true = y_true.reshape(len(y_true), 1)
    y_pred = y_pred.reshape(len(y_pred), 1)
    diff = y_true - y_pred
    mbe = diff.mean()
    # print('MBE = ', mbe)
    return mbe


##########################################################################
##########################################################################


def plotstats(fig, var_list):
    length = len(var_list)
    for i in range(length):
        # plt.subplot(i+1, 1, 1)
        ax = fig.add_subplot(length + 1, 1, i + 1)
        var = var_list[i]
        stats_text = ""
        for j in range(len(models)):
            df_final = df[~np.isnan(df[var])]
            if var == "precip":
                print(
                    f"number of data points before condtion {len(df_final['precip'])}"
                )
                df_final = df_final[df_final["precip"] > 0.01]
                print(f"number of data points after condtion {len(df_final['precip'])}")
            else:
                pass
            # df_final = df_final[np.abs(df_final[var] - df_final[var].mean()) <= (2 * df_final[var].std())]
            model = models[j]
            model_name = model.strip("_").upper()
            # print(str(round(mean_absolute_error(df[var].values, df[var + model].values),2)))
            if "ffmc" in var_list:
                if model_name == "ERA5":
                    model_name += "       "
                    pass
                elif model_name == "WRF01":
                    model_name = "WRF        "
                else:
                    pass
            else:
                if model_name == "ERA5":
                    # model_name += "       "
                    pass
                elif model_name == "WRF01":
                    model_name = "WRF "
                else:
                    pass
            r2value = round(
                stats.pearsonr(df_final[var].values, df_final[var + model].values)[0], 2
            )
            rmse = str(
                round(
                    mean_squared_error(
                        df_final[var].values,
                        df_final[var + model].values,
                        squared=False,
                    ),
                    2,
                )
            )
            # print(model)
            # print(len(df_final[var].values))
            mbe = str(round(MBE(df_final[var].values, df_final[var + model].values), 2))
            mae = str(
                round(
                    mean_absolute_error(
                        df_final[var].values, df_final[var + model].values
                    ),
                    2,
                )
            )
            df_final = df_final.groupby("time").mean()
            var_model = df_final[var + model].values
            ax.plot(
                df_final.index,
                var_model,
                label=model_name,
                zorder=2,
                color=colors[j + 1],
            )
            stats_text += f"{model_name}   (r): {r2value} (mbe): {mbe} (rmse): {rmse} (mae): {mae} \n"

        anchored_text = AnchoredText(
            stats_text[:-3],
            loc="upper right",
            prop={"size": 8, "zorder": 10},
            bbox_to_anchor=(1.015, 1.2),
            bbox_transform=ax.transAxes,
        )

        try:
            ax.set_ylabel(fr"$({var_dict[var]['units']})$", fontsize=14)
        except:
            pass
        var_obs = df_final[var].values
        ax.set_title(var_dict[var.lower()]["description"], fontsize=14)
        ax.tick_params(axis="x", rotation=45)
        ax.plot(
            df_final.index,
            var_obs,
            label="Observation",
            zorder=2,
            color=colors[0],
            lw=2,
        )
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
                bbox_to_anchor=(0.5, 1.6),
                ncol=4,
                fancybox=True,
                shadow=True,
            )
        else:
            pass
    ax.set_xlabel("Time")
    return


fwi_list = ["ffmc", "dmc", "dc", "bui", "isi", "fwi"]

fig = plt.figure(figsize=[10, 14])
# fig.suptitle(
#     f'Comparison of Model Derived FWI vs Observations at {len(unique)} Weather Stations \n {date_range[0].strftime("%Y%m%d")} - {date_range[-1].strftime("%Y%m%d")}',
#     fontsize=14,
# )

plotstats(fig, fwi_list)
# fig.tight_layout()

fig.savefig(str(save_dir) + f"/fwi-vars-{domain}-{intercomp_today_dir}-mean.png")
plt.close()

##########################################################################
##########################################################################
met_list = ["temp", "td", "rh", "ws", "wdir", "precip"]
# met_unit = ["C", "%", "km h^-1", "mm"]
# length = len(met_list)
models = ["_era5", "_wrf01"]

fig = plt.figure(figsize=[10, 14])
# fig.suptitle(
#     f'Comparison of Model Derived Met vs Observations at {len(unique)} Weather Stations \n {date_range[0].strftime("%Y%m%d")} - {date_range[-1].strftime("%Y%m%d")}',
#     fontsize=14,
# )
plotstats(fig, met_list)

# fig.tight_layout()
fig.savefig(str(save_dir) + f"/met-vars-{domain}-{intercomp_today_dir}-mean.png")
plt.close()
