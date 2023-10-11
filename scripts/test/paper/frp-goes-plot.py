#!/Users/crodell/miniconda3/envs/fwf/bin/python

import context
import json
import salem
import gc

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
# plt.rcParams.update({'font.size': 16})

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

#################### INPUTS ####################
## define model domain and path to fwf data
save_fig = False
case_study = "barrington_lake_fire"  # ['sparks_lake', 'lytton_creek', 'barrington_lake_fire', 'ewf_031', 'quebec_fire_334', 'donnie_creek', 'wildcat', 'marshall_fire', 'oak_fire', 'caldor_fire', 'fire_east_tulare', 'rossmoore_fire', 'crater_creek', 'mcdougall_creek']
# print(case_study)
save_dir = Path(str(data_dir) + f"/images/frp/goes/paper/")
save_dir.mkdir(parents=True, exist_ok=True)
################## END INPUTS ####################

# test = xr.open_dataset("/Volumes/WFRT-Ext22/frp/goes/g18/2023/OR_ABI-L2-FDCF-M6_G18_s20232190020203_e20232190029511_c20232190030022.nc")
#################### OPEN FILES ####################


## open case study json file
with open(str(root_dir) + f"/json/fire-cases.json", "r") as fp:
    case_dict = json.load(fp)
#

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
) = open_frp(case_study, case_info)
# norm_d = xr.open_dataset(str(data_dir)+f"/norm/fwi-daily-{domain}.nc")
# norm_h = xr.open_dataset(str(data_dir)+f"/norm/fwi-hourly-{domain}.nc")


# Mask =  frp_ds['Mask'].values
# Power =  frp_ds['Power'].values
# Power =  xr.where((frp_ds['Mask'] == 10) | (frp_ds['Mask'] == 30), frp_ds['Power'], np.nan)
# Mask_test = Mask[~np.isnan(Power)]
# flag_values =  np.array(test['Mask'].attrs['flag_values'])
# flag_meanings =  np.array(test['Mask'].attrs['flag_meanings'].split())
# flag_meanings[flag_values ==10]

fwf_range_daily = pd.date_range(
    fwf_range[0] - pd.Timedelta(days=2), fwf_range[-1] + pd.Timedelta(days=2)
)
print(case_study)
yy, xx = build_tree(case_study, case_info, frp_lats, frp_lons)


try:
    hourly_ds = xr.open_dataset(
        str(data_dir) + f"/frp/analysis/wrf/{case_study}-hourly.nc"
    )
    daily_ds = xr.open_dataset(
        str(data_dir) + f"/frp/analysis/wrf/{case_study}-daily-.nc"
    )
except:
    print("Making FWI netcdf")
    try:
        # hourly_ds = xr.combine_nested([open_fwf(doi, filein, domain, "hourly", yy, xx, utc_offset) for doi in fwf_range], "time")
        daily_ds = xr.combine_nested(
            [
                open_fwf(doi, filein, domain, "daily", yy, xx, utc_offset)
                for doi in fwf_range_daily
            ],
            "time",
        )
    except:
        # hourly_ds = xr.combine_nested([open_fwf(doi, filein, domain, "hourly", yy, xx, utc_offset) for doi in fwf_range[:-1]], "time")
        daily_ds = xr.combine_nested(
            [
                open_fwf(doi, filein, domain, "daily", yy, xx, utc_offset)
                for doi in fwf_range_daily[:-1]
            ],
            "time",
        )
    daily_ds["time"] = daily_ds["Time"]
    daily_ds = daily_ds.resample(time="1H").nearest()
    # hourly_ds.to_netcdf(str(data_dir) + f"/frp/analysis/wrf/{case_study}-hourly.nc", mode = 'w')
    # daily_ds.to_netcdf(str(data_dir) + f"/frp/analysis/wrf/{case_study}-daily.nc", mode = 'w')
    # hourly_ds = normalize(hourly_ds, yy, xx, norm_h).rename('S').to_dataset()
    # daily_ds = normalize(daily_ds, yy, xx, norm_d).rename('S').to_dataset()

hourly_ds = xr.open_dataset(str(data_dir) + f"/frp/analysis/wrf/{case_study}-hourly.nc")
# hourly_ds = normalize(hourly_ds, yy, xx, norm_h).rename('S').to_dataset()
# daily_ds = normalize(daily_ds, yy, xx, norm_d).rename('S').to_dataset()


