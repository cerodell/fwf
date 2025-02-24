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
    file_list = sorted(Path(f"/Volumes/ThunderBay/CRodell/fires/d02/").glob(year + "*"))
    static_ds = salem.open_xr_dataset(str(data_dir) + "/static/static-vars-wrf-d02.nc")

    lons, lats = static_ds["XLONG"].values, static_ds["XLAT"].values

    static_ds["lats"] = (("south_north", "west_east"), lats)
    static_ds["lons"] = (("south_north", "west_east"), lons)
    static_ds["lats"].attrs = static_ds.attrs
    static_ds["lons"].attrs = static_ds.attrs

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

    file_list_len = len(file_list)
    ds_list = []
    good_files = []
    bad_files = []
    for ii, file in enumerate(file_list):
        try:
            # ds = xr.open_zarr(file)
            ds = xr.open_dataset(file)
            for var in ds:
                ds[var].attrs = static_ds.attrs
            ds.attrs["pyproj_srs"] = static_ds.attrs["pyproj_srs"]
            if np.all(np.isnan(ds["FRP"].values)) == True:
                bad_files.append(file)
                print("BAD!")
            else:
                ISI = xr.where(np.isnan(ds["FRP"].values) == True, np.nan, ds["R"])
                frp_vals = ds["FRP"].mean(("south_north", "west_east")).dropna("time")
                r_values = stats.pearsonr(
                    frp_vals,
                    ISI.mean(("south_north", "west_east")).dropna("time"),
                )[0]
                if len(frp_vals) < 0:
                    print(f"To short of fire buring time {len(frp_vals)}")
                else:
                    print(np.round(r_values, 2))
                    ds = get_solar_hours(ds)

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
                    static_roi = add_static(ds, static_ds[["ZoneST", "lats", "lons"]])

                    fuel_date_range = pd.date_range(
                        ds.attrs["initialdat"][:-3] + "-01",
                        ds.attrs["finaldate"],
                        freq="MS",
                    )
                    fuels_ds = xr.combine_nested(
                        [open_fuels(moi) for moi in fuel_date_range], concat_dim="time"
                    )
                    # fuels_roi = ds.salem.transform(fuels_ds, interp="linear")
                    fuels_roi = ds.salem.lookup_transform(fuels_ds, method=np.sum)
                    fuels_roi = fuels_roi.reindex(time=ds.time, method="ffill")
                    fuels_roi = xr.where(fuels_roi < 0, 0, fuels_roi)
                    fuels_roi["Total_Fuel_Load"] = (
                        fuels_roi["Live_Leaf"]
                        + fuels_roi["Live_Wood"]
                        + fuels_roi["Dead_Foliage"]
                        + fuels_roi["Dead_Wood"]
                    )

                    for var in list(static_roi):
                        ds[var] = static_roi[var]

                    time_shape = ds.time.shape
                    ds["id"] = (("time"), np.full(time_shape, float(ds.attrs["id"])))
                    ds["area_ha"] = (
                        ("time"),
                        np.full(time_shape, float((ds.attrs["area_ha"]))),
                    )
                    ds["AF"] = (("time"), np.array(nan_time))

                    for var in list(fuels_roi):
                        ds[var] = fuels_roi[var]

                    # ds["S"] = np.log1p(ds["S"])
                    # ds["Total_Fuel_Load"] = np.log1p(ds["Total_Fuel_Load"])
                    # ds["Live_Leaf"] = np.log1p(ds["Live_Leaf"])
                    # ds["Live_Wood"] = np.log1p(ds["Live_Wood"])
                    # ds["Dead_Foliage"] = np.log1p(ds["Dead_Foliage"])
                    # ds["Dead_Wood"] = np.log1p(ds["Dead_Wood"])

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
                            ds.stack(z=("time", "south_north", "west_east"))
                            .reset_index("z")
                            .dropna("z")
                            .reset_coords()
                        )
                    else:
                        ds_mean = ds.mean(
                            ("south_north", "west_east"), skipna=True
                        ).dropna("time")
                        time_shape = ds_mean.time.shape
                        ds_mean["burn_time"] = (
                            ("time"),
                            np.full(time_shape, float(len(ds_mean.time))),
                        )
                        ds_mean["r_values"] = (
                            ("time"),
                            np.full(time_shape, float(r_values)),
                        )

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
        f"/Users/crodell/fwf/data/ml-data/training-data/{year}-fires-averaged-v21.nc"
    )
    print(save_dir)
    final_ds, encoding = compressor(final_ds)
    final_ds.to_netcdf(save_dir, encoding=encoding, mode="w")


# print('--------------------------------')

print(
    stats.pearsonr(
        final_ds["FRP"],
        final_ds["S"],
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
#         dim=("south_north", "west_east"),
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
