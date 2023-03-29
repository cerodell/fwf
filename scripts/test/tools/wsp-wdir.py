import context
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from context import data_dir, xr_dir, wrf_dir

from wrf import (
    getvar,
    g_uvmet,
    get_cartopy,
    ll_to_xy,
    interplevel,
    omp_set_num_threads,
    omp_get_max_threads,
)

domain = "d02"

wrf_file = Dataset(str(data_dir) + f"/wrf/wrfout_{domain}_2021-01-14_00:00:00", "r")


wsp_wdir = g_uvmet.get_uvmet10_wspd_wdir(wrf_file)
U10 = getvar(wrf_file, "U10")
V10 = getvar(wrf_file, "V10")


# Define the latitude and longitude arrays in degrees
lats = wsp_wdir.XLAT.values
lons = wsp_wdir.XLONG.values

# Convert latitude and longitude to radians
lats_rad = np.radians(lats)
lons_rad = np.radians(lons)

# Calculate rotation angle
theta = np.arctan2(np.cos(lats_rad) * np.sin(lons_rad), np.sin(lats_rad))

# Calculate sine and cosine of rotation angle
sin_theta = np.sin(theta)
cos_theta = np.cos(theta)

# Define the u and v wind components in model coordinates
u_model = U10
v_model = V10
# Rotate the u and v wind components to Earth coordinates
u_earth = u_model * cos_theta - v_model * sin_theta
v_earth = u_model * sin_theta + v_model * cos_theta

# Print the results
# print("u_earth:", u_earth)
# print("v_earth:", v_earth)


wsp_model = np.sqrt(U10 ** 2 + V10 ** 2)
wsp_earth = np.sqrt(u_earth ** 2 + v_earth ** 2)

# wsp_earth = wsp_wdir.sel(wspd_wdir = 'wspd')
