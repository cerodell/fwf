import context
import salem
import json
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.neighbors import KDTree

from datetime import datetime
from utils.wrf_ import read_wrf
from utils.eccc import read_eccc
from utils.era5 import read_era5

from context import data_dir, root_dir


plt.rc("font", family="sans-serif")
plt.rc("text", usetex=True)
plt.rcParams.update({"font.size": 18})


__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


def get_time_offest(case_study, case_info):

    domain = case_info["domain"]
    static_ds = salem.open_xr_dataset(
        str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
    )
    pyproj_srs = static_ds.attrs["pyproj_srs"]
    df_center = pd.DataFrame(
        {
            "latitude": [np.mean([case_info["min_lat"], case_info["max_lat"]])],
            "longitude": [np.mean([case_info["min_lon"], case_info["max_lon"]])],
        }
    )
    print(df_center)
    center_x, center_y = get_locs(pyproj_srs, df_center)

    utc_offset = static_ds["ZoneST"].interp(
        west_east=center_x, south_north=center_y, method="nearest"
    )
    return utc_offset


def build_tree(case_study, case_info, frp_lats, frp_lons):
    domain = case_info["domain"]

    static_ds = salem.open_xr_dataset(
        str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
    )
    shape = static_ds.XLAT.shape
    locs = pd.DataFrame(
        {"lats": static_ds.XLAT.values.ravel(), "lons": static_ds.XLONG.values.ravel()}
    )
    ## build kdtree
    fwf_tree = KDTree(locs)
    print("Fire KDTree built")
    yy, xx = [], []
    # df = pd.DataFrame(
    #     {'lat': [case_info['min_lat'],case_info['max_lat'], case_info['max_lat'], case_info['min_lat']],
    #     'lon': [case_info['min_lon'],case_info['min_lon'], case_info['max_lon'], case_info['max_lon']]
    #     }
    # )
    df = pd.DataFrame({"lat": frp_lats, "lon": frp_lons})
    for index, row in df.iterrows():
        ## arange wx station lat and long in a formate to query the kdtree
        single_loc = np.array([row.lat, row.lon]).reshape(1, -1)
        ## query the kdtree retuning the distacne of nearest neighbor and index
        dist, ind = fwf_tree.query(single_loc, k=1)
        ## set condition to pass on fire farther than 0.1 degrees
        if dist > 0.1:
            pass
        else:
            ## if condition passed reformate 1D index to 2D indexes
            ind_2d = np.unravel_index(int(ind), shape)
            ## append the indexes to lists
            yy.append(ind_2d[0])
            xx.append(ind_2d[1])
    yy, xx = np.array(yy), np.array(xx)
    # yy, yy_counts = np.unique(yy, return_counts=True)
    # xx, xx_counts = np.unique(xx, return_counts=True)

    return yy, xx


def normalize(ds, yy, xx, norm_ds):
    norm_ds_i = norm_ds.isel(south_north=yy, west_east=xx)
    norm_ds_i = norm_ds_i.mean(dim=["south_north", "west_east"])
    ds = (ds["S"] - norm_ds_i["S_min"]) / (
        norm_ds_i["S_max"] - norm_ds_i["S_min"]
    ).rename("S")
    return ds


def open_fwf(doi, filein, domain, model, yy, xx, utc_offset, var_list=False):
    ds = xr.open_dataset(
        filein + f"/fwf-{model}-{domain}-{doi.strftime('%Y%m%d06')}.nc"
    ).chunk("auto")

    if model == "hourly":
        ds["time"] = ds["Time"]
        ds = ds.isel(time=slice(0, 24))
        ds["time"] = ds["time"] - np.timedelta64(int(utc_offset), "h")
        if var_list == False:
            ds = ds[["S", "F"]]
        else:
            ds = ds[var_list]

    elif model == "daily":
        ds = ds.isel(time=0)
        if var_list == False:
            ds = ds[["S", "mS"]]
        else:
            ds = ds[var_list]
    ds = ds.isel(south_north=yy, west_east=xx)
    ds = ds.mean(dim=["south_north", "west_east"])

    return ds


