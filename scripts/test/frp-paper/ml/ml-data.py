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

# year = "2023"
for year in ["2021", "2022", "2023"]:
    method = "full"
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
            south_north=slice(
                float(ds.attrs["max_y"]) + 4, float(ds.attrs["min_y"]) - 4
            ),
            west_east=slice(float(ds.attrs["min_x"]) - 4, float(ds.attrs["max_x"]) + 4),
        )
        fwi_max_roi = ds.salem.transform(fwi_max_doi, interp="linear")
        fwi_max_roi = xr.where(fwi_max_roi <= 0, 1, fwi_max_roi)

        fwi_min_doi = fwi_min.sel(
            dayofyear=dayofyear,
            south_north=slice(
                float(ds.attrs["max_y"]) + 4, float(ds.attrs["min_y"]) - 4
            ),
            west_east=slice(float(ds.attrs["min_x"]) - 4, float(ds.attrs["max_x"]) + 4),
        )
        fwi_min_roi = ds.salem.transform(fwi_min_doi, interp="linear")
        fwi_min_roi = xr.where(fwi_min_roi <= 0, 0.1, fwi_min_roi)

        norm_fwi = (ds["S"] - fwi_min_roi) / (fwi_max_roi - fwi_min_roi)

        if np.all(np.isinf(norm_fwi.values)) == True:
            raise ValueError("STOP!! NFWI is INF!")

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
            ):
                pass
            else:
                ISI = xr.where(np.isnan(ds["FRP"].values) == True, np.nan, ds["R"])
                r_values = stats.pearsonr(
                    ds["FRP"].mean(("x", "y")).dropna("time"),
                    ISI.mean(("x", "y")).dropna("time"),
                )[0]
                if r_values >= 0.399:
                    print(r_values)
                    ds = get_solar_hours(ds)
                    # ds["solar_hour"] = xr.where(
                    #     np.isnan(ds["FRP"].values) == True, np.nan, ds["solar_hour"]
                    # )

                    # nan_space = []
                    nan_time = []
                    for i in range(len(ds.time)):
                        nan_array = np.isnan(ds["FRP"].isel(time=i)).values
                        # zero_full = np.zeros(nan_array.shape)
                        # zero_full[nan_array == False] = 1
                        unique, counts = np.unique(nan_array, return_counts=True)
                        # nan_space.append(zero_full)
                        if unique[0] == False:
                            nan_time.append(counts[0])
                        else:
                            nan_time.append(0)
                    static_roi = add_static(ds, static_ds)
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
                    if norm_fwi == True:
                        ds["NFWI"] = norm_fwi_ds(ds, fwi_max, fwi_min)
                        ds = ds.drop_vars("quantile")

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
                        # fuels_roi[var] = xr.where(
                        #     np.isnan(ds["FRP"].values) == True, np.nan, fuels_roi[var]
                        # )
                        ds[var] = fuels_roi[var]

                    # for var in list(ds):
                    #     try:
                    #         ds[var] = xr.where(
                    #             np.isnan(ds["FRP"].values) == True, np.nan, ds[var]
                    #         )
                    #     except:
                    #         pass

                    if spatially_averaged == False:
                        print(f"Passed: {i}/{file_list_len}")
                        ds_list.append(
                            ds.stack(z=("time", "x", "y"))
                            .reset_index("z")
                            .dropna("z")
                            .reset_coords()
                        )
                    else:
                        ds_mean = ds.mean(("x", "y")).dropna("time").compute()
                        # ds_mean = ds.mean(("x", "y")).compute()
                        # r_values = stats.pearsonr(ds_mean['FRP'], ds_mean['R'])[0]
                        # if r_values >= 0.399:
                        print(f"Passed: {i}/{file_list_len}")
                        ds_list.append(ds_mean)
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
            xr.combine_nested(ds_list, concat_dim="time")
            .reset_index("time")
            .reset_coords()
        )

    save_dir = (
        f"/Users/crodell/fwf/data/ml-data/training-data/{year}-fires-averaged-v3.nc"
    )
    print(save_dir)
    final_ds, encoding = compressor(final_ds)
    final_ds.to_netcdf(save_dir, encoding=encoding, mode="w")
