import context
import salem
import json
import math
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
import geopandas as gpd

import matplotlib.pyplot as plt
import matplotlib.colors

from datetime import datetime, timedelta
from utils.wrf_ import read_wrf
from utils.eccc import read_eccc
from netCDF4 import Dataset

from context import data_dir, root_dir


import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from matplotlib import cm
import netCDF4 as nc
from scipy.interpolate import interp2d

"""
FOr DMC
“The daylength, varying with season, has an effect roughly proportional
to three less than the number of hours between sunrise and sunset” (Van Wagner 1987).
https://github.com/ecmwf-projects/geff/blob/master/src/mo_fwi.f90

chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://gml.noaa.gov/grad/solcalc/solareqns.PDF

"""

doi = pd.Timestamp("2021-06-15")

# static_ds = salem.open_xr_dataset(str(data_dir) + "/static/static-vars-ecmwf-era5-land.nc")
static_ds = salem.open_xr_dataset(str(data_dir) + "/static/static-vars-wrf-d02.nc")


month = int(doi.month) - 1
L_e_old = [6.5, 7.5, 9.0, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8.0, 7.0, 6.0]
L_e_old = L_e_old[month]

lat = static_ds.XLAT.values
L_e = np.zeros_like(lat)
dayOfYear = doi.day_of_year
latInRad = np.deg2rad(lat)
declinationOfEarth = 23.45 * np.sin(np.deg2rad(360.0 * (283.0 + dayOfYear) / 365.0))

L_e = np.where(
    -np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth)) <= -1.0, 24, L_e
)
L_e = np.where(
    -np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth)) >= 1.0, 1e-2, L_e
)

# hourAngle = np.rad2deg(np.arccos(-np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth))))
L_e = (
    np.where(
        L_e == 0,
        2.0
        * np.rad2deg(
            np.arccos(-np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth)))
        )
        / 15,
        L_e,
    )
    - 3
)
fig, ax = plt.subplots(figsize=(8, 6))
static_ds["L_e"] = (("south_north", "west_east"), L_e)
static_ds["L_e"].attrs = static_ds.attrs
static_ds["L_e"].salem.quick_map(ax=ax)
ax.set_title(
    f"Day length factor {L_e_old} from Van Wagner 1987 \n Valid: {doi.strftime('%Y %b %d')}"
)

# if -np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth)) <= -1.0:
#     return 24.0
# elif -np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth)) >= 1.0:
#     return 0.0
# else:
#     hourAngle = np.rad2deg(np.arccos(-np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth))))
#     return 2.0*hourAngle/15.0


# # Physical constants
# Re     = 6.371E6        # Radius of Earth in m
# eps    = 0.82           # Emissivity fraction
# sigma  = 5.67E-8        # Stephan Boltzmann constant in W / m^2 / K^4
# c_s    = 712            # heat capacity of Silicon rock in J /kg / K
# rho_s  = 2650           # density of Silicon rock in kg/m^3
# c_w    = 4000           # heat capacity of water in J /kg / K
# rho_w  = 1000           # density of water in kg/m^3
# years  = 365.25*24*3600 # seconds in a year
# S0     = 1361           # solar insolation in W m-2
# Q      = S0/4           # solar absorbtion/4 (in W m-2)
# dg2rad = np.pi/180.0    # converstion factor for degree to radians
# days   = 24*3600        # seconds per day
# ecc    = 0.017          # Eccentricity of Earth's Orbit
# mjax   = 149.6*10**9    # Major-axis of Earth in m
# months = years/12       # Seconds in a month

# # set model parameters
# alpha = 0.32             # Albedo of earth
# eps   = 0.82             # Emissivity
# depth = 100              # Depth of ocean mixed layer/land active layer, in m
# tilt = 23.45*np.pi/180   # Current Earth Tilt
# tilt_max = 24.5*np.pi/180 # Maximum tilt
# tilt_min = 22.1*np.pi/180 # Minimum tilt

# # create grid and set initial conditions
# N     = 300                         # set number of segments
# y_F   = np.linspace(-1,1,N+1)       # set position of interfaces
# y_T   = (y_F[0:N]+y_F[1:N+1])/2     # set position of midpoints
# dy    = y_F[1]-y_F[0]               # get segment length
# model_lat   = np.arcsin(y_T)/dg2rad       # latitude at segment centers

# # Set the diffusion coefficient
# D     = 0.1              # diffusion coefficient

# # set time integration parameters
# t_end = 7*years                   # integration end time
# dt    = days                    # time integration maxium step size
# out_dt= years/12                  # time between plots
# times = np.arange(0,t_end,out_dt)  # array of timesteps for output
# Nt = np.linspace(0,365.24,10000,endpoint=False)
# tt = Nt*days

# # set initial conditions
# T0 = 288 + 0*y_T                     # constant initial temperature

