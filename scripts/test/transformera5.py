import context

import salem
import numpy as np
import xarray as xr
import geopandas as gpd
import pandas as pd
from context import data_dir

# era5_ds = salem.open_xr_dataset("/Volumes/WFRT-Data02/era5/era5-2022080500.nc")
# era5_ds = era5_ds.isel(time=1)
# era5_ds["tp"] = era5_ds["tp"]*1000

filein = "/Volumes/WFRT-Data02/era5/era5-2022080500.nc"
wrf_model = "wrf4"
domain = "d02"
doi = pd.Timestamp(f"{filein[-13:-9]}-{filein[-9:-7]}-{filein[-7:-5]}")

era5_ds = salem.open_xr_dataset(filein)
int_time = era5_ds.time.values
tomorrow = pd.to_datetime(str(int_time[0] + np.timedelta64(1, "D")))
era5_ds_tomorrow = salem.open_xr_dataset(
    f'/Volumes/WFRT-Data02/era5/era5-{tomorrow.strftime("%Y%m%d%H")}.nc'
)
era5_ds = xr.merge([era5_ds, era5_ds_tomorrow])

era5_ds = era5_ds.sel(
    time=slice(doi.strftime("%Y%m%dT06"), tomorrow.strftime("%Y%m%dT05"))
)

era5_ds["T"] = era5_ds.t2m - 273.15
era5_ds["TD"] = era5_ds.d2m - 273.15
era5_ds["r_o_hourly"] = era5_ds.tp * 1000
# era5_ds['r_o_hourly'] = xr.where(era5_ds['r_o_hourly'] < 0, 0, era5_ds['r_o_hourly'])

# era5_ds["WD"] = 180 + ((180 / np.pi) * np.arctan2(era5_ds["u10"], era5_ds["v10"]))
era5_ds["SNOWH"] = era5_ds["sd"]
era5_ds["U10"] = era5_ds["u10"]
era5_ds["V10"] = era5_ds["v10"]

keep_vars = [
    "r_o_hourly",
    "SNOWC",
    "SNOWH",
    "SNW",
    "T",
    "TD",
    "U10",
    "V10",
    "W",
    "WD",
    "r_o",
    "H",
]
era5_ds = era5_ds.drop([var for var in list(era5_ds) if var not in keep_vars])

krig_ds = salem.open_xr_dataset(str(data_dir) + "/d02-grid.nc")
fwf_d02_ds = xr.open_dataset(
    f'/Volumes/Scratch/FWF-WAN00CG/d02/{doi.strftime("%Y%m")}/fwf-hourly-d02-{doi.strftime("%Y%m%d06")}.nc'
)
fwf_d02_ds["time"] = ("time", fwf_d02_ds.Time.values)
fwf_d02_ds = fwf_d02_ds.sel(
    time=slice(doi.strftime("%Y%m%dT06"), tomorrow.strftime("%Y%m%dT05"))
)

# krig_ds = fwf_d02_ds.salem.grid.to_dataset()
# krig_ds = krig_ds.rename({'x': 'west_east','y': 'south_north'})
# krig_ds = krig_ds.assign_coords({"XLONG": fwf_d02_ds.XLONG})
# krig_ds = krig_ds.assign_coords({"XLAT": fwf_d02_ds.XLAT})
# print(krig_ds)
# krig_ds.to_netcdf(str(data_dir) +"/d02-grid.nc", mode="w")

era5_ds = krig_ds.salem.transform(era5_ds, interp="spline")
era5_ds = era5_ds.assign_coords(
    {"XLONG": (("south_north", "west_east"), fwf_d02_ds.XLONG.values)}
)
era5_ds = era5_ds.assign_coords(
    {"XLAT": (("south_north", "west_east"), fwf_d02_ds.XLAT.values)}
)

time_array = era5_ds.time.values
era5_ds["time"] = np.arange(0, len(era5_ds.time.values))
era5_ds = era5_ds.assign_coords({"Time": ("time", time_array)})
era5_ds["SNOWC"] = (
    ("time", "south_north", "west_east"),
    fwf_d02_ds["SNOWC"].values,
)
era5_ds["SNOWH"] = (
    ("time", "south_north", "west_east"),
    fwf_d02_ds["SNOWH"].values,
)
era5_ds["SNW"] = (("time", "south_north", "west_east"), fwf_d02_ds["SNW"].values)

era5_ds["r_o_hourly"] = xr.where(era5_ds["r_o_hourly"] < 0, 0, era5_ds["r_o_hourly"])
r_oi = era5_ds["r_o_hourly"].values
r_accumulated_list = []
for i in range(len(era5_ds.time)):
    r_hour = np.sum(r_oi[:i], axis=0)
    r_accumulated_list.append(r_hour)
r_o = np.stack(r_accumulated_list)
r_o = xr.DataArray(r_o, name="r_o", dims=("time", "south_north", "west_east"))
era5_ds["r_o"] = r_o

RH = (
    (6.11 * 10 ** (7.5 * (era5_ds.TD / (237.7 + era5_ds.TD))))
    / (6.11 * 10 ** (7.5 * (era5_ds.T / (237.7 + era5_ds.T))))
    * 100
)
RH = xr.where(RH > 100, 100, RH)
RH = xr.DataArray(RH, name="H", dims=("time", "south_north", "west_east"))
era5_ds["H"] = RH
if np.min(era5_ds.H) > 90:
    raise ValueError("ERROR: Check TD nonphysical RH values")

