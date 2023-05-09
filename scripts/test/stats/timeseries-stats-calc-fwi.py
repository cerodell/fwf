"""
This script compares how well the fwf model did compare to observed values.
It solves FWI from obs met and model met at obs points. Creates a time series of
all met/fwi values averaged across all wx stations in the model domain.
"""

import context
import json
import numpy as np
import pandas as pd
import xarray as xr

import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText


from scipy import stats
from sklearn.metrics import mean_squared_error, mean_absolute_error

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
import matplotlib


import warnings

warnings.filterwarnings("ignore")
# cp -r /Volumes/Scratch/FWF-WAN00CG/d03/202104 202104


##################################################################
##################### Define Inputs   ###########################
## time of interest
start, stop = "2021-05-01", "2021-10-01"
bias = "-mcodes"
## default moisture code values
F = 85.0
P = 6.0
D = 15.0

## models to compare
models = ["", "_wrf05", "_wrfbias"]
trail_name = "WRF05060708"

## define directory to save figures
save_dir = Path(str(data_dir) + f"/images/stats/test/")
save_dir.mkdir(parents=True, exist_ok=True)


##################################################################
#################### Open Data Files   ###########################

#### Open Datafiles and modify based on inputs
## open fwf attribute json file, used for axis labels in plotting
with open(str(root_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)

## open intercomparsion data
ds_wmo = xr.open_dataset(
    str(data_dir) + "/intercomp/d02/WRF05060708/20210101-20221031.nc"
)

## slice data acrcoss time of interest and drop any wx station with nan values.
## droping the nan values gibves a contiual data stream over the time of int
ds_wmo = ds_wmo.sel(time=slice(start, stop))
ds_wmo = ds_wmo.load()
ds_wmo = ds_wmo.dropna(dim="wmo")


##################################################################
######################### Solve FWI  #############################
## create datasets for each model and the observations. Used as input to solve FWI
ds_all = []
for model in models:
    if model == "_wrfbias":
        ds_time = xr.Dataset(
            {
                "F": (["time", "wmo"], ds_wmo["ffmc_wrf05"].values),
                "P": (["time", "wmo"], ds_wmo["dmc_wrf05"].values),
                "D": (["time", "wmo"], ds_wmo["dc_wrf05"].values),
                "W": (["time", "wmo"], ds_wmo["ws_wrf05"].values),
                "WD": (["time", "wmo"], ds_wmo["wdir_wrf05"].values),
                # "T": (["time", "wmo"], ds_wmo["temp_wrf05"].values + 0.8),
                # "TD": (["time", "wmo"], ds_wmo["td_wrf05"].values - 0.4),
                "T": (["time", "wmo"], ds_wmo["temp_wrf05"].values),
                "TD": (["time", "wmo"], ds_wmo["td_wrf05"].values),
                # "H": (["time", "wmo"], ds_wmo['rh'+model].values),
                "r_o": (["time", "wmo"], ds_wmo["precip_wrf05"].values),
            }
        )
    else:
        ds_time = xr.Dataset(
            {
                "F": (["time", "wmo"], ds_wmo["ffmc" + model].values),
                "P": (["time", "wmo"], ds_wmo["dmc" + model].values),
                "D": (["time", "wmo"], ds_wmo["dc" + model].values),
                "W": (["time", "wmo"], ds_wmo["ws" + model].values),
                "WD": (["time", "wmo"], ds_wmo["wdir" + model].values),
                "T": (["time", "wmo"], ds_wmo["temp" + model].values),
                "TD": (["time", "wmo"], ds_wmo["td" + model].values),
                # "H": (["time", "wmo"], ds_wmo['rh'+model].values),
                "r_o": (["time", "wmo"], ds_wmo["precip" + model].values),
                # "r_o": (["time", "wmo"], ds_wmo["precip_era5"].values),
            }
        )

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
    F = 85.0
    P = 6.0
    D = 15.0
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
        if model == "_wrfbias":
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
    ds_all.append(ds_concat)

# ds_all[1]['S'] = ds_all[1]['S'] + 3.4
# ds_all[2]["S"] = ds_all[2]["S"] + 3.4


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


colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]


