import context
import json
import salem

import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
from matplotlib.cm import get_cmap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.ticker as mticker
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import string


import cartopy.crs as crs
from cartopy.feature import NaturalEarthFeature
from datetime import datetime

from wrf import (
    to_np,
    getvar,
    smooth2d,
    get_cartopy,
    cartopy_xlim,
    cartopy_ylim,
    latlon_coords,
    interplevel,
)

from context import wrf_dir, data_dir
from cartopy.io.img_tiles import GoogleTiles
import warnings

warnings.simplefilter("ignore")


class ShadedReliefESRI(GoogleTiles):
    # shaded relief
    def _image_url(self, tile):
        x, y, z = tile
        url = (
            "https://server.arcgisonline.com/ArcGIS/rest/services/"
            "World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}.jpg"
        ).format(z=z, y=y, x=x)
        return url


domain = "d02"
ds = xr.open_dataset(
    str(data_dir) + f"/heatwave/wrfout_{domain}_2021062506_2021070100.nc"
)


# ds_anom_og = xr.open_dataset('data.nc', decode_times=False)
# ds_anom_og['T'] = ds_anom_og['T'].values.astype(str)
# ds_anom_og.to_netcdf('data_1.nc')


gog_dir = "/Volumes/GoogleDrive/Shared drives/WAN00CG-01/21071900"
ncfile = Dataset(str(gog_dir) + f"/wrfout_{domain}_2021-07-20_21:00:00")

# Extract the pressure, geopotential height, and wind variables
p = getvar(ncfile, "pressure")
wrf_ds = salem.open_xr_dataset(str(gog_dir) + f"/wrfout_{domain}_2021-07-20_21:00:00")
# wrf_ds = wrf_ds.isel(Time = 0)
# ds_anom = salem.open_xr_dataset('data_1.nc')
# del ds_anom['P']
# del ds_anom['T']

# # ds_anom1 = ds_anom.isel(T= 5)
# # grid = wrf_ds.salem.grid
# # ds_anom1 = ds_anom1.isel(P= 0)
# # ds_anom1['phiclim'] = ds_anom1.phiclim.astype(float)
# blah = wrf_ds.salem.transform(ds_anom, interp='linear')

# ds_anom1 = ds_anom.isel(T= 5)

### Open color map json
with open(str(data_dir) + "/json/colormaps-hw.json") as f:
    cmaps = json.load(f)

var, index = "T", 18
vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
name, colors, sigma = (
    str(cmaps[var]["name"]),
    cmaps[var]["colors"],
    cmaps[var]["sigma"],
)
levels = cmaps[var]["levels"]

# colors = colors[-24:]


# %%


ds1 = ds.isel(Time=10)
intitalized_a = np.array(ds.isel(Time=7).Time.dt.strftime("%Y-%m-%dT%H"))
intitalized_a = datetime.strptime(str(intitalized_a), "%Y-%m-%dT%H").strftime(
    "%H UTC %A %d %B, %Y"
)

intitalized_cbde = np.array(ds.isel(Time=11).Time.dt.strftime("%Y-%m-%dT%H"))
intitalized_cbde = datetime.strptime(str(intitalized_cbde), "%Y-%m-%dT%H").strftime(
    "%H UTC %A %d %B, %Y"
)

intitalized_fghi = np.array(ds.isel(Time=15).Time.dt.strftime("%Y-%m-%dT%H"))
intitalized_fghi = datetime.strptime(str(intitalized_fghi), "%Y-%m-%dT%H").strftime(
    "%H UTC %A %d %B, %Y"
)


ty1, ty2 = 0, -1
tx1, tx2 = 0, -1
# levels = np.arange(0, 46.5, 0.5)
skip = 8
cmap = LinearSegmentedColormap.from_list("meteoblue", colors, N=len(levels))
# lats, lons = ds.XLAT.values, ds.XLONG.values
lats, lons = ds.XLAT.values[ty1:ty2, tx1:tx2], ds.XLONG.values[ty1:ty2, tx1:tx2]