# # Calculate Heat capacity
# vol= 4 *np.pi* Re**2 * depth                                 # Volume of top x-meters of earth (given by depth)
# C_e = 0.7 * (c_w * vol * rho_w) + 0.3 * (c_s * vol * rho_s ) # heat capacity of earth in J K-1
# Cbar  =  C_e/(4*np.pi*Re**2)                                 # heat capacity per unit area in J m-2 K-1

# #Albedo Function
# def albedo(y):
#     alb = 0*y+alpha
#     return(alb)

# def ASR(y,t,Albedo,Tilt,Ellipse):
#     phi = np.arcsin(y)
#     asr, dec = [], []
#     for time in t:
#         if Ellipse == True:
#             r = mjax*(1-ecc**2)/(1+ecc*np.cos(2*np.pi/years*(time-3*days)))
#             S = S0*(mjax/r)**2
#         else:
#             S = S0
#         delta = Tilt*np.sin(2*np.pi/years*(time-79*days)) #Declination Angle
#         declinationOfEarth = 23.45*np.sin(np.deg2rad(360.0*(283.0+dayOfYear)/365.0))

#         h0 = np.where((abs(delta)-np.pi/2+abs(phi) < 0), np.arccos(-np.tan(phi)*np.tan(delta)),
#                    np.where((phi*delta > 0), np.pi, 0))
#         Q = S/np.pi*(h0*np.sin(phi)*np.sin(delta)+np.cos(phi)*np.cos(delta)*np.sin(h0)) #Daily Average Insolation
#         sol = Q*(1-Albedo(y_T))
#         asr.append(2*np.rad2deg(h0)/15.0)

#     return(asr)

# Solar = np.transpose(np.array(ASR(y_T,tt,albedo,tilt,False)))

# Solar_max = np.transpose(np.array(ASR(y_T,tt,albedo,tilt_max,False)))
# Solar_min = np.transpose(np.array(ASR(y_T,tt,albedo,tilt_min,False)))
# Solar_ellipse = np.transpose(np.array(ASR(y_T,tt,albedo,tilt,True)))

# plt.figure(figsize=(12,6))
# plt.gca().set_facecolor('k')
# cmap = plt.cm.YlOrRd
# Solar_ma = np.ma.masked_where(Solar_ellipse==0, Solar_ellipse)-3

# C=plt.contourf(tt/days,model_lat,Solar_ma,100,cmap=cmap,zorder=10)
# plt.contour(tt/days,model_lat,Solar_ma,10,colors='k',zorder=20, )
# plt.ylabel('Latitude (deg)', fontsize=20 )
# plt.xlabel('Day of Year', fontsize=20 )
# plt.title('Daily Averaged ASR', fontsize=25)
# plt.tick_params(labelsize=15)
# clb = plt.colorbar(C)
# clb.set_label('Daylength Factor', size=20)
# plt.show()


# era5_land = salem.open_xr_dataset(
#     f"/Volumes/WFRT-Ext22/ecmwf/era5-land/199001/era5-land-1990010200.nc"
# )
# fwf_hourly = salem.open_xr_dataset(
#     "/Volumes/WFRT-Ext24/fwf-data/ecmwf/era5-land/02/fwf-hourly-era5-land-1990010200.nc"
# )
# fwf_daily = salem.open_xr_dataset(
#     "/Volumes/WFRT-Ext24/fwf-data/ecmwf/era5-land/02/fwf-daily-era5-land-1990010100.nc"
# )
# daily_ds = salem.open_xr_dataset(
#     "/Volumes/WFRT-Ext24/fwf-data/wrf/d02/02/fwf-hourly-d02-2021011106.nc"
# )
# domain = "d02"
# var = "D"
# year = 2006


# ### Open color map json
# with open(str(root_dir) + "/json/colormaps-dev.json") as f:
#     cmaps = json.load(f)

# # with open(str(root_dir) + f"/json/fwf-attrs.json", "r") as fp:
# #     var_dict = json.load(fp)
# var2 = cmaps[var]["name"]
# title = cmaps[var]["title"].lower().replace(" ", "_")
# vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]

# # nrcan_ds = salem.open_xr_dataset(str(data_dir) + f"/ecmwf/{title}_1994.nc").sel(Time = pd.to_datetime("1994-07-01").strftime("%j"))
# # nrcan_ds = nrcan_ds.roll(Longitude=int(len(nrcan_ds["Longitude"]) / 2))

# # era5_ds = salem.open_xr_dataset(str(data_dir) + f"/ecmwf/hist/ECMWF_FWI_{var2.upper()}_{year}0701_1200_hr_v4.0_con.nc").isel(time = 0)
# # era5_ds = era5_ds.roll(longitude=int(len(era5_ds["longitude"]) / 2))
# ds = salem.open_xr_dataset(
#     f"/Volumes/WFRT-Ext25/fwf-data/ecmwf/era5/02/fwf-daily-era5-{year}080100.nc"
# ).isel(time=0)
# ds_0 = salem.open_xr_dataset(
#     f"/Volumes/WFRT-Ext25/fwf-data/ecmwf/era5/02/fwf-daily-era5-{1992}080100.nc"
# ).isel(time=0)

