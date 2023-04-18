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


__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

########################### INPUTS ###########################

config = {"wrf": ["d02", "d03"], "eccc": ["rdps", "hrdps"]}
domains = ["d02", "d03", "rdps", "hrdps"]

domains = ["era5"]
trail_name = "03"
fwf_dir = f"/Volumes/WFRT-Ext24/fwf-data/"

######################### END INPUTS #########################

#################### Open static datasets ####################

with open(str(root_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)

# try:
#     domains_ds = xr.open_dataset(str(data_dir) + f'/intercomp/{trail_name}/provs-20210101-20221231.nc')
# except:
ds = xr.open_dataset(
    str(data_dir) + f"/intercomp/{trail_name}/era5/20200101-20221231.nc",
)  # chunks = 'auto')
ds["time"] = ds["Time"]
## drop a bad weather station
ds = ds.drop_sel(wmo=2275)

# rdps.sel(time =slice("2022-01-11", "2022-12-31")).isel(wmo = 100)['rh'].plot()

# ds = ds.sel(time=slice("2021-04-01", "2022-10-31"))
for var in ["elev", "name", "prov", "id", "domain"]:
    ds[var] = ds[var].astype(str)
# prov_unique, prov_counts = np.unique(ds.prov.values, return_counts=True)

## get wmo stations that are with every domain
idx = np.where(
    (ds.prov == "BC")
    | (ds.prov == "AB")
    | (ds.prov == "SA")
    | (ds.prov == "YT")
    | (ds.prov == "NT")
)[0]
prov_ds = ds.isel(wmo=idx)
# prov_ds = ds
# prov_ds.sel(domain = 'obs').isel(wmo = 100)['dc'].plot()
# prov_ds.sel(domain = 'era5').isel(wmo = 100)['dc'].plot()

# idx_hrdps, counts = np.unique(np.where(prov_ds.sel(domain = 'hrdps').isel(time = 0)['temp'].notnull())[0], return_counts=True)
# prov_ds = prov_ds.isel(wmo = idx_hrdps)

######################## Set up plotting stuff ###########################

## define directory to save figures
save_dir = Path(str(data_dir) + f"/images/stats/{trail_name}/era5")
save_dir.mkdir(parents=True, exist_ok=True)

date_range = pd.date_range(prov_ds.Time.values[0], prov_ds.Time.values[-1])
time = np.array(prov_ds.Time.dt.strftime("%Y-%m-%d"), dtype="<U10")
start_time = datetime.strptime(str(time[0]), "%Y-%m-%d").strftime("%Y%m%d")
end_time = datetime.strptime(str(time[-1]), "%Y-%m-%d").strftime("%Y%m%d")
colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

all_obs_ds = prov_ds.sel(domain="obs")
domains_ds = [prov_ds.sel(domain=domain) for domain in domains]

# o_ds = obs_ds['temp'].drop
# fct_ds = xr.where(obs_ds['temp'].isnull(),  np.nan, domains_ds[0]['temp'])


# print(np.unique(var_obs.isnull(), return_counts=True))

# fcts_df = [prov_ds.sel(domain = 'd02').to_dataframe()]

# test = prov_ds['temp']


########################################################################
# %%
# fig = plt.figure(figsize=[10, 14])
# var_list = ["temp", "td", "rh", "ws", "wdir", "precip"]
var_list = ["ffmc", "dmc", "dc", "bui", "isi", "fwi"]
length = len(var_list)
for i in range(length):
    # ax = fig.add_subplot(length + 1, 1, i + 1)
    fig, (ax, ax2, ax3) = plt.subplots(
        1, 3, sharey=True, facecolor="w", figsize=[14, 3]
    )
    var = var_list[i]
    stats_text = ""
    obs_ds = all_obs_ds[var]
    obs_mean = obs_ds.mean(dim="wmo")  # .dropna(dim = 'time')
    obs_flat_null = obs_ds.values.ravel()
    obs_flat = obs_flat_null[~np.isnan(obs_flat_null)]
    # find indexes two outside standard deviation
    idx = np.where(np.abs(obs_flat - np.mean(obs_flat)) > 2 * np.std(obs_flat))
    obs_flat = np.delete(obs_flat, idx)

    for j in range(len(domains)):
        fct_ds = xr.where(obs_ds.isnull(), np.nan, domains_ds[j][var])
        fct_flat = fct_ds.values.ravel()
        fct_flat = fct_flat[~np.isnan(obs_flat_null)]
        fct_flat = np.delete(fct_flat, idx)
        if var == "precip":
            fct_flat = fct_flat[obs_flat > 0.01]
            obs_flat = obs_flat[obs_flat > 0.01]
        else:
            pass
        print(np.unique(obs_ds.isnull(), return_counts=True))
        print(np.unique(fct_ds.isnull(), return_counts=True))
        r2value = round(stats.pearsonr(obs_flat, fct_flat)[0], 2)
        rmse = str(
            round(
                mean_squared_error(
                    obs_flat,
                    fct_flat,
                    squared=False,
                ),
                2,
            )
        )
        mbe = str(round(MBE(obs_flat, fct_flat), 2))
        mae = str(
            round(
                mean_absolute_error(obs_flat, fct_flat),
                2,
            )
        )
        fct_mean = fct_ds.mean(dim="wmo")  # .dropna(dim = 'time')
        ax.plot(
            fct_mean.Time,
            fct_mean,
            label=domains[j],
            zorder=10,
            color=colors[j],
            lw=0.8,
            # alpha = 0.8
        )
        ax2.plot(
            date_range,
            fct_mean,
            label=domains[j],
            zorder=10,
            color=colors[j],
            lw=0.8,
            # alpha = 0.8
        )
        ax3.plot(
            date_range,
            fct_mean,
            label=domains[j],
            zorder=10,
            color=colors[j],
            lw=0.8,
            # alpha = 0.8
        )
        stats_text += (
            f"{domains[j]}   (r): {r2value} (mbe): {mbe} (rmse): {rmse} (mae): {mae} \n"
        )
    anchored_text = AnchoredText(
        stats_text[:-3],
        loc="upper right",
        prop={"size": 8, "zorder": 10},
        bbox_to_anchor=(2.015, 1.27),
        bbox_transform=ax.transAxes,
    )
    try:
        ax.set_ylabel(fr"$({var_dict[var]['units']})$", fontsize=14)
    except:
        pass
    print(var)
    # ax.set_title(var_dict[var.lower()]["description"], fontsize=14)
    ax.tick_params(axis="x", rotation=45)
    ax2.tick_params(axis="x", rotation=45)
    ax3.tick_params(axis="x", rotation=45)
    ax.plot(
        obs_mean.Time,
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
    ax3.plot(
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
    ax3.yaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
    ax3.xaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
    ax3.add_artist(anchored_text)
    # ax.set_xlim([pd.Timestamp('2020-01-01'), pd.Timestamp('2020-12-01')])
    # ax2.set_xlim([pd.Timestamp('2021-01-01'), pd.Timestamp('2021-12-01')])
    # ax3.set_xlim([pd.Timestamp('2022-01-01'), pd.Timestamp('2022-12-01')])
    ax.set_xlim([pd.Timestamp("2020-03-15"), pd.Timestamp("2020-11-15")])
    ax2.set_xlim([pd.Timestamp("2021-03-15"), pd.Timestamp("2021-11-15")])
    ax3.set_xlim([pd.Timestamp("2022-03-15"), pd.Timestamp("2022-11-15")])
    # hide the spines between ax and ax2
    ax.spines["right"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax3.spines["left"].set_visible(False)
    ax3.yaxis.tick_right()
    ax3.tick_params(labelright="on")
    plt.subplots_adjust(wspace=0.08)

    d = 0.015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color="k", clip_on=False)
    ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)
    ax.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)
    ax2.plot((-d, +d), (-d, +d), **kwargs)
    kwargs.update(transform=ax3.transAxes)  # switch to the bottom axes
    ax3.plot((-d, +d), (1 - d, 1 + d), **kwargs)
    ax3.plot((-d, +d), (-d, +d), **kwargs)
    ax2.legend(
        loc="upper center",
        bbox_to_anchor=(0.48, 1.12),
        ncol=6,
        fancybox=True,
        shadow=True,
        prop={"size": 7},
    )
    fig.suptitle(var_dict[var.lower()]["description"], fontsize=18, y=1.2)
    fig.savefig(str(save_dir) + f"/{var}.png", bbox_inches="tight", dpi=250)


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
