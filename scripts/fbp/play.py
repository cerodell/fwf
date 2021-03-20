import context
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from wrf import ll_to_xy, xy_to_ll

from pylab import *
import matplotlib.pyplot as plt

from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


domain = "d02"
wrf_model = "wrf3"


## Path to fuel converter spreadsheet
fuel_converter = str(data_dir) + "/fbp/fuel_converter.csv"
fc_df = pd.read_csv(fuel_converter)
fc_df = fc_df.drop_duplicates(subset=["CFFDRS"])
fc_df["Code"] = fc_df["National_FBP_Fueltypes_2014"]
fc_df = fc_df.set_index("CFFDRS")


df = pd.read_csv(str(data_dir) + "/test/misr_fbp.csv")

df_test = df[df["HFI"] > 100000]

# ['Orbit', 'Path', 'Block', 'Lon', 'Lat', 'Perimeter', 'Area',
# 'Num_Hgts', 'Fire_MSL', 'Median_Hgt_AGL', 'Max_Hgt_AGL', 'Std_hgt', 'FRP',
# 'Datetime', 'Biome_Name', 'Biome_Class', 'x', 'y', 'ASPECT', 'FUELS', 'GS',
#  'HGT', 'SAZ', 'ZoneDT', 'ZoneST', 'BUI', 'CFB', 'DSR', 'F', 'FMC', 'H', 'HFI',
#  'ISF', 'ISI', 'ISZ', 'R', 'ROS', 'RSF', 'RSZ', 'S', 'SFC', 'SNOWC', 'SNW', 'T',
#  'TD', 'TFC', 'U10', 'V10', 'W', 'WD', 'm_o', 'r_o', 'r_o_hourly']

plt.scatter(df.R.values, df.ISF.values)

df.ISZ.plot()


unique, count = np.unique(df.FUELS.values, return_counts=True)


## bring in state/prov boundaries
states_provinces = cfeature.NaturalEarthFeature(
    category="cultural",
    name="admin_1_states_provinces_lines",
    scale="50m",
    facecolor="none",
)
## make fig for make with projection
fig = plt.figure(figsize=[16, 8])
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
divider = make_axes_locatable(ax)
ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)
## add map features
ax.gridlines()
ax.add_feature(cfeature.LAND, zorder=1)
ax.add_feature(cfeature.LAKES, zorder=10)
ax.add_feature(cfeature.OCEAN, zorder=10)
ax.add_feature(cfeature.BORDERS, zorder=1)
ax.add_feature(cfeature.COASTLINE, zorder=1)
ax.add_feature(states_provinces, edgecolor="gray", zorder=6)
ax.set_xlabel("Longitude", fontsize=18)
ax.set_ylabel("Latitude", fontsize=18)
## create tick mark labels and style
ax.set_xticks(list(np.arange(-160, -40, 10)), crs=ccrs.PlateCarree())
ax.set_yticks(list(np.arange(30, 80, 10)), crs=ccrs.PlateCarree())
ax.tick_params(axis="both", which="major", labelsize=14)
ax.tick_params(axis="both", which="minor", labelsize=14)

ax.scatter(df_test["Lon"], df_test["Lat"], zorder=10)


# filein = f'/Volumes/cer/fireweather/data/fwf-hourly-{domain}-2018040106-2018100106.zarr'
# ds = xr.open_zarr(filein)

# # filein = f'/Users/rodell/Google Drive/Shared drives/Research/FireSmoke/ZARR_Data/fwf-hourly-{domain}-2018040106-2018100106.nc'
# # ds = xr.open_dataset(filein)


# static_filein = str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}.zarr"
# static_ds = xr.open_zarr(static_filein)
# FUELS = static_ds.FUELS.values.astype(int)

# # fuel_unique, fuel_count = np.unique(FUELS, return_counts = True)
# # fuel_count[fuel_unique == fc_dict["C1"]["Code"]]


# ## Path to fuel converter spreadsheet
# fuel_converter = str(data_dir) + "/fbp/fuel_converter.csv"
# ## Open fuels converter
# fc_df = pd.read_csv(fuel_converter)
# fc_df = fc_df.drop_duplicates(subset=["CFFDRS"])
# fc_df["Code"] = fc_df["National_FBP_Fueltypes_2014"]
# ## set index
# fc_df = fc_df.set_index("CFFDRS")
# fc_dict = fc_df.transpose().to_dict()


# var = 'BUI'
# var_array = ds[var].values
# # var_indexed = var_array[:,FUELS == fc_dict["C2"]["Code"]]
# # index = np.where(FUELS == fc_dict["C2"]["Code"])

# fueltype = list(fc_dict)[:-8]
# for fuel in fueltype:
#     try:
#         print('--------------------------------------')
#         print(f'{fuel} {var} min: {np.min(var_array[:,FUELS == fc_dict[fuel]["Code"]])}')
#         print(f'{fuel} {var} max: {np.max(var_array[:,FUELS == fc_dict[fuel]["Code"]])}')
#         print(f'{fuel} {var} mean: {np.mean(var_array[:,FUELS == fc_dict[fuel]["Code"]])}')
#         print(f'{fuel} {var} median: {np.median(var_array[:,FUELS == fc_dict[fuel]["Code"]])}')
#     except:
#         pass


# static_filein = str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}.zarr"
# static_ds = xr.open_zarr(static_filein)

# keep_list = ['CFB','ROS','TFC','HFI']

# ds_dropped = ds.drop_vars([i for i in list(ds) if i not in keep_list])

# saveout = f'/Users/rodell/Google Drive/Shared drives/Research/FireSmoke/ZARR_Data/fwf-hourly-{domain}-2018040106-2018100106.nc'

# ds_dropped.to_netcdf(saveout)
# filein = f'/Volumes/cer/fireweather/data/fwf-hourly-{domain}-2018040106-2018100106.zarr'

# saveout = f'/Users/rodell/Google Drive/Shared drives/Research/FireSmoke/ZARR_Data/fwf-hourly-{domain}-2018040106-2018100106.zarr'


# test = xr.open_zarr(saveout)

# ds = xr.open_zarr(filein)
# ### Get a wrf file
# if wrf_model == "wrf3":
#     wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CP-04/18072000/wrfout_{domain}_2018-07-20_11:00:00"
# else:
#     wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CG-01/21022000/wrfout_{domain}_2021-02-20_11:00:00"
# wrf_file = Dataset(wrf_filein, "r")

# ## get idex form lat and lon locations of fires
# xy_np = ll_to_xy(wrf_file, 53.2853, -126.2849)
# x = xy_np[0]
# y = xy_np[1]


# ds_case = ds.isel(south_north= y, west_east= x)

# static_ds = static_ds.isel(south_north= y, west_east= x)
# ds_case = ds_case.sel(time=slice('2018-08-10T00', '2018-08-20T00'))


# ds_case.ROS.plot()