# # era5_ds["longitude"] = ds['west_east'].values
# # nrcan_ds["Longitude"] = ds['west_east'].values

# # ds = ds.sel(south_north = slice(85,20), west_east =slice(-170,-60))
# # ds_0 = ds_0.sel(south_north = slice(85,20), west_east =slice(-170,-60))

# # era5_ds = era5_ds.sel(latitude = slice(85,20), longitude =slice(-170,-60))
# # nrcan_ds = nrcan_ds.sel(Latitude = slice(85,20), Longitude =slice(-170,-60))

# # static_ds = static_ds.sel(south_north = slice(85,30), west_east =slice(-170,-60))

# # trans = static_ds_d02['ZoneST'].salem.transform(static_ds)


# fig = plt.figure(figsize=(12, 4))
# ax = fig.add_subplot(1, 1, 1)
# ds[var].salem.quick_map(oceans=True, vmax=600, vmin=vmin, cmap="jet", ax=ax)

# fig = plt.figure(figsize=(12, 4))
# ax = fig.add_subplot(1, 1, 1)
# ds_0[var].salem.quick_map(oceans=True, vmax=600, vmin=vmin, cmap="jet", ax=ax)
# # fig = plt.figure(figsize=(12, 4))
# # ax = fig.add_subplot(1, 1, 1)
# # era5_ds[var2].salem.quick_map(oceans =True, vmax = vmax, vmin = vmin, cmap='jet',ax = ax)
# # plt.show()

# # fig = plt.figure(figsize=(12, 4))
# # ax = fig.add_subplot(1, 1, 1)
# # nrcan_ds[var2.upper()].salem.quick_map(oceans =True, vmax = vmax, vmin = vmin, cmap='jet',ax = ax)
# # plt.show()


# my_dc = ds[var].values
# # my_dc = era5_ds[var2].values
# # ec_dc = nrcan_ds[var2.upper()].values
# past_ds = ds_0[var].values
# my_dc1 = np.where(np.isnan(past_ds), np.nan, my_dc)

# diff = past_ds - my_dc1

# ds[var2 + "_diff"] = (("south_north", "west_east"), diff)
# fig = plt.figure(figsize=(12, 4))
# ax = fig.add_subplot(1, 1, 1)
# ds[var2 + "_diff"].salem.quick_map(
#     oceans=True, cmap="coolwarm_r", vmin=-100, vmax=100, ax=ax
# )
# plt.show()
# print(float(ds[var2 + "_diff"].mean()), " MEAN")
# print(float(ds[var2 + "_diff"].min()), " MIN")
# print(float(ds[var2 + "_diff"].max()), " MAX")

# # (ds[var].isel(time = 0) - era5_ds['dc'].isel(time = 0)).salem.quick_map(oceans =True, cmap='coolwarm',)

# # # vmin, vmax = 0, 1

# # name, colors, sigma = (
# #     str(cmaps[var]["name"]),
# #     cmaps[var]["colors18"],
# #     cmaps[var]["sigma"],
# # )
# # # levels = cmaps[var]["levels"]
# # levels = np.arange(0,1.1,.1)
# # Cnorm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)

# # doi_daily_ds = salem.open_xr_dataset(f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/02/fwf-hourly-{domain}-2023051006.nc")['S']#.isel(time = 0)
# # static_ds = salem.open_xr_dataset(str(data_dir)+f"/static/static-vars-wrf-{domain}.nc")
# # doi_daily_ds['south_north'] = static_ds['south_north']
# # doi_daily_ds['west_east'] = static_ds['west_east']

# # daily_ds = xr.open_dataset(str(data_dir)+f"/norm/fwi-daily-{domain}.nc")
# # houlry_ds = xr.open_dataset(str(data_dir)+f"/norm/fwi-hourly-{domain}.nc")

# # nomr_ds = (doi_daily_ds - houlry_ds['S_min'])/ (houlry_ds['S_max'] -houlry_ds['S_min'])
# # nomr_ds['Time'] = doi_daily_ds['Time']
# # static_ds = salem.open_xr_dataset(str(data_dir)+f"/static/static-vars-wrf-{domain}.nc")
# # static_ds['S_norm'] = doi_daily_ds.isel(time =15)
# # static_ds['S_norm'].attrs = static_ds.attrs
# # static_ds['S_norm'].salem.quick_map(prov = True, states= True, oceans =True, vmax = vmax, vmin = vmin, cmap='jet',)
# # doi_daily_ds.isel(time =15).salem.quick_map(prov = True, states= True, oceans =True, vmax = 40)

