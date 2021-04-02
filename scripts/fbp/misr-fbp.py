import context
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from wrf import ll_to_xy, xy_to_ll

from pylab import *
from datetime import datetime
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

domain = "d02"
wrf_model = "wrf3"
date = pd.Timestamp(2018, 7, 18)

## Open MISR dataframe
misr_path = "/Users/rodell/Google Drive/Shared drives/Research/FireSmoke/BlueSky_Emissions/misr_plumes.csv"
df = pd.read_csv(misr_path)
df["Datetime"] = pd.to_datetime(df["Datetime"])
## drop non 2018 fires
df = df[(df["Datetime"].dt.year == 2018)]

## Open static dataset (contains elevation, fuels type, and time zone mask)
static_ds = xr.open_zarr(
    str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}.zarr"
)

# ## Open FBP dataset
# forecast_date = date.strftime("%Y%m%d06")
# filein = f"/Volumes/cer/fireweather/data/fwf-hourly-{domain}-2018040106-2018100106.zarr"
# fbp_ds = xr.open_zarr(filein)
# # fbp_ds = fbp_ds.drop_vars("FMC")
# fbp_ds["W"].attrs["units"] = "km hr^-1"

### Get a wrf file
if wrf_model == "wrf3":
    wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CP-04/18072000/wrfout_{domain}_2018-07-20_11:00:00"
else:
    wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CG-01/21022000/wrfout_{domain}_2021-02-20_11:00:00"
wrf_file = Dataset(wrf_filein, "r")


wrf_ds = xr.open_dataset(wrf_filein)

LANDMASK = wrf_ds.LANDMASK.values[0, :, :]

FUELS = static_ds.FUELS.values
FUELS_water = np.where((FUELS == 118) | (FUELS == 119) | (FUELS == 120), 0, FUELS)
FUELS_water = np.where(FUELS_water != 0, 1, FUELS_water)

plt.imshow(FUELS_water[::-1])
plt.imshow(LANDMASK[::-1])

test = FUELS_water == LANDMASK

unique, count = np.unique(test, return_counts=True)


test = np.where(LANDMASK == 0)
test2 = np.where(FUELS == 118)
test3 = np.where(FUELS == 120)


## make lats and long of wrf domain to array
lats, lons = fbp_ds.XLAT.values, fbp_ds.XLONG.values
## get shape of domian
shape = lats.shape


## get idex form lat and lon locations of fires
xy_np = ll_to_xy(wrf_file, df["Lat"].values, df["Lon"].values, meta=False)

## add to misr dataframe
df["x"] = xy_np[0]
df["y"] = xy_np[1]
## drop fires out of bonds of model domain
df = df.drop(df.index[np.where((df["x"] <= 0) | (df["y"] <= 0))])
df = df.drop(df.index[np.where((df["x"] > shape[1]) | (df["y"] > shape[0]))])

## print lat/lng for fire in model domain and lat and long ofr miser for santiny check
print(
    f'WRF Lat: {np.round(lats[df["y"].values[0],df["x"].values[0]],3)} WRF Long: {np.round(lons[df["y"].values[0],df["x"].values[0]],3)}'
)
print(
    f'MISR Lat : {float(df["Lat"].values[0])} MISR Long: {float(df["Lon"].values[0])}'
)
print(f'index y: {int(df["y"].values[0])} index x: {int(df["x"].values[0])}')


for var in list(static_ds):
    df[var] = static_ds[var].values[df["y"].values, df["x"].values]

# FUELS = df.FUELS.values
# water = FUELS[FUELS>=118]

misr_times = df["Datetime"].values.astype("datetime64[h]")
model_times = fbp_ds.Time.values.astype("datetime64[h]")

index_list = []
for times in misr_times:
    try:
        index_list.append(int(np.where(model_times == times)[0]))
    except:
        print(times)

# fbp_ds_sliced = fbp_ds[dict(time = index_list, south_north = df["y"].values , west_east = df["x"].values)]
fbp_ds_sliced = fbp_ds.isel(time=index_list)

x, y = df["x"].values, df["y"].values
var_list = list(fbp_ds_sliced)

for var in var_list:
    df[var] = fbp_ds_sliced[var].values[:, y, x][0]

df.to_csv(str(data_dir) + "/test/misr_fbp.csv")


# # ## define coordinates for bundled dataset
# coords = {"fire": df["Fire_MSL"].values, "time": ("fire", fbp_ds_sliced.Time.values)}
# for var in list(df):
#     coords.update({var: ("fire", df[var].values)})

# def make_fire_ds(var, x, y):
#     """
#     Bundels MISR and FBP data into one dataset
#     """
#     var_array = fbp_ds_sliced[var].values[:,y, x][0]
#     var_da = xr.DataArray(var_array, name=var, dims=("fire"), coords=coords)
#     var_da.attrs = fbp_ds_sliced[var].attrs
#     return var_da

# # # ## new dataset with point forecasts of wrf/fwi/fbp at each fire in the misr dataframe
# fire_ds = xr.merge([make_fire_ds(var, x, y) for var in var_list])

# def rechunk(ds):
#     ds = ds.chunk(chunks = 'auto')
#     ds = ds.unify_chunks()
#     for var in list(ds):
#         ds[var].encoding = {}
#     return ds

# fire_ds = rechunk(fire_ds)
# fire_ds.to_zarr(str(data_dir) + "/test/misr_fbp.zarr" )


# plt.plot(HFI)
# ########### Set up ploting stuff  #############
# ## Choose Variabels to plot
# var_list = ["F", "HFI", "ROS", "W"]
# length = len(var_list)

# ## get list of default matplotlib colors
# colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

# ## Define fire...could loop and plot everyone if you wish
# case_ds = fire_ds.isel(fire=3)

# ## Make Fig title
# fig_title = f"Fire: {case_ds.coords['fire'].values} \n Lat, Long: [{case_ds.coords['Lat'].values}, {case_ds.coords['Lon'].values}]"
# ## Make fig adding subplots based on var list length
# fig = plt.figure(figsize=[12, 12])
# fig.suptitle(fig_title, fontsize=12)
# for i in range(length):
#     ax = fig.add_subplot(length + 1, 1, i + 1)
#     var = var_list[i]
#     var_array = case_ds[var].values
#     try:
#         ax.set_ylabel(
#             f"{case_ds[var].attrs['description']} \n ({case_ds[var].attrs['units']})"
#         )
#     except:
#         ax.set_ylabel(f"{case_ds[var].attrs['description']}")
#     ax.yaxis.grid(linewidth=0.4, linestyle="--")
#     ax.xaxis.grid(linewidth=0.4, linestyle="--")
#     ax.plot(case_ds.time, var_array, color=colors[i])
#     ax.axvline(
#         case_ds.coords["Datetime"].values,
#         color="k",
#         linestyle="--",
#         label="MISR OverPass",
#     )
#     if i != length-1:
#         pass
#     else:
#         ax.set_xticks([])


# ax.legend()

# fig.savefig(str(data_dir) + f"/images/MISR-FBP-{domain}-{forecast_date}.png")

# print("Total Run Time: ", datetime.now() - startTime)
