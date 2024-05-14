#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import context
import salem
import dask
import zarr
import os
import numpy as np
import pandas as pd
import xarray as xr
from scipy import interpolate
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt

from utils.solar_hour import get_solar_hours
from context import root_dir, data_dir
import warnings

# Suppress runtime warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


# https://medium.com/@khadijamahanga/using-latitude-and-longitude-data-in-my-machine-learning-problem-541e2651e08c

# from dask.distributed import LocalCluster, Client

# cluster = LocalCluster(
#     n_workers=2,
#     # threads_per_worker=4,
#     memory_limit="16GB",
#     processes=False,
# )
# client = Client(cluster)
# print(client)
## # On workstation
## http://137.82.23.185:8787/status
## # On personal
##  http://10.0.0.88:8787/status

year = "2021"

method = "all"
spatially_averaged = True
norm_fwi = False
file_list = sorted(Path(f"/Volumes/WFRT-Ext23/fire/{method}").glob(year + "*"))
static_ds = salem.open_xr_dataset(
    str(data_dir) + "/static/static-rave-3km.nc"
).drop_vars(["time", "xtime"])

lons, lats = static_ds.salem.grid.ll_coordinates
lon_sin = np.sin(np.radians(lons))
lon_cos = np.cos(np.radians(lons))
lat_sin = np.sin(np.radians(lats))
lat_cos = np.cos(np.radians(lats))

static_ds["lat_sin"] = (("y", "x"), lat_sin)
static_ds["lat_cos"] = (("y", "x"), lat_cos)
static_ds["lon_sin"] = (("y", "x"), lon_sin)
static_ds["lon_cos"] = (("y", "x"), lon_cos)


ASPECT_sin = np.sin(np.radians(static_ds["ASPECT"].values))
ASPECT_cos = np.cos(np.radians(static_ds["ASPECT"].values))
static_ds["ASPECT_sin"] = (("y", "x"), ASPECT_sin)
static_ds["ASPECT_cos"] = (("y", "x"), ASPECT_cos)

SAZ_sin = np.sin(np.radians(static_ds["SAZ"].values))
SAZ_cos = np.cos(np.radians(static_ds["SAZ"].values))
static_ds["SAZ_sin"] = (("y", "x"), SAZ_sin)
static_ds["SAZ_cos"] = (("y", "x"), SAZ_cos)

if norm_fwi == True:
    print("Normalize FWI")
    fwi_climo_ds = xr.open_zarr(
        f"/Volumes/WFRT-Ext23/ecmwf/era5-land/S-hourly-climatology-19910101-20201231-compressed.zarr"
    )[
        "S"
    ]  # .sel(dayofyear=int(doi.strftime("%j")) - 1, hour=int(doi.strftime("%H")))
    fwi_max = fwi_climo_ds.sel(quantile=1).max("hour")
    fwi_min = fwi_climo_ds.sel(quantile=0).min("hour")


def add_index(static_roi, fire_ds):
    static_roi = static_roi.expand_dims("time")
    static_roi.coords["time"] = pd.Series(fire_ds.time.values[0])
    return static_roi.reindex(time=fire_ds.time, method="ffill")


def add_static(fire_ds, static_ds):
    return add_index(fire_ds.salem.transform(static_ds, interp="nearest"), fire_ds)


def open_fuels(moi):
    fuel_dir = f"/Volumes/WFRT-Ext23/fuel-characteristics/fuel-load/"
    # fuels_ds = salem.open_xr_dataset(fuel_dir + f'{moi.strftime("%Y")}/CFUEL_timemean_{moi.strftime("%Y_%m")}.nc').sel(lat = slice(75,20), lon = slice(-170, -50))
    fuels_ds = salem.open_xr_dataset(
        fuel_dir + f'{2021}/CFUEL_timemean_2021{moi.strftime("_%m")}.nc'
    ).sel(lat=slice(75, 20), lon=slice(-170, -50))
    fuels_ds.coords["time"] = moi
    return fuels_ds