# # static_ds['S'] = houlry_ds['S_max']
# # static_ds['S'].attrs = static_ds.attrs
# # static_ds['S'].salem.quick_map()


# # static_ds['S_max_daily'] = (daily_ds['S_max']- houlry_ds['S_max'])
# # static_ds['S_max_daily'].attrs = static_ds.attrs
# # static_ds['S_max_daily'].salem.quick_map(vmin = -20, vmax = 20, cmap ='coolwarm', prov = True, states= True, oceans =True)

# # doi_daily_ds =salem.open_xr_dataset(f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/02/fwf-hourly-{domain}-2023081706.nc")['S'].isel(time = 0)
# # doi_daily_ds.salem.quick_map(prov = True, states= True, oceans =True, vmax = 40)
# # #
# test["H"].isel(time=20).salem.quick_map(prov=True, states=True, oceans=True)

# # grid_ds = xr.open_dataset(str(data_dir) + f"/{model}/{domain}-grid.nc")

# # static_ds = xr.open_dataset(str(data_dir) + f"/static/static-vars-{model}-{domain}.nc")
# # tzone = static_ds["ZoneST"].values
# # landmask = static_ds["LAND"]


# # ds_01 = salem.open_xr_dataset(
# #     f"/Volumes/WFRT-Ext24/fwf-data/{model}/{domain}/01/fwf-daily-{domain}-{doi.strftime('%Y%m%d%H')}.nc"
# # ).isel(time=0)

# # ds_02 = salem.open_xr_dataset(
# #     f"/Volumes/WFRT-Ext24/fwf-data/{model}/{domain}/02/fwf-daily-{domain}-{doi.strftime('%Y%m%d%H')}.nc"
# # ).isel(time=0)

# # fig = plt.figure(figsize=(12, 6))
# # ax = fig.add_subplot(1, 1, 1)
# # ds_01["D"].salem.quick_map(ax=ax, vmin=0, vmax=425)

# # fig = plt.figure(figsize=(12, 6))
# # ax = fig.add_subplot(1, 1, 1)
# # ds_02["D"].salem.quick_map(ax=ax, vmin=0, vmax=425)


# # ds_02["diff"] = ds_01["D"] - ds_02["D"]
# # print(f"Mean diff of FWI {float(ds_02[var2+'_diff'].mean())}")
# # print(f"Max diff of FWI {float(ds_02[var2+'_diff'].max())}")
# # print(f"Min diff of FWI {float(ds_02[var2+'_diff'].min())}")
# # ds_02["diff"].attrs = ds_02["T"].attrs
# # fig = plt.figure(figsize=(12, 6))
# # ax = fig.add_subplot(1, 1, 1)
# # ds_02["diff"].salem.quick_map(cmap="coolwarm", ax=ax, vmin=-200, vmax=200)

# # for var in ds:
# #     print(var)
# #     print(np.unique(np.isnan(ds[var]), return_counts=True))

# # for var in ds:
# #     print(var)
# #     ds[var] = ds[var].interpolate_na(dim="west_east", fill_value="extrapolate")
# #     ds[var] = ds[var].interpolate_na(dim="south_north", fill_value="extrapolate")
# # ds["diff"] = ds["mS"] - ds["S"]
# # print(f"Mean diff of FWI {float(ds[var2+'_diff'].mean())}")
# # print(f"Max diff of FWI {float(ds[var2+'_diff'].max())}")
# # print(f"Min diff of FWI {float(ds[var2+'_diff'].min())}")
# # ds["diff"].attrs = ds["T"].attrs
# # ds["diff"].salem.quick_map(cmap="coolwarm", vmin=-15, vmax=15)
# # fig = plt.figure(figsize=(12, 6))
# # ax = fig.add_subplot(1, 1, 1)
# # ds['r_o'].salem.quick_map(ax=ax, cmap="coolwarm", vmin = 0, vmax =100)

# # for var in ds:
# #     print(var, np.unique(np.isnan(ds[var]), return_counts=True))


# # for var in ds:
# #     masked_array = ds[var].to_masked_array()
# #     masked_array.mask = landmask
# #     ds[var] = (("south_north", "west_east"), masked_array)
# #     ds[var].attrs["pyproj_srs"] = ds.attrs["pyproj_srs"]

# # ds["TEST"] = ds["mRt"] - 12
# # ds["TEST"].attrs["pyproj_srs"] = ds.attrs["pyproj_srs"]
# # fig = plt.figure(figsize=(12, 6))
# # ax = fig.add_subplot(1, 1, 1)
# # ds["TEST"].salem.quick_map(ax=ax, cmap="coolwarm", vmin=-12, vmax=12)
# # # condition_broadcast = xr.broadcast(landmask, ds['F'])[0]


# ###################################################################################################
# ###################################################################################################

