#!/Users/crodell/miniconda3/envs/fwx/bin/python


"""
Script generates the frp v fwi figures used in the ams hourly fwi paper
"""
import context
import json
import gc

import numpy as np
import xarray as xr
import pandas as pd
from scipy import stats
from pathlib import Path

import matplotlib.colors
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import plotly.express as px


from utils.frp import (
    open_fwf,
    open_frp,
    set_axis_postion,
    build_tree,
    get_time_offest,
    normalize,
    normalize_era5,
    set_axis_postion_full_fwx,
    hourly_precip,
)
from context import data_dir, root_dir

plt.rc("font", family="sans-serif")
plt.rc("text", usetex=True)
plt.rcParams.update({"font.size": 18})

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

#################### INPUTS ####################
## define model domain and path to fwf data
save_fig = True
paper = False
norms = False
int_plot = False
full_fwx = False
case_study = "fire_east_tulare"  # ['barrington_lake_fire', 'wildcat', 'marshall_fire', 'oak_fire', 'caldor_fire', 'fire_east_tulare', 'rossmoore_fire', 'crater_creek', 'lytton_creek]
# print(case_study)

if paper == True:
    save_dir = Path("/Users/crodell/ams-fwf/LaTeX/img/fwf/")
    save_dir.mkdir(parents=True, exist_ok=True)
else:
    save_dir = Path(str(data_dir) + f"/images/frp/goes/hfi/")
    save_dir.mkdir(parents=True, exist_ok=True)
################## END INPUTS ####################

#################### OPEN FILES ####################
## open case study json file
with open(str(root_dir) + f"/json/fire-cases.json", "r") as fp:
    case_dict = json.load(fp)
#
print(case_study)
case_info = case_dict[case_study]
domain = case_info["domain"]
filein = f"/Volumes/WFRT-Ext21/fwf-data/wrf/{domain}/01/"

(frp_ds, frp_da, frp_da_og, frp_lats, frp_lons, utc_offset, start, stop) = open_frp(
    case_study, case_info
)


fwf_range = pd.date_range(
    start.astype("datetime64[D]") - pd.Timedelta(days=1),
    stop.astype("datetime64[D]") + pd.Timedelta(days=1),
)
yy, xx = build_tree(case_study, case_info, frp_lats, frp_lons)


if full_fwx == True:
    var_list = ["S", "HFI"]
    var_listD = var_list + ["D", "U", "P"]
else:
    var_list = var_listD = False

hourly_ds = xr.combine_nested(
    [
        open_fwf(doi, filein, domain, "hourly", yy, xx, utc_offset, var_list)
        for doi in fwf_range
    ],
    "time",
).sel(
    time=slice(start, stop)
)  # .compute()
fwf_range = pd.date_range(
    start.astype("datetime64[D]") - pd.Timedelta(days=2),
    stop.astype("datetime64[D]") + pd.Timedelta(days=2),
)


if norms == True:
    # norm_h = xr.open_dataset(str(data_dir) + f"/norm/fwi-hourly-{domain}.nc")
    norm_ds = normalize_era5(hourly_ds, yy, xx, utc_offset).rename("S").to_dataset()
    # hourly_ds = normalize(hourly_ds, yy, xx, norm_h).rename("S").to_dataset()


# %%
# start = date_range[0]
# stop = date_range[-1]
# start = "2021-07-24-T00"
# stop = "2021-07-29T00"
# start = date_range[non_nan_indices[result[1][0]]]
# stop = date_range[non_nan_indices[result[0][0]]+(24*10)]


frp_raw = frp_da.values
frp_da_interp = frp_da.interpolate_na(dim="time", method="linear").ffill(dim="time")


# nfwi = norm_ds['S'].values
hfwi = hourly_ds["S"].values
hfrp = frp_da_interp.values
hhfi = hourly_ds["HFI"].values
study_range = hourly_ds.time.values
unique, counts = np.unique(np.isnan(frp_raw), return_counts=True)
print(f"Precent of values that where observed {round((counts[0]/len(hfrp))*100,2)}")
hfwip = hfwi[np.isnan(frp_raw) == False]
hhfip = hhfi[np.isnan(frp_raw) == False]
hfrpp = hfrp[np.isnan(frp_raw) == False]


pearsonr_h_interp_final = stats.pearsonr(hfwip, hfrpp)
pearsonr_hfi_interp_final = stats.pearsonr(hhfip, hfrpp)


