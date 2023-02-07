import context

import numpy as np
import xarray as xr
import geopandas as gpd
import pandas as pd


import salem

from netCDF4 import Dataset
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from context import data_dir
from pykrige.ok import OrdinaryKriging
from datetime import datetime

from utils.fwi import solve_ffmc


from wrf import (
    to_np,
    getvar,
    smooth2d,
    get_cartopy,
    cartopy_xlim,
    cartopy_ylim,
    latlon_coords,
)

startTime = datetime.now()

fwf_d02_ds = salem.open_xr_dataset(
    "/Volumes/Scratch/FWF-WAN00CG/d02/202107/fwf-daily-d02-2021070106.nc"
)
# fwf_d02_ds = fwf_d02_ds.chunk('auto')
fwf_d03_ds = salem.open_xr_dataset(
    "/Volumes/Scratch/FWF-WAN00CG/d03/202107/fwf-daily-d03-2021070106.nc"
)
# fwf_d03_ds = fwf_d03_ds.chunk('auto')


## define the desired grid resolution in meters
resolution = 4_000  # grid cell size in meters

x0, x1 = float(fwf_d02_ds.west_east.min()), float(fwf_d02_ds.west_east.max())
y0, y1 = float(fwf_d02_ds.south_north.min()), float(fwf_d02_ds.south_north.max())

## make grid based on dataset bounds and resolution
gridx = np.arange(x0, x1, resolution)
gridy = np.arange(y0, y1, resolution)

## use salem to create a dataset with the grid.
krig_ds = salem.Grid(
    nxny=(len(gridx), len(gridy)),
    dxdy=(resolution, resolution),
    x0y0=(x0, y0),
    proj="+R=6370000 +lat_0=90 +lat_ts=53.25 +lon_0=-110 +no_defs+proj=stere +units=m +x_0=0 +y_0=0",
    pixel_ref="corner",
).to_dataset()
## print dataset
# krig_ds


# fwf_d02_dsT = krig_ds.salem.transform(fwf_d02_ds, interp='spline')

fwf_d02_ds = fwf_d02_ds.isel(time=0)


def solve_ffmc(ds):
    W, T, H, r_o = (ds.W, ds.T, ds.H, ds.r_o)
    try:
        F = ds.F
    except:
        print("Initalizing FFMC")
        F = np.full(W.shape, 85, dtype=float)

    # #Eq. 1
    m_o = 147.2 * (101 - F) / (59.5 + F)

    ########################################################################
    ### Solve for the effective raut
    r_f = xr.where(r_o > 0.5, (r_o - 0.5), xr.where(r_o < 1e-7, 1e-5, r_o))
    ########################################################################
    ### (1) Solve the Rautfagner 1985 (m_r)
    m_o = xr.where(
        m_o <= 150,
        m_o + (42.5 * r_f * np.exp((-100 / (251 - m_o))) * (1 - np.exp((-6.93 / r_f)))),
        m_o
        + (42.5 * r_f * np.exp((-100 / (251 - m_o))) * (1 - np.exp((-6.93 / r_f))))
        + (0.0015 * np.power((m_o - 150), 2) * np.power(r_f, 0.5)),
    )

    m_o = np.where(m_o > 250, 250, np.where(m_o < 0, 0.0, m_o))

    ########################################################################
    ### (2a) Solve Equilibrium Moisture content for dry

    E_d = (
        0.942 * np.power(H, 0.679)
        + 11 * np.exp((H - 100) / 10)
        + 0.18 * (21.1 - T) * (1 - np.exp((-0.115 * H)))
    )

    ########################################################################
    ### (2b) Solve Equilibrium Moisture content for wett

    E_w = (
        0.618 * (np.power(H, 0.753))
        + 10 * np.exp((H - 100) / 10)
        + 0.18 * (21.1 - T) * (1 - np.exp((-0.115 * H)))
    )
    ########################################################################
    ### (3a) ate step to k_d (k_a)
    k_a = 0.424 * (1 - np.power(H / 100, 1.7)) + 0.0694 * (np.power(W, 0.5)) * (
        1 - np.power(H / 100, 8)
    )

    ########################################################################
    ### (3b) Log dryfor hourly computation, log to base 10 (k_d)
    k_d = k_a * 0.581 * np.exp(0.0365 * T)

    ########################################################################
    ### (4a) ate steps to k_w (k_b)
    k_b = 0.424 * (1 - np.power(((100 - H) / 100), 1.7)) + 0.0694 * np.power(W, 0.5) * (
        1 - np.power(((100 - H) / 100), 8)
    )

    ########################################################################
    ### (4b)  Log wettfor hourly computation, log to base 10 (k_w)
    k_w = k_b * 0.581 * np.exp(0.0365 * T)

    ########################################################################
    ### (5a) ate dry moisture code (m_d)
    m_d = E_d + (m_o - E_d) * 10 ** (-k_d)

    ########################################################################
    ### (5b) ate wet moisture code (m_w)
    m_w = E_w - (E_w - m_o) * 10 ** (-k_w)

    ########################################################################
    ### (5c) combwet, neutral moisture codes
    m = xr.where(m_o > E_d, m_d, m_w)
    m = xr.where((E_d >= m_o) & (m_o >= E_w), m_o, m)
    # m_o = xr.DataArray(m, name="m_o", dims=("temp", "wind", "rh", "precip"))
    # ds["m_o"] = m_o

    ########################################################################
    ### (6) Solve for FFMC
    F = (59.5 * (250 - m)) / (147.2 + m)  ## Van 1985
    # F = xr.DataArray(F, name="F", dims=("temp", "wind", "rh", "precip"))
    ds["F"] = F

    return ds