# # tzone_shp = str(data_dir) + "/shp/buffed_oceans/buffed_oceans.shp"
# # df = salem.read_shapefile(tzone_shp)

# # name = df.loc[df["featurecla"] == "Ocean"]
# # dsr = ds["F"].salem.roi(shape=name, all_touched=True)

# # array_values = dsr.values * 0
# # # array_values[np.isnan(array_values)] = 1


# # ds["mask"] = (("south_north", "west_east"), array_values)
# # ds["mask"].attrs["pyproj_srs"] = ds["F"].attrs["pyproj_srs"]

# # fig = plt.figure(figsize=(12, 6))
# # ax = fig.add_subplot(1, 1, 1)
# # ds["mask"].salem.quick_map(ax=ax, cmap="coolwarm")

# # # ## 1 is for land 0 is for ocean
# # masked_arr = np.ma.masked_where(ds["mask"] == 0, ds["mask"])

# # for var in static_ds:
# #     result = np.ma.array(
# #         static_ds[var], mask=masked_arr.mask
# #     )  # fill_value=masked_arr.fill_value)
# #     static_ds[var] = (("south_north", "west_east"), result)
# #     static_ds[var].attrs["pyproj_srs"] = ds["F"].attrs["pyproj_srs"]
# #     grid_ds[var] = static_ds[var]  # .to_masked_array()
# #     # grid_ds[var].mask = masked_arr.mask
# # grid_ds["LAND"] = (("south_north", "west_east"), masked_arr.mask)
# # grid_ds["LAND"].attrs["pyproj_srs"] = ds["F"].attrs["pyproj_srs"]
# # fig = plt.figure(figsize=(12, 6))
# # ax = fig.add_subplot(1, 1, 1)
# # grid_ds["LAND"].salem.quick_map(ax=ax, cmap="coolwarm")
# # grid_ds.to_netcdf(str(data_dir) + f"/static/static-vars-{model}-{domain}-test.nc")

# ###################################################################################################
# ###################################################################################################


# # test = xr.where(condition_broadcast, ds['F'], 0)

# # .isel(time = -1)
# # ds

# # ds = ds.chunk('auto')
# # ds = ds.chunk('auto')

# # startTime = datetime.now()
# # for var in ds:
# #     masked_array = ds[var].to_masked_array()
# #     masked_array.mask = landmask
# #     masked_array.fill_value = 0
# #     ds[var] = (('time','south_north', 'west_east'), masked_array)
# #     ds[var].attrs['pyproj_srs'] = ds.attrs['pyproj_srs']
# # print("Mask: ", datetime.now() - startTime)

# # startTime = datetime.now()
# # ds = ds.fillna(0)
# # print("Fillnan: ", datetime.now() - startTime)

# # fig = plt.figure(figsize=(12, 6))
# # ax = fig.add_subplot(1, 1, 1)
# # ds['T'].isel(time = 24).salem.quick_map(ax=ax, cmap="coolwarm")


# # test = ds.where(landmask)


# # fig = plt.figure(figsize=(12, 6))
# # ax = fig.add_subplot(1, 1, 1)
# # ds['S'].salem.quick_map(ax=ax, cmap="coolwarm")


# # W = ds['W']
# # W = np.ma.array(W, mask=landmask, fill_value=0)

# # ds['W'] = (('south_north', 'west_east'), W)
# # ds['W'].attrs['pyproj_srs'] = ds['F'].attrs['pyproj_srs']

# # fig = plt.figure(figsize=(12, 6))
# # ax = fig.add_subplot(1, 1, 1)
# # ds['W'].salem.quick_map(ax=ax, cmap="coolwarm")


# # test_ds = salem.open_xr_dataset(str(data_dir)+f"/static/static-vars-{model}-{domain}.nc")


# # test_ds['LAND'].salem.quick_map(cmap = 'terrain')
# # tester = test_ds['LAND'].to_masked_array()


# # result = np.ma.array(ds['F'], mask=tester.mask,) #fill_value=masked_arr.fill_value)
# # ds['result'] = (('south_north', 'west_east'), result)
# # ds['result'].attrs['pyproj_srs'] = ds['F'].attrs['pyproj_srs']
# # fig = plt.figure(figsize=(12, 6))
# # ax = fig.add_subplot(1, 1, 1)
# # ds['result'].salem.quick_map(ax=ax, cmap="coolwarm")

# # grid = grid.astype(bool)


# # # Create a NumPy array with a mask
# # a = np.array([1, 2, 3, 4])
# # mask = np.array([True, False, False, True])

# # # Create a masked array in xarray
# # xa = xr.DataArray(a, dims='dim', coords={'dim': range(len(a))}).to_masked_array()
# # xa.fill_value = 0
# # xa.mask = mask

# # # Print the masked array
# # print(xa)


# # grid = ~grid