def norm_fwi_ds(ds, fwi_max, fwi_min):
    fwi_date_range = pd.to_datetime(ds.time)
    dayofyear = xr.DataArray(
        fwi_date_range.dayofyear, dims="time", coords=dict(time=fwi_date_range)
    )
    hours = xr.DataArray(
        fwi_date_range.hour, dims="time", coords=dict(time=fwi_date_range)
    )
    fwi_max_doi = fwi_max.sel(
        dayofyear=dayofyear,
        south_north=slice(float(ds.attrs["max_y"]) + 4, float(ds.attrs["min_y"]) - 4),
        west_east=slice(float(ds.attrs["min_x"]) - 4, float(ds.attrs["max_x"]) + 4),
    )
    fwi_max_roi = ds.salem.transform(fwi_max_doi, interp="linear")
    fwi_max_roi = xr.where(fwi_max_roi <= 0, 0.1, fwi_max_roi)

    fwi_min_doi = fwi_min.sel(
        dayofyear=dayofyear,
        south_north=slice(float(ds.attrs["max_y"]) + 4, float(ds.attrs["min_y"]) - 4),
        west_east=slice(float(ds.attrs["min_x"]) - 4, float(ds.attrs["max_x"]) + 4),
    )
    fwi_min_roi = ds.salem.transform(fwi_min_doi, interp="linear")
    fwi_min_roi = xr.where(fwi_min_roi < 0, 0, fwi_min_roi)

    return (ds["S"] - fwi_min_roi) / (fwi_max_roi - fwi_min_roi)


