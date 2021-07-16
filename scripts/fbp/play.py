import context
import json
import salem
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
from affine import Affine
from pathlib import Path
from netCDF4 import Dataset
from osgeo import osr, gdal, ogr

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.ndimage as ndimage
from scipy.ndimage.filters import gaussian_filter

from context import data_dir, wrf_dir, vol_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))


filein = (
    "/Volumes/cer/fireweather/data/FWF-WAN00CP-04-OG/fwf-hourly-d02-2018040106.zarr"
)

ds = xr.open_zarr(filein)

ds1 = ds.isel(time=54)
ds1.HFI.plot()

filein = "/Volumes/cer/fireweather/data/FWF-WAN00CP-04-OG/fwf-hourly-d02-2018040106-test.zarr"

ds = xr.open_zarr(filein)

ds1 = ds.isel(time=54)
ds1.HFI.plot()
## Choose wrf domain
domain = "d02"
wrf_model = "wrf4"

save_zarr = str(data_dir) + f"/fbp/fuels-{wrf_model}-{domain}-2019.zarr"
## Path to Fuel converter spreadsheet
fuel_converter = str(data_dir) + "/fbp/fuel_converter_dev.csv"
## Path to any wrf file used in transformation
if wrf_model == "wrf3":
    wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CP-04/18093000/wrfout_{domain}_2018-10-02_11:00:00"
else:
    wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CG-01/21022000/wrfout_{domain}_2021-02-20_11:00:00"

## Path to 2019 nrcan fuels data tif
# CFL_filein = str(vol_dir) + f"/fuels/resampled/{domain}/CFL.tif"

## Path to 2016 land fire US fuels data tif
CBH_filein = str(vol_dir) + f"/fuels/resampled/{domain}/CBH.tif"
# CBH_filein = (
#     str(vol_dir) + "/fuels/can_fuels2019b/CBH_m_p.tif"
# )

## Path to 2016 land fire US fuels data tif
us_CBH_filein = str(vol_dir) + f"/fuels/resampled/{domain}/us_CBH.tif"
# us_CBH_filein = (
#     str(vol_dir) + "/fuels/LF2020_CBH_200_CONUS/Tif/LC20_CBH_200.tif"
# )

## Open all files mentioned above
fc_df = pd.read_csv(fuel_converter)
wrf_ds = salem.open_xr_dataset(wrf_filein)
XLONG, XLAT = wrf_ds.XLONG.values[0], wrf_ds.XLAT.values[0]

# CFL_tiff = salem.open_xr_dataset(CFL_filein)
CBH_tiff = salem.open_xr_dataset(CBH_filein)
us_CBH_tiff = salem.open_xr_dataset(us_CBH_filein)


## Using nearest neighbor transformation tif to wrf domain
# CFL_ds = wrf_ds.salem.transform(CFL_tiff)
CBH_ds = wrf_ds.salem.transform(CBH_tiff)
us_CBH_ds = wrf_ds.salem.transform(us_CBH_tiff)


# CFL_ds['data'] = xr.where(CFL_ds['data']<0, 0, CFL_ds['data'])
CBH_ds["data"] = xr.where(CBH_ds["data"] < 0, np.nan, CBH_ds["data"])
us_CBH_ds["data"] = xr.where(us_CBH_ds["data"] < 0, np.nan, us_CBH_ds["data"])


CBH = CBH_ds["data"].values * 0.1
us_CBH = us_CBH_ds["data"].values * 0.1

ind = np.isnan(CBH)
CBH[ind] = us_CBH[ind]

## loop all tiffs of AK to gridded adn mask fuels type tag to be the same as CFFDRS
folders = ["%.2d" % i for i in range(1, 21)]
print(folders)
for folder in folders:
    ak_filein = str(vol_dir) + f"/fuels/resampled/{domain}/ak_{folder}_CBH.tif"
    ak_tiff = salem.open_xr_dataset(ak_filein)
    ak_ds = wrf_ds.salem.transform(ak_tiff, ks=1)
    ak_ds["data"] = xr.where(ak_ds["data"] < 0, np.nan, ak_ds["data"])
    ak_array = ak_ds.data.values * 0.1
    ind = np.isnan(CBH)
    CBH[ind] = ak_array[ind]

p = plt.pcolormesh(XLONG, XLAT, CBH)
plt.colorbar(p)
plt.show()