# # # Find all 0s next to a 1
# # mask = (grid[:-1, :] == 1) & (grid[1:, :] == 0)
# # mask = np.pad(mask, ((1, 0), (0, 0)), mode='constant', constant_values=False)

# # # Set all masked values to 1
# # grid = np.where(mask, 1, grid)


# # # Convert the binary array to a masked array
# # masked_array = np.ma.masked_where(grid == 1,wrf_ds['F'])


# # ds['F_masked'] = (('south_north', 'west_east'), masked_array)


# # fig = plt.figure(figsize=(12, 6))
# # ax = fig.add_subplot(1, 1, 1)
# # dsr.salem.quick_map(ax=ax, cmap="coolwarm")

# # # test = data * 1000

# # # Print the masked array
# # print(masked_array)


# # # # Create a binary grid
# # # grid = np.array([[1, 0, 0, 1],
# # #                  [0, 0, 1, 0],
# # #                  [1, 1, 0, 1],
# # #                  [1, 0, 0, 0]])
# # # print(grid)

# # # Find all 0s next to a 1
# # # mask = (grid[:-1, :] == 1) & (grid[1:, :] == 0)
# # # mask = np.pad(mask, ((1, 0), (0, 0)), mode='constant', constant_values=False)

# # # # Set all masked values to 1
# # # grid2 = np.where(mask, 0, grid)

# # # # Print the updated grid
# # # print(grid2)


# # # Create a binary grid
# # grid = np.array([[1, 0, 0, 1],
# #                  [0, 0, 1, 0],
# #                  [1, 1, 0, 1],
# #                  [1, 0, 0, 0]])

# # # Find all 0s next to a 1
# # for i in range(0,10):
# #     mask = (grid[:-1, :] == 1) & (grid[1:, :] == 0)
# #     mask = np.pad(mask, ((1, 0), (0, 0)), mode='constant', constant_values=False)

# #     # Set all masked values to 1
# #     grid = np.where(mask, 1, grid)

# #     # Print the updated grid
# #     print(grid)

# # # ds = salem.open_xr_dataset(
# # #     f"/Volumes/WFRT-Ext24/fwf-data/{model}/{domain}/01/fwf-daily-{domain}-{doi.strftime('%Y%m%d%H')}.nc"
# # # )

# # # fig = plt.figure(figsize=(12, 6))
# # # ax = fig.add_subplot(1, 1, 1)
# # # ds.isel(time=0)["D"].salem.quick_map(ax=ax, cmap="coolwarm",vmin =0 , vmax =800)


# # # int_ds = salem.open_xr_dataset(
# # #         f"/Volumes/Scratch/fwf-data/{model}/d02/202108/fwf-hourly-{domain}-2021080106.nc"

# # # )

# # # int_ds = salem.open_xr_dataset(
# # #         f"/Volumes/Scratch/fwf-data/{model}/d02/202108/fwf-daily-{domain}-2021080106.nc"

# # # )

# # # # int_ds = int_ds.isel(time =0)
# # # time_interval = int_ds.Time.values


# # # # Calculate the time delta
# # # if time_interval.size == 1:
# # #     daily_ds = int_ds
# # #     print("This is dataset is a has a daily time step, will solve FWI without finding noon local")
# # # else:
# # #     delta = time_interval[1] - time_interval[0]
# # #     hours = delta.astype('timedelta64[h]')
# # #     print('Time interval in hours:', hours)
# # #     if hours == 1:
# # #         print("This is dataset is a has a hourly time interval, will solve FWI by finding noon local")
# # #     elif hours == 24:
# # #         daily_ds = int_ds
# # #         print("This is dataset is a has a daily time interval, will solve FWI without finding noon local")
# # #     else:
# # #         raise ValueError(f"Sadly this is an incompatible time interval of {hours}. FWF currently only works with hourly or daily time intervals")


# # # from netCDF4 import Dataset
# # # from wrf import (
# # #     getvar,
# # # )

# # # ## open domain config file with variable names and attributes
# # # with open(str(data_dir) + "/json/eccc-config.json") as f:
# # #     econfig = json.load(f)


# # # def solve_TD(ds):
# # #     p = ds["P0"].values  # *.01
# # #     qv = ds["QV"].values
# # #     qv[qv < 0] = 0
# # #     tdc = qv * p / (0.622 + qv)
# # #     td = (243.5 * np.log(tdc) - 440.8) / (19.48 - np.log(tdc))
# # #     ds["TD"] = (("south_north", "west_east"), td)
# # #     return ds


# # # def solve_RH(ds):
# #     TD = ds.TD.values
# #     T = ds.T.values
# #     RH = (
# #         (6.11 * 10 ** (7.5 * (TD / (237.7 + TD))))
# #         / (6.11 * 10 ** (7.5 * (T / (237.7 + T))))
# #         * 100
# #     )
# #     RH = xr.where(RH > 100, 100, RH)
# #     ds["H"] = (("south_north", "west_east"), RH)
# #     if np.min(ds.H) > 90:
# #         raise ValueError("ERROR: Check TD unphysical RH values")
# #     return ds