# %%

non_nan_indices = np.where(~np.isnan(frp_da))[0]
diff_arr = np.diff(non_nan_indices)
indices = np.where(diff_arr == 1)[0]
groups = np.split(indices, np.where(np.diff(indices) != 1)[0] + 1)
result = [group for group in groups if len(group) > 6]

if (
    date_range[non_nan_indices[result[1][0]]]
    - date_range[non_nan_indices[result[0][0]]]
).astype("timedelta64[h]") >= 24:
    start = date_range[non_nan_indices[result[0][0]]]
else:
    start = date_range[non_nan_indices[result[1][0]]]

if (date_range[non_nan_indices[result[-1][0]]] - start).astype("timedelta64[D]") > 8:
    stop = date_range[non_nan_indices[result[0][0]] + (24 * 10)]
else:
    stop = date_range[non_nan_indices[result[-1][0]]]


# %%
# start = date_range[0]
# stop = date_range[-1]
# start = "2021-07-24-T00"
# stop = "2021-07-29T00"
# start = date_range[non_nan_indices[result[1][0]]]
# stop = date_range[non_nan_indices[result[0][0]]+(24*10)]
frp_da = frp_da.sel(t=slice(start, stop))
frp_raw = frp_da.values
frp_da_interp = frp_da.interpolate_na(dim="t", method="linear").ffill(
    dim="t"
)  # pchip or linear
frp_da_og_slice = frp_da_og.sel(t=slice(start, stop))
hourly_ds = hourly_ds.sel(time=slice(start, stop))
daily_ds = daily_ds.sel(time=slice(hourly_ds["time"][0], hourly_ds["time"][-1]))
frp_ds = frp_ds.sel(t=slice(start, stop))


hfwi = hourly_ds["S"].values
hfrp = frp_da_interp.values
dfwi = daily_ds["S"].values
study_range = hourly_ds.time.values
unique, counts = np.unique(np.isnan(frp_raw), return_counts=True)
print(f"Precent of values that where observed {round((counts[0]/len(hfrp))*100,2)}")
hfwip = hfwi[np.isnan(frp_da.values) == False]
dfwip = dfwi[np.isnan(frp_da.values) == False]
hfrpp = hfrp[np.isnan(frp_da.values) == False]

# hfwi[np.isnan(hfrp)] = np.nan
# dfwi[np.isnan(hfrp)] = np.nan


pearsonr_h_interp_final = stats.pearsonr(hfwip, hfrpp)
pearsonr_d_interp_final = stats.pearsonr(dfwip, hfrpp)
# ################################ Plot Interp NEW FRP vs FWI ################################
year = pd.to_datetime(study_range[-1]).strftime("%Y")


fig = plt.figure(figsize=(12, 4))
fig.suptitle(f"    Fire Weather Index vs Fire Radiative Power", fontsize=20, y=1.11)

ax = fig.add_subplot(1, 1, 1)
title_line1 = (
    r"\fontsize{18pt}{22pt}\selectfont " + f"{case_study.replace('_', ' ').title()}"
)
title_line2 = r"\fontsize{12pt}{15pt}\selectfont " + f"{case_info['loc']}" + f", {year}"
title = f"{title_line1}\n{title_line2}"
ax.set_title(title, loc="center", fontdict={"usetex": True})

ax.set_title(
    f"r: {round(pearsonr_h_interp_final[0],2)} Hourly FWI \nr: {round(pearsonr_d_interp_final[0],2)}   Daily FWI    \n  Values observed: {round((counts[0]/len(frp_raw))*100,2)}%",
    loc="right",
    fontsize=12,
)
ax2 = ax.twinx()
ax.plot(hourly_ds.time.values, hfwi, color="tab:blue", lw=1.2, label="Hourly")
ax.plot(daily_ds.time.values, dfwi, color="tab:blue", ls="--", lw=1.2, label="Daily")
ax.plot(hourly_ds.time.values, hfwi, color="tab:red", lw=1, label="FRP", zorder=0)
set_axis_postion(ax, "FWI")