# %%
################################ Plot FRP vs FWI ################################
year = pd.to_datetime(study_range[-1]).strftime("%Y")


fig = plt.figure(figsize=(14, 4))
# fig.suptitle(f"    Fire Weather Index vs Fire Radiative Power", fontsize=22, y=1.3, x =0.52)

ax = fig.add_subplot(1, 1, 1)
title_line1 = (
    r"\fontsize{22pt}{24pt}\selectfont " + f"{case_study.replace('_', ' ').title()}"
)
title_line2 = r"\fontsize{18pt}{17pt}\selectfont " + f"{case_info['loc']}" + f", {year}"
title = f"{title_line1}\n{title_line2}"
ax.set_title(title, loc="center", fontdict={"usetex": True}, y=1.2)
# fig.suptitle(title, y=1.11)

if case_info["goes"] == "g16":
    sate = "GOES-East"
elif case_info["goes"] == "g17":
    sate = "GOES-West"
elif case_info["goes"] == "g18":
    sate = "GOES-West"
else:
    pass
if case_info["domain"] == "d02":
    reso = "12-km"
elif case_info["domain"] == "d03":
    reso = "4-km"
else:
    pass

ax.set_title(
    f"Satellite: {sate} \n WRF Domain: {reso} \n \n r: {round(pearsonr_h_interp_final[0],2)} Hourly FWI  \n r: {round(pearsonr_hfi_interp_final[0],2)} Hourly HFI  \n  Values observed: {round((counts[0]/len(frp_raw))*100,2)}"
    + r"$\%$",
    loc="right",
    fontsize=16,
)
ax.plot(hourly_ds.time, hfwi, color="tab:blue", lw=1.2, label="HFWI")
ax.plot(hourly_ds.time, hfwi, color="k", lw=1, label="HFRP", zorder=0)
ax.plot(hourly_ds.time, hfwi, color="tab:red", lw=1.0, label="HHFI", zorder=0)
# ax.plot(hourly_ds.time, hfwi, color="tab:blue", lw=1., ls = '--', label="NFWI")
set_axis_postion(ax, "FWI")

ax2 = ax.twinx()
ax2.plot(frp_da.time, frp_da, color="k", lw=1.2, label="FRP")
ax2.plot(frp_da.time, hfrp, lw=1.1, color="k", ls="dotted", label="FRP")
set_axis_postion(ax2, "FRP (MW)")


ax3 = ax.twinx()
ax3.plot(hourly_ds.time, hhfi, color="tab:red", lw=1.2, label="HHFI")
set_axis_postion(ax3, r"HFI (kW $m^{-1}$)", color=False, side="right", offset=80)

# ax4 = ax.twinx()
# ax4.plot(hourly_ds.time, hfwi, color="tab:blue", lw=1.2, ls = '--', label="NFWI")
# set_axis_postion(ax4, "NFWI ", color= False, side= 'left', offset = 80)


tkw = dict(size=4, width=1.5, labelsize=18)
ax.tick_params(
    axis="x",
    **tkw,
)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d-%H"))
# plt.gca().set_xticks(hourly_ds.time.values.astype("datetime64[D]"))
# plt.gca().xaxis.set_major_formatter()
ax.set_xlabel(f"Local DateTime (MM-DD-HH)", fontsize=18)
ax.legend(
    # loc="upper right",
    bbox_to_anchor=(0.42, 1.2),
    ncol=3,
    fancybox=True,
    shadow=True,
    fontsize=16,
)
fig.autofmt_xdate()


if save_fig == True:
    if paper == True:
        plt.savefig(str(save_dir) + f"/{case_study}.pdf", bbox_inches="tight")
        plt.savefig(str(save_dir) + f"/{case_study}.png", dpi=250, bbox_inches="tight")
    else:
        plt.savefig(str(save_dir) + f"/{case_study}.png", dpi=250, bbox_inches="tight")

# %%

# ############################ Map FRP on WRF GRID ################################

# static_ds = xr.open_dataset((str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"))
# fire = np.full_like(static_ds.XLONG, 0)
# for i in range(len(xx)):
#     fire[yy[i], xx[i]] += 1
# static_ds["fire"] = (("south_north", "west_east"), fire)
# static_ds1 = static_ds.isel(
#     west_east=slice(xx.min() - 5, xx.max() + 5),
#     south_north=slice(yy.min() - 5, yy.max() + 5),
# )


# cmap = matplotlib.pyplot.get_cmap("Reds", fire.max() + 5)


