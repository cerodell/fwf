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

from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta
from sklearn.metrics import mean_squared_error

wrf_model = "wrf3"

domain = "d03"
# date = pd.Timestamp("today")
date = pd.Timestamp(2018, 10, 1)
intercomp_today_dir = date.strftime("%Y%m%d")

ds = xr.open_zarr(
    str(data_dir) + "/intercomp/" + f"intercomp-{domain}-{intercomp_today_dir}.zarr",
)

if domain == "d02":
    res = "12 km"
else:
    res = "4 km"


df = ds.to_dataframe().dropna()
df = df.reset_index()
df = df[~np.isnan(df.bui)]
# wmos = ds.wmo.values
# lats = ds.lats.values
# lngs = ds.lons.values

# # ffmc = test.ffmc.values
# # unique, count = np.unique(np.isnan(bui), return_counts=True)
# df_list = []
# for i in range(len(wmos)):
#     df_list.append(df.loc[df['wmo'] == wmos[i]].sum(axis=0))

# wmos_good, diff_list, lats_list, longs_list  = [], [], [], []
# for i in range(len(wmos)):
#     df2 = df_list[i]
#     diff = df2['precip'] - df2['precip_day1']
#     if diff == 0.0:
#         pass
#     else:
#         longs_list.append(lngs[i])
#         lats_list.append(lats[i])
#         wmos_good.append(wmos[i])
#         diff_list.append(diff)


# ## bring in state/prov boundaries
# states_provinces = cfeature.NaturalEarthFeature(
#     category="cultural",
#     name="admin_1_states_provinces_lines",
#     scale="50m",
#     facecolor="none",
# )

# time = np.array(ds.time.dt.strftime("%Y-%m-%d"), dtype="<U10")
# start_time = datetime.strptime(str(time[0]), "%Y-%m-%d").strftime("%Y%m%d")
# end_time = datetime.strptime(str(time[-1]), "%Y-%m-%d").strftime("%Y%m%d")
# ## make fig for make with projection
# fig = plt.figure(figsize=[16, 8])
# ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

# divider = make_axes_locatable(ax)
# ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)

# # cax = divider.append_axes('right', size='5%', pad=0.05)

# ## add map features
# ax.gridlines()
# ax.add_feature(cfeature.LAND, zorder=1)
# ax.add_feature(cfeature.LAKES, zorder=1)
# ax.add_feature(cfeature.OCEAN, zorder=1)
# ax.add_feature(cfeature.BORDERS, zorder=1)
# ax.add_feature(cfeature.COASTLINE, zorder=1)
# ax.add_feature(states_provinces, edgecolor="gray", zorder=2)
# ax.set_xlabel("Longitude", fontsize=18)
# ax.set_ylabel("Latitude", fontsize=18)

# ## create tick mark labels and style
# ax.set_xticks(list(np.arange(-160, -40, 10)), crs=ccrs.PlateCarree())
# ax.set_yticks(list(np.arange(30, 80, 10)), crs=ccrs.PlateCarree())
# ax.tick_params(axis="both", which="major", labelsize=14)
# ax.tick_params(axis="both", which="minor", labelsize=14)

# ## add title and adjust subplot buffers
# if domain == "d02":
#     res = "12 km"
# elif domain == "d03":
#     res = "4 km"
# else:
#     res = ""

# Plot_Title = f"Observed Minus Modeled Total Accumulated Precipitation \n From {start_time} - {end_time} \n  Mean Diff {str(round(np.mean(diff_list),3))}  Min Diff {str(round(np.min(diff_list),3))}   Max Diff {str(round(np.max(diff_list),3))}  WRF Domian {res} "
# ax.set_title(Plot_Title, fontsize=20, weight="bold")
# vmin, vmax = floor(min(diff_list)), ceil(max(diff_list)),
# vmin, vmax = -250, 250

# for i in range(len(wmos_good)):
#     sb = ax.scatter(longs_list[i],lats_list[i], c=diff_list[i], vmin=vmin, vmax=vmax, s=50, cmap = 'coolwarm', zorder = 10)

# fig.add_axes(ax_cb)
# # ticks = fc_df.CFFDRS.values[:-4]
# # # tick_levels = fc_df.National_FBP_Fueltypes_2014.values[:-3].astype(float)
# # tick_levels = list(np.array(levels) - 0.5)
# # # tick_levels[-1] = levels[-1]
# cbar = plt.colorbar(sb, cax=ax_cb)
# # cbar.ax.set_yticklabels(ticks)  # set ticks of your format
# # cbar.ax.axes.tick_params(length=0)


