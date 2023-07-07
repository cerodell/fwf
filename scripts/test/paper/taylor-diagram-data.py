import context
import numpy as np
import pandas as pd
import xarray as xr

import skill_metrics as sm
import matplotlib.pyplot as plt
from matplotlib import rcParams

from scipy import stats
from utils.stats import MBE
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error, mean_absolute_error

from datetime import datetime, date, timedelta

from pathlib import Path
from utils.taylor import srl
from context import data_dir, root_dir


__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

########################### INPUTS ###########################

# model = "nwp"
# domains = ["d02", "d03", "rdps", "hrdps"]

model = "wrf"
domains = ["d02", "d03"]
trail_name = "02"
fwf_dir = f"/Volumes/WFRT-Ext24/fwf-data/"

## define directory to save figures
save_dir = Path(str(data_dir) + f"/intercomp/{trail_name}/{model}/")
save_dir.mkdir(parents=True, exist_ok=True)
######################### END INPUTS #########################

############ Open static datasets and prepare ################

prov_ds = xr.open_dataset(
    str(data_dir) + f"/intercomp/{trail_name}/{model}/d03-20210401-20221101-null.nc"
)
all_obs_ds = prov_ds.sel(domain="obs")
domains_ds = [prov_ds.sel(domain=domain) for domain in domains]


########################################################################


def solve_stats(j, idx, var, obs_ds, obs_flat, obs_flat_null, name):

    fct_ds = xr.where(obs_ds.isnull(), np.nan, domains_ds[j][var])
    fct_flat = fct_ds.values.ravel()
    fct_flat = fct_flat[~np.isnan(obs_flat_null)]
    fct_flat = np.delete(fct_flat, idx)

    if var == "precip":
        fct_flat = fct_flat[obs_flat > 0.0]
        obs_flat = obs_flat[obs_flat > 0.0]
    else:
        pass

    std_dev = np.std(fct_flat)
    r2value = stats.pearsonr(obs_flat, fct_flat)[0]
    rmse = mean_squared_error(
        obs_flat,
        fct_flat,
        squared=False,
    )
    rms = mean_squared_error(
        obs_flat,
        fct_flat,
    )
    mbe = MBE(obs_flat, fct_flat)
    mae = mean_absolute_error(obs_flat, fct_flat)

    d = {
        "domain": f"{domains[j]}-{name}",
        "std_dev": std_dev,
        "rms": rms,
        "r": r2value,
        "mbe": mbe,
        "rmse": rmse,
        "mae": mae,
    }
    df = pd.DataFrame(data=d, index=[0])

    return df, obs_flat


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
    var = var_list[i]
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
    print(len(wx_count))
    # print(list(wx_station[np.where(wx_count < 30)[0]]))
    print(len(list(wx_station[np.where(wx_count < 30)[0]])))
    print("=============================================")
    dfs = []
    for j in range(len(domains)):
        df_i, obs_flat_final = solve_stats(
            j,
            idx,
            var,
            obs_ds,
            obs_flat,
            obs_flat_null,
            name="noon  ",
        )
        dfs.append(df_i)
        try:
            if var == "rh":
                name = "min   "
            else:
                name = "max   "
            df_i, obs_flat_final = solve_stats(
                j,
                idx,
                "m" + var,
                obs_ds,
                obs_flat,
                obs_flat_null,
                name=name,
            )
            dfs.append(df_i)
        except:
            pass
        try:
            df_i, obs_flat_final = solve_stats(
                j,
                idx,
                "h" + var,
                obs_ds,
                obs_flat,
                obs_flat_null,
                name="hourly",
            )
            dfs.append(df_i)
        except:
            pass

    combined_df = pd.concat(dfs)

    obs_df = {
        "domain": f"obs",
        "std_dev": np.std(obs_flat_final),
        "rms": 0,
        "r": 1,
        "mbe": 0,
        "rmse": 0,
        "mae": 0,
    }
    obs_df = pd.DataFrame(data=obs_df, index=[0])

    combined_df = pd.concat([combined_df, obs_df]).reset_index()
    combined_df = combined_df.drop("index", axis=1)

    combined_df.to_csv(str(save_dir) + f"/{var}-stats.csv")