# hexl = []
# for i in range(cmap.N):
#     rgba = cmap(i)
#     hexl.append(matplotlib.colors.rgb2hex(rgba))

# hexl = ["green"] + hexl[6:]

# fig = plt.figure(figsize=(8, 8))
# ax = fig.add_subplot(1, 1, 1)
# if case_study == "caldor_fire":
#     x, y = 4, -3
#     XLONG = static_ds1["XLONG"].values[x:y, x:y]
#     XLAT = static_ds1["XLAT"].values[x:y, x:y]
#     weights = static_ds1["fire"].values[x:y, x:y]
# else:
#     XLONG = static_ds1["XLONG"].values
#     XLAT = static_ds1["XLAT"].values
#     weights = static_ds1["fire"].values
# sc = ax.pcolormesh(
#     XLONG,
#     XLAT,
#     weights,
#     zorder=1,
#     cmap=matplotlib.colors.ListedColormap(hexl),
#     alpha=0.5,
# )


# cbar = plt.colorbar(sc, ax=ax, pad=0.008)
# cbar.set_label("Weighted Count", rotation=270, fontsize=20, labelpad=20)

# # # Get the tick positions and labels
# # ticks = cbar.get_ticks()
# # labels = cbar.ax.get_yticklabels()  # Corrected line

# # # Offset the tick positions to center them
# # new_ticks = ticks + 0.5
# # cbar.set_ticks(new_ticks)

# # # Set the tick labels at the new positions
# # cbar.set_ticklabels(labels)

# XLONG = frp_ds["lons"].values
# XLAT = frp_ds["lats"].values

# fire = np.full_like(XLONG, np.nan)
# fire[~np.isnan(frp_ds.mean(dim="time")["Power"].values)] = 1
# ax.scatter(
#     XLONG[~np.isnan(frp_ds.mean(dim="time")["Power"].values)],
#     XLAT[~np.isnan(frp_ds.mean(dim="time")["Power"].values)],
#     color="k",
#     s=10,
# )
# ax.set_title(
#     f"GOES FRP Locations overlaid on WRF GRID \n {case_study.replace('_',' ').title()}",
#     fontsize=22,
# )
# ax.set_xlabel("Longitude", fontsize=20)
# ax.set_ylabel("Latitude", fontsize=20)
# if save_fig == True:
#     if paper == True:
#         plt.savefig(
#             str(save_dir) + f"/map-frp-count-{case_study}.pdf", bbox_inches="tight"
#         )
#         plt.savefig(
#             str(save_dir) + f"/map-frp-count-{case_study}.png",
#             dpi=250,
#             bbox_inches="tight",
#         )
#     else:
#         plt.savefig(
#             str(save_dir) + f"/map-frp-count-{case_study}.png",
#             dpi=250,
#             bbox_inches="tight",
#         )
# # %%

# if full_fwx == True:
#     hourly_ds = hourly_ds.compute()
#     daily_ds_wx = daily_ds_og2.compute()
#     daily_ds_fwx = daily_ds_wx.copy()
#     hourly_ds = hourly_precip(hourly_ds)
#     daily_ds_wx["time"] = daily_ds_wx["time"] + np.timedelta64(int(12), "h")
#     daily_ds_wx = daily_ds_wx.sel(time=slice(start, stop))
#     daily_ds_wx["Time"] = daily_ds_wx["time"]

#     daily_ds_fwx["time"] = daily_ds_fwx["time"] + np.timedelta64(int(16), "h")
#     daily_ds_fwx = daily_ds_fwx.sel(time=slice(start, stop))
#     daily_ds_fwx["Time"] = daily_ds_fwx["time"]
#     hourly_ds["Time"] = hourly_ds["time"]