# Download and add the states and coastlines
states = NaturalEarthFeature(
    category="cultural",
    scale="50m",
    facecolor="none",
    name="admin_1_states_provinces_shp",
)

sub_name = list(string.ascii_uppercase)

# height_500 = ds1.height_interp_500.values
# height_500 = smooth2d(height_500, 3, cenweight=4)
# height_500 = height_500.values[ty1:ty2, tx1:tx2]


# temp_500 = interplevel(ds1.temp - 273.15, ds1.pressure, 500)
# temp_500 = smooth2d(temp_500.values, 3, cenweight=4)
# temp_500 = temp_500[ty1:ty2, tx1:tx2]


slp = ds1.slp.values
slp = smooth2d(slp, 3, cenweight=4)
slp = slp.values[ty1:ty2, tx1:tx2]


temp_925 = interplevel(ds1.temp - 273.15, ds1.pressure, 925.0)
# temp_925 = smooth2d(temp_925.values, 3, cenweight=4)
temp_925 = temp_925[ty1:ty2, tx1:tx2]
cart_proj = get_cartopy(p)
Cnorm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)

fig = plt.figure(figsize=(14, 10))
ax = fig.add_subplot(1, 1, 1, projection=cart_proj)
ax.add_feature(states, linewidth=0.5, edgecolor="black", zorder=9)
ax.coastlines("50m", linewidth=0.8)
CS = ax.contour(
    lons,
    lats,
    slp,
    # levels=np.arange(960, 1032, 2),
    linewidths=0.9,
    colors="black",
    zorder=10,
    transform=crs.PlateCarree(),
)
contourf = ax.contourf(
    lons,
    lats,
    temp_925,
    levels=levels,
    norm=Cnorm,
    colors=colors,
    extend="both",
    zorder=9,
    transform=crs.PlateCarree(),
)

# fig.subplots_adjust(right=0.99, wspace=-0.45)
# cbaxes = fig.add_axes([0.88, 0.04, 0.03, 0.8])
# clb = fig.colorbar(contourf, cax=cbaxes, pad=0.2)
# clb = fig.colorbar(contourf,  pad=0.2)

plt.show()
# # Create a figure
# fig = plt.figure(figsize=(14, 10))
# for i in range(1, 10):
#     ax = fig.add_subplot(3, 3, i, projection=crs.PlateCarree())
#     ax.text(
#         0.022,
#         0.96,
#         sub_name[i - 1],
#         ha="center",
#         va="center",
#         transform=ax.transAxes,
#         zorder=10,
#         color="k",
#         bbox=dict(facecolor="white", edgecolor="k", lw=0.5),
#     )
#     ds1 = ds.isel(Time=10 + i)
#     slp = ds1.slp
#     smooth_slp = smooth2d(slp, 3, cenweight=4)
#     smooth_slp = smooth_slp.values[ty1:ty2, tx1:tx2]
#     wsp = ds1.wspd_wdir10.values[ty1:ty2, tx1:tx2]

#     # ind_low = np.unravel_index(np.argmin(np.where((lons<-123.8) & (lats<45),smooth_slp, 99999), axis=None), smooth_slp.shape)
#     # ind_high = np.unravel_index(np.argmax(np.where((lons<-114) & (lats>45),smooth_slp, -99999), axis=None), smooth_slp.shape)
#     # ind_high = np.unravel_index(np.argmax(smooth_slp, axis=None), smooth_slp.shape)
#     ind_high = np.unravel_index(
#         np.argmax(np.where((lons < -114) & (lats > 45), smooth_slp, -99999), axis=None),
#         smooth_slp.shape,
#     )