# # def rename_vars(ds):
# #     var_dict = econfig[domain]
# #     var_list = list(ds)
# #     for key in list(var_dict.keys()):
# #         # Check if the key is not in the list of valid keys
# #         if key not in var_list:
# #             # Remove the key from the dictionary
# #             del var_dict[key]
# #     ds = ds.rename(var_dict)
# #     ds = ds.rename(
# #         {
# #             "rlon": "west_east",
# #             "rlat": "south_north",
# #         }
# #     )
# #     var_list = list(ds)
# #     if "TD" not in var_list:
# #         ds = solve_TD(ds)
# #     if "H" not in var_list:
# #         ds = solve_RH(ds)
# #     if "SNOWH" not in var_list:
# #         ds["SNOWH"] = (("south_north", "west_east"), np.zeros_like(ds["T"].values))
# #     ds = ds.chunk("auto")
# #     return ds


# # startTime = datetime.now()

# # model = "eccc"
# # domain = "hrdps"

# # save_dir = f"/Volumes/WFRT-Ext24/{model}/{domain}/"
# # doi = pd.Timestamp("2022-01-14")
# # i = 20
# # path = (
# #     f'{save_dir}{doi.strftime("%Y%m")}/{doi.strftime("%Y%m%d00")}_{str(i).zfill(2)}.nc'
# # )
# # hrdps_ds = xr.open_dataset(
# #     f'{save_dir}{doi.strftime("%Y%m")}/{doi.strftime("%Y%m%d00")}_{str(i).zfill(2)}.nc'
# # )

# # save_dir1 = f"/Volumes/WFRT-Ext24/{model}/rdps/"
# # path1 = (
# #     f'{save_dir1}{doi.strftime("%Y%m")}/{doi.strftime("%Y%m%d00")}_{str(i).zfill(2)}.nc'
# # )
# # rdps_ds = xr.open_dataset(path1, chunks="auto").isel(height1=0, height2=0, sfctype=0)
# # rdps_ds = rdps_ds.rename(econfig["rdps"])

# # # print(list(hrdps_ds.dims))


# # ds = xr.open_dataset(path, chunks="auto")
# # dim_list = list(ds.dims)
# # dim_dict = {
# #     "time": -1,
# #     "level": 0,
# #     "height1": 0,
# #     "height2": 0,
# #     "sfctype": 0,
# #     "time1": -1,
# #     "time2": -1,
# #     "height": 0,
# # }
# # for key in list(dim_dict.keys()):
# #     # Check if the key is not in the list of valid keys
# #     if key not in dim_list:
# #         # Remove the key from the dictionary
# #         del dim_dict[key]
# # ds = rename_vars(ds.isel(dim_dict))
# # if "time" in list(dim_dict):
# #     ds = ds.assign_coords(time=ds.time.values)
# # elif "time2" in list(dim_dict):
# #     ds = ds.assign_coords(time=ds.time2.values)
# # ds = ds.expand_dims(dim="time")

# # ds


# # ds['SD'] = (("south_north", "west_east"), np.zeros_like(ds["TT"].values))
# # ds = ds.assign_coords(time=ds.time2.values)
# # ds = ds.expand_dims(dim ='time')
# # ds = ds.rename(econfig[domain])

# # df = pd.read_csv(str(data_dir)+f'/{model}/{domain}/check.csv')

# # filtered_df = df.loc[df['good_nc'] == -99]

# # date_range = pd.date_range(f"2021-01-01", f"2021-03-01")
# # # ds = xr.open_dataset(save_dir_i)
# # path_in_str = str(data_dir)+'/wrf/wrfout_d02_2021-01-14_00:00:00'
# # wrf_ds = xr.open_dataset(path_in_str).isel(Time = 0)

# # wrf_file = Dataset(path_in_str, "r")
# # #
# # TD = getvar(wrf_file, "rh2")

# # p = wrf_ds['PSFC'].values*.01
# # qv = wrf_ds['Q2'].values
# # qv[qv < 0] = 0

# # tdc = qv*p/ (0.622+qv)
# # td = (243.5 * np.log(tdc)- 440.8) / (19.48 - np.log(tdc))


# # omp_set_num_threads(8)
# # print(f"read files with {omp_get_max_threads()} threads")
# # startTime = datetime.now()
# # print("begin readwrf: ", str(startTime))

# # path_in_str = str(str(data_dir) + '/wrf/uvic_d01_2020-09-01_07 00 00')
# # print(path_in_str)
# # wrf_file = Dataset(path_in_str, "r")

# # T = getvar(wrf_file, "T2", meta=True) - 273.15
# # TD = getvar(wrf_file, "td2", meta=True, units="degC")
# # # H = getvar(wrf_file, "rh2", meta=True)