startTimeF = datetime.now()
fwf_d02_ds = solve_ffmc(fwf_d02_ds)
print(f"Solve FFMC time {datetime.now() - startTimeF}")


lon, lat = fwf_d02_dsT.salem.grid.ll_coordinates
# fwf_d02_dsT['lon'], fwf_d02_dsT['lat'] = lon, lat
# fwf_d03_dsT = krig_ds.salem.transform(fwf_d03_ds, interp='spline')

# fwf_unified = xr.where(fwf_d03_dsT.notnull(),fwf_d03_dsT, fwf_d02_dsT)
# print(f"Unification time {datetime.now() - startTime}")

# # resolution = 1000
# # ## make grid based on dataset bounds and resolution
# # gridx = np.arange(x0, x1, resolution)
# # gridy = np.arange(y0, y1, resolution)

# # ## use salem to create a dataset with the grid.
# # krig_ds = salem.Grid(
# #     nxny=(len(gridx), len(gridy)),
# #     dxdy=(resolution, resolution),
# #     x0y0=(x0, y0),
# #     proj="+R=6370000 +lat_0=90 +lat_ts=53.25 +lon_0=-110 +no_defs+proj=stere +units=m +x_0=0 +y_0=0",
# #     pixel_ref="corner",
# # ).to_dataset()
# # ## print dataset
# # krig_ds


# # testT = krig_ds.salem.transform(test, interp='spline')


# # wrf_d02_dsT['lon'], wrf_d02_dsT['lat'] = lon, lat
# # gpm25 = gpd.GeoDataFrame(
# #     df,
# #     crs="EPSG:4326",
# #     geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
# # ).to_crs("North_Pole_Stereographic")
# # gpm25["Easting"], gpm25["Northing"] = gpm25.geometry.x, gpm25.geometry.y
# # gpm25.head()


# # nlags = 15
# # variogram_model = "spherical"

# # startTime = datetime.now()
# # krig = OrdinaryKriging(
# #     x=gpm25["Easting"],
# #     y=gpm25["Northing"],
# #     z=gpm25["tp"],
# #     variogram_model=variogram_model,
# #     # enable_statistics=True,
# #     nlags=nlags,
# # )
# # print(f"OK build time {datetime.now() - startTime}")


# # ax = plt.axes(projection=cart_proj)
# # ax.set_global()
# # era5_dsT["tp"].plot(
# #     ax=ax,
# #     transform=ccrs.PlateCarree(),
# #     # levels=[0, 5, 10, 20, 40, 80, 160, 300, 600],
#     cmap="Reds",
# )
# ax.coastlines()
# ax.set_extent([-180, -49, 25, 80], crs=ccrs.PlateCarree())
