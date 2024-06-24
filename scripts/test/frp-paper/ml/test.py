#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import salem
import numpy as np
import pandas as pd
import xarray as xr
from utils.geoutils import make_KDtree
from utils.frp import set_axis_postion_full_fwx

from utils.solar_hour import get_solar_hours
import matplotlib.dates as mdates


import matplotlib.pyplot as plt

from context import data_dir


ds = xr.open_dataset("/Volumes/ThunderBay/CRodell/fires/2023-26564768.nc")
ds_mean = ds.mean(("x", "y")).dropna("time").compute()

ds_data = xr.open_dataset(
    "/Users/crodell/fwf/data/ml-data/training-data/2023-fires-averaged-v4.nc"
)

df = ds_data.to_dataframe().reset_index()


test = ds_data.isel(time=np.where(ds_data["id"] == 26564768)[0])
from scipy.ndimage import gaussian_filter1d

y = test["U"].values[:72]
x = test.time.values[:72]
sigma = 1
y_smooth_gaussian = gaussian_filter1d(y, sigma=sigma)

# Plot the original and smoothed data
plt.figure(figsize=(10, 6))
plt.plot(x, y, label="Original Data")
plt.plot(x, y_smooth_gaussian, label="Gaussian Smoothing", color="purple")
plt.title("Gaussian Smoothing")
plt.xlabel("X")
plt.ylabel("Y")
plt.legend()
plt.show()


ds = xr.open_zarr(
    "/Volumes/WFRT-Ext21/fwf-data/adda/d01/01/fwf-hourly-d01-2004010100.zarr"
)

doi = pd.Timestamp("2023-06-06")
domain = "d02"


static_ds = salem.open_xr_dataset(str(data_dir) + f"/static/static-vars-wrf-d02.nc")


def open_fwf(doi, domain):

    fwf_dir = "/Volumes/WFRT-Ext24/fwf-data/wrf/"
    static = salem.open_xr_dataset(
        str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
    )
    fwf_hourly = xr.open_dataset(
        f"{fwf_dir}/{domain}/04/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc"
    ).chunk("auto")
    print(list(fwf_hourly))
    fwf_hourly = fwf_hourly  # [['S', 'R', 'SNOWC', 'r_o', 'F']]
    fwf_hourly["time"] = fwf_hourly["Time"]
    fwf_daily = (
        xr.open_dataset(
            f"{fwf_dir}/{domain}/04/fwf-daily-{domain}-{doi.strftime('%Y%m%d06')}.nc"
        )["U"]
        .to_dataset()
        .chunk("auto")
    )
    fwf_daily["time"] = fwf_daily["Time"]
    fwf_hourly["U"] = fwf_daily["U"].reindex(time=fwf_hourly.Time, method="ffill")
    fwf_hourly["west_east"] = static["west_east"]
    fwf_hourly["south_north"] = static["south_north"]
    for var in list(fwf_hourly):
        fwf_hourly[var].attrs = static.attrs
    fwf_hourly.attrs = static.attrs
    del static
    return fwf_hourly


def open_fuels(moi):
    fuel_dir = f"/Volumes/WFRT-Ext23/fuel-characteristics/fuel-load/"
    fuels_ds = salem.open_xr_dataset(
        fuel_dir + f'{2021}/CFUEL_timemean_2021{moi.strftime("_%m")}.nc'
    ).sel(lat=slice(90, 10), lon=slice(-180, -30))
    fuels_ds.coords["time"] = moi
    return fuels_ds


fwf_ds = open_fwf(doi, domain)  # .isel(time = slice(0,24))
fuel_date_range = pd.date_range(
    fwf_ds["Time"].values[0],
    fwf_ds["Time"].values[-1],
    freq="MS",
)
if len(fuel_date_range) == 0:
    fuel_date_range = [pd.Timestamp(fwf_ds["Time"].values[0])]
fuels_ds = xr.combine_nested(
    [open_fuels(moi) for moi in fuel_date_range], concat_dim="time"
)

fuels_ds = fwf_ds.salem.transform(fuels_ds, interp="linear").reindex(
    time=fwf_ds.Time, method="ffill"
)
for var in list(fuels_ds):
    fwf_ds[var] = fuels_ds[var]


