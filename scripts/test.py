import context
import json
import math
import salem
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

from context import data_dir, root_dir
from utils.diagnostic import solve_RH, solve_TD, solve_W_WD, solve_r_o

# from utils.geoutils import get_locs


# ds_2014 = salem.open_wrf_dataset(
#        str(data_dir)+  f"/adda/wrfout_d01_2001-06-30_21_00_00"
#     )


ds = xr.open_zarr(
    "/Volumes/WFRT-Ext21/fwf-data/adda/d01/01/fwf-hourly-d01-2002081100.zarr"
)

# fig = plt.figure(figsize=(12, 6))
# ax = fig.add_subplot(1, 1, 1)
# ds["D"].isel(time = 0).salem.quick_map(ax=ax, cmap="jet",  vmax =500, oceans = True, lakes = True, prov = True, states = True)

fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(1, 1, 1)
ds["S"].isel(time=0).salem.quick_map(
    ax=ax, cmap="jet", vmax=40, oceans=True, lakes=True, prov=True, states=True
)


# ds = xr.open_zarr('/Volumes/WFRT-Ext21/fwf-data/adda/d01/01/2001/fwf-daily-d01-2001041100.zarr')

# fig = plt.figure(figsize=(12, 6))
# ax = fig.add_subplot(1, 1, 1)
# ds["D"].isel(time = 0).salem.quick_map(ax=ax, cmap="jet",  vmax =500, oceans = True)


# ds = xr.open_zarr('/Volumes/WFRT-Ext21/fwf-data/adda/d01/01/fwf-hourly-d01-2001010200.zarr')

# fig = plt.figure(figsize=(12, 6))
# ax = fig.add_subplot(1, 1, 1)
# ds["S"].isel(time = 23).salem.quick_map(ax=ax, cmap="jet", vmax =40)


# static_ds = salem.open_xr_dataset(
#     str(data_dir) + f"/static/static-vars-adda-d01.nc"
# )
# # # print(static_ds)


# fig = plt.figure(figsize=(12, 6))
# ax = fig.add_subplot(1, 1, 1)
# static_ds["ZoneST"].salem.quick_map(ax=ax, cmap="terrain")


# # ds_2014_00 = xr.open_dataset(
# #         f"/Volumes/WFRT-Ext20/2014/cstm_d01_2014-12-31_23_00_00.nc"
# #     )

# ds_2001 = xr.open_dataset(
#         f"/Volumes/ThunderBay/CRodell/ADDA_V2/2001/cstm_d01_2001-12-31_23_00_00.nc"
#     )['precipitation_0m'].isel(time =0 )
# ds_2001.plot()

# ds_2002 = xr.open_dataset(
#         f"/Volumes/ThunderBay/CRodell/ADDA_V2/test/cstm_d01_2002-01-01_00_00_00.nc"
#     )['precipitation_0m'].isel(time =0 )
# ds_2002.plot()
# ds_t2d = xr.open_dataset(
#         f"/Volumes/WFRT-Ext20/td2/2001/TD2_2001-03-26_05.nc"
#     )

# ds_grid = ds.salem.grid.to_dataset()
# rave = xr.open_dataset(
#     "/Volumes/WFRT-Ext24/rave/RAVE-HrlyEmiss-3km_v1r3_blend_s202310080800000_e202310080859590_c202310081002430.nc"
# )


# model = "wrf"
# domain = "d02"
# doi = pd.Timestamp("2021-01-06")
# trial = '01'
# # print(list(xr.open_dataset(f'/Volumes/Scratch/fwf-data/wrf/{domain}/{doi.strftime("%Y%m")}/fwf-hourly-{domain}-{doi.strftime("%Y%m%d06")}.nc')))
# hourly_ds = salem.open_xr_dataset(
#     f'/Volumes/WFRT-EXT24/fwf-data/{model}/{domain}/{trial}/fwf-hourly-{domain}-{doi.strftime("%Y%m%d06")}.nc'
# )

# hourly_ds_old = xr.open_dataset(
#     f'/Volumes/WFRT-EXT24/fwf-data/{model}/{domain}/04/fwf-hourly-{domain}-{doi.strftime("%Y%m%d06")}.nc'
# )
# hourly_ds_old['south_north'] = hourly_ds['south_north']
# hourly_ds_old['west_east'] = hourly_ds['west_east']
# daily_ds = salem.open_xr_dataset(
#     f'/Volumes/WFRT-EXT24/fwf-data/{model}/{domain}/{trial}/fwf-daily-{domain}-{doi.strftime("%Y%m%d06")}.nc'
# )

# x, y  = get_locs(pyproj_srs= daily_ds.attrs['pyproj_srs'], df = None, lat = 40 , lon = -104)

# fig = plt.figure()
# ax = fig.add_subplot(1,1,1)
# ax.plot(hourly_ds['S'].time, hourly_ds['S'].interp(south_north= y, west_east=x), color = 'tab:blue')
# ax.plot(hourly_ds_old['S'].Time, hourly_ds_old['S'].interp(south_north= y, west_east=x), color = 'tab:red')
# # ax.legend()
# fig.autofmt_xdate(rotation=45)

