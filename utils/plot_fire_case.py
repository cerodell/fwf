#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import context
import salem
import numpy as np
import xarray as xr
from pathlib import Path


from scipy import stats
from utils.stats import MBE, RMSE
from sklearn.metrics import r2_score

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from context import root_dir, data_dir
import matplotlib.dates as mdates


def drop_outside_std(ds_time_avg, arr, num_std=4):
    arr = ds_time_avg["OBS_FRP"].values
    # Calculate mean and standard deviation
    mean = np.nanmean(arr)
    std = np.nanstd(arr)

    # Define range based on number of standard deviations
    lower_bound = mean - num_std * std
    upper_bound = mean + num_std * std

    # Filter values within the range
    filtered_arr = arr[(arr >= lower_bound) & (arr <= upper_bound)]

    return float(np.max(filtered_arr))


def plot_fire(fire_i, ds, persist, dt, save_dir, plot_method):
    ds_map = ds.rename({"FRP": "OBS_FRP"})[["OBS_FRP", "MODELED_FRP"]].compute()

    nan_space = []
    nan_time = []
    for i in range(len(ds_map.time)):
        nan_array = np.isnan(ds_map["OBS_FRP"].isel(time=i)).values
        zero_full = np.zeros(nan_array.shape)
        zero_full[nan_array == False] = 1
        unique, counts = np.unique(nan_array, return_counts=True)
        nan_space.append(zero_full)
        if unique[0] == False:
            nan_time.append(counts[0])
        else:
            nan_time.append(0)

    # ds_map = ds_map.isel(time = slice(0,(len(ds.time)//24)*24))

    if persist == True:
        ds_active = ds_map.isel(time=slice(0, dt))
        nan_array = np.isnan(ds_active["OBS_FRP"]).values
        zero_full = np.zeros(nan_array.shape)
        zero_full[nan_array == False] = 1
        nan_space = np.sum(np.stack(zero_full), axis=0)
        # nan_space = np.stack(zero_full)

        active_list = []
        nan_time = []
        for i in range(dt, len(ds_map.time), dt):
            ds_active = ds_map.isel(time=slice(i, i + dt))
            nan_array = np.isnan(ds_active["OBS_FRP"]).values
            ds_active["MODELED_FRP"] = xr.where(
                nan_space <= 0, np.nan, ds_active["MODELED_FRP"]
            )
            # if plot_method== 'sum':
            ## scale the sum according to the number of time each grid was used, this prevents over counting
            # ds_active["MODELED_FRP"] = ds_active["MODELED_FRP"] / nan_space
            zero_full = np.zeros(nan_array.shape)
            zero_full[nan_array == False] = 1
            nan_space = np.sum(np.stack(zero_full), axis=0)
            # nan_space = np.stack(zero_full)
            active_list.append(ds_active)
        ds_map = xr.combine_nested(active_list, concat_dim="time")
    else:
        ds_map = xr.where(np.isnan(ds_map["OBS_FRP"].values) == True, np.nan, ds_map)

    ds_map = ds_map.salem.roi(shape=fire_i, all_touched=True)

    ds_space_avg = ds_map.mean(dim=("x", "y"))
    ds_space_sum = ds_map.sum(dim=("x", "y"))

    ds_time_avg = ds_map.mean(dim=("time"))
    ds_time_sum = ds_map.sum(dim=("time"))
    ds_time_avg = ds_time_avg.salem.roi(shape=fire_i, all_touched=True)
    ds_time_sum = ds_time_sum.salem.roi(shape=fire_i, all_touched=True)

    plt.rcParams.update({"font.size": 16})

    fig = plt.figure(figsize=(16, 12))
    # Create a gridspec layout
    # The first row (for maps) is twice the height of the second row (for line plots)
    gs = gridspec.GridSpec(2, 2, height_ratios=[3, 1])
    g = salem.GoogleVisibleMap(
        x=[fire_i.min_x, fire_i.max_x],
        y=[fire_i.min_y, fire_i.max_y],
        scale=2,  # scale is for more details
        maptype="satellite",
        size_x=40,
        size_y=40,
    )  # try out also: 'terrain'

    if plot_method == "norm":
        nan_space = []
        nan_time = []
        for i in range(len(ds_map.time)):
            nan_array = np.isnan(ds_map["OBS_FRP"].isel(time=i)).values
            zero_full = np.zeros(nan_array.shape)
            zero_full[nan_array == False] = 1
            unique, counts = np.unique(nan_array, return_counts=True)
            nan_space.append(zero_full)
            if unique[0] == False:
                nan_time.append(counts[0])
            else:
                nan_time.append(0)

        nan_space = np.sum(np.stack(nan_space), axis=0)
        ds_space = ds_space_sum
        ds_time = ds_time_sum
        ds_time = ds_time / (nan_space * 9)
        ds_space = ds_space / (np.array(nan_time) * 9)
        model_title = "MODELED FIRE RADIATIVE POWER NORM. (MW)"
        obs_title = "OBSERVED FIRE RADIATIVE POWER NORM. (MW)"
        vmax = (
            drop_outside_std(ds_time, ds_time["OBS_FRP"].values)
            + float(ds_time["MODELED_FRP"].max())
        ) / 2

    elif plot_method == "sum":
        ds_space = ds_space_sum
        ds_time = ds_time_sum
        model_title = "MODELED FIRE RADIATIVE POWER SUM. (MW)"
        obs_title = "OBSERVED FIRE RADIATIVE POWER SUM. (MW)"
        vmax = (
            (
                (
                    drop_outside_std(ds_time, ds_time["OBS_FRP"].values)
                    + float(ds_time["MODELED_FRP"].max())
                )
                / 2
            )
            // 50
            * 50
        )
        if vmax > 2000:
            vmax -= 500

    elif plot_method == "mean":
        ds_space = ds_space_avg
        ds_time = ds_time_avg
        model_title = "MODELED FIRE RADIATIVE POWER MEAN (MW)"
        obs_title = "OBSERVED FIRE RADIATIVE POWER MEAN (MW)"
        vmax = (
            (
                (
                    drop_outside_std(ds_time, ds_time["OBS_FRP"].values)
                    + float(ds_time["MODELED_FRP"].max())
                )
                / 2
            )
            // 50
            * 50
        )
        if vmax > 2000:
            vmax -= 500
        if vmax < 10:
            vmax = 30

    for var in list(ds_map):
        ds_time[var].attrs = ds.attrs
    ds_time.attrs = ds.attrs

    # First map on the top left
    ax = fig.add_subplot(gs[0, 0])
    ax.set_title(model_title)
    sm = salem.Map(g.grid, factor=1, countries=False, cmap="YlOrRd", vmax=vmax, vmin=0)
    sm.set_shapefile(fire_i, lw=1.5, color="tab:red")
    sm.set_data(ds_time["MODELED_FRP"], overplot=True)
    sm.set_scale_bar(
        location=(0.88, 0.94),
    )
    sm.visualize(ax=ax)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    # Second map on the top right
    ax = fig.add_subplot(gs[0, 1])
    ax.set_title(obs_title)
    sm = salem.Map(g.grid, factor=1, countries=False, cmap="YlOrRd", vmax=vmax, vmin=0)
    sm.set_shapefile(fire_i, lw=1.5, color="tab:red")
    sm.set_data(ds_time["OBS_FRP"], overplot=True)
    sm.set_scale_bar(location=(0.88, 0.94))
    sm.visualize(ax=ax)
    ax.set_yticklabels([])
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    ax = fig.add_subplot(gs[1, :])

    ax.plot(
        ds_space.time,
        ds_space["OBS_FRP"],
        color="k",
        label="OBSERVED FRP",
        lw=2.5,
        zorder=1,
    )
    ax.plot(
        ds_space.time,
        ds_space["MODELED_FRP"],
        color="tab:red",
        label="MODELED FRP",
        lw=1.85,
        zorder=10,
    )
    # ax.plot(
    #     ds_space.time,
    #     ds_space_avg_modeled,
    #     color="tab:red",
    #     ls = '--',
    #     lw=1.85,
    #     zorder=10,
    # )
    ax.legend(
        ncol=3,
        fancybox=True,
        shadow=True,
        bbox_to_anchor=(0.38, 1.25),
    )
    # Set major and minor ticks format
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))

    # Rotate date labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    ds_nan_free = ds_space.dropna("time")
    MODELED_FRP = ds_nan_free["MODELED_FRP"].values
    OBS_FRP = ds_nan_free["OBS_FRP"].values

    ax.set_title(
        "pearsonr: " + str(np.round(stats.pearsonr(OBS_FRP, MODELED_FRP)[0], 2)) +
        # "\n r2_score: " + str(np.round(r2_score(OBS_FRP, MODELED_FRP), 2)) +
        "\n mbe: "
        + str(np.round(MBE(OBS_FRP, MODELED_FRP), 2))
        + "\n rmse: "
        + str(np.round(RMSE(OBS_FRP, MODELED_FRP), 2)),
        loc="right",
    )
    # Adjust layout for a better fit
    save_dir = Path(save_dir + "/img")
    save_dir.mkdir(parents=True, exist_ok=True)

    if persist == True:
        fig.tight_layout()
        fig.savefig(
            str(save_dir)
            + f"/{int(fire_i['id'].values[0])}-{plot_method}-persist-{dt}.png"
        )
        plt.close()
    else:
        fig.tight_layout()
        fig.savefig(str(save_dir) + f"/{int(fire_i['id'].values[0])}-{plot_method}.png")
        plt.show()

    return
