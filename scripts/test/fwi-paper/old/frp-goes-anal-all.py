#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import json
import salem

import numpy as np
import xarray as xr
import pandas as pd
from scipy import stats
from pathlib import Path

from sklearn.neighbors import KDTree

import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from utils.frp import open_fwf, set_axis_postion, get_locs
from context import data_dir, root_dir


__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

#################### INPUTS ####################
## define model domain and path to fwf data
save_fig = True
case_study = "mcdougall_creek"

################## END INPUTS ####################

#################### OPEN FILES ####################

## open case study json file
with open(str(root_dir) + f"/json/fire-cases.json", "r") as fp:
    case_dict = json.load(fp)

# for case_study in list(case_dict):
for case_study in ["wildcat"]:

    # print(case_study)
    try:
        case_info = case_dict[case_study]
        domain = case_info["domain"]
        goes = case_info["goes"]
        save_dir = Path(str(data_dir) + f"/images/frp/goes/")
        save_dir.mkdir(parents=True, exist_ok=True)
        filein = f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/02/"

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
        center_x, center_y = get_locs(pyproj_srs, df_center)
        utc_offset = static_ds["ZoneDT"].interp(
            west_east=center_x, south_north=center_y, method="nearest"
        )

        frp_ds = xr.open_dataset(
            str(data_dir) + f"/frp/analysis/{case_study}-goes-test.nc"
        )
        frp_da = frp_ds["Power"].mean(dim=["x", "y"])
        frp_date_range = frp_da["t"].values
        keep_dates = np.where((frp_date_range <= pd.to_datetime("2020-01-01")) == False)
        frp_da = frp_da.isel(t=keep_dates[0])
        frp_da = frp_da.sortby("t")
        frp_da_og = frp_da
        frp_da = frp_da.resample(t="1H").mean()
        # frp_da_re = frp_da
        # frp_da = frp_da.interpolate_na(dim="t", method="linear") #pchip or linear
        frp_da_og["time"] = frp_da_og["t"]
        frp_da["time"] = frp_da["t"]

        date_range = frp_da["t"].values
        date_range2 = pd.date_range(
            date_range[0] - np.timedelta64(2, "D"),
            date_range[-1] + np.timedelta64(2, "D"),
            freq="D",
        )
        ## open fwf hourly
        hourly_ds = xr.combine_nested(
            [open_fwf(doi, filein, domain, "hourly") for doi in date_range2], "time"
        )
        daily_ds = xr.combine_nested(
            [open_fwf(doi, filein, domain, "daily") for doi in date_range2], "time"
        )

        hourly_ds["time"] = hourly_ds["Time"]
        hourly_ds["time"] = hourly_ds["time"] - np.timedelta64(int(utc_offset), "h")

        daily_ds["time"] = daily_ds["Time"]
        daily_ds = daily_ds.resample(time="1H").nearest()
        # daily_ds["time"] = daily_ds["time"] - np.timedelta64(int(utc_offset), "h")
        # daily_ds["time"] = daily_ds["time"] + np.timedelta64(12, "h")

        frp_da["time"] = frp_da["time"] - np.timedelta64(int(utc_offset), "h")
        frp_da["t"] = frp_da["time"]

        frp_da_og["time"] = frp_da_og["time"] - np.timedelta64(int(utc_offset), "h")
        frp_da_og["t"] = frp_da_og["time"]

        shape = hourly_ds.XLAT.shape
        locs = pd.DataFrame(
            {
                "lats": hourly_ds.XLAT.values.ravel(),
                "lons": hourly_ds.XLONG.values.ravel(),
            }
        )
        ## build kdtree
        fwf_tree = KDTree(locs)
        print("Fire KDTree built")
        yy, xx = [], []
        df = pd.DataFrame(
            {
                "lat": [
                    case_info["min_lat"],
                    case_info["max_lat"],
                    case_info["max_lat"],
                    case_info["min_lat"],
                ],
                "lon": [
                    case_info["min_lon"],
                    case_info["min_lon"],
                    case_info["max_lon"],
                    case_info["max_lon"],
                ],
            }
        )
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

        date_range = frp_da["t"].values
        hourly_ds = hourly_ds.isel(
            south_north=slice(yy.min(), yy.max()), west_east=slice(xx.min(), xx.max())
        ).sel(time=slice(date_range[0], date_range[-1]))
        hourly_ds = hourly_ds.mean(dim=["south_north", "west_east"])
        daily_ds = daily_ds.isel(
            south_north=slice(yy.min(), yy.max()), west_east=slice(xx.min(), xx.max())
        ).sel(time=slice(date_range[0], date_range[-1]))
        daily_ds = daily_ds.mean(dim=["south_north", "west_east"])

        # %%

        non_nan_indices = np.where(~np.isnan(frp_da))[0]
        diff_arr = np.diff(non_nan_indices)
        indices = np.where(diff_arr == 1)[0]
        groups = np.split(indices, np.where(np.diff(indices) != 1)[0] + 1)
        result = [group for group in groups if len(group) > 5]
        start = date_range[non_nan_indices[result[0][0]]]
        stop = date_range[non_nan_indices[result[0][0]] + (24 * 5)]
        # start = date_range[0]
        # stop = date_range[-1]
        # start = "2021-09-16-T00"
        # stop = "2021-09-29-T00"
        frp_da_slice = frp_da.sel(t=slice(start, stop))
        frp_raw = frp_da_slice.values
        frp_da_slice_int = frp_da_slice.interpolate_na(dim="t", method="linear").ffill(
            dim="t"
        )  # pchip or linear
        frp_da_og_slice = frp_da_og.sel(t=slice(start, stop))
        hourly_ds_slice = hourly_ds.sel(time=slice(start, stop))
        daily_ds_slice = daily_ds.sel(time=slice(start, stop))

        hfwi = hourly_ds_slice["S"].values
        hfrp = frp_da_slice_int.values
        dfwi = daily_ds_slice["S"].values
        study_range = hourly_ds_slice.time.values
        hfwip = hfwi[np.isnan(hfrp) == False]
        dfwip = dfwi[np.isnan(hfrp) == False]
        hfrpp = hfrp[np.isnan(hfrp) == False]

        unique, counts = np.unique(np.isnan(frp_raw), return_counts=True)
        pearsonr_h_interp_final = stats.pearsonr(hfwip, hfrpp)
        pearsonr_d_interp_final = stats.pearsonr(dfwip, hfrpp)
        # ################################ Plot Interp NEW FRP vs FWI ################################
        start = pd.to_datetime(study_range[0]).strftime("%B %d")
        stop = pd.to_datetime(study_range[-1]).strftime("%B %d")
        start_save = pd.to_datetime(study_range[0]).strftime("%Y%m%d")
        stop_save = pd.to_datetime(study_range[-1]).strftime("%Y%m%d")
        year = pd.to_datetime(study_range[-1]).strftime("%Y")

        fig = plt.figure(figsize=(12, 4))
        fig.suptitle(f"Fire Weather Index vs Fire Radiative Power", fontsize=18, y=1.08)
        ax = fig.add_subplot(1, 1, 1)
        ax.set_title(
            f"{case_study.replace('_', ' ').title()}",
            loc="center",
            fontsize=14,
        )
        ax.set_title(
            f"r: {round(pearsonr_h_interp_final[0],2)} Hourly FWI \nr: {round(pearsonr_d_interp_final[0],2)}   Daily FWI \n Percentage of observed values {round((counts[0]/len(frp_raw))*100,2)}",
            loc="right",
            fontsize=10,
        )
        ax2 = ax.twinx()
        ax.plot(
            hourly_ds_slice.time.values, hfwi, color="tab:blue", lw=1.2, label="Hourly"
        )
        ax.plot(
            daily_ds_slice.time.values,
            dfwi,
            color="tab:blue",
            ls="--",
            lw=1.2,
            label="Daily",
        )
        ax.plot(
            hourly_ds_slice.time.values,
            hfwi,
            color="tab:red",
            lw=1,
            label="FRP",
            zorder=0,
        )
        set_axis_postion(ax, "FWI")

        ax2.plot(frp_da_slice.time, frp_da_slice, color="tab:red", lw=1.2, label="FRP")
        ax2.plot(
            frp_da_slice.time, hfrp, lw=1.1, color="tab:red", ls="dotted", label="FRP"
        )

        # ax2.plot(frp_da_og_slice.t, frp_da_og_slice, color="pink", lw=1.2, label="FRP")

        set_axis_postion(ax2, "FRP (MW)")
        tkw = dict(size=4, width=1.5, labelsize=14)
        ax.tick_params(
            axis="x",
            **tkw,
        )
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d-%H"))
        ax.set_xlabel("Local DateTime (MM-DD)", fontsize=16)
        ax.legend(
            # loc="upper right",
            bbox_to_anchor=(0.38, 1.18),
            ncol=3,
            fancybox=True,
            shadow=True,
            fontsize=12,
        )
        fig.autofmt_xdate()
        print("------------------------------------")
        print(case_study)
        print(
            f"r: {round(pearsonr_h_interp_final[0],2)} Hourly FWI \nr: {round(pearsonr_d_interp_final[0],2)}   Daily FWI "
        )
        print(
            f"Precent of values that where observed {round((counts[0]/len(frp_raw))*100,2)}"
        )
        if save_fig == True:
            plt.savefig(
                str(save_dir) + f"/{case_study}.png",
                dpi=250,
                bbox_inches="tight",
            )
        del fwf_tree
        del frp_ds
        del frp_da
        del hourly_ds
        del daily_ds
    except:
        print("------------------------------------")
        print(case_study)
        print("ERROR")