W = np.sqrt(era5_ds["U10"].values ** 2 + era5_ds["V10"].values ** 2) * 3.6
W = xr.DataArray(W, name="W", dims=("time", "south_north", "west_east"))
era5_ds["W"] = W
era5_ds["WD"] = 180 + ((180 / np.pi) * np.arctan2(era5_ds["U10"], era5_ds["V10"]))

era5_ds.attrs = fwf_d02_ds.attrs
keep_vars = [
    "SNOWC",
    "SNOWH",
    "SNW",
    "T",
    "TD",
    "U10",
    "V10",
    "W",
    "WD",
    "r_o",
    "H",
]
era5_ds = era5_ds.drop([var for var in list(era5_ds) if var not in keep_vars])

# print(f'WIND MIN {float(era5_ds["W"].min())}')
# print(f'RH MIN {float(era5_ds["H"].min())}')
# print(f'RH MAX {float(era5_ds["H"].max())}')
# print(f'WD MIN {float(era5_ds["WD"].min())}')
# print(f'WD MAX {float(era5_ds["WD"].max())}')
# print(f'r_o MIN {float(era5_ds["r_o"].min())}')


# wrfd02_ds = salem.open_xr_dataset(str(data_dir) + f"/wrf/wrfout_d02_2021-01-14_00:00:00")

# fwf_d02_ds = salem.open_xr_dataset(
#     "/Volumes/Scratch/FWF-WAN00CG/d02/202107/fwf-daily-d02-2021070106.nc"
# )
# # fwf_d02_ds = salem.open_wrf_dataset("/Volumes/Scratch/FWF-WAN00CG/d02/202107/fwf-daily-d02-2021070106.nc")
# import matplotlib.pyplot as plt


# test = fwf_d02_ds.salem.transform(era5_ds, interp="spline")

# # test = xr.where(test.isnull(),1000, test )
# fig = plt.figure(figsize=(12, 6))
# ax = fig.add_subplot(1, 1, 1)
# ax.imshow(test.t2m.values[::-1])
# # fig_name = f'temp_wsp({int(da.W.mean())})_rh({int(da.H.mean())})_precip({int(da.r_o.mean())})'
# plt.savefig(f"test.png", dpi=250, bbox_inches="tight")


# # test.t2m.plot()
# # print(test)

# print(np.unique(test.t2m.isnull(), return_counts=True))


# df = era5_ds["tp"].to_dataframe().reset_index()

# wrfd02_ds = salem.open_wrf_dataset(str(data_dir) + f"/wrf/wrfout_d02_2021-01-14_00:00:00")
# tempd02 =  wrfd02_ds.T2.isel(time = 0)

# ## define the desired grid resolution in meters
# resolution = 4_000  # grid cell size in meters

# x0, x1 = float(wrfd02_ds.west_east.min()),  float(wrfd02_ds.west_east.max())
# y0, y1 = float(wrfd02_ds.south_north.min()),  float(wrfd02_ds.south_north.max())

# ## make grid based on dataset bounds and resolution
# gridx = np.arange(x0, x1, resolution)
# gridy = np.arange(y0, y1, resolution)

# ## use salem to create a dataset with the grid.
# krig_ds = salem.Grid(
#     nxny=(len(gridx), len(gridy)),
#     dxdy=(resolution, resolution),
#     x0y0=(x0, y0),
#     proj="+R=6370000 +lat_0=90 +lat_ts=53.25 +lon_0=-110 +no_defs+proj=stere +units=m +x_0=0 +y_0=0",
#     pixel_ref="corner",
# ).to_dataset()
# ## print dataset
# krig_ds

# wrfd02_dsT = krig_ds.salem.transform(tempd02, interp='spline')
# # lon, lat = wrfd02_dsT.salem.grid.ll_coordinates


# wrfd03_ds = salem.open_wrf_dataset(str(data_dir) + f"/wrf/wrfout_d03_2021-01-14_00:00:00")
# tempd03 =  wrfd03_ds.T2.isel(time = 0)

# wrfd03_dsT = krig_ds.salem.transform(tempd03, interp='spline')


# test = xr.where(wrfd03_dsT.notnull(),wrfd03_dsT+10, wrfd02_dsT )

# resolution = 1000
# ## make grid based on dataset bounds and resolution
# gridx = np.arange(x0, x1, resolution)
# gridy = np.arange(y0, y1, resolution)

# ## use salem to create a dataset with the grid.
# krig_ds = salem.Grid(
#     nxny=(len(gridx), len(gridy)),
#     dxdy=(resolution, resolution),
#     x0y0=(x0, y0),
#     proj="+R=6370000 +lat_0=90 +lat_ts=53.25 +lon_0=-110 +no_defs+proj=stere +units=m +x_0=0 +y_0=0",
#     pixel_ref="corner",
# ).to_dataset()
# ## print dataset
# krig_ds


# testT = krig_ds.salem.transform(test, interp='spline')


# # wrfd02_dsT['lon'], wrfd02_dsT['lat'] = lon, lat
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
# #     cmap="Reds",
# # )
# # ax.coastlines()
# # ax.set_extent([-180, -49, 25, 80], crs=ccrs.PlateCarree())
