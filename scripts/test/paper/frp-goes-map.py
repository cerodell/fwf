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
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from utils.frp import (
    open_fwf,
    open_frp,
    set_axis_postion,
    build_tree,
    get_time_offest,
    normalize,
)
from context import data_dir, root_dir

plt.rc("font", family="sans-serif")
plt.rc("text", usetex=True)
plt.rcParams.update({"font.size": 16})

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

#################### INPUTS ####################
## define model domain and path to fwf data
save_fig = False
case_study = "boston_bar"
doi = "2021-08-23"
print(case_study)
save_dir = Path(str(data_dir) + f"/images/frp/goes/noaa/")
save_dir.mkdir(parents=True, exist_ok=True)
################## END INPUTS ####################

test = xr.open_dataset(
    "/Volumes/WFRT-Ext22/frp/goes/g18/2023/OR_ABI-L2-FDCF-M6_G18_s20232190020203_e20232190029511_c20232190030022.nc"
)
#################### OPEN FILES ####################


## open case study json file
with open(str(root_dir) + f"/json/fire-cases.json", "r") as fp:
    case_dict = json.load(fp)


case_info = case_dict[case_study]
domain = case_info["domain"]
filein = f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/02/"


(
    frp_ds,
    frp_da,
    frp_da_og,
    frp_lats,
    frp_lons,
    utc_offset,
    date_range,
    fwf_range,
) = open_frp(case_study, case_info, doi=doi)
yy, xx = build_tree(case_study, case_info, frp_lats, frp_lons)
frp_ds = frp_ds.sel(t=slice("2021-08-18T12:05:05", "2021-08-25T12:00"))
# hourly_ds = xr.open_dataset(str(data_dir) + f"/frp/analysis/wrf/{case_study}-hourly.nc")
# daily_ds = xr.open_dataset(str(data_dir) + f"/frp/analysis/wrf/{case_study}-daily.nc")

static_ds = xr.open_dataset((str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"))
fire = np.full_like(static_ds.XLONG, False, dtype=bool)
fire[yy, xx] = True
static_ds["fire"] = (("south_north", "west_east"), fire)
static_ds1 = static_ds.isel(
    west_east=slice(xx.min() - 5, xx.max() + 5),
    south_north=slice(yy.min() - 5, yy.max() + 5),
)


fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(1, 1, 1)
XLONG = static_ds1["XLONG"].values
XLAT = static_ds1["XLAT"].values
ax.pcolormesh(
    XLONG,
    XLAT,
    static_ds1["fire"],
    zorder=1,
    cmap=matplotlib.colors.ListedColormap(["green", "red"]),
    alpha=0.5,
)

XLONG = frp_ds["lons"].values
XLAT = frp_ds["lats"].values
fire = frp_ds["Power"].sel(t=doi).mean(dim="t")
sc = ax.pcolormesh(XLONG, XLAT, fire, zorder=1, cmap="inferno")
cbar = plt.colorbar(sc, ax=ax, pad=0.008)
ax.set_title(
    f"GOES FRP overlaid on WRF GRID \n {case_study.replace('_',' ').title()} \n {doi}",
    fontsize=14,
)
# ax.set_title(f"GOES FRP {doi} \n {case_study.replace('_',' ').title()}", fontsize=14)
cbar.set_label("FRP (MW)", rotation=270, fontsize=14, labelpad=20)
ax.set_xlabel("Longitude", fontsize=16)
ax.set_ylabel("Latitude", fontsize=16)
# plt.savefig(str(save_dir) + f"/map-frp-{case_study}-{doi}.png", dpi=250, bbox_inches="tight")


# frp_ds = frp_ds.resample(t="1H").mean()
frp_date_range = frp_ds["t"].values
keep_dates = np.where((frp_date_range <= pd.to_datetime("2020-01-01")) == False)
frp_ds = frp_ds.isel(t=keep_dates[0])
frp_ds = frp_ds.sortby("t")
df = frp_ds.to_dataframe().reset_index()
df = df[df["Power"].notna()]
df = df.set_index(pd.DatetimeIndex(df["t"]))

import matplotlib.image as mpimg

# Filter rows based on the target datetime
# df_sample = df[df.index.date == doi.date()]
df_sample = df
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(1, 1, 1)
sc = ax.scatter(
    df_sample["lons"],
    df_sample["lats"],
    zorder=9,
    c=mdates.date2num(df_sample.index.values),
    # alpha =0.5
)

cbar = plt.colorbar(sc, ax=ax, pad=0.008, alpha=1)
loc = mdates.AutoDateLocator()
cbar.ax.yaxis.set_major_locator(loc)
cbar.ax.yaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))
ax.set_title(f"Fire Hot Spots {case_study.replace('_',' ').title()}", fontsize=14)
cbar.set_label("Datetime", rotation=270, fontsize=14, labelpad=20)
ax.set_xlabel("Longitude", fontsize=16)
ax.set_ylabel("Latitude", fontsize=16)