ax2.plot(frp_da.time, frp_da, color="tab:red", lw=1.2, label="FRP")
ax2.plot(frp_da.time, hfrp, lw=1.1, color="tab:red", ls="dotted", label="FRP")
# ax2.plot(frp_da_og_slice.t, frp_da_og_slice, color="pink", lw=1.2, label="FRP")

set_axis_postion(ax2, "FRP (MW)")
tkw = dict(size=4, width=1.5, labelsize=16)
ax.tick_params(
    axis="x",
    **tkw,
)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
# plt.gca().xaxis.set_major_formatter()
ax.set_xlabel(f"Local DateTime (MM-DD)", fontsize=16)
ax.legend(
    # loc="upper right",
    bbox_to_anchor=(0.35, 1.18),
    ncol=3,
    fancybox=True,
    shadow=True,
    fontsize=12,
)
fig.autofmt_xdate()

# index = np.argmax(hfwi)
# fwi_max= str(round(hfwi[index],2))
# frp_max= str(round(frp_da.values[index],2))

# print(f"Normalized MAX FWI: {fwi_max}")
# print(f"FRP at MAX FWI:     {frp_max}")

# index = np.argmin(hfwi)
# fwi_min= str(round(hfwi[index],2))
# frp_min= str(round(frp_da.values[index],2))

# print(f"Normalized MIN FWI: {fwi_min}")
# print(f"FRP at MIN FWI:     {frp_min}")

if save_fig == True:
    plt.savefig(
        str(save_dir) + f"/{case_study}.png",
        dpi=250,
        bbox_inches="tight",
    )


static_ds = xr.open_dataset((str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"))
fire = np.full_like(static_ds.XLONG, 0)
for i in range(len(xx)):
    fire[yy[i], xx[i]] += 1
static_ds["fire"] = (("south_north", "west_east"), fire)
static_ds1 = static_ds.isel(
    west_east=slice(xx.min() - 5, xx.max() + 5),
    south_north=slice(yy.min() - 5, yy.max() + 5),
)

from pylab import *

cmap = cm.get_cmap("Reds", fire.max() + 5)  # PiYG
hexl = []
for i in range(cmap.N):
    rgba = cmap(i)
    hexl.append(matplotlib.colors.rgb2hex(rgba))

hexl = ["green"] + hexl[6:]

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(1, 1, 1)
XLONG = static_ds1["XLONG"].values
XLAT = static_ds1["XLAT"].values
sc = ax.pcolormesh(
    XLONG,
    XLAT,
    static_ds1["fire"],
    zorder=1,
    cmap=matplotlib.colors.ListedColormap(hexl),
    alpha=0.5,
)
# ax.pcolormesh(
#     XLONG, XLAT, static_ds1['fire'], zorder=1, color = 'k', alpha=0.5
# )
cbar = plt.colorbar(sc, ax=ax, pad=0.008)
cbar.set_label("Weighted Count", rotation=270, fontsize=14, labelpad=20)
XLONG = frp_ds["lons"].values
XLAT = frp_ds["lats"].values
# fire = frp_ds["Power"].mean(dim ='t')
fire = np.full_like(XLONG, np.nan)
fire[~np.isnan(frp_ds.mean(dim="t")["Power"].values)] = 1

# ax.pcolormesh(
#     XLONG, XLAT, fire, zorder=1,  cmap= matplotlib.colors.ListedColormap(['k']),alpha=0.2
# )
ax.scatter(
    XLONG[~np.isnan(frp_ds.mean(dim="t")["Power"].values)],
    XLAT[~np.isnan(frp_ds.mean(dim="t")["Power"].values)],
    color="k",
    s=10,
)
ax.set_title(
    f"GOES FRP Locations overlaid on WRF GRID \n {case_study.replace('_',' ').title()}",
    fontsize=14,
)
ax.set_xlabel("Longitude", fontsize=16)
ax.set_ylabel("Latitude", fontsize=16)
plt.savefig(
    str(save_dir) + f"/map-frp-count-{case_study}.png", dpi=250, bbox_inches="tight"
)
# del daily_ds
# del hourly_ds
# del frp_ds
# del frp_da
# del frp_da_og
# gc.collect()
# except:
#     try:
#         del daily_ds
#         del hourly_ds
#         del frp_ds
#         del frp_da
#         del frp_da_og
#         gc.collect()
#     except:
#         pass