#     # def plot_real(hourly_ds,daily_ds, title, casestudy_name, at_wmo = False):
#     colors_list = plt.rcParams["axes.prop_cycle"].by_key()["color"]
#     start_fwx = pd.to_datetime(hourly_ds.Time.values[0]).strftime("%B %d")
#     stop_fwx = pd.to_datetime(hourly_ds.Time.values[-1]).strftime("%B %d")
#     start_save = pd.to_datetime(hourly_ds.Time.values[0]).strftime("%Y%m%d")
#     stop_save = pd.to_datetime(hourly_ds.Time.values[-1]).strftime("%Y%m%d")
#     year = pd.to_datetime(hourly_ds.Time.values[-1]).strftime("%Y")
#     fig = plt.figure(figsize=(14, 12))
#     # fig.suptitle("Fire Weather Index System Sensitivity Case Study", fontsize=20)
#     ax = fig.add_subplot(2, 1, 1)
#     ax.set_title(f"{title} \n \nFire Weather", loc="left", fontsize=20)
#     ax.set_title(
#         f"WRF Domain: {reso} \n{start_fwx} - {stop_fwx}, {year}",
#         loc="right",
#         fontsize=20,
#     )
#     ffmc = ax
#     dmc = ax.twinx()
#     dc = ax.twinx()
#     isi = ax.twinx()
#     bui = ax.twinx()
#     fwi = ax.twinx()
#     marker = "D"
#     ffmc.plot(hourly_ds["Time"], hourly_ds.F, color=colors_list[1], lw=2, zorder=9)
#     # ffmc.plot(daily_ds_og['Time'],daily_ds_og.F, color=colors_list[1], lw=1, ls = '-.', zorder =9)
#     ffmc.scatter(
#         daily_ds_fwx["Time"],
#         daily_ds_fwx.F,
#         color=colors_list[1],
#         zorder=10,
#         marker=marker,
#     )

#     # dmc.plot(daily_ds_og.Time,daily_ds_og.P, color=colors_list[2], lw=2)
#     # dmc.plot(daily_ds_og.Time,daily_ds_og.P, color=colors_list[2], lw=1, ls = '-.', zorder = 7)
#     dmc.scatter(
#         daily_ds_fwx.Time, daily_ds_fwx.P, color=colors_list[2], zorder=8, marker=marker
#     )

#     # dc.plot(daily_ds.Time,daily_ds.D, color=colors_list[5], lw=2)
#     # dc.plot(daily_ds_og.Time,daily_ds_og.D, color=colors_list[5], lw=1, ls = '-.', zorder = 7)
#     dc.scatter(
#         daily_ds_fwx.Time, daily_ds_fwx.D, color=colors_list[5], zorder=8, marker=marker
#     )

#     isi.plot(hourly_ds.Time, hourly_ds.R, color=colors_list[4], lw=2, zorder=9)
#     # isi.plot(daily_ds_og.Time,daily_ds_og.R, color=colors_list[4], lw=1, ls = '-.', zorder = 9)
#     isi.scatter(
#         daily_ds_fwx.Time,
#         daily_ds_fwx.R,
#         color=colors_list[4],
#         zorder=10,
#         marker=marker,
#     )

#     # bui.plot(daily_ds_og.Time,daily_ds_og.U, color=colors_list[7], lw=2)
#     # bui.plot(daily_ds_og.Time,daily_ds_og.U, color=colors_list[7], lw=1, ls = '-.', zorder = 7)
#     bui.scatter(
#         daily_ds_fwx.Time, daily_ds_fwx.U, color=colors_list[7], zorder=8, marker=marker
#     )

#     fwi.plot(hourly_ds.Time, hourly_ds.S, color="firebrick", lw=2, zorder=9)
#     # fwi.plot(daily_ds_og.Time,daily_ds_og.S, color=colors_list[3], lw=1, ls = '-.', zorder = 9)
#     fwi.scatter(
#         daily_ds_fwx.Time, daily_ds_fwx.S, color="firebrick", zorder=10, marker=marker
#     )

#     set_axis_postion_full_fwx(ffmc, "left", 0, "FFMC")
#     set_axis_postion_full_fwx(dmc, "left", 80, "DMC")
#     set_axis_postion_full_fwx(dc, "left", 160, "DC")
#     set_axis_postion_full_fwx(isi, "right", 0, "ISI")
#     set_axis_postion_full_fwx(bui, "right", 80, "BUI")
#     set_axis_postion_full_fwx(fwi, "right", 160, "FWI")
#     ax.set_xticklabels([])

#     # set_axis_postion_full_fwx(ffmc, "left", 0, "FFMC")
#     # set_axis_postion_full_fwx(dmc, "left", 80, "DMC")
#     # set_axis_postion_full_fwx(dc, "left", 160, "DC")
#     # set_axis_postion_full_fwx(isi, "right", 0, "ISI")
#     # set_axis_postion_full_fwx(fwi, "right", 80, "FWI")