#     if i == 1:
#         ind_low = np.unravel_index(
#             np.argmin(
#                 np.where((lons < -123.8) & (lats < 45), smooth_slp, 99999), axis=None
#             ),
#             smooth_slp.shape,
#         )
#         # ind_high = np.unravel_index(np.argmax(np.where((lons<-114) & (lats>45),smooth_slp, -99999), axis=None), smooth_slp.shape)
#     elif i == 2:
#         ind_low = np.unravel_index(
#             np.argmin(
#                 np.where((lons < -124) & (lats < 45), smooth_slp, 99999), axis=None
#             ),
#             smooth_slp.shape,
#         )
#         # ind_high = np.unravel_index(np.argmax(np.where((lons<-114) & (lats>45),smooth_slp, -99999), axis=None), smooth_slp.shape)
#     elif i == 6:
#         ind_low = np.unravel_index(
#             np.argmin(
#                 np.where((lons < -124.5) & (lats < 43.8), smooth_slp, 99999), axis=None
#             ),
#             smooth_slp.shape,
#         )
#         ind_high = np.unravel_index(
#             np.argmax(
#                 np.where((lons < -114) & (lats > 50), smooth_slp, -99999), axis=None
#             ),
#             smooth_slp.shape,
#         )
#     elif i == 9:
#         ind_low = np.unravel_index(
#             np.argmin(
#                 np.where((lons < -124.5) & (lats < 45), smooth_slp, 99999), axis=None
#             ),
#             smooth_slp.shape,
#         )
#         ind_high = np.unravel_index(
#             np.argmax(
#                 np.where((lons > -123) & (lats > 50), smooth_slp, -99999), axis=None
#             ),
#             smooth_slp.shape,
#         )
#     else:
#         ind_low = np.unravel_index(
#             np.argmin(
#                 np.where((lons < -123.8) & (lats < 45), smooth_slp, 99999), axis=None
#             ),
#             smooth_slp.shape,
#         )

#     t2 = ds1.T2.values - 273.15
#     t2 = t2[ty1:ty2, tx1:tx2]
#     u10, v10 = (
#         ds1.uvmet10.values[0, ty1:ty2, tx1:tx2] * (60 * 60 / 1000),
#         ds1.uvmet10.values[1, ty1:ty2, tx1:tx2] * (60 * 60 / 1000),
#     )
#     # (1.943844)
#     valid = np.array(ds1.Time.dt.strftime("%Y-%m-%dT%H"))
#     valid = datetime.strptime(str(valid), "%Y-%m-%dT%H").strftime("%H UTC %A %d %B, %Y")
#     ax.set_title(f"Valid: {valid}")

#     divider = make_axes_locatable(ax)
#     ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)

#     ax.add_feature(states, linewidth=0.5, edgecolor="black", zorder=9)
#     ax.coastlines("50m", linewidth=0.8)

#     ax.text(
#         lons[ind_low[0], ind_low[1]],
#         lats[ind_low[0], ind_low[1]],
#         "L",
#         transform=crs.Geodetic(),
#         zorder=10,
#         color="red",
#         fontweight="bold",
#         bbox=dict(facecolor="white", edgecolor="k", lw=0.5, boxstyle="round", pad=0.2),
#     )

#     ax.text(
#         lons[ind_high[0], ind_high[1]],
#         lats[ind_high[0], ind_high[1]],
#         "H",
#         transform=crs.Geodetic(),
#         zorder=10,
#         color="blue",
#         fontweight="bold",
#         bbox=dict(facecolor="white", edgecolor="k", lw=0.5, boxstyle="round", pad=0.2),
#     )

#     CS = ax.contour(
#         lons,
#         lats,
#         smooth_slp,
#         levels=np.arange(960, 1032, 2),
#         linewidths=0.4,
#         colors="black",
#         zorder=9,
#     )
#     cb = ax.clabel(CS, inline=1, fontsize=7, fmt="%1.0f", inline_spacing=-2.4, zorder=9)

#     contourf = ax.contourf(
#         lons,
#         lats,
#         t2,
#         levels=levels,
#         cmap=cmap,
#         extend="both",
#         zorder=4,
#         alpha=0.9,
#     )

#     ax.barbs(
#         lons[::skip, ::skip],
#         lats[::skip, ::skip],
#         u10[::skip, ::skip],
#         v10[::skip, ::skip],
#         length=3,
#         zorder=8,
#         lw=0.4,
#     )

#     # # Set the map bounds
#     ax.set_xlim([-130, -114])
#     ax.set_ylim([43.2, 55.5])
#     # Add the gridlines