def open_frp(case_study, case_info, doi=False, max_comp=False):
    frp_ds = xr.open_dataset(
        str(data_dir) + f"/frp/analysis/goes/{case_study}-goes-test.nc"
    )
    frp_ds = frp_ds.rename({"t": "time"})
    keep_dates = np.where(
        (frp_ds["time"].values <= pd.to_datetime("2020-01-01")) == False
    )
    frp_ds = frp_ds.isel(time=keep_dates[0])
    frp_ds = frp_ds.sortby("time")

    utc_offset = get_time_offest(case_study, case_info)
    frp_ds["time"] = frp_ds["time"] - np.timedelta64(int(utc_offset), "h")
    if case_study == "marshall_fire":
        pass
    else:
        frp_ds["Power"] = xr.where(
            (frp_ds["Mask"] == 10) | (frp_ds["Mask"] == 30) | (frp_ds["Mask"] == 13),
            frp_ds["Power"],
            np.nan,
        )

    frp_da = frp_ds["Power"].mean(dim=["x", "y"])
    frp_da_og = frp_da
    frp_da = frp_da.resample(time="1H").mean()
    date_range = frp_da["time"].values

    non_nan_indices = np.where(~np.isnan(frp_da))[0]
    diff_arr = np.diff(non_nan_indices)
    g12 = np.where(diff_arr > 6)[0]
    if max_comp == False:
        if len(g12) > 0:
            if (
                date_range[non_nan_indices[g12[0]]] - date_range[non_nan_indices[0]]
            ).astype("timedelta64[h]") >= 6:
                start_int = 0
                start = date_range[non_nan_indices[start_int]]
                stop = date_range[non_nan_indices[g12[0]]]
                print("Passed 1")
            else:
                start_int = g12[0]
                start = date_range[non_nan_indices[start_int]]
                stop = date_range[non_nan_indices[g12[1]]]
                print("Passed 2")
        else:
            start_int = 0
            start = date_range[non_nan_indices[start_int]]
            stop = date_range[non_nan_indices[-1]]
            print("Passed 3")

        if (stop - start).astype("timedelta64[D]") > 10:
            print(
                f"{case_study} passed 12 hours of missing data test but exceed ten days of observations, truncating to short comparison time"
            )
            stop = date_range[non_nan_indices[start_int] + (24 * 10)]
        if (stop - start).astype("timedelta64[h]") < 24:
            if case_study not in [
                "marshall_fire",
                "caldor_fire",
                "fire_east_tulare",
                "lytton_creek",
                "lazy_fire",
            ]:
                raise ValueError(
                    f"{case_study} does not pass conditions, must be thrown out"
                )

        if case_study == "caldor_fire":
            # start = np.datetime64('2021-08-17-T10:00')
            start = np.datetime64("2021-08-16T10:00:00.000000000")
        if case_study == "marshall_fire":
            start = np.datetime64("2021-12-30T00:00:00.000000000")
            # stop = np.datetime64('2021-12-30T22:00:00.000000000')
            stop = np.datetime64("2021-12-31T12:00:00.000000000")
        if case_study == "fire_east_tulare":
            start = np.datetime64("2021-09-15T12:00:00.000000000")
            stop = np.datetime64("2021-09-20T02:00:00.000000000")
        if case_study == "lytton_creek":
            start = np.datetime64("2021-06-30T12:00:00.000000000")
            stop = np.datetime64("2021-07-06T00:00:00.000000000")
        #     start = date_range[non_nan_indices[0]]
        #     stop = date_range[non_nan_indices[-1]]
        if case_study == "wildcat":
            # start = np.datetime64('2021-08-17-T10:00')
            start = np.datetime64("2021-07-22T22:00:00.000000000")

    else:
        start = date_range[non_nan_indices[0]]
        stop = date_range[non_nan_indices[-1]]

    frp_da = frp_da.sel(time=slice(start, stop))
    frp_da_og = frp_da_og.sel(time=slice(start, stop))
    frp_ds = frp_ds.sel(time=slice(start, stop))

    if doi != False:
        frp_lats = frp_ds["lats"].values[
            ~np.isnan(frp_ds.sel(time=doi).mean(dim="time")["Power"].values)
        ]
        frp_lons = frp_ds["lons"].values[
            ~np.isnan(frp_ds.sel(time=doi).mean(dim="time")["Power"].values)
        ]
    else:
        frp_lats = frp_ds["lats"].values[
            ~np.isnan(frp_ds.mean(dim="time")["Power"].values)
        ]
        frp_lons = frp_ds["lons"].values[
            ~np.isnan(frp_ds.mean(dim="time")["Power"].values)
        ]

    return frp_ds, frp_da, frp_da_og, frp_lats, frp_lons, utc_offset, start, stop