# plt.savefig(str(save_dir) + f"/map-frp-{case_study}-growth.png", dpi=250, bbox_inches="tight")


# # fire = np.invert(np.isnan(frp_ds["Power"].mean(dim ='t')))
# # ax.pcolormesh(
# #     XLONG, XLAT, fire, zorder=1, cmap= matplotlib.colors.ListedColormap(['green', 'red']), alpha=0.5
# # )


# # # Filter rows based on the target datetime
# # doi = expected_range[np.argmax(obs_size)]
# # df_sample = df[df.index.date == doi.date()]

# # inds  = []
# # for loc in df_sample.itertuples(index=True, name="Pandas"):
# #     ## arange wx station lat and long in a formate to query the kdtree
# #     single_loc = np.array([loc.latitude, loc.longitude]).reshape(1, -1)
# #     ## query the kdtree retuning the distacne of nearest neighbor and index
# #     dist, ind = fwf_tree.query(single_loc, k=1)
# #     ## set condition to pass on fire farther than 0.1 degrees
# #     if dist > 0.1:
# #         pass
# #     else:
# #         inds.append(int(ind))

# # static_i = static_ds.stack(locs=['south_north', 'west_east'])
# # static_i = static_i.isel(locs =inds)
# # XLONG1 = static_i.XLONG.values
# # XLAT1 = static_i.XLAT.values

# # fig = plt.figure(figsize=(8, 8))
# # ax = fig.add_subplot(1, 1, 1)
# # XLONG = hourly_ds["XLONG"].values
# # XLAT = hourly_ds["XLAT"].values
# # test = np.isin(XLAT, XLAT1).astype(int)
# # test = test.astype(float)
# # ax.pcolormesh(
# #     XLONG, XLAT, test, zorder=1, cmap= matplotlib.colors.ListedColormap(['green', 'red']), alpha=0.5
# # )
# # sc = ax.scatter(
# #     df_sample["longitude"], df_sample["latitude"], zorder=9, c=df_sample["frp"], cmap ='inferno'
# # )
# # cbar = plt.colorbar(sc, ax=ax, pad=0.008)
# # ax.set_title(f"Fire Radiative Power {case_study.replace('_',' ')} \n {doi.strftime('%d %b %Y')}", fontsize=14)
# # cbar.set_label("FRP (MW)", rotation=270, fontsize=14, labelpad=20)
# # ax.set_xlabel("Longitude", fontsize=16)
# # ax.set_ylabel("Latitude", fontsize=16)
# # # if case_study == 'mb_096':
# # #     img = mpimg.imread(str(data_dir) + f'/frp/mb_096_true.jpeg')
# # #     ax.imshow(img,extent=[case_info['min_lon'],case_info['max_lon'], case_info['min_lat'],case_info['max_lat']])
# # # else:
# # #     pass
# # if save_fig == True:
# #     plt.savefig(str(save_dir) + f"/map-frp-{doi.strftime('%Y%m%d')}.png", dpi=250, bbox_inches="tight")