#     # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d-%H'))
#     date_array = daily_ds_wx["time"] - np.timedelta64(int(12), "h")
#     extended_date_array = np.append(date_array, date_array[-1] + np.timedelta64(1, "D"))
#     # plt.gca().set_xticks(extended_date_array)
#     tkw = dict(size=4, width=1.5, labelsize=18)
#     ax.tick_params(
#         axis="x",
#         **tkw,
#     )
#     # ax.set_xlabel("Local DateTime (MM-DD-HH)", fontsize=16)

#     ax = fig.add_subplot(2, 1, 2)
#     ax.set_title(f"Weather Inputs", loc="left", fontsize=20)
#     temp = ax
#     rh = ax.twinx()
#     wsp = ax.twinx()
#     # wdir = ax.twinx()
#     precip = ax.twinx()

#     temp.plot(hourly_ds.Time, hourly_ds.T, color=colors_list[3], lw=2, zorder=9)
#     temp.scatter(
#         daily_ds_wx.Time, daily_ds_wx.T, color=colors_list[3], zorder=10, marker=marker
#     )

#     rh.plot(hourly_ds.Time, hourly_ds.H, color=colors_list[0], lw=2, zorder=9)
#     rh.scatter(
#         daily_ds_wx.Time, daily_ds_wx.H, color=colors_list[0], zorder=10, marker=marker
#     )

#     # wdir.plot(hourly_ds.Time, hourly_ds.WD, color="grey", lw=2, zorder = 9)

#     wsp.plot(hourly_ds.Time, hourly_ds.W, color="k", lw=2, zorder=9)
#     wsp.scatter(daily_ds_wx.Time, daily_ds_wx.W, color="k", zorder=10, marker=marker)
#     precip.plot(
#         hourly_ds.Time, hourly_ds.r_o_hourly, color=colors_list[2], lw=2, zorder=6
#     )
#     r_oi = np.array(daily_ds_wx.r_o)
#     r_oi[r_oi < 0.09] = 0
#     precip.scatter(
#         daily_ds_wx.Time, r_oi, color=colors_list[2], zorder=7, marker=marker
#     )
#     precip.set_ylim(0)

#     set_axis_postion_full_fwx(temp, "left", 0, "Temperature (C)")
#     set_axis_postion_full_fwx(rh, "left", 80, "Relative Humidity " + r"$(\%)$")
#     set_axis_postion_full_fwx(wsp, "right", 0, "Wind Speed (km/hr)")
#     # set_axis_postion_full_fwx(wdir, "right", 80, "Wind Direction (deg)")
#     set_axis_postion_full_fwx(precip, "right", 80, "Precipitation (mm)")

#     plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d-%H"))
#     # plt.gca().set_xticks(extended_date_array)
#     ax.set_xlabel("Local DateTime (MM-DD-HH)", fontsize=20)
#     tkw = dict(size=4, width=1.5, labelsize=18)
#     ax.tick_params(
#         axis="x",
#         **tkw,
#     )
#     fig.autofmt_xdate()

#     if save_fig == True:
#         if paper == True:
#             plt.savefig(
#                 str(save_dir) + f"/{case_study}-fwx.pdf",
#                 bbox_inches="tight",
#             )
#             plt.savefig(
#                 str(save_dir) + f"/{case_study}-fwx.png",
#                 dpi=250,
#                 bbox_inches="tight",
#             )
#         else:
#             plt.savefig(
#                 str(save_dir) + f"/{case_study}-fwx.png",
#                 dpi=250,
#                 bbox_inches="tight",
#             )
# else:
#     pass


# # FF0000


# # %%

# if int_plot == True:
#     import plotly.graph_objects as go
#     from plotly.subplots import make_subplots

#     df = frp_da.to_dataframe()
#     df["FWI"] = hfwi

#     # Create figure with secondary y-axis
#     fig = make_subplots(specs=[[{"secondary_y": True}]])

#     fig.add_trace(
#         go.Scatter(x=df.index, y=df["FWI"], name="FWI"),
#         secondary_y=False,
#     )

#     # Add traces
#     fig.add_trace(
#         go.Scatter(x=df.index, y=df["Power"], name="FRP"),
#         secondary_y=True,
#     )
#     # Add figure title
#     fig.update_layout(title_text="FRP v FWI")

#     # Set x-axis title
#     fig.update_xaxes(title_text="Time")

#     # Set y-axes titles
#     fig.update_yaxes(title_text="<b>FRP</b>", secondary_y=True)
#     fig.update_yaxes(title_text="<b>FWI</b>", secondary_y=False)

#     fig.show()
# # %%
