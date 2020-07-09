import context
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from context import data_dir, xr_dir, wrf_dir, root_dir
from datetime import datetime, date, timedelta
startTime = datetime.now()


import matplotlib as mpl
import matplotlib.colors
import cartopy.crs as crs
import matplotlib.pyplot as plt
# from wrf import (getvar, g_uvmet)

from wrf import (to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ALL_TIMES, xy_to_ll,ll_to_xy)



### BRing in zarr FWF forecast data 
hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 

hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)


center_lon = float(hourly_ds.CEN_LON)
### Bring in WRF Data and open

# wrf_folder = date.today().strftime('/%y%m%d00/')
wrf_folder = '/20070100/'
filein = str(wrf_dir) + wrf_folder
wrf_file_dir = sorted(Path(filein).glob('wrfout_d03_*'))


wrf_file = Dataset(wrf_file_dir[-1],'r')
LANDMASK    = getvar(wrf_file, "LANDMASK")





# lat, lon = 44, -129.3
# lat, lon = 49.2923,-74.8584
lat, lon = 50.6745, -120.3273
xy = ll_to_xy(wrf_file, lat, lon)
print("x wrf: ", np.array(xy[0]))
print("y wrf: ", np.array(xy[1]))
ll = xy_to_ll(wrf_file, 20, 10)
# print(np.array(ll))


xlong = np.array(hourly_ds.XLONG)
xlong = xlong[::8,::8]
xlat = np.array(hourly_ds.XLAT)
xlat = xlat[::8,::8]

points = list(zip(xlat.ravel(), xlong.ravel()))
# ----- search nearest grid point ----- #
from scipy.spatial import cKDTree
gridTree = cKDTree(list(zip(xlat.ravel(), xlong.ravel())))
grid_shape = xlong.shape
# for stnname, stnloc in stns.items():
dist, inds = gridTree.query((lat, lon))
print(np.unravel_index(inds, grid_shape))
# ------------------------------ #

# xlist = [1,3,5,7]
# ylist = [2,4,6,8]

# points = list(zip(xlist, ylist))
# gridTree = cKDTree(list(zip(xlist, ylist)))
# grid_shape = [1,2]
# # for stnname, stnloc in stns.items():
# x, y = 5, 5
# dist, inds = gridTree.query((x, y))
# print(np.unravel_index(inds, grid_shape))












# R_o = 6371                    ## earths rad km 
# phi_o = 57                    ## lat in degs where intersected by the projection plane
# dxy   = 4                     ## 4km of grid spacing 
# deg2rad = (np.pi/180)         ## degree to radians
# lat_ref = 42.94568253         ## domain low left lat
# lon_ref = -130.33840942       ## domain low left long

# L_ref = R_o * (1 + np.sin(phi_o * deg2rad))

# r_ref = L_ref * np.tan(0.5 * ((90 - lat_ref) * deg2rad))
# # print("r_ref: ", r_ref)

# x_ref = r_ref * np.cos(lon_ref * deg2rad)
# y_ref = r_ref * np.sin(lon_ref * deg2rad)
# print("x_ref: ", x_ref )
# print("y_ref: ", y_ref )

# ####################################
# L = R_o * (1 + np.sin(phi_o * deg2rad))
# # L = L- L_ref
# r = L * np.tan(0.5 * ((90 - lat) * deg2rad))
# # r = r - r_ref
# print("r: ", r)

# xi = r * np.cos(lon  * deg2rad)
# yj = r * np.sin(lon * deg2rad)
# print("xi: ", int(xi/dxy))
# print("yj: ", int((yj/dxy)))

# x = int(( xi - x_ref) / dxy)
# y = round((( yj - y_ref) / dxy),0)
# print("x: ", x )
# print("y: ", y )






# def myll2xy(lat, lon):
    # R_o = 6371                    ## earths rad km 
    # phi_o = 57                    ## lat in degs where intersected by the projection plane
    # dxy   = 4                     ## 4km of grid spacing 
    # deg2rad = (np.pi/180)         ## degree to radians
    # lat_ref = 42.94568253         ## domain low left lat
    # lon_ref = -130.33840942       ## domain low left long

    # L = R_o * (1 + np.sin(phi_o * deg2rad))
    # L2 = R_o * (1 + np.sin(lat_ref * deg2rad))

    # r_ref = L * np.tan(0.5 * ((90 - lat_ref) * deg2rad))
    # print("r_ref: ", r_ref)

    # x_ref = r_ref * np.cos(lon_ref * deg2rad)
    # y_ref = r_ref * np.sin(lon_ref * deg2rad)

    # r = (L) * np.tan(0.5 * ((90 - (lat)) * deg2rad))
    # # r = (r - r_ref)
    # # r = (r_ref -r )

    # print("r: ", r)
    # xi = r * np.cos(lon  * deg2rad)
    # yj = r * np.sin(lon * deg2rad)

    # print("xi: ", int(xi/dxy))
    # print("yj: ", int((yj/dxy)))

    # x = int(( xi - x_ref) / dxy)
    # y = int(( yj - y_ref) / dxy)

    # # # x, y = int(xi), int(yj)
    # print("x: ", x )
    # print("y: ", y )
    # return x , y

# # x, y = myll2xy(90, 0)
# x_ref, y_ref = myll2xy( 42., -130.33840942)
# xy = ll_to_xy(wrf_file,  42., -130.33840942)
# print("x wrf: ", np.array(xy[0]))
# print("y wrf: ", np.array(xy[1]))


# ll = xy_to_ll(wrf_file, 1200, 0)
# print(np.array(ll))




# print("x: ", x)
# print("y: ", y)
# print("x_ref: ", x_ref)
# print("y_ref: ", y_ref)

