import context
import json
import salem

import numpy as np
import xarray as xr
import pandas as pd
import geopandas as gpd
from scipy import stats
from pathlib import Path

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import cartopy.crs as ccrs
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1 import make_axes_locatable
from netCDF4 import Dataset
from wrf import ll_to_xy

from context import data_dir, root_dir


__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

#################### INPUTS ####################


## define model domain and path to fwf data
save_fig = True
domain = "d02"
filein = f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/02/"
case_study = "six_rivers"

################## END INPUTS ####################

#################### OPEN FILES ####################

save_dir = Path(str(data_dir) + f"/images/frp/{case_study}")
save_dir.mkdir(parents=True, exist_ok=True)
################## END OPEN ####################


########################### FUNCTIONS ##########################


def set_axis_postion(ax, label):
    ax.set_ylabel(label, fontsize=16)
    ax.yaxis.label.set_color(ax.get_lines()[0].get_color())
    tkw = dict(size=4, width=1.5, labelsize=14)
    ax.tick_params(
        axis="y",
        colors=ax.get_lines()[0].get_color(),
        **tkw,
    )
    # ax.grid(True)
    ax.grid(which="major", axis="x", linestyle="--", zorder=2, lw=0.3)


######################### END FUNCTIONS ##########################


ds = xr.open_dataset(
    str(data_dir)
    + f"/frp/analysis/{domain}/{case_study.replace('_','-')}-interp-grid.nc"
)
############################## End Analyzing datasets  ##############################


hfwi = ds["S"].isel(method=1).values
frp = ds["FRP"].isel(method=1).values
dfwi = ds["S"].isel(method=0).values
pearsonr_h_interp_final = stats.pearsonr(hfwi, frp)
pearsonr_d_interp_final = stats.pearsonr(dfwi, frp)
data_range = ds.Time.values
# ################################ Plot Interp NEW FRP vs FWI ################################
start = pd.to_datetime(data_range[0]).strftime("%B %d")
stop = pd.to_datetime(data_range[-1]).strftime("%B %d")
start_save = pd.to_datetime(data_range[0]).strftime("%Y%m%d")
stop_save = pd.to_datetime(data_range[-1]).strftime("%Y%m%d")
year = pd.to_datetime(data_range[-1]).strftime("%Y")


# fig = plt.figure(figsize=(12, 4))
# fig.suptitle(f"FWI vs FRP", fontsize=20)
# ax = fig.add_subplot(2, 1, 1)

# ax.set_title(
#     f"{start} - {stop}, {year} \n",
#     loc="right",
#     fontsize=14,
# )
# ax.set_title(f"r: {round(pearsonr_h_interp_final[0],2)} Hourly FWI \nr: {round(pearsonr_d_interp_final[0],2)}   Daily FWI ", loc="right", fontsize=10)
# ax.plot(data_range, hfwi, color='tab:blue', lw = 1.2, label = 'Hourly')
# ax.plot(data_range, dfwi, color='tab:blue', ls = '--', lw = 1.2, label = 'Daily')
# ax.plot(data_range, hfwi, color='tab:red', lw = 1, label = 'FRP', zorder = 0)
# ax.fill_between(data_range, y1=30, y2=100, color='tab:red',  interpolate=True, alpha=.25)

# ax.set_xticklabels([])
# set_axis_postion(ax, 'FWI')
# # ax.grid(which='major', axis='x', linestyle='--', zorder = 2, lw = 0.3)
# ax.set_xlim(data_range[0], data_range[-1])
# ax.set_ylim(0, hfwi.max()+5)

# ax.legend(
#     # loc="upper right",
#     bbox_to_anchor=(0.35, 1.4),
#     ncol=3,
#     fancybox=True,
#     shadow=True,
#     fontsize=12,
# )
# # set_axis_postion(ax, "FWI")
# ax = fig.add_subplot(2, 1, 2)

# ax.plot(data_range, frp, color='tab:red', lw = 1.2, label = 'FRP')
# set_axis_postion(ax, 'FRP (MW)')


# # set_axis_postion(ax2, "FRP")
# tkw = dict(size=4, width=1.5, labelsize=14)
# ax.tick_params(
#     axis="x",
#     **tkw,
# )
# plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
# ax.set_xlabel("Local DateTime (MM-DD)", fontsize=16)
# ax.set_xlim(data_range[0], data_range[-1])


# ################################ Plot Interp NEW FRP vs FWI ################################

fig = plt.figure(figsize=(12, 4))
fig.suptitle(f"Fire Weather Index vs Fire Radiative Power", fontsize=18, y=1.08)
ax = fig.add_subplot(1, 1, 1)

ax.set_title(
    f"{case_study.replace('_', ' ').title()}",
    loc="center",
    fontsize=14,
)
ax.set_title(
    f"r: {round(pearsonr_h_interp_final[0],2)} Hourly FWI \nr: {round(pearsonr_d_interp_final[0],2)}   Daily FWI ",
    loc="right",
    fontsize=10,
)
ax2 = ax.twinx()
ax.plot(data_range, hfwi, color="tab:blue", lw=1.2, label="Hourly")
ax.plot(data_range, dfwi, color="tab:blue", ls="--", lw=1.2, label="Daily")
ax.plot(data_range, hfwi, color="tab:red", lw=1, label="FRP", zorder=0)

set_axis_postion(ax, "FWI")

ax2.plot(data_range, frp, color="tab:red", lw=1.2, label="FRP")


set_axis_postion(ax2, "FRP (MW)")
tkw = dict(size=4, width=1.5, labelsize=14)
ax.tick_params(
    axis="x",
    **tkw,
)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
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

if save_fig == True:
    plt.savefig(
        str(save_dir) + f"/timeseries-interp-final-{start_save}-{stop_save}.png",
        dpi=250,
        bbox_inches="tight",
    )


# ####################### End Plot Interp FRP vs FWI ############################