# ## set map bounds
# if wrf_model == "wrf3":
#     ax.set_xlim([-140, -60])
#     ax.set_ylim([36, 70])
# elif wrf_model == "wrf4":
#     ax.set_xlim([-174, -30])
#     ax.set_ylim([25, 80])
# else:
#     pass

# fig.savefig( str(data_dir) + f"/images/stats/precip-{domain}-diff.png", dpi=240)


# # df = ds.to_dataframe().dropna()


# var_list = list(ds)[::3]
# time = np.array(ds.time.dt.strftime("%Y-%m-%d"), dtype="<U10")
# start_time = datetime.strptime(str(time[0]), "%Y-%m-%d").strftime("%Y%m%d")
# end_time = datetime.strptime(str(time[-1]), "%Y-%m-%d").strftime("%Y%m%d")
# colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]


# fig = plt.figure(figsize=[12, 18])  # figsize=[8, 8]
# length = len(var_list)
# for i in range(length):
#     # plt.subplot(i+1, 1, 1)
#     ax = fig.add_subplot(length+1, 1, i+1)
#     var = var_list[i]
#     df_final = df[np.abs(df[var]-df[var].mean()) <= (2*df[var].std())]
#     df_final = df_final[np.abs(df_final[var + "_day1"]-df_final[var + "_day1"].mean()) <= (2*df_final[var + "_day1"].std())]
#     df_final = df_final.groupby('time').mean()
#     var_obs = df_final[var].values
#     var_model = df_final[var + "_day1"].values
#     ax.set_ylabel(var.upper())
#     ax.set_xticks([])
#     ax.plot(df_final.index, var_obs, label = 'Obs')
#     ax.plot(df_final.index, var_model, label = 'Model')

# ax.plot(df_final.index, var_obs, color = colors[0])
# ax.plot(df_final.index, var_model, color = colors[1])
# ax.set_xlabel("Time")
# ax.legend(
#     loc="upper center",
#     bbox_to_anchor=(0.5, 16.08),
#     ncol=2,
#     fancybox=True,
#     shadow=True,
# )
# fig.savefig(
#     str(data_dir) + f"/images/stats/all-vars-{domain}-mean.png"
# )
# plt.close()


# fig = plt.figure(figsize=[14, 14])  # figsize=[8, 8]
# length = len(var_list)
# fwi_list = var_list[:7]
# length = len(fwi_list)
# for i in range(length):
#     # plt.subplot(i+1, 1, 1)
#     ax = fig.add_subplot(length+1, 1, i+1)
#     var = fwi_list[i]
#     df_final = df[np.abs(df[var]-df[var].mean()) <= (2*df[var].std())]
#     df_final = df_final[np.abs(df_final[var + "_day1"]-df_final[var + "_day1"].mean()) <= (2*df_final[var + "_day1"].std())]
#     df_final = df_final.groupby('time').mean()
#     var_obs = df_final[var].values
#     var_model = df_final[var + "_day2"].values
#     ax.set_ylabel(var.upper())
#     ax.plot(df_final.index, var_obs, label = 'Obs')
#     ax.plot(df_final.index, var_model, label = 'Model')

# ax.set_xlabel("Time")
# ax.legend(
#     loc="upper center",
#     bbox_to_anchor=(0.5, 1.08),
#     ncol=2,
#     fancybox=True,
#     shadow=True,
# )
# fig.savefig(
#     str(data_dir) + f"/images/stats/fwi-vars-{domain}-mean.png"
# )
# plt.close()


# fig = plt.figure(figsize=[14, 14])  # figsize=[8, 8]
# length = len(var_list)
# met_list = var_list[7:]
# length = len(met_list)
# for i in range(length):
#     # plt.subplot(i+1, 1, 1)
#     ax = fig.add_subplot(length+1, 1, i+1)
#     var = met_list[i]
#     df_final = df[np.abs(df[var]-df[var].mean()) <= (2*df[var].std())]
#     df_final = df_final[np.abs(df_final[var + "_day1"]-df_final[var + "_day1"].mean()) <= (2*df_final[var + "_day1"].std())]
#     df_final = df_final.groupby('time').mean()
#     var_obs = df_final[var].values
#     var_model = df_final[var + "_day2"].values
#     ax.set_ylabel(var.upper())
#     ax.plot(df_final.index, var_obs, label = 'Obs')
#     ax.plot(df_final.index, var_model, label = 'Model')