# def getunique(array):
#     unique, count = np.unique(array[~np.isnan(array)], return_counts=True)
#     unique = np.unique(array[~np.isnan(array)]).astype(int)
#     return unique, count

# cfl_unique, cfl_count = getunique(CFL_ds.data.values)
# cbh_unique, cbh_count = getunique(CBH_ds.data.values)

# ## with converter US fuels in CFFDRS mask and replace location of missing data that use array can fill
# fbp2019 = np.array(fbp2019_ds.data)
# fbp_unique, fbp_count = getunique(fbp2019)
# for i in range(len(fc_df.National_FBP_Fueltypes_2019.values)):
#     if fc_df.National_FBP_Fueltypes_2019[i] == -99:
#         pass
#     else:
#         fbp2019[fbp2019 == fc_df.National_FBP_Fueltypes_2019[i]] = fc_df.FWF_Code[i]
# fbp2019_unique_new, fbp2019_count_new = getunique(fbp2019)

# fbp2019[fbp2019 == 0] = np.nan
# fbp2019[fbp2019 == 65535] = np.nan


# ## take US Anderson 13 fuel valsue and convert to CFFDRS fuel types
# us_array = us_ds.values
# us_array_og = us_array

# us_unique, us_count = getunique(us_array_og)
# ## Ensure ponderosa fuel types carry over
# mask = np.where((XLONG < -100) & (us_array_og == 9))

# us_count[us_unique == 9]
# for i in range(len(fc_df.LF_16.values)):
#     if fc_df.LF_16[i] == -99:
#         pass
#     else:
#         us_array[us_array == float(fc_df.LF_16[i])] = fc_df.FWF_Code[i]
#         # if fc_df.LF_16[i] == 6:
#         #     us_array[us_array == fc_df.LF_16[i]] = fc_df.FWF_Code[i]
#         #     us_array = np.where((XLONG < -96) & (us_array == fc_df.FWF_Code[i]), 3, us_array)
#         # else:
#         #     us_array[us_array == fc_df.LF_16[i]] = fc_df.FWF_Code[i]

# us_array = np.where((XLONG > -120) & (us_array == 5), 3, us_array)
# us_array = np.where((XLONG < -96) & (us_array == 11), 3, us_array)
# us_array[mask] = 7


# # XLAT = XLAT.ravel()
# # XLONG = XLONG.ravel()
# # us_array = us_array.ravel()
# # mask = list(np.where((XLAT< 49.0) & (XLONG < -100)  & (us_array == 3))[0])
# # us_array[mask] = np.random.choice([3,3,3,3,3,3,3,3,7],len(mask))
# # us_array = np.reshape(us_array, us_array_og.shape)

# us_unique_new, us_count_new = getunique(us_array)

# ind = np.isnan(fbp2019)
# fbp2019[ind] = us_array[ind]


# ## loop all tiffs of AK to gridded adn mask fuels type tag to be the same as CFFDRS
# folders = ["%.2d" % i for i in range(1, 21)]
# print(folders)
# for folder in folders:
#     ak_filein = str(vol_dir) + f"/fuels/resampled/{domain}/ak_{folder}.tif"
#     ak_tiff = salem.open_xr_dataset(ak_filein)
#     ak_ds = wrf_ds.salem.transform(ak_tiff.data, ks=1)
#     ak_array = ak_ds.values
#     for i in range(len(fc_df.AK_Fuels.values)):
#         if fc_df.AK_Fuels[i] == -99:
#             pass
#         else:
#             ak_array[ak_array == fc_df.AK_Fuels[i]] = fc_df.FWF_Code[i]

#     ind = np.isnan(fbp2019)
#     fbp2019[ind] = ak_array[ind]

# fbp_unique, fbp_count = getunique(fbp2019)

# ## concidered remianing missing data to be water
# ind = np.isnan(fbp2019)
# fbp2019[np.isnan(fbp2019)] = 17


# ## make dataset add coordinates and write to zarr file
# fuels_ds = xr.DataArray(fbp2019, name="fuels", dims=("south_north", "west_east"))
# T2 = wrf_ds.T2
# fuels_ds = xr.merge([fuels_ds, T2])
# fuels_ds = fuels_ds.drop_vars("T2")
# fuels_final = fuels_ds.isel(Time=0)
# fuels_final.to_zarr(save_zarr, mode="w")

# ### Timer
# print("Total Run Time: ", datetime.now() - startTime)
