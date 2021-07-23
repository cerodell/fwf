#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

"""
Creates a time zone mask for each grid point in model domain.

"""
import context
import math
import salem
import numpy as np
import pandas as pd
import xarray as xr
from context import data_dir, xr_dir, wrf_dir, tzone_dir
import timezonefinder, pytz
from pathlib import Path
from mpl_toolkits.axes_grid1 import make_axes_locatable

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


from datetime import datetime, date, timedelta

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


## Define model/domain and datetime of interest
# date = pd.Timestamp("today")
# date = pd.Timestamp(2018, 7, 20)
domain = "d03"
wrf_model = "wrf4"
season = "ST"

## Path to hourly/daily fwi data
if wrf_model == "wrf3":
    wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CP-04/18072000/wrfout_{domain}_2018-07-20_11:00:00"
else:
    wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CG-01/21022000/wrfout_{domain}_2021-02-20_11:00:00"

tzone_shp = str(tzone_dir) + "/timezones-with-oceans/combined-shapefile-with-oceans.shp"

## Open hourly/daily fwi data
# hourly_ds = xr.open_zarr(hourly_file_dir)
wrf_ds_og = xr.open_dataset(wrf_filein)
wrf_ds = salem.open_xr_dataset(wrf_filein)
df_og = salem.read_shapefile(tzone_shp)
df_og_tz = list(df_og["tzid"])

df = salem.read_shapefile(tzone_shp)
df = df[df["tzid"].str.contains("America")]
df = df[df["min_y"] > 10]
# df = df.append(df_og.loc[df_og['tzid'] == 'Etc/GMT-8'])
# df = df[df['max_y'] < float(wrf_ds.XLAT.max()+10)]
# df = df[df['min_x'] > float(wrf_ds.XLONG.min()-10)]
# df = df[df['max_x'] < float(wrf_ds.XLONG.max()+10)]


var_array = wrf_ds.T2.isel(Time=0)
lats = var_array.XLAT.values
lons = var_array.XLONG.values