file_list_len = len(file_list)
ds_list = []
for i, file in enumerate(file_list):
    try:
        ds = xr.open_zarr(file)
        if (
            (np.all(np.isnan(ds["FRP"].values)) == True)
            or (np.all(np.isnan(ds["NDVI"].values)) == True)
            or (np.all(np.isnan(ds["LAI"].values)) == True)
            or (
                float(
                    (
                        pd.Timestamp(ds.attrs["finaldate"])
                        - pd.Timestamp(ds.attrs["initialdat"])
                    ).total_seconds()
                    / 3600
                )
                < 24
            )
        ):
            pass
        else:
            ds = get_solar_hours(ds)
            # ds['solar_hour'] = xr.where(
            #         np.isnan(ds["FRP"].values) == True, np.nan, ds['solar_hour']
            #     )
            static_roi = add_static(ds, static_ds)
            fuel_date_range = pd.date_range(
                ds.attrs["initialdat"][:-3] + "-01", ds.attrs["finaldate"], freq="MS"
            )
            fuels_ds = xr.combine_nested(
                [open_fuels(moi) for moi in fuel_date_range], concat_dim="time"
            )
            fuels_roi = ds.salem.transform(fuels_ds, interp="linear")
            fuels_roi = fuels_roi.reindex(time=ds.time, method="ffill")
            fuels_roi = xr.where(fuels_roi < 0, 0, fuels_roi)
            if norm_fwi == True:
                ds["NFWI"] = norm_fwi_ds(ds, fwi_max, fwi_min)
                ds = ds.drop_vars("quantile")

            for var in list(static_roi):
                ds[var] = static_roi[var]

            time_shape = ds.time.shape
            ds["id"] = (("time"), np.full(time_shape, float(ds.attrs["id"])))
            ds["area_ha"] = (
                ("time"),
                np.full(time_shape, float((ds.attrs["area_ha"]))),
            )
            ds["burn_time"] = (
                ("time"),
                np.full(
                    time_shape,
                    float(
                        (
                            pd.Timestamp(ds.attrs["finaldate"])
                            - pd.Timestamp(ds.attrs["initialdat"])
                        ).total_seconds()
                        / 3600
                    ),
                ),
            )

            WD_sin = np.sin(np.radians(ds["WD"].values))
            WD_cos = np.cos(np.radians(ds["WD"].values))
            ds["WD_sin"] = (("time", "y", "x"), WD_sin)
            ds["WD_cos"] = (("time", "y", "x"), WD_cos)

            for var in list(fuels_roi):
                ds[var] = fuels_roi[var]

            if spatially_averaged == False:
                ds_list.append(
                    ds.stack(z=("time", "x", "y"))
                    .reset_index("z")
                    .dropna("z")
                    .reset_coords()
                )
                print(f"Passed: {i}/{file_list_len}")
            else:
                ds_mean = ds.mean(("x", "y"))

                # ds_mean['Time'] = ds_mean['time']
                time_len = len(ds_mean["time"])
                # ds_mean['time'] = np.arange(0, len(ds_mean['time']))
                # Define block size (24 hours)
                block_size = 24
                # Group data into blocks

                # Initialize an empty list to collect processed blocks
                processed_blocks = []

                # Loop over each block
                for j in range(0, time_len, block_size):
                    block = ds_mean.isel(time=slice(j, j + block_size))
                    nan_ratio = block["FRP"].isnull().sum() / block["FRP"].size

                    # Check the NaN ratio and fill NaNs if less than 20%
                    if nan_ratio < 0.2:
                        # Fill NaN values with the mean of the block
                        # fig = plt.figure()
                        # block['FRP'].plot(color = 'tab:blue', zorder =10)
                        block["FRP"] = block["FRP"].interpolate_na("time")
                        times = np.arange(len(block["FRP"]))

                        # Mask where the NaN values are
                        mask = np.isnan(block["FRP"])

                        # Indices where the data is NOT NaN
                        x_known = np.where(~mask)[0]
                        y_known = block["FRP"].values[~mask]

                        # Create a function to extrapolate based on available data
                        f_extrapolate = interpolate.interp1d(
                            x_known, y_known, fill_value="extrapolate"
                        )

                        block["FRP"] = (
                            "time",
                            np.clip(f_extrapolate(times), a_min=1, a_max=None),
                        )
                        # block['FRP'].plot(color = 'tab:red', lw = 4, zorder =1)
                        block = block.isel(time=slice(0, block_size))
                        if (len(block.time) == block_size) & (
                            np.all(np.isnan(block["FRP"].values)) == False
                        ):
                            ds_list.append(block)
                            print(
                                f"Passed: {i}/{file_list_len} on block {int(j/block_size)}/{int(time_len/block_size)}"
                            )
                        # processed_blocks.append(block)

    except:
        pass


def compressor(ds, var_dict=None):
    """
    this function comresses datasets
    """
    # ds = ds.load()
    # ds.attrs["TITLE"] = "FWF MODEL USING OUTPUT FROM WRF V4.2.1 MODEL"
    comp = dict(zlib=True, complevel=3)
    encoding = {var: comp for var in ds.data_vars}
    if var_dict == None:
        pass
    else:
        for var in ds.data_vars:
            ds[var].attrs = var_dict[var]
    return ds, encoding


if spatially_averaged == False:
    final_ds = xr.combine_nested(ds_list, concat_dim="z")
else:
    final_ds = (
        xr.combine_nested(ds_list, concat_dim="time").reset_index("time").reset_coords()
    )

# for var in list(final_ds):
#     print('-----------------------------')
#     print(var)
#     print(np.any(np.isnan(final_ds[var].values)))
#     print('-----------------------------')
save_dir = f"/Volumes/WFRT-Ext23/mlp-data/{year}-fires-averaged-lstm-{block_size}h.nc"
print(save_dir)
final_ds, encoding = compressor(final_ds)
final_ds.to_netcdf(save_dir, encoding=encoding, mode="w")

# import matplotlib.pyplot as plt


# plt.scatter(ds['solar_hour'].mean(("x", "y")), ds['time'].values.astype('datetime64[h]').astype(int)% 24)
# ds['solar_hour'].mean(("x", "y"))
# ds['time'].values.astype('datetime64[h]').astype(int)% 24