# def open_fwf(doi, filein, domain,model):
#     if model == "hourly":
#         indexer = slice(0, 24)
#     elif model == "daily":
#         indexer = 0
#     ds = (
#         xr.open_dataset(
#             filein + f"/fwf-{model}-{domain}-{doi.strftime('%Y%m%d06')}.nc"
#         )
#         .isel(time=indexer)
#         # .chunk("auto")
#     )
#     # try:
#     #     ds = ds[["S", "F", "HFI", "R"]]
#     # except:
#     ds = ds[["S", "F", "R"]]
#     # print(len(ds['south_north']))
#     # print(doi)
#     # ds = ds.transpose('west_east', 'south_north', 'time')
#     return ds


def hourly_precip(hourly_ds):
    mask = hourly_ds.time.dt.hour == 23
    idx = np.where(mask == True)[0]
    rain = []
    rain.append(list(hourly_ds["r_o"].isel(time=slice(0, idx[0])).values))
    # for j in range(len(idx)):
    for i in range(len(idx)):
        try:
            print(i)
            hrd = hourly_ds["r_o"].isel(time=slice(idx[i] + 1, idx[i + 1])).values
            for j in range(i + 1):
                h23 = hourly_ds["r_o"].isel(time=idx[j]).values
                hrd = hrd + h23
                print("j", j)
                if i == j:
                    rain.append([float(hrd[0])])
            rain.append(list(hrd))
        except:
            print(i)
            hrd = hourly_ds["r_o"].isel(time=slice(idx[i] + 1, -1)).values
            for j in range(i + 1):
                h23 = hourly_ds["r_o"].isel(time=idx[j]).values
                hrd = hrd + h23
                print("j", j)
                if i == j:
                    rain.append([float(hrd[0])])
            rain.append(list(hrd))
    rain.append(list([rain[-1][-1]]))
    flattened_list = [item for sublist in rain for item in sublist]
    hourly_ds["r_o"] = ("time", flattened_list)
    if hourly_ds["r_o"].values[0] != 0.0:
        hourly_ds["r_o"] = hourly_ds["r_o"] - hourly_ds["r_o"].values[0]

    r_oi = np.array(hourly_ds["r_o"])
    r_hourly = np.diff(r_oi, prepend=0)
    r_hourly[r_hourly < 0.1] = 0
    r_hourly = xr.DataArray(r_hourly, name="r_o_hourly", dims=("time"))
    hourly_ds["r_o_hourly"] = r_hourly
    return hourly_ds


def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)


def set_axis_postion_full_fwx(ax, side, offset, label):
    ax.spines[side].set_position(("outward", offset))
    make_patch_spines_invisible(ax)
    ax.spines[side].set_visible(True)
    ax.yaxis.set_label_position(side)
    ax.yaxis.set_ticks_position(side)
    ax.set_ylabel(label, fontsize=20)
    try:
        color = ax.get_lines()[0].get_color()
    except:
        color = ax.collections[0].get_edgecolor()
    ax.yaxis.label.set_color(color)
    tkw = dict(size=4, width=1.5, labelsize=18)
    ax.tick_params(
        axis="y",
        colors=color,
        **tkw,
    )
    # ax.grid(True)
    ax.grid(which="major", axis="x", linestyle="--", zorder=2, lw=0.3)


def set_axis_postion(ax, label, color=False):
    ax.set_ylabel(label, fontsize=20)
    try:
        ax.yaxis.label.set_color(ax.get_lines()[0].get_color())
    except:
        ax.yaxis.label.set_color(color=color, labelsize=20)
    tkw = dict(size=4, width=1.5, labelsize=18)
    ax.tick_params(
        axis="y",
        colors=ax.get_lines()[0].get_color(),
        **tkw,
    )
    # ax.grid(True)
    ax.grid(which="major", axis="x", linestyle="--", zorder=2, lw=0.3)


def get_locs(pyproj_srs, df):
    # get_locs_time = datetime.now()
    gpm25 = gpd.GeoDataFrame(
        df,
        crs="EPSG:4326",
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
    ).to_crs(pyproj_srs)

    x = xr.DataArray(
        np.array(gpm25.geometry.x),
        dims="loc",
        coords=dict(loc=np.arange(len(df))),
    )
    y = xr.DataArray(
        np.array(gpm25.geometry.y),
        dims="loc",
        coords=dict(loc=np.arange(len(df))),
    )
    try:
        x = x.assign_coords(frp=("loc", df["frp"]))
        y = y.assign_coords(frp=("loc", df["frp"]))
    except:
        pass
    return x, y