# (hourly_ds['S'] - hourly_ds_old['S']).isel(time = 20).plot()


# daily_cy = salem.open_xr_dataset(
#     f'/Volumes/WFRT-EXT23/fwf-data/{model}/{domain}/{trial}/fwf-daily-{domain}-{doi.strftime("%Y%m%d00")}.nc'
# )
# daily_cy.sel(west_east=slice(-130, -110), south_north=slice(55, 45))[
#     "D"
# ].salem.quick_map(cmap="coolwarm")
# (daily_cy["D"] - daily_ly["D"]).salem.quick_map(cmap="coolwarm", vmin=-500, vmax=500)

# daily_cy["D"].salem.quick_map(vmax=3000)


# daily_cy["F"].salem.quick_map(vmax=101)

# daily = daily.sel(south_north = slice(84, 46))

# era5_ds = salem.open_xr_dataset(f"/Volumes/WFRT-Ext25/ecmwf/era5-land/{doi.strftime('%Y%m')}/era5-land-{doi.strftime('%Y%m%d00')}.nc")

# # filein = f"/Volumes/WFRT-Ext23/{model}/{domain}/"
# if domain == "era5":
#     filein = f"/Volumes/ThunderBay/CRodell/{model}/{domain}/"
# elif domain == "era5-land":
#     filein = f"/Volumes/WFRT-Ext25/{model}/{domain}/"
# # file_list = [
# #     f"{filein}{(doi + pd.Timedelta(days=i)).strftime('%Y%m')}/{domain}-{(doi + pd.Timedelta(days=i)).strftime('%Y%m%d00.nc')}"
# #     for i in range(0, 2)
# # ]

# date_range = pd.date_range(doi, doi + pd.Timedelta(days=1))

# def era5_land(doi):
#   file_yesterday = f"{filein}{(doi + pd.Timedelta(days=-1)).strftime('%Y%m')}/{domain}-{(doi + pd.Timedelta(days=-1)).strftime('%Y%m%d00.nc')}"
#   file = f"{filein}{(doi).strftime('%Y%m')}/{domain}-{(doi).strftime('%Y%m%d00.nc')}"

#   ds_yesterday = xr.open_dataset(file_yesterday).isel(time = 23).chunk("auto")
#   ds = xr.open_dataset(file).chunk("auto")
#   ds['tp'][0] = ds['tp'][0] - ds_yesterday['tp'].values
#   old_tp = ds['tp']
#   r_oi = np.array(ds['tp'])
#   r_o_plus1 = np.dstack((np.zeros_like(ds['tp'][0]).T, r_oi.T)).T
#   r_hourly_list = []
#   for i in range(len(ds.time)):
#       r_hour = r_oi[i] - r_o_plus1[i]
#       r_hourly_list.append(r_hour)
#   r_hourly = np.stack(r_hourly_list)
#   r_hourly = xr.DataArray(
#       r_hourly, name="tp", dims=("time", "latitude", "longitude")
#   )
#   ds["tp"] = r_hourly
#   return ds


# ds = xr.combine_nested(
#             [era5_land(date) for date in date_range],
#             concat_dim="time",
#             ).chunk("auto")
# # ds = xr.open_mfdataset(file_list)
# # print(ds)
# try:
#     ds = ds.isel(expver=0)
# except:
#     pass
# ds["t2m"] = ds["t2m"] - 273.15
# ds["d2m"] = ds["d2m"] - 273.15
# ds["tp"] = ds["tp"] * 1000
# # ds = formate(ds, model, domain)
# # ds["W"] = ds["W"] * 3.6
# # ds = ds.isel(time=slice(0, 36))
# # if domain == "era5":
# #     ds = ds.roll(west_east=int(len(ds["west_east"]) / 2))


# with open(str(root_dir) + "/json/rename.json") as f:
#     rename = json.load(f)
# var_dict = rename[domain]
# ds = ds.rename(var_dict["dims"])

# domain_grid = xr.open_dataset(str(data_dir) + f"/{model}/{domain}-grid.nc")

# ds["south_north"] = domain_grid["south_north"]
# ds["west_east"] = domain_grid["west_east"]
# ds["XLAT"] = (("south_north", "west_east"), domain_grid["XLAT"].values)
# ds["XLONG"] = (("south_north", "west_east"), domain_grid["XLONG"].values)
# ds = ds.assign_coords({"Time": ("time", ds.time.values)})
# ds = ds.set_coords(["XLAT", "XLONG"])
# ds["time"] = np.arange(0, len(ds.time.values))

# var_list = list(ds)
# for key in list(var_dict.keys()):
#     # Check if the key is not in the list of valid keys
#     if key not in var_list:
#         # Remove the key from the dictionary
#         del var_dict[key]
# ds = ds.rename(var_dict)
# var_list = list(ds)
# if "TD" not in var_list:
#     ds = solve_TD(ds)
# if "H" not in var_list:
#     ds = solve_RH(ds)
# if "WD" not in var_list:
#     ds = solve_W_WD(ds)
# if "SNOWH" not in var_list:
#     ds["SNOWH"] = ds["T"] * 0
# if "r_o" not in var_list:
#     ds = solve_r_o(ds)


