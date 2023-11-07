import context
import json
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

from matplotlib import ticker as mtick

from context import data_dir, root_dir

import warnings

warnings.filterwarnings("ignore")

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

#################### INPUTS ####################
## define model domain and path to fwf data
save_fig = True
case_study = "marshall_fire"
print(case_study)
save_dir = Path(str(data_dir) + f"/images/era5/")
save_dir.mkdir(parents=True, exist_ok=True)
################## END INPUTS ####################


#################### OPEN FILES ####################


## open case study json file
with open(str(root_dir) + f"/json/fire-cases.json", "r") as fp:
    case_dict = json.load(fp)


def convert_to_0_360(longitude):
    # Add 180 to the angle and use modulo 360 to ensure it stays in the 0-360 range.
    result = (longitude + 360) % 360
    return result


case_info = case_dict[case_study]
lat = np.mean([case_info["min_lat"], case_info["max_lat"]])
lon = np.mean(
    [convert_to_0_360(case_info["min_lon"]), convert_to_0_360(case_info["max_lon"])]
)

# date_range = pd.date_range('2021-08-16', '2021-08-25') ## caldor fire
# date_range = pd.date_range('2022-07-22', '2022-07-26') ## oak fire
# date_range = pd.date_range('2021-07-22', '2021-07-26') ## wildcat fire
date_range = pd.date_range("2021-12-29", "2022-01-01")  ## marshall fire


def solve_RH(ds):
    """
    Function to calculate relative humidity (RH) from dew point temperature (C) and temperature (C)
    """
    ## Extract temperature and dew point temperature data from input dataset
    td = ds["d2m"]
    t = ds["t2m"]
    ## Calculate relative humidity as a percentage using inverted clausius clapeyron
    rh = (
        (6.11 * 10 ** (7.5 * (td / (237.7 + td))))
        / (6.11 * 10 ** (7.5 * (t / (237.7 + t))))
        * 100
    )
    ## Set any RH values above 100 to 100
    rh = xr.where(rh > 100, 100, rh)
    ## Create a new dataset variable for relative humidity and assign calculated values to it
    ds["r2"] = rh
    if (
        np.min(ds.r2) > 90
    ):  # check if any RH values are nonphysical (i.e., less than 0 or greater than 100)
        raise ValueError(
            "ERROR: Check TD nonphysical RH values"
        )  # if so, raise a value error with a warning message
    return ds


def solve_W_WD(ds):

    ## Define the latitude and longitude arrays in degrees
    lons_rad = np.deg2rad(ds["latitude"])
    lats_rad = np.deg2rad(ds["longitude"])
    lons_rad, lats_rad = np.meshgrid(lats_rad, lons_rad)

    ## Calculate rotation angle
    theta = np.arctan2(np.cos(lats_rad) * np.sin(lons_rad), np.sin(lats_rad))

    ## Calculate sine and cosine of rotation angle
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    ## Define the u and v wind components in domain coordinates
    u_domain = ds["u10"].values
    v_domain = ds["v10"].values

    ## Rotate the u and v wind components to Earth coordinates
    u_earth = u_domain * cos_theta - v_domain * sin_theta
    v_earth = u_domain * sin_theta + v_domain * cos_theta
    ds["u_earth"] = ("time", u_earth[0])
    ds["v_earth"] = ("time", v_earth[0])

    ## Solve for wind speed
    wsp = np.sqrt(u_earth ** 2 + v_earth ** 2)
    ds["wsp"] = ("time", wsp[0])

    ## Solve for wind direction on Earth coordinates
    wdir = 180 + ((180 / np.pi) * np.arctan2(u_earth, v_earth))
    ds["wdir"] = ("time", wdir[0])

    return ds


def open_era5(doi):
    return xr.open_dataset(
        f"/Volumes/ThunderBay/CRodell/ecmwf/era5/{doi.strftime('%Y%m')}/era5-{doi.strftime('%Y%m%d00')}.nc"
    ).interp(latitude=lat, longitude=lon, method="linear")


ds = xr.combine_nested([open_era5(doi) for doi in date_range], concat_dim="time")

ds = solve_RH(ds)
ds = solve_W_WD(ds)
ds["tp"] = xr.where(ds["tp"] < 0.05, 0, ds["tp"])

ds["time"] = ds["time"] - np.timedelta64(7, "h")


def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)


def set_axis_postion(ax, side, offset, label):
    ax.spines[side].set_position(("outward", offset))
    make_patch_spines_invisible(ax)
    ax.spines[side].set_visible(True)
    ax.yaxis.set_label_position(side)
    ax.yaxis.set_ticks_position(side)
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


colors_list = plt.rcParams["axes.prop_cycle"].by_key()["color"]
start = pd.to_datetime(ds.time.values[0]).strftime("%B %d")
stop = pd.to_datetime(ds.time.values[-1]).strftime("%B %d")
start_save = pd.to_datetime(ds.time.values[0]).strftime("%Y%m%d")
stop_save = pd.to_datetime(ds.time.values[-1]).strftime("%Y%m%d")
year = pd.to_datetime(ds.time.values[-1]).strftime("%Y")

# fig_name = "temp_" + time
fig = plt.figure(figsize=(14, 6))
fig.suptitle(f"Weather During {case_study.replace('_',' ').capitalize()}", fontsize=20)
ax = fig.add_subplot(1, 1, 1)
ax.set_title(f"Weather Inputs", loc="left", fontsize=14)
temp = ax
rh = ax.twinx()
wsp = ax.twinx()
wdir = ax.twinx()
precip = ax.twinx()

temp.plot(ds.time, ds.t2m, color=colors_list[3], lw=2, zorder=9)

rh.plot(ds.time, ds.r2, color=colors_list[0], lw=2, zorder=9)

wdir.plot(ds.time, ds.wdir, color="grey", lw=2, zorder=9)
wsp.plot(ds.time, ds.wsp, color="k", lw=2, zorder=9)
precip.plot(ds.time, ds.tp, color=colors_list[2], lw=2, zorder=9)


set_axis_postion(temp, "left", 0, "Temperature (C)")
set_axis_postion(rh, "left", 80, "Relative Humidity (%)")
set_axis_postion(wsp, "right", 0, "Wind Speed (m/s)")
set_axis_postion(wdir, "right", 80, "Wind Direction (deg)")
set_axis_postion(precip, "right", 160, "Precipitation (mm)")

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d-%H"))
# plt.gca().set_xticks(ds_Dloc.time.values)
ax.set_xlabel("Local Datetime (MM-DD-HH)", fontsize=16)
tkw = dict(size=4, width=1.5, labelsize=14)
ax.tick_params(
    axis="x",
    **tkw,
)
plt.savefig(
    str(save_dir) + f'/{case_study.replace(" ","_")}-{start_save}-{stop_save}.png',
    dpi=250,
    bbox_inches="tight",
)