# # wsp_wdir = g_uvmet.get_uvmet10_wspd_wdir(wrf_file, units="km h-1")
# # wsp_array = np.array(wsp_wdir[0])
# # wdir_array = np.array(wsp_wdir[1])
# # W = xr.DataArray(wsp_array, name="W", dims=("south_north", "west_east"))
# # WD = xr.DataArray(wdir_array, name="WD", dims=("south_north", "west_east"))
# # U10 = getvar(wrf_file, "U10", meta=True)
# # V10 = getvar(wrf_file, "V10", meta=True)

# # ##varied parameterization scheme to forecast rain..note this is a sum of rain from the starts of the model run
# # rain_c = getvar(wrf_file, "RAINC", meta=True)
# # # rain_sh = getvar(wrf_file, "RAINSH", meta=True)
# # rain_nc = getvar(wrf_file, "RAINNC", meta=True)
# # # r_o_i = rain_c + rain_sh + rain_nc
# # r_o_i = rain_c  + rain_nc

# # r_o = xr.DataArray(r_o_i, name="r_o", dims=("south_north", "west_east"))

# # SNW = getvar(wrf_file, "SNOWNC", meta=True)
# # # SNOWC = getvar(wrf_file, "SNOWC", meta=True)
# # SNOWH = getvar(wrf_file, "SNOWH", meta=True)

# # # var_list = [T, TD, H, W, WD, r_o, SNW, SNOWC, SNOWH, U10, V10]
# # var_list = [T, TD, W, WD, r_o, SNW, SNOWH, U10, V10]
# # ds = xr.merge(var_list)

# # ds_list.append(ds)

# ### Combine xarray and rename to match van wangers defs
# # wrf_ds = xr.combine_nested(ds_list, "time")
# # wrf_ds = ds
# # wrf_ds = wrf_ds.rename_vars({"T2": "T", "td2": "TD", "SNOWNC": "SNW"})
# # # wrf_ds["SNW"] = wrf_ds.SNW - wrf_ds.SNW.isel(time=0)
# # # wrf_ds["r_o"] = wrf_ds.r_o - wrf_ds.r_o.isel(time=0)

# # RH = (
# #     (6.11 * 10 ** (7.5 * (wrf_ds.TD / (237.7 + wrf_ds.TD))))
# #     / (6.11 * 10 ** (7.5 * (wrf_ds.T / (237.7 + wrf_ds.T))))
# #     * 100
# # )
# # RH = xr.where(RH > 100, 100, RH)
# # RH = xr.DataArray(RH, name="H", dims=( "south_north", "west_east"))
# # wrf_ds["H"] = RH
# # if np.min(wrf_ds.H) > 90:
# #     raise ValueError("ERROR: Check TD unphysical RH values")

# # wrf_file = Dataset(str(pathlist[0]), "r")
# # nc_attrs = wrf_file.ncattrs()
# # for nc_attr in nc_attrs:
# #     wrf_ds.attrs[nc_attr] = repr(wrf_file.getncattr(nc_attr))

# # print(list(wrf_ds))
# # if wright == True:
# #     print(wrf_ds)
# #     time = np.array(wrf_ds.Time.dt.strftime("%Y-%m-%dT%H"))
# #     timestamp = datetime.strptime(str(time[0]), "%Y-%m-%dT%H").strftime("%Y%m%d%H")
# #     wrf_ds = wrf_ds.load()
# #     for var in list(wrf_ds):
# #         wrf_ds[var].encoding = {}

# #     wrf_ds_dir = str(save_dir) + str(f"wrfout-{domain}-{timestamp}.nc")
# #     wrf_ds.to_netcdf(wrf_ds_dir, mode="w")
# #     print(f"wrote {wrf_ds_dir}")
# # else:
# #     pass

# # grid_ds = salem.open_xr_dataset(str(data_dir) + f"/wrf/uvic_d01_2020-09-01_07 00 00")
# # grid_ds = grid_ds.copy()[['T2']].sel(Time = 0)

# # wrf_ds.attrs["pyproj_srs"] = grid_ds.attrs["pyproj_srs"]
# # for var in list(wrf_ds):
# #     grid_ds[var] =  wrf_ds[var]
# #     grid_ds[var].attrs["pyproj_srs"] = grid_ds.attrs["pyproj_srs"]
# #     fig = plt.figure(figsize=(12, 6))
# #     ax = fig.add_subplot(1, 1, 1)
# #     grid_ds[f"{var}"].salem.quick_map(
# #         ax=ax, cmap="coolwarm", extend="both"
# #     )
# #     fig.savefig(
# #         str(data_dir) + f'/images/downscale/{var}.png',
# #         dpi=250,
# #         bbox_inches="tight",
# #     )
# # print("readwrf run time: ", datetime.now() - startTime)