# keep_vars = ["SNOWH", "r_o", "T", "TD", "U10", "V10", "H", "QV", "W", "WD"]
# ds = ds.drop([var for var in list(ds) if var not in keep_vars])
# ds.attrs["pyproj_srs"] = domain_grid.attrs["pyproj_srs"]

# ds["W"] = ds["W"] * 3.6
# ds = ds.isel(time=slice(0, 36))
# if domain == "era5":
#     ds = ds.roll(west_east=int(len(ds["west_east"]) / 2))

# (ds['r_o'][1] - ds['r_o'][2]).plot()


# daily_ds = salem.open_xr_dataset("/Volumes/WFRT-Ext22/fwf-data/ecmwf/era5/02/fwf-daily-era5-2022081600.nc")
# daily_ds =daily_ds.sel(south_north = slice(daily.south_north.max(), daily.south_north.min()), west_east = slice(daily.west_east.min(), daily.west_east.max()))
# daily_ds['D'].salem.quick_map(vmax = 600)
# daily_ds['P'].salem.quick_map(vmax = 60)


# static_ds = salem.open_xr_dataset(
#       str(data_dir) + f"/static/static-vars-{model.lower()}-{domain}.nc"
#   )
# print(test)
# copy = test.isel(time=slice(24,55))
# copy.attrs['START_DATE'] = "'2023-02-20_00:00:00'"
# copy.attrs['SIMULATION_START_DATE'] = "'2023-02-20_00:00:00'"
# print(copy)
# doi = pd.Timestamp('2023-02-20')
# copy.to_netcdf(f'/Volumes/WFRT-EXT23/fwf-data/{model}/{domain}/{doi.strftime("%Y%m")}/fwf-hourly-{domain}-{doi.strftime("%Y%m%d06")}.nc')


# doi = pd.Timestamp('2023-01-01')
# scratch = xr.open_dataset(f'/Volumes/Scratch/fwf-data/wrf/{domain}/{doi.strftime("%Y%m")}/fwf-hourly-{domain}-{doi.strftime("%Y%m%d06")}.nc')

# doi = pd.Timestamp('2021-01-01')
# EXT24 = salem.open_xr_dataset(f'/Volumes/WFRT-EXT24/fwf-data/{model}/{domain}/04/fwf-hourly-{domain}-{doi.strftime("%Y%m%d06")}.nc')


# doi = pd.Timestamp('2023-01-11')
# test4 = xr.open_dataset(f'/Volumes/WFRT-EXT24/fwf-data/{model}/{domain}/04/fwf-hourly-{domain}-{doi.strftime("%Y%m%d06")}.nc')

# static_ds = xr.open_dataset(
#       str(data_dir) + f"/static/static-vars-{model.lower()}-{domain}.nc"
#   )
# grid_ds = salem.open_xr_dataset(str(data_dir) + f"/wrf/{domain}-grid.nc")


# hourly_ds = hourly_ds[['F',
#  'm_o',
#  'T',
#  'TD',
#  'W',
#  'WD',
#  'r_o',
#  'SNW',
#  'SNOWC',
#  'SNOWH',
#  'U10',
#  'V10',
#  'H',
#  'r_o_hourly',
#  'R',
#  'S',]]

# for var in list(hourly_ds):
#   print(var)
#   hourly_ds[var].transpose('time', 'south_north', 'west_east')

# hourly_ds = hourly_ds.transpose('time', 'south_north', 'west_east')

# # daily_ds.isel(time =0)['h16S'].salem.quick_map(oceans=True, cmap = 'jet', vmin = 0, vmax =30)
# # daily_ds.isel(time =0)['S'].salem.quick_map(oceans=True, cmap = 'jet', vmin = 0, vmax =30)

# # daily_ds['diff'] = daily_ds.isel(time =0)['S'] - daily_ds.isel(time =0)['h16S']
# # daily_ds['diff'].attrs =  daily_ds['S'].attrs
# # daily_ds['diff'].salem.quick_map(oceans=True, cmap = 'coolwarm', vmin = -10, vmax =10)
# # U = 30
# # B = 1.49e-11
# # L = 500 * 1000
# # L_r = 1000

# # c = U - ((B * (L ** 2)) / (4 * np.pi ** 2))
# # print(c)

# # c = U - (B / (np.pi ** 2 * ((4 / L ** 2) + (1 / L_r ** 2))))
# # print(c)


# # P2 = 50
# # P1 = 100
# # T = 273.15
# # r = 10 / 1000
# # Tv = T * (1 + 0.61 * r)
# # a = 29.3

# # z = a * Tv * np.log(P1 / P2)
# # print(z, " m")


# # T = 35 + 273.15
# # a = 0.61
# # r = 30 / 1000
# # rL = 0
# # ri = 0

# # Tv = T * (1 + (a * r) - rL - ri)

# # print("Tv ", Tv - 273.15)


# # fc = 1.45e-4 * np.sin()

# # IVP = (tilr + fc) / rho * ()