zero_full = np.zeros(lats.shape)
tzid = list(df["tzid"])
if season == "DT":
    for tz in tzid:
        print(tz)
        name = df.loc[df["tzid"] == tz]
        timezone = pytz.timezone(tz)
        dt = datetime.utcnow()
        offset = timezone.utcoffset(dt)
        seconds = offset.total_seconds()
        if (
            tz == "America/Whitehorse"
            or tz == "America/Dawson"
            or tz == "America/Regina"
            or tz == "America/Swift_Current"
            or tz == "America/Phoenix"
            or tz == "America/Indiana/Indianapolis"
            # or tz ==  "America/Indiana/Knox"
            or tz == "America/Indiana/Marengo"
            or tz == "America/Indiana/Petersburg"
            # or tz ==  "America/Indiana/Tell_City"
            or tz == "America/Indiana/Vevay"
            or tz == "America/Indiana/Vincennes"
            or tz == "America/Indiana/Winamac"
        ):
            hours = abs(int(seconds // 3600))
        else:
            hours = abs(int(seconds // 3600)) - 1
        dsr = var_array.salem.roi(shape=name)
        index = np.where(dsr == dsr)
        zero_full[index[0], index[1]] = hours
elif season == "ST":
    for tz in tzid:
        print(tz)
        name = df.loc[df["tzid"] == tz]
        timezone = pytz.timezone(tz)
        dt = datetime.utcnow()
        offset = timezone.utcoffset(dt)
        seconds = offset.total_seconds()
        # if (
        #     tz    == "America/Phoenix"
        #     or tz ==  "America/Indiana/Indianapolis"
        #     # or tz ==  "America/Indiana/Knox"
        #     or tz ==  "America/Indiana/Marengo"
        #     or tz ==  "America/Indiana/Petersburg"
        #     # or tz ==  "America/Indiana/Tell_City"
        #     or tz ==  "America/Indiana/Vevay"
        #     or tz ==  "America/Indiana/Vincennes"
        #     or tz ==  "America/Indiana/Winamac"
        # ):
        #     hours = abs(int(seconds // 3600)) + 1
        # else:
        hours = abs(int(seconds // 3600))
        dsr = var_array.salem.roi(shape=name)
        index = np.where(dsr == dsr)
        zero_full[index[0], index[1]] = hours
else:
    raise ValueError("ERROR: This is not a valid time of year")

ds_zones = xr.DataArray(
    zero_full.astype(int), name="Zone", dims=("south_north", "west_east")
)

T2 = wrf_ds.T2
attrs = T2.attrs
ds_zones.attrs = attrs
ds_zones.attrs["description"] = "Time Zone Offsets From UTC"
ds_zones.attrs["units"] = "hours_"
ds_zones = xr.merge([ds_zones, T2])
ds_zones = ds_zones.drop_vars("T2")
ds_zones = ds_zones.isel(Time=0)
ds_zones = ds_zones.compute()
ds_zones.to_zarr(
    str(tzone_dir) + str(f"/tzone_{wrf_model}_{domain}-{season}.zarr"), mode="w"
)


# test = xr.open_zarr(str(tzone_dir) + str(f"/tzone_{wrf_model}_{domain}-{season}.zarr"))
# print(test.Zone.values)


####################################
## plot for santity check
####################################
## set plot title and save dir/name
if domain == "d02":
    res = "12 km"
else:
    res = "4 km"
if season == "DT":
    toy = "Summer"
else:
    toy = "Winter"

Plot_Title = (
    f"Time Zone Offsets From UTC during {toy} \n {wrf_model.upper()} {res} Domain"
)
save_file = f"/images/{wrf_model}-{domain}-tzone-{season}.png"
save_dir = str(data_dir) + save_file


## bring in state/prov boundaries
states_provinces = cfeature.NaturalEarthFeature(
    category="cultural",
    name="admin_1_states_provinces_lines",
    scale="50m",
    facecolor="none",
)


## make fig for make with projection
fig = plt.figure(figsize=[16, 8])
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(central_longitude=0))

## add map features
ax.gridlines()
ax.add_feature(cfeature.LAND, zorder=1)
ax.add_feature(cfeature.LAKES, zorder=1)
ax.add_feature(cfeature.OCEAN, zorder=9)
ax.add_feature(cfeature.BORDERS, zorder=10)
ax.add_feature(cfeature.COASTLINE, zorder=10)
ax.add_feature(states_provinces, edgecolor="gray", zorder=2)
ax.set_xlabel("Longitude", fontsize=18)
ax.set_ylabel("Latitude", fontsize=18)

## create tick mark labels and style
ax.set_xticks(list(np.arange(-160, -40, 10)), crs=ccrs.PlateCarree())
ax.set_yticks(list(np.arange(30, 80, 10)), crs=ccrs.PlateCarree())
# ax.yaxis.tick_right()
# ax.yaxis.set_label_position("right")
ax.tick_params(axis="both", which="major", labelsize=14)
ax.tick_params(axis="both", which="minor", labelsize=14)

## add title and adjust subplot buffers
ax.set_title(Plot_Title, fontsize=20, weight="bold")
fig.subplots_adjust(hspace=0.8)
divider = make_axes_locatable(ax)
ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)

## get d01 lats and lon
lats, lons = np.array(wrf_ds.XLAT), np.array(wrf_ds.XLONG)
lats, lons = lats[0], lons[0]
lons = np.where(
    lons > -179, lons, np.nan
)  ## mask out past international dateline.....catorpy hates the dateline

## plot d01
ax.plot(lons[0], lats[0], color="k", linewidth=2, zorder=10, alpha=1)
ax.plot(lons[-1].T, lats[-1].T, color="k", linewidth=2, zorder=10, alpha=1)
ax.plot(lons[:, 0], lats[:, 0], color="k", linewidth=2, zorder=10, alpha=1)
ax.plot(
    lons[:, -1].T,
    lats[:, -1].T,
    color="k",
    linewidth=2,
    zorder=10,
    alpha=1,
)


levels = np.unique(zero_full)
if wrf_model == "wrf3":
    levels = [3, 4, 5, 6, 7, 8, 9, 10]
    levels = [-10, -9, -8, -7, -6, -5, -4, -3]
elif wrf_model == "wrf4":
    levels = [3, 4, 5, 6, 7, 8, 9, 10]
    levels = [-10, -9, -8, -7, -6, -5, -4, -3]
else:
    pass

# divider = make_axes_locatable(ax)


contourf = ax.contourf(
    lons,
    lats,
    (zero_full + 0.5) * -1,
    zorder=8,
    alpha=0.5,
    levels=levels,
    cmap="Dark2_r",
)

fig.add_axes(ax_cb)
ticks = levels[1:]
tick_levels = list(np.array(levels) - 0.5)
cbar = plt.colorbar(contourf, cax=ax_cb, ticks=tick_levels)
cbar.ax.set_yticklabels(ticks)  # set ticks of your format
cbar.ax.axes.tick_params(length=0)

## set map bounds
## set map bounds
if wrf_model == "wrf3":
    ax.set_xlim([-144, -55])
    ax.set_ylim([36, 70])
elif wrf_model == "wrf4":
    ax.set_xlim([-174, -29])
    ax.set_ylim([25, 80])
else:
    pass


## tighten up fig
plt.tight_layout()
plt.show()
## save as png
# fig.savefig(save_dir, dpi=240)