fwf_ds = get_solar_hours(fwf_ds)
# hour_sin = np.sin(2 * np.pi * fwf_ds["solar_hour"] / 24)
# hour_cos = np.cos(2 * np.pi * fwf_ds["solar_hour"] / 24)

# %%
# Define the phase shift for the sine function to peak at 16:00
phi_sin = -np.pi
# Compute hour_sin and hour_cos with the phase shift
fwf_ds["hour_sin"] = np.sin((2 * np.pi * fwf_ds["solar_hour"] / 24) + phi_sin)
fwf_ds["hour_cos"] = np.cos((2 * np.pi * fwf_ds["solar_hour"] / 24) + phi_sin)
# fwf_ds['hour_sin'] = np.sin(2 * np.pi * fwf_ds["solar_hour"] / 24)
# fwf_ds['hour_cos'] = np.cos(2 * np.pi * fwf_ds["solar_hour"] / 24)

fwf_ds["R_hour_sin_Live_Wood"] = fwf_ds["hour_sin"] * fwf_ds["R"] * fwf_ds["Live_Wood"]
fwf_ds["R_hour_cos_Live_Wood"] = fwf_ds["hour_cos"] * fwf_ds["R"] * fwf_ds["Live_Wood"]
fwf_ds["R_hour_sin_Dead_Wood"] = fwf_ds["hour_sin"] * fwf_ds["R"] * fwf_ds["Dead_Wood"]
fwf_ds["R_hour_cos_Dead_Wood"] = fwf_ds["hour_cos"] * fwf_ds["R"] * fwf_ds["Dead_Wood"]
fwf_ds["R_hour_sin_Live_Leaf"] = fwf_ds["hour_sin"] * fwf_ds["R"] * fwf_ds["Live_Leaf"]
fwf_ds["R_hour_cos_Live_Leaf"] = fwf_ds["hour_cos"] * fwf_ds["R"] * fwf_ds["Live_Leaf"]
fwf_ds["R_hour_sin_Dead_Foliage"] = (
    fwf_ds["hour_sin"] * fwf_ds["R"] * fwf_ds["Dead_Foliage"]
)
fwf_ds["R_hour_cos_Dead_Foliage"] = (
    fwf_ds["hour_cos"] * fwf_ds["R"] * fwf_ds["Dead_Foliage"]
)

# fwf_ds["U_Dead_Wood"] = fwf_ds["Dead_Wood"] * fwf_ds["U"]
# fwf_ds["U_Live_Wood"] = fwf_ds["Live_Wood"] * fwf_ds["U"]
# fwf_ds["U_Live_Leaf"] = fwf_ds["Live_Leaf"] * fwf_ds["U"]
# fwf_ds["U_Dead_Foliage"] = fwf_ds["Dead_Foliage"] * fwf_ds["U"]

lat_sin = np.sin(np.radians(fwf_ds.XLAT.values))
lat_cos = np.cos(np.radians(fwf_ds.XLAT.values))

lon_sin = np.sin(np.radians(fwf_ds.XLONG.values))
lon_cos = np.cos(np.radians(fwf_ds.XLONG.values))

fwf_ds["lat_sin"] = (("south_north", "west_east"), lat_sin)
fwf_ds["lat_cos"] = (("south_north", "west_east"), lat_cos)

fwf_ds["lon_sin"] = (("south_north", "west_east"), lon_sin)
fwf_ds["lon_cos"] = (("south_north", "west_east"), lon_cos)


fwf_ds["U_lat_sin_Live_Wood"] = fwf_ds["U"] * lat_sin * fwf_ds["Live_Wood"]
fwf_ds["U_lat_cos_Live_Wood"] = fwf_ds["U"] * lat_cos * fwf_ds["Live_Wood"]
fwf_ds["U_lat_sin_Dead_Wood"] = fwf_ds["U"] * lat_sin * fwf_ds["Dead_Wood"]
fwf_ds["U_lat_cos_Dead_Wood"] = fwf_ds["U"] * lat_cos * fwf_ds["Dead_Wood"]
fwf_ds["U_lat_sin_Live_Leaf"] = fwf_ds["U"] * lat_sin * fwf_ds["Live_Leaf"]
fwf_ds["U_lat_cos_Live_Leaf"] = fwf_ds["U"] * lat_cos * fwf_ds["Live_Leaf"]
fwf_ds["U_lat_sin_Dead_Foliage"] = fwf_ds["U"] * lat_sin * fwf_ds["Dead_Foliage"]
fwf_ds["U_lat_cos_Dead_Foliage"] = fwf_ds["U"] * lat_cos * fwf_ds["Dead_Foliage"]