#     if i == 1:
#         print(i)
#         gl = ax.gridlines(
#             draw_labels=True,
#             linewidth=0.5,
#             color="gray",
#             alpha=0.5,
#             linestyle="dotted",
#             zorder=5,
#         )
#         gl.top_labels = False
#         gl.bottom_labels = False
#         gl.right_labels = False
#         gl.xlocator = mticker.FixedLocator(list(np.arange(-180, 180, 2)))
#     elif i == 4:
#         print(i)
#         gl = ax.gridlines(
#             draw_labels=True,
#             linewidth=0.5,
#             color="gray",
#             alpha=0.5,
#             linestyle="dotted",
#             zorder=5,
#         )
#         gl.top_labels = False
#         gl.bottom_labels = False
#         gl.right_labels = False

#         gl.xlocator = mticker.FixedLocator(list(np.arange(-180, 180, 2)))
#     elif i == 7:
#         print(i)
#         gl = ax.gridlines(
#             draw_labels=True,
#             linewidth=0.5,
#             color="gray",
#             alpha=0.5,
#             linestyle="dotted",
#             zorder=5,
#         )
#         gl.top_labels = False
#         gl.right_labels = False
#         gl.left_labels = True
#         gl.bottom_labels = True
#         gl.xlocator = mticker.FixedLocator(list(np.arange(-180, 180, 3)))
#     elif i == 8:
#         print(i)
#         gl = ax.gridlines(
#             draw_labels=True,
#             linewidth=0.5,
#             color="gray",
#             alpha=0.5,
#             linestyle="dotted",
#             zorder=5,
#         )
#         gl.top_labels = False
#         gl.right_labels = False
#         gl.left_labels = False
#         gl.bottom_labels = True
#         gl.xlocator = mticker.FixedLocator(list(np.arange(-180, 180, 3)))
#     elif i == 9:
#         print(i)
#         gl = ax.gridlines(
#             draw_labels=True,
#             linewidth=0.5,
#             color="gray",
#             alpha=0.5,
#             linestyle="dotted",
#             zorder=5,
#         )
#         gl.top_labels = False
#         gl.right_labels = False
#         gl.left_labels = False
#         gl.bottom_labels = True
#         gl.xlocator = mticker.FixedLocator(list(np.arange(-180, 180, 3)))
#     else:
#         gl = ax.gridlines(
#             draw_labels=False,
#             linewidth=0.5,
#             color="gray",
#             alpha=0.5,
#             linestyle="dotted",
#             zorder=5,
#         )
#     plt.subplots_adjust(wspace=0.0)


# # plt.title("Sea Level Pressure (hPa)")
# fig.tight_layout(rect=[0, 0.03, 1, 0.9])
# fig.subplots_adjust(right=0.99, wspace=-0.45)
# cbaxes = fig.add_axes([0.88, 0.04, 0.03, 0.8])
# clb = fig.colorbar(contourf, cax=cbaxes, pad=0.2)
# # clb.ax.set_title('Temp at 2m ($^\circ$C)', ha='right', fontsize=8, rotation=-90)
# clb.ax.get_yaxis().labelpad = 14
# clb.ax.set_ylabel("Temperature at 2m ($^\circ$C)", rotation=270, fontsize=11)
# # fig.suptitle(f'UBC WRF-NAM 4km Domain \n  ')
# plt.figtext(0.6, 0.965, f"Init [A]:              {intitalized_a}", fontsize=12)
# plt.figtext(0.6, 0.94, f"Init [B, C, D, E]: {intitalized_cbde}", fontsize=12)
# plt.figtext(0.6, 0.915, f"Init [F, G, H, I]:  {intitalized_fghi}", fontsize=12)

# plt.figtext(0.1, 0.975, f"UBC WRF-NAM 4km Domain", fontsize=14)
# plt.figtext(
#     0.1,
#     0.9,
#     "Temperature at 2m ($^\circ$C)  \nSea Level Pressure (hPa) \n10m Wind (full barb = 10$km\,h^{-1}$)",
#     fontsize=11,
# )

# # plt.savefig('/Users/rodell/Desktop/sample2.png', dpi = 250)

# plt.show()
# # %%