# %%

# start = date_range2[4].strftime("%Y-%m-%d-T00")
# stop = date_range2[-2].strftime("%Y-%m-%d-T00")
# start = "2021-07-24-T00"
# stop = "2021-07-30-T00"
# frp_da_slice = frp_da.sel(t = slice(start, stop))
# frp_da_og_slice = frp_da_og.sel(t = slice(start, stop))

# hourly_ds_slice = hourly_ds.sel(time = slice(start, stop))
# daily_ds_slice = daily_ds.sel(time = slice(start, stop))


# hfwi = hourly_ds_slice["S"].values
# hfrp = frp_da_slice.values
# dfwi = daily_ds_slice["S"].values
# study_range = hourly_ds_slice.time.values

# pearsonr_h_interp_final = stats.pearsonr(hfwi, hfrp)
# pearsonr_d_interp_final = stats.pearsonr(dfwi, hfrp)
# # ################################ Plot Interp NEW FRP vs FWI ################################
# start = pd.to_datetime(study_range[0]).strftime("%B %d")
# stop = pd.to_datetime(study_range[-1]).strftime("%B %d")
# start_save = pd.to_datetime(study_range[0]).strftime("%Y%m%d")
# stop_save = pd.to_datetime(study_range[-1]).strftime("%Y%m%d")
# year = pd.to_datetime(study_range[-1]).strftime("%Y")

