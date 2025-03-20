import context
import json

import salem
import numpy as np
import xarray as xr
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm

import matplotlib.colors
from datetime import datetime

from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from context import data_dir, root_dir, wrf_dir

with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

from wrf import (
    getvar,
    g_uvmet,
    get_cartopy,
    ll_to_xy,
    interplevel,
    omp_set_num_threads,
    omp_get_max_threads,
    smooth2d
)


plt.rcParams.update({"font.size": 14})  # Adjust the value as needed

def cart_proj_manually(ds):
    #this assumes that the cart proj is in LamberConformal which is generally true for WRF, but not always
    # to confirm, check ds.attrs['MAP_PROJ_CHAR']
    cen_lat = getattr(ds, 'MOAD_CEN_LAT', None)
    cen_lon = getattr(ds, 'STAND_LON', None)
    true_lat1 = getattr(ds, 'TRUELAT1', None)
    true_lat2 = getattr(ds, 'TRUELAT2', None)
    lccProjParams_HRRR = { 'central_latitude'   : cen_lat,
                       'central_longitude'  : cen_lon,
                       'standard_parallels' : (true_lat1, true_lat2),
                     }
    crs = ccrs.LambertConformal(**lccProjParams_HRRR)
    return crs


wrf_ds = salem.open_wrf_dataset('/NASPANGEA2/HISTORICAL_WEATHER/FA_DTN_20_YEAR/2022/08/15/wrfsfc_d03_20220815_2000.nc')
cart_proj = cart_proj_manually(wrf_ds)

for doi in pd.date_range("2024-07-15", "2024-07-15"):
    wrf_daily_d03 = salem.open_xr_dataset(f"/NASPANGEA2/HISTORICAL_WEATHER/FA_DTN_20_YEAR/cffdrs/fwi/fwf-hourly-d03-{doi.strftime('%Y%m%d00')}.nc")#.rename_vars({'r_o_tomorrow': 'r_o'})

    for var in wrf_daily_d03:
        try:
            fig = plt.figure(figsize = (10,10))
            ax= fig.add_subplot(1,1,1, projection=cart_proj)

            vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
            title, colors = str(cmaps[var]["title"]), cmaps[var]["colors18"]
            levels = cmaps[var]["levels"]
            # custom_cmap = LinearSegmentedColormap.from_list(
            #     "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
            # )
            Cnorm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)

            contourf = plt.contourf(
                    wrf_daily_d03.XLONG.values,
                    wrf_daily_d03.XLAT.values,
                    # ndimage.gaussian_filter(da.values, sigma=sigma),
                    smooth2d(wrf_daily_d03[var].isel(time =0).values, 1, cenweight=2),
                    levels=levels,
                    linestyles="None",
                    norm=Cnorm,
                    colors=colors,
                    extend="both",
                    transform=ccrs.PlateCarree()
                )
            ax.add_feature(cfeature.BORDERS, edgecolor='black', linewidth=1)

            # Attach colorbar to this specific subplot
            cbar = fig.colorbar(contourf, ax=ax, orientation="vertical", pad=0.02, shrink=0.8)
            cbar.set_label(title)  # Label for the colorbar

            # State/Province borders (higher resolution)
            # provinces = cfeature.NaturalEarthFeature(
            #     category='cultural',
            #     name='admin_1_states_provinces_lines',
            #     scale='10m',
            #     facecolor='none'
            # )
            # ax.add_feature(provinces, edgecolor='gray', linewidth=0.8)  # Adjust color & width as needed

            ax.add_feature(cfeature.STATES, edgecolor='black', linewidth=.8)

            # Coastlines (for context)
            ax.add_feature(cfeature.COASTLINE, edgecolor='black', linewidth=1)

            # Major lakes
            ax.add_feature(cfeature.LAKES, edgecolor='none', facecolor='#417793', linewidth=0.8)

            # plt.colorbar(contourf, ax=ax, pad=.05)

            
            ax.set_title(title+ '\n' + doi.strftime('%Y-%m-%d'))
            fig.tight_layout()
            # plt.savefig(f"{root_dir}/img/fa/sample-{var}.png", dpi = 250)
        except:
            plt.close()


# doi = pd.Timestamp("2022-08-15")
# wrf_daily_d03 = salem.open_xr_dataset(f"/NASPANGEA2/HISTORICAL_WEATHER/FA_DTN_20_YEAR/cffdrs/fwi/fwf-daily-d03-{doi.strftime('%Y%m%d00')}.nc")
# wrf_hourly_d03 = salem.open_xr_dataset(f"/NASPANGEA2/HISTORICAL_WEATHER/FA_DTN_20_YEAR/cffdrs/fwi/fwf-hourly-d03-{doi.strftime('%Y%m%d00')}.nc")






# # Create figure and axis
# fig = plt.figure(figsize=(10, 14))
# ax = fig.add_subplot(1, 1, 1, projection=cart_proj)

# # ---- ADD MAP FEATURES ----
# ax.add_feature(cfeature.BORDERS, edgecolor='black', linewidth=1)  # Country borders
# ax.add_feature(cfeature.COASTLINE, edgecolor='black', linewidth=1)  # Coastlines
# ax.add_feature(cfeature.STATES, edgecolor='black', linewidth=.8)

# # ---- ADD GRID CELL LINES ----
# lons = wrf_daily_d03.XLONG.values
# lats = wrf_daily_d03.XLAT.values

# # Plot vertical lines (longitude grid lines)
# for i in range(lons.shape[1]):  # Loop over columns
#     ax.plot(lons[:, i], lats[:, i], color="black", linewidth=0.3, alpha=0.5, transform=ccrs.PlateCarree())

# # Plot horizontal lines (latitude grid lines)
# for i in range(lats.shape[0]):  # Loop over rows
#     ax.plot(lons[i, :], lats[i, :], color="black", linewidth=0.3, alpha=0.5, transform=ccrs.PlateCarree())

# # Set title
# ax.set_title('Domain Surface Grids')

# # Adjust layout
# fig.tight_layout()
# plt.savefig(f"{root_dir}/img/fa/surface-grids.png", dpi = 250)