def plotstats(fig, var_list, var_names, models, font_size):
    length = len(var_list)
    for i in range(length):
        # plt.subplot(i+1, 1, 1)
        ax = fig.add_subplot(length + 1, 1, i + 1)
        var = var_list[i]
        var_name = var_names[i]
        stats_text = ""
        for k in range(len(models) - 1):
            k = k + 1
            model = models[k]
            # print(model)
            model_name = model.strip("_").upper()
            # print(model_name)

            if model == "_wrf05":
                color = colors[0]
            elif model == "_wrf06":
                color = colors[3]
            else:
                color = colors[2]

            if model_name == "ERA5":
                # model_name += "       "
                pass
            elif model_name == "WRF01":
                model_name = "WRF "

            obs_var, model_var = (
                ds_all[0][var].values.ravel(),
                ds_all[k][var].values.ravel(),
            )
            if var == "r_o":
                print(f"number of data points before condition {len(obs_var)}")
                obs_var_int = obs_var[obs_var > 0.01]
                model_var = model_var[obs_var > 0.01]
                # obs_var_int = obs_var
                # model_var = model_var
                obs_var = obs_var_int
                print(f"number of data points after condition {len(obs_var)}")
                # print(ds_all[0][var] > 0.01)
                ax.plot(
                    date_range,
                    # ds_all[k][var][ds_all[0][var] > 0.01].mean(dim="wmo").values,
                    ds_all[k][var].mean(dim="wmo").values,
                    label=model_name,
                    color=color,
                    lw=2,
                )
            else:
                ax.plot(
                    date_range,
                    ds_all[k][var].mean(dim="wmo").values,
                    label=model_name,
                    color=color,
                    lw=2,
                )

            r2value = round(stats.pearsonr(obs_var, model_var)[0], 2)
            # rmse = str(
            #     round(
            #         mean_squared_error(
            #             obs_var, model_var, squared=False
            #         ),
            #         2,
            #     )
            # )
            # print(model)
            # print(len(df_final[var].values))

            mbe = str(round(MBE(obs_var, model_var), 2))
            mae = str(round(mean_absolute_error(obs_var, model_var), 2))
            stats_text += f"{model_name}  \n r: {r2value}\n mbe: {mbe}\n mae: {mae}  \n"

        anchored_text = AnchoredText(
            stats_text[:-3],
            loc="upper right",
            prop={"size": font_size, "zorder": 10},
            bbox_to_anchor=(1.1, 1.05),
            bbox_transform=ax.transAxes,
        )

        try:
            ax.set_ylabel(fr"$({var_dict[var_name]['units']})$", fontsize=16)
        except:
            pass
        ax.set_title(var_dict[var_name.lower()]["description"], fontsize=16)
        ax.tick_params(axis="x", rotation=45)
        ax.plot(
            date_range,
            ds_all[0][var].mean(dim="wmo").values,
            label="Observation",
            zorder=2,
            color="k",
            lw=1.5,
        )
        ax.yaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
        ax.xaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
        ax.add_artist(anchored_text)
        # if var_name == "dc":
        #     ax.set_ylim([0, 600])
        # else:
        #     pass

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


matplotlib.rcParams.update({"font.size": 18})

##########################################################################
fwi_list = ["F", "P", "D"]
fwi_names = ["ffmc", "dmc", "dc"]

fig = plt.figure(figsize=[16, 14])
plotstats(fig, fwi_list, fwi_names, models, font_size=11)
fig.subplots_adjust(hspace=0.5)
fig.savefig(str(save_dir) + f"/fwi-vars-mean-codes{bias}.png")

# plt.close()

##########################################################################
fwi_list = ["U", "R", "S"]
fwi_names = ["bui", "isi", "fwi"]

fig = plt.figure(figsize=[16, 14])
plotstats(fig, fwi_list, fwi_names, models, font_size=11)
fig.subplots_adjust(hspace=0.5)
fig.savefig(str(save_dir) + f"/fwi-vars-mean-index{bias}.png")

# plt.close()

##########################################################################
# met_list = ["T", "TD", "H", "W", "WD", "r_o"]
# met_name = ["temp", "td", "rh", "ws", "wdir", "precip"]
met_list = ["T", "H", "W", "r_o"]
met_name = ["temp", "rh", "ws", "precip"]
models = ["", "_wrf05", "_wrfbias"]

fig = plt.figure(figsize=[16, 14])
plotstats(fig, met_list, met_name, models, font_size=14)
fig.savefig(str(save_dir) + f"/met-vars-mean{bias}.png")
# plt.close()
