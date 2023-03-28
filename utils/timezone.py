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

import pytz
from pathlib import Path
from mpl_toolkits.axes_grid1 import make_axes_locatable

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from datetime import datetime, date, timedelta
from context import data_dir, xr_dir, wrf_dir, tzone_dir

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


season = "ST"
model = "era5"
domain = "earth"


filein = str(data_dir) + f"/{model}/{domain}-grid.nc"

tzone_shp = str(tzone_dir) + "/timezones-with-oceans/combined-shapefile-with-oceans.shp"

## Open datasets
ds = salem.open_xr_dataset(filein)
pyproj_srs = ds.attrs["pyproj_srs"]
df = salem.read_shapefile(tzone_shp)
# df = df[df["tzid"].str.contains("America")]
# df = df[df["min_y"] > 14]


lats = ds.XLAT.values
lons = ds.XLONG.values
zero_full = np.zeros(lats.shape)

ds["var"] = (("south_north", "west_east"), zero_full)
var_array = ds["var"]
var_array.attrs["pyproj_srs"] = pyproj_srs


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
            hours = int(seconds // 3600) * -1
        else:
            # hours = abs(int(seconds // 3600)) - 1
            hours = int(seconds // 3600) * -1
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
        hours = int(seconds // 3600) * -1
        dsr = var_array.salem.roi(shape=name)
        index = np.where(dsr == dsr)
        zero_full[index[0], index[1]] = hours
else:
    raise ValueError("ERROR: This is not a valid time of year")


ds_zones = xr.DataArray(
    zero_full.astype(int), name="Zone", dims=("south_north", "west_east")
)

# attrs = T2.attrs
# ds_zones.attrs = attrs
# ds_zones.attrs["description"] = "Time Zone Offsets From UTC"
# ds_zones.attrs["units"] = "hours"
# ds_zones = xr.merge([ds_zones, T2])


ds_zones = ds_zones.compute()
ds["ZoneST"] = (("south_north", "west_east"), ds_zones.values)
ds["ZoneST"].attrs["pyproj_srs"] = pyproj_srs
ds1 = ds.sel(west_east=slice(-170, -20), south_north=slice(88, 20))

ds1["ZoneST"].salem.quick_map(cmap="coolwarm", vmin=-11, vmax=11)
ds = ds.drop("var")
# ds.to_netcdf(
#     str(tzone_dir) + f"/tzone-{model}-{domain}-{season}.nc", mode="w"
# )


# ####################################
# ## plot for santity check
# ####################################
# ## set plot title and save dir/name
# if domain == "d02":
#     res = "12 km"
# else:
#     res = "4 km"
# if season == "DT":
#     toy = "Summer"
# else:
#     toy = "Winter"

# Plot_Title = (
#     f"Time Zone Offsets From UTC during {toy} \n {model.upper()} {res} Domain"
# )
# save_file = f"/images/{model}-{domain}-tzone-{season}.png"
# save_dir = str(data_dir) + save_file


# ## bring in state/prov boundaries
# states_provinces = cfeature.NaturalEarthFeature(
#     category="cultural",
#     name="admin_1_states_provinces_lines",
#     scale="50m",
#     facecolor="none",
# )


# ## make fig for make with projection
# fig = plt.figure(figsize=[16, 8])
# ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(central_longitude=0))

# ## add map features
# ax.gridlines()
# ax.add_feature(cfeature.LAND, zorder=1)
# ax.add_feature(cfeature.LAKES, zorder=1)
# ax.add_feature(cfeature.OCEAN, zorder=9)
# ax.add_feature(cfeature.BORDERS, zorder=10)
# ax.add_feature(cfeature.COASTLINE, zorder=10)
# ax.add_feature(states_provinces, edgecolor="gray", zorder=2)
# ax.set_xlabel("Longitude", fontsize=18)
# ax.set_ylabel("Latitude", fontsize=18)

# ## create tick mark labels and style
# ax.set_xticks(list(np.arange(-160, -40, 10)), crs=ccrs.PlateCarree())
# ax.set_yticks(list(np.arange(30, 80, 10)), crs=ccrs.PlateCarree())
# # ax.yaxis.tick_right()
# # ax.yaxis.set_label_position("right")
# ax.tick_params(axis="both", which="major", labelsize=14)
# ax.tick_params(axis="both", which="minor", labelsize=14)

# ## add title and adjust subplot buffers
# ax.set_title(Plot_Title, fontsize=20, weight="bold")
# fig.subplots_adjust(hspace=0.8)
# divider = make_axes_locatable(ax)
# ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)

# ## get d01 lats and lon
# # lats, lons = np.array(ds.XLAT), np.array(ds.XLONG)
# # lats, lons = lats[0], lons[0]
# lons = np.where(
#     lons > -179, lons, np.nan
# )  ## mask out past international dateline.....catorpy hates the dateline

# ## plot d01
# ax.plot(lons[0], lats[0], color="k", linewidth=2, zorder=10, alpha=1)
# ax.plot(lons[-1].T, lats[-1].T, color="k", linewidth=2, zorder=10, alpha=1)
# ax.plot(lons[:, 0], lats[:, 0], color="k", linewidth=2, zorder=10, alpha=1)
# ax.plot(
#     lons[:, -1].T,
#     lats[:, -1].T,
#     color="k",
#     linewidth=2,
#     zorder=10,
#     alpha=1,
# )


# levels = np.unique(zero_full)
# if model == "wrf3":
#     levels = [3, 4, 5, 6, 7, 8, 9, 10]
#     levels = [-10, -9, -8, -7, -6, -5, -4, -3]
# elif model == "wrf":
#     levels = [3, 4, 5, 6, 7, 8, 9, 10]
#     levels = [-10, -9, -8, -7, -6, -5, -4, -3]
# else:
#     pass

# # divider = make_axes_locatable(ax)


# contourf = ax.contourf(
#     lons,
#     lats,
#     (zero_full + 0.5) * -1,
#     zorder=8,
#     alpha=0.5,
#     levels=levels,
#     cmap="Dark2_r",
# )

# fig.add_axes(ax_cb)
# # ticks = levels[1:]
# # tick_levels = list(np.array(levels) - 0.5)
# cbar = plt.colorbar(contourf, cax=ax_cb, ) #ticks=tick_levels)
# # cbar.ax.set_yticklabels(ticks)  # set ticks of your format
# # cbar.ax.axes.tick_params(length=0)

# ## set map bounds
# ## set map bounds
# if model == "wrf3":
#     ax.set_xlim([-144, -55])
#     ax.set_ylim([36, 70])
# elif model == "wrf":
#     ax.set_xlim([-174, -29])
#     ax.set_ylim([25, 80])
# else:
#     pass


# ## tighten up fig
# plt.tight_layout()
# plt.show()
# ## save as png
# # fig.savefig(save_dir, dpi=240)
