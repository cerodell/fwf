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
from pathlib import Path
from scipy import stats
from datetime import datetime
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

from utils.solar_hour import get_solar_hours
from context import root_dir, data_dir
import warnings

# Suppress runtime warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
# https://medium.com/@khadijamahanga/using-latitude-and-longitude-data-in-my-machine-learning-problem-541e2651e08c


counter = 0
# year = "2023"
for year in ["2021", "2022", "2023"]:
    # for year in ["2021"]:
    # method = "full"
    spatially_averaged = True
    norm_fwi = False
    file_list = sorted(Path(f"/Volumes/ThunderBay/CRodell/fires/").glob(year + "*"))
    static_ds = salem.open_xr_dataset(
        str(data_dir) + "/static/static-rave-3km.nc"
    ).drop_vars(["time", "xtime"])

    curves_ds = salem.open_xr_dataset(str(data_dir) + "/static/curves-rave-3km.nc")
    curves_ds["CLIMO_FRP"] = curves_ds["OFFSET_NORM"] * curves_ds["MAX"]

    rave_ds = xr.open_dataset(
        "/Volumes/ThunderBay/CRodell/rave/2023/10/RAVE-HrlyEmiss-3km_v2r0_blend_s202310310000000_e202310312359590_c202312011700470.nc"
    )

    grid_ds = salem.open_xr_dataset(str(data_dir) + "/static/static-rave-3km-grid.nc")
    grid_ds["area"] = (
        ("y", "x"),
        np.nan_to_num(rave_ds["area"].data[::-1]),
    )  # Invert and fill NaN values
    grid_ds["area"].attrs = grid_ds.attrs

    lons, lats = static_ds.salem.grid.ll_coordinates
    lon_sin = np.sin(np.radians(lons))
    lon_cos = np.cos(np.radians(lons))
    lat_sin = np.sin(np.radians(lats))
    lat_cos = np.cos(np.radians(lats))

    static_ds["lats"] = (("y", "x"), lats)
    static_ds["lons"] = (("y", "x"), lons)

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

        # fwi_max = salem.open_xr_dataset('/Volumes/ThunderBay/CRodell/climo/SMAX-rave-3km-climatology-19910101-20201231.zarr')
        # fwi_min = salem.open_xr_dataset('/Volumes/ThunderBay/CRodell/climo/SMIN-rave-3km-climatology-19910101-20201231.zarr')

        fwi_max = salem.open_xr_dataset(
            "/Volumes/ThunderBay/CRodell/climo/SMAX-rave-3km-climatology-20210101-20231031.zarr"
        )
        fwi_min = 0.01
        isi_max = salem.open_xr_dataset(
            "/Volumes/ThunderBay/CRodell/climo/RMAX-rave-3km-climatology-20210101-20231031.zarr"
        )
        isi_min = 0.01
        bui_max = salem.open_xr_dataset(
            "/Volumes/ThunderBay/CRodell/climo/UMAX-rave-3km-climatology-20210101-20231031.zarr"
        )
        bui_min = salem.open_xr_dataset(
            "/Volumes/ThunderBay/CRodell/climo/UMIN-rave-3km-climatology-20210101-20231031.zarr"
        )

    def add_index(static_roi, fire_ds):
        static_roi = static_roi.expand_dims("time")
        static_roi.coords["time"] = pd.Series(fire_ds.time.values[0])
        return static_roi.reindex(time=fire_ds.time, method="ffill")

    def add_static(fire_ds, static_ds):
        return add_index(fire_ds.salem.transform(static_ds, interp="nearest"), fire_ds)

    def add_curves(fire_ds, curves_ds):
        return

    def open_fuels(moi):
        fuel_dir = f"/Volumes/ThunderBay/CRodell/ecmwf/fuel-load/"
        fuels_ds = salem.open_xr_dataset(
            fuel_dir + f'{2021}/CFUEL_timemean_2021{moi.strftime("_%m")}.nc'
        ).sel(lat=slice(75, 20), lon=slice(-170, -50))
        fuels_ds.coords["time"] = moi
        return fuels_ds

    # def norm_fwi_ds(ds, fwi_max, fwi_min):
    #     fwi_date_range = pd.to_datetime(ds.time)
    #     dayofyear = xr.DataArray(
    #         fwi_date_range.dayofyear, dims="time", coords=dict(time=fwi_date_range)
    #     )
    #     hours = xr.DataArray(
    #         fwi_date_range.hour, dims="time", coords=dict(time=fwi_date_range)
    #     )
    #     fwi_max_roi = fwi_max.sel(
    #         dayofyear=dayofyear,
    #         x=ds.x,
    #         y=ds.y,
    #     )
    #     fwi_max_roi = xr.where(fwi_max_roi <= 1, 1, fwi_max_roi)

    #     fwi_min_roi = fwi_min.sel(
    #         dayofyear=dayofyear,
    #         x=ds.x,
    #         y=ds.y,
    #     )
    #     fwi_min_roi = xr.where(fwi_min_roi <= 0, 0.01, fwi_min_roi)

    #     norm_fwi = ((ds["S"] - fwi_min_roi) / (fwi_max_roi - fwi_min_roi)).rename({'S':'NFWI'})

    #     if np.all(np.isinf(norm_fwi['NFWI'].values)) == True:
    #         raise ValueError("STOP!! NFWI is INF!")

    #     return norm_fwi['NFWI']

    def norm_fwi_ds(
        ds,
        fwi_max,
        fwi_min,
        isi_max,
        isi_min,
        bui_max,
        bui_min,
    ):
        fwi_date_range = pd.to_datetime(ds.time)
        month = xr.DataArray(
            fwi_date_range.month, dims="time", coords=dict(time=fwi_date_range)
        )

        fwi_max_roi = fwi_max.sel(
            month=month,
            x=ds.x,
            y=ds.y,
        )
        fwi_max_roi = xr.where(fwi_max_roi <= 1, 1, fwi_max_roi)

        fwi_min_roi = fwi_min
        norm_fwi = ((ds["S"] - fwi_min_roi) / (fwi_max_roi - fwi_min_roi)).rename(
            {"S": "NFWI"}
        )

        if np.all(np.isinf(norm_fwi["NFWI"].values)) == True:
            raise ValueError("STOP!! NFWI is INF!")

        ds["NFWI"] = norm_fwi["NFWI"]
        ################################################

        isi_max = isi_max.sel(
            month=month,
            x=ds.x,
            y=ds.y,
        )
        isi_max_roi = xr.where(isi_max <= 1, 1, isi_max)

        isi_min_roi = isi_min
        norm_isi = ((ds["R"] - isi_min_roi) / (isi_max_roi - isi_min_roi)).rename(
            {"R": "NISI"}
        )
        ds["NISI"] = norm_isi["NISI"]

        if np.all(np.isinf(norm_isi["NISI"].values)) == True:
            raise ValueError("STOP!! NISI is INF!")
        ################################################
        bui_max = bui_max.sel(
            month=month,
            x=ds.x,
            y=ds.y,
        )
        bui_max_roi = xr.where(bui_max <= 1, 1, bui_max)

        bui_min_roi = bui_min.sel(
            month=month,
            x=ds.x,
            y=ds.y,
        )
        norm_bui = ((ds["U"] - bui_min_roi) / (bui_max_roi - bui_min_roi)).rename(
            {"U": "NBUI"}
        )
        ds["NBUI"] = norm_bui["NBUI"]
        if np.all(np.isinf(norm_bui["NBUI"].values)) == True:
            raise ValueError("STOP!! NBUI is INF!")

        return ds

    file_list_len = len(file_list)
    ds_list = []
    good_files = []
    bad_files = []
    for ii, file in enumerate(file_list):
        try:
            # ds = xr.open_zarr(file)
            ds = xr.open_dataset(file)
            ds = ds.drop_vars(["FRP_SD", "PM25", "QA"])
            if (
                np.all(np.isnan(ds["FRP"].values))
                == True
                # or (np.all(np.isnan(ds["NDVI"].values)) == True)
                # or (np.all(np.isnan(ds["LAI"].values)) == True)
            ):
                bad_files.append(file)
                print("BAD!")
            else:
                ISI = xr.where(np.isnan(ds["FRP"].values) == True, np.nan, ds["R"])
                frp_vals = ds["FRP"].mean(("x", "y")).dropna("time")
                r_values = stats.pearsonr(
                    ds["FRP"].mean(("x", "y")).dropna("time"),
                    ISI.mean(("x", "y")).dropna("time"),
                )[0]
                print(np.round(r_values, 2))
                ds = get_solar_hours(ds)
                # ds["solar_hour"] = xr.where(
                #     np.isnan(ds["FRP"].values) == True, np.nan, ds["solar_hour"]
                # )

                nan_space = []
                nan_time = []
                for i in range(len(ds.time)):
                    nan_array = np.isnan(ds["FRP"].isel(time=i)).values
                    zero_full = np.zeros(nan_array.shape)
                    zero_full[nan_array == False] = 1
                    unique, counts = np.unique(nan_array, return_counts=True)
                    nan_space.append(zero_full)
                    if unique[0] == False:
                        nan_time.append(counts[0])
                    else:
                        nan_time.append(0)
                static_roi = add_static(ds, static_ds)
                curves_roi = ds.salem.transform(curves_ds, interp="nearest")
                fire_time = ds.time.values
                hour_one = pd.Timestamp(fire_time[0]).hour
                curves_roi = curves_roi.roll(time=-hour_one, roll_coords=True)

                grid_roi = add_static(ds, grid_ds)
                ds["area"] = grid_roi["area"]

                # curves_roi['time'] = fire_time[:24]
                OFFSET_NORM = curves_roi["OFFSET_NORM"].values
                N = len(fire_time)
                ds["OFFSET_NORM"] = (
                    ("time", "y", "x"),
                    np.tile(OFFSET_NORM, (N // 24 + 1, 1, 1))[:N, :, :],
                )

                CLIMO_FRP = curves_roi["CLIMO_FRP"].values
                N = len(fire_time)
                ds["CLIMO_FRP"] = (
                    ("time", "y", "x"),
                    np.tile(CLIMO_FRP, (N // 24 + 1, 1, 1))[:N, :, :],
                )

                fuel_date_range = pd.date_range(
                    ds.attrs["initialdat"][:-3] + "-01",
                    ds.attrs["finaldate"],
                    freq="MS",
                )
                fuels_ds = xr.combine_nested(
                    [open_fuels(moi) for moi in fuel_date_range], concat_dim="time"
                )
                fuels_roi = ds.salem.transform(fuels_ds, interp="linear")
                fuels_roi = fuels_roi.reindex(time=ds.time, method="ffill")
                fuels_roi = xr.where(fuels_roi < 0, 0, fuels_roi)
                fuels_roi["Total_Fuel_Load"] = (
                    fuels_roi["Live_Leaf"]
                    + fuels_roi["Live_Wood"]
                    + fuels_roi["Dead_Foliage"]
                    + fuels_roi["Dead_Wood"]
                )

                if norm_fwi == True:
                    # ds["NFWI"] = norm_fwi_ds(ds, fwi_max, fwi_min)
                    ds = norm_fwi_ds(
                        ds, fwi_max, fwi_min, isi_max, isi_min, bui_max, bui_min
                    )
                    # ds = ds.drop_vars("quantile")

                for var in list(static_roi):
                    # static_roi[var] = xr.where(
                    #     np.isnan(ds["FRP"].values) == True, np.nan, static_roi[var]
                    # )
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
                ds["AF"] = (("time"), np.array(nan_time))

                for var in list(fuels_roi):
                    ds[var] = fuels_roi[var]

                ds["R"] = np.log1p(ds["R"])
                ds["U"] = np.log1p(ds["U"])
                ds["Total_Fuel_Load"] = np.log1p(ds["Total_Fuel_Load"])
                for var in list(ds):
                    try:
                        ds[var] = xr.where(
                            np.isnan(ds["FRP"].values) == True, np.nan, ds[var]
                        )
                    except:
                        pass

                if spatially_averaged == False:
                    print(f"Passed: {ii}/{file_list_len}")
                    ds_list.append(
                        ds.stack(z=("time", "x", "y"))
                        .reset_index("z")
                        .dropna("z")
                        .reset_coords()
                    )
                else:
                    ds_mean = ds.mean(("x", "y"), skipna=True)
                    # Create a mask of the original non-null values
                    # original_non_null_mask = ds['FRP'].notnull()

                    # # Forward fill along the time dimension
                    # forward_filled = ds['FRP'].ffill(dim='time')

                    # # Backward fill along the time dimension
                    # backward_filled = forward_filled.bfill(dim='time')

                    # # Combine the original non-null values with the forward/backward filled values
                    # filled_data = ds['FRP'].where(original_non_null_mask, other=backward_filled)

                    # for var in ['FRP']:
                    # #     if (var == 'FRP') or (var=='FRE'):
                    # #         frp_mean = ds[var].quantile(
                    # #                 [0.75],
                    # #                 dim=("x", "y"),
                    # #                 skipna=True,
                    # #             ).isel(quantile=0).drop_vars('quantile')
                    # #     else:
                    #     # frp_mean = ds[var].mean(("x", "y"),  skipna=True)
                    #     plt.figure()
                    #     ds[var].mean(("x", "y"),  skipna=True).plot()

                    #     frp_mean = ds[var].sum(("x", "y"),  skipna=True) / ds['area'].sum(("x", "y"),  skipna=True)
                    #     frp_mean_series = frp_mean.to_series()

                    #     # Identify the missing data (NaNs)
                    #     missing_data = frp_mean_series.isna()

                    #     # Calculate the length of each gap
                    #     gap_lengths = missing_data.groupby((missing_data != missing_data.shift()).cumsum()).transform('size') * missing_data

                    #     # Set a threshold for filling gaps (e.g., 6 hours)
                    #     threshold = 6

                    #     # Fill gaps that are under the threshold
                    #     filled_frp_mean_series = frp_mean_series.copy()
                    #     for gap_length in range(1, threshold + 1):
                    #         filled_frp_mean_series = filled_frp_mean_series.where(gap_lengths != gap_length, filled_frp_mean_series.interpolate(method='cubic'))

                    #     filled_frp_mean_series = filled_frp_mean_series.clip(lower=0)

                    #     # # Apply Gaussian smoothing while preserving original nulls
                    #     sigma = 2  # Define the standard deviation for Gaussian kernel

                    #     # # Create a mask of non-null values
                    #     non_null_mask = ~filled_frp_mean_series.isna()

                    #     # # Perform Gaussian smoothing only on non-null values
                    #     smoothed_frp_mean_series = filled_frp_mean_series.copy()
                    #     smoothed_values = gaussian_filter1d(filled_frp_mean_series[non_null_mask], sigma=sigma)
                    #     smoothed_frp_mean_series[non_null_mask] = smoothed_values

                    #     # Convert the smoothed Series back to an xarray DataArray
                    #     smoothed_frp_mean = xr.DataArray(smoothed_frp_mean_series, coords=frp_mean.coords, dims=frp_mean.dims)
                    #     # ds[var] =
                    #     # # Plot everything on the same figure
                    #     # plt.figure(figsize=(12, 6))
                    #     # plt.plot(frp_mean_series, label=f'Original {var} Mean', linestyle='--', marker='o')
                    #     # plt.plot(filled_frp_mean_series, label=f'Interpolated {var} Mean', linestyle='-', marker='x')
                    #     # plt.plot(smoothed_frp_mean_series, label=f'Smoothed {var} Mean', linestyle='-', marker='.')

                    #     # plt.title(f'{var} Mean Time Series')
                    #     # plt.xlabel('Time')
                    #     # plt.ylabel(f'{var} Mean')
                    #     # plt.legend()
                    #     # plt.grid(True)
                    #     # plt.show()

                    #     ds_mean[var] = smoothed_frp_mean
                    #     plt.figure()
                    #     ds_mean[var].plot()

                    ds_mean = ds_mean.dropna("time")

                    print(f"Passed: {ii}/{file_list_len}")
                    print("Length of data: ", len(ds_mean.time))
                    counter += 1
                    ds_list.append(ds_mean)
                    good_files.append(file)
        except:
            print(f"DID NOT RUN!! {file}")

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
            xr.combine_nested(ds_list, concat_dim="time")
            .reset_index("time")
            .reset_coords()
        )

    save_dir = (
        f"/Users/crodell/fwf/data/ml-data/training-data/{year}-fires-averaged-v12.nc"
    )
    print(save_dir)
    final_ds, encoding = compressor(final_ds)
    final_ds.to_netcdf(save_dir, encoding=encoding, mode="w")


# print('--------------------------------')

print(
    stats.pearsonr(
        final_ds["FRP"],
        final_ds["R"],
    )[0]
)
print("--------------------------------")

# print(stats.pearsonr(
#            final_ds['FRE'],
#            final_ds['S'],
#         )[0])
# print('--------------------------------')

# print(stats.pearsonr(
#            final_ds['FRE'],
#            final_ds['NFWI'],
#         )[0])

# print('--------------------------------')

# print((counter/(len(good_files)+len(bad_files)))*100)

# quant_ds = ds['FRP'].quantile(
#         [0, 0.25, 0.5, 0.75, .90, 0.95, 1],
#         dim=("x", "y"),
#         skipna=True,
#     )#.dropna("time")

# fig = plt.figure(figsize=(8,4))
# ax = fig.add_subplot(1,1,1)
# ax.plot(quant_ds['time'], quant_ds.isel(quantile=0), label = '0')
# ax.plot(quant_ds['time'], quant_ds.isel(quantile=1), label = '25')
# ax.plot(quant_ds['time'], quant_ds.isel(quantile=2), label = '50')
# ax.plot(quant_ds['time'], quant_ds.isel(quantile=3), label = '75')
# ax.plot(quant_ds['time'], quant_ds.isel(quantile=4), label = '90')
# ax.plot(quant_ds['time'], quant_ds.isel(quantile=5), label = '95')
# ax.plot(quant_ds['time'], quant_ds.isel(quantile=6), label = '100')
# ax.legend()