fwf_ds["U_lon_sin_Live_Wood"] = fwf_ds["U"] * lon_sin * fwf_ds["Live_Wood"]
fwf_ds["U_lon_cos_Live_Wood"] = fwf_ds["U"] * lon_cos * fwf_ds["Live_Wood"]
fwf_ds["U_lon_sin_Dead_Wood"] = fwf_ds["U"] * lon_sin * fwf_ds["Dead_Wood"]
fwf_ds["U_lon_cos_Dead_Wood"] = fwf_ds["U"] * lon_cos * fwf_ds["Dead_Wood"]
fwf_ds["U_lon_sin_Live_Leaf"] = fwf_ds["U"] * lon_sin * fwf_ds["Live_Leaf"]
fwf_ds["U_lon_cos_Live_Leaf"] = fwf_ds["U"] * lon_cos * fwf_ds["Live_Leaf"]
fwf_ds["U_lon_sin_Dead_Foliage"] = fwf_ds["U"] * lon_sin * fwf_ds["Dead_Foliage"]
fwf_ds["U_lon_cos_Dead_Foliage"] = fwf_ds["U"] * lon_cos * fwf_ds["Dead_Foliage"]


moi = int(pd.Timestamp(fwf_ds["Time"].values[0]).strftime("%m")) - 1
fuels_ds = (
    salem.open_xr_dataset(f"{data_dir}/fuel-load/fuels_2021_wrf_{domain}.nc")
    .isel(month=moi)
    .drop_vars("month")
)
time_coords = fwf_ds["Time"].values
fuels_ds = fuels_ds.expand_dims(time=[time_coords[0]])
fuels_ds = fuels_ds.reindex(time=time_coords, method="ffill")
for var in list(fuels_ds):
    fwf_ds[var] = (("time", "south_north", "west_east"), fuels_ds[var].values)


for var in list(fwf_ds):
    fwf_ds[var].attrs = static_ds.attrs
fwf_ds.attrs = static_ds.attrs

y, x = make_KDtree(27.92145, -81.09624, static_ds)
# y, x = make_KDtree(49.01554,-76.43027, static_ds)
# y, x = make_KDtree(57.47797,-121.16833, static_ds)


ds_i = fwf_ds.isel(west_east=x, south_north=y, time=slice(0, 48))
static_i = static_ds.isel(west_east=x, south_north=y)
ds_i["time"] = ds_i["Time"] - pd.Timedelta(int(static_i["ZoneST"]), "hour")

# %%
fig = plt.figure(figsize=(12, 4))
hs = fig.add_subplot(1, 1, 1)
isi = hs.twinx()
isi_hs = hs.twinx()
ds_i["hour_sin"].plot(ax=hs, color="tab:blue")
set_axis_postion_full_fwx(hs, "left", 0, "Sin(Solar Hour)")
hs.set_title("")

ds_i["R"].plot(ax=isi, color="tab:green")
set_axis_postion_full_fwx(isi, "right", 0, "ISI")
isi.set_title("")


ds_i["R_hour_sin_Live_Wood"].plot(ax=isi_hs, color="tab:red")
set_axis_postion_full_fwx(isi_hs, "left", 120, "ISI x Sin(Solar Hour) \n x Live Wood")
y_min, y_max = isi_hs.get_ylim()
if abs(y_min) > abs(y_max):
    higher_abs_value = abs(y_min)
else:
    higher_abs_value = abs(y_max)
isi_hs.set_ylim(-higher_abs_value, higher_abs_value)
isi_hs.set_title("Feature Engineering")
hs.xaxis.set_major_formatter(mdates.DateFormatter("%H"))
hs.set_xlabel("Local Hour")
fig.tight_layout()