# fig = plt.figure(figsize=(12, 4))
# fig.suptitle(f"Fire Weather Index vs Fire Radiative Power", fontsize=18, y=1.08)
# ax = fig.add_subplot(1, 1, 1)
# ax.set_title(
#     f"{case_study.replace('_', ' ').title()}",
#     loc="center",
#     fontsize=14,
# )
# ax.set_title(
#     f"r: {round(pearsonr_h_interp_final[0],2)} Hourly FWI \nr: {round(pearsonr_d_interp_final[0],2)}   Daily FWI ",
#     loc="right",
#     fontsize=10,
# )
# ax2 = ax.twinx()
# ax.plot( hourly_ds_slice.time.values, hfwi, color="tab:blue", lw=1.2, label="Hourly")
# ax.plot( daily_ds_slice.time.values, dfwi, color="tab:blue", ls="--", lw=1.2, label="Daily")
# ax.plot( hourly_ds_slice.time.values, hfwi, color="tab:red", lw=1, label="FRP", zorder=0)
# set_axis_postion(ax, "FWI")

# ax2.plot(frp_da_slice.time, hfrp, color="tab:red", lw=1.2, label="FRP")
# ax2.plot(frp_da_og_slice.t, frp_da_og_slice, color="pink", lw=1.2, label="FRP")

# set_axis_postion(ax2, "FRP (MW)")
# tkw = dict(size=4, width=1.5, labelsize=14)
# ax.tick_params(
#     axis="x",
#     **tkw,
# )
# plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d-%H"))
# ax.set_xlabel("Local DateTime (MM-DD)", fontsize=16)
# ax.legend(
#     # loc="upper right",
#     bbox_to_anchor=(0.38, 1.18),
#     ncol=3,
#     fancybox=True,
#     shadow=True,
#     fontsize=12,
# )
# fig.autofmt_xdate()

# if save_fig == True:
#     plt.savefig(
#         str(save_dir) + f"/timeseries-goes.png",
#         dpi=250,
#         bbox_inches="tight",
#     )

# # %%