# ax.set_xlabel("Time")
# ax.legend(
#     loc="upper center",
#     bbox_to_anchor=(0.5, 1.08),
#     ncol=2,
#     fancybox=True,
#     shadow=True,
# )
# fig.savefig(
#     str(data_dir) + f"/images/stats/met-vars-{domain}-mean.png"
# )
# plt.close()

cmap = cm.get_cmap("tab10", len(list(ds)[::3]) + 1)  # PiYG
colors = []
for i in range(cmap.N):
    rgba = cmap(i)
    colors.append(matplotlib.colors.rgb2hex(rgba))

var_dict = {
    "bui": {"ext": 20},
    "dc": {"ext": 80},
    "dmc": {"ext": 21},
    "ffmc": {"ext": 74},
    "fwi": {"ext": 5},
    "isi": {"ext": 2},
}


def reject_outliers(x, y, m=3):
    return (
        x[abs(x - np.mean(x)) < m * np.std(x)],
        y[abs(x - np.mean(x)) < m * np.std(x)],
    )


def checkstats(var, color):
    time = np.array(ds.time.dt.strftime("%Y-%m-%d"), dtype="<U10")
    start_time = datetime.strptime(str(time[0]), "%Y-%m-%d").strftime("%Y%m%d")
    end_time = datetime.strptime(str(time[-1]), "%Y-%m-%d").strftime("%Y%m%d")
    # var_obs = ds[var].values.flatten()
    # var_modeld = ds[var + "_day1"].values.flatten()
    var_obs = df[var].values
    var_modeld = df[var + "_day1"].values
    ind = ~np.isnan(var_obs)
    var_obs_ = var_obs[ind]
    var_modeld_ = var_modeld[ind]
    try:
        index = np.where(var_obs_ > var_dict[var]["ext"])[0]
        var_obs_ = var_obs_[index]
        var_modeld_ = var_modeld_[index]
        index = np.where(var_modeld_ > var_dict[var]["ext"])[0]
        var_obs_ = var_obs_[index]
        var_modeld_ = var_modeld_[index]
    except:
        pass
    var_obs_, var_modeld_ = reject_outliers(var_obs_, var_modeld_)
    var_modeld_, var_obs_ = reject_outliers(var_modeld_, var_obs_)
    result = scipy.stats.linregress(var_modeld_, var_obs_)
    rmse = str(round(mean_squared_error(var_obs_, var_modeld_, squared=False), 3))
    print(len(var_modeld_) == len(var_obs_))
    print(var.upper())
    print("slope ", result.slope)
    print("intercept ", result.intercept)
    print("rvalue ", result.rvalue)
    print("pvalue ", result.pvalue)
    print("stderr ", result.stderr)
    print("rmse ", rmse)
    print("-------------------------")
    plt.close()
    fig = plt.figure()  # figsize=[8, 8]
    ax = fig.add_subplot(1, 1, 1)
    ax.set_title(
        f"WRF3 Domain {res} for {var.upper()} \n slope: {round(result.slope,3)}  intercept: {round(result.intercept,3)}  rvalue: {round(result.rvalue,3)}  rmse: {rmse}  \n {start_time}-{end_time}"
    )
    # ax.set_title(
    #     f"WRF3 Domain {res} for {var.upper()} \n  rvalue: {round(rvalue,3)}  rmse: {rmse}  \n {start_time}-{end_time}"
    # )
    ax.scatter(var_modeld_, var_obs_, s=0.5, color=color, label="data")
    xpoints = ypoints = ax.get_xlim()
    ax.plot(
        xpoints,
        ypoints,
        linestyle="--",
        color="k",
        lw=0.6,
        scalex=False,
        scaley=False,
        label="y = x",
    )
    ax.plot(
        var_modeld_,
        result.intercept + result.slope * var_modeld_,
        "r",
        label="fitted line",
    )
    ax.legend()
    ax.set_xlabel("Modeled")
    ax.set_ylabel("Observed")
    fig.savefig(
        str(data_dir) + f"/images/stats/{var}-{domain}-{start_time}-{end_time}.png"
    )
    plt.close()

    return


var_list = list(ds)[::3]
for i in range(len(var_list)):
    checkstats(var_list[i], colors[i])