plt.savefig(
    str(data_dir) + "/images/frp-paper/feature-eng-time-isi-hour-sin.png", dpi=250
)


# %%
fig = plt.figure(figsize=(12, 4))
hs = fig.add_subplot(1, 1, 1)
isi = hs.twinx()
isi_hs = hs.twinx()

ds_i["hour_cos"].plot(ax=hs, color="tab:blue")
set_axis_postion_full_fwx(hs, "left", 0, "Cos(Solar Hour)")
hs.set_title("")

ds_i["R"].plot(ax=isi, color="tab:green")
set_axis_postion_full_fwx(isi, "right", 0, "ISI")
isi.set_title("")

ds_i["R_hour_cos_Live_Wood"].plot(ax=isi_hs, color="tab:red")
set_axis_postion_full_fwx(isi_hs, "left", 120, "ISI x Cos(Solar Hour) \n x Live Wood")
y_min, y_max = isi_hs.get_ylim()
if abs(y_min) > abs(y_max):
    higher_abs_value = abs(y_min)
else:
    higher_abs_value = abs(y_max)
isi_hs.set_ylim(-higher_abs_value, higher_abs_value)
isi_hs.set_title("Feature Engineering")
hs.xaxis.set_major_formatter(mdates.DateFormatter("%H"))
hs.set_xlabel("Local Hour")
fig.tight_layout()
plt.savefig(
    str(data_dir) + "/images/frp-paper/feature-eng-time-isi-hour-cos.png", dpi=250
)

# %%


# ds_space = fwf_ds.isel(time = 18)

# #%%
# fig = plt.figure(figsize=(16, 10))
# cmap = 'jet'
# ax = fig.add_subplot(2, 2, 1)
# ds_space['U_lat_sin_Live_Wood'].salem.quick_map(oceans = True, lakes = True, ax=ax, vmax = 800, cmap =cmap)
# ax.set_title("BUI x Sin(Latitude) x Live Wood Fuel Load")

# ax = fig.add_subplot(2, 2, 2)
# ds_space['U'].salem.quick_map(oceans = True, lakes = True, ax=ax, vmax = 200, cmap =cmap)
# ax.set_title("BUI")

# ax = fig.add_subplot(2, 2, 3)
# ds_space['lat_sin'].salem.quick_map(oceans = True, lakes = True, ax=ax, cmap =cmap)
# ax.set_title("Sin(Latitude)")

# ax = fig.add_subplot(2, 2, 4)
# ds_space['Live_Wood'].salem.quick_map(oceans = True, lakes = True, ax=ax, vmax = 20, cmap =cmap)
# ax.set_title(r"Live Wood Fuel Load ($kg$ $m^{-2}$)")
# fig.tight_layout()
# # plt.savefig(str(data_dir) + '/images/frp-paper/feature-eng-map-bui-lat-sin-load.png', dpi = 250)


# # # %%
# # fig = plt.figure(figsize=(16, 10))
# # cmap = 'jet'
# # ax = fig.add_subplot(2, 2, 1)
# # ds_space['U_lat_cos_Live_Wood'].salem.quick_map(oceans = True, lakes = True, ax=ax, vmax = 800, cmap =cmap)
# # ax.set_title("BUI x Cos(Latitude) x Live Wood Fuel Load")

# # ax = fig.add_subplot(2, 2, 2)
# # ds_space['U'].salem.quick_map(oceans = True, lakes = True, ax=ax, vmax = 200, cmap =cmap)
# # ax.set_title("BUI")

# # ax = fig.add_subplot(2, 2, 3)
# # ds_space['lat_cos'].salem.quick_map(oceans = True, lakes = True, ax=ax, cmap =cmap)
# # ax.set_title("Cos(Latitude)")

# # ax = fig.add_subplot(2, 2, 4)
# # ds_space['Live_Wood'].salem.quick_map(oceans = True, lakes = True, ax=ax, vmax = 20, cmap =cmap)
# # ax.set_title(r"Live Wood Fuel Load ($kg$ $m^{-2}$)")
# # fig.tight_layout()
# # # plt.savefig(str(data_dir) + '/images/frp-paper/feature-eng-map-bui-lat-cos-load.png', dpi = 250)

# # # %%
