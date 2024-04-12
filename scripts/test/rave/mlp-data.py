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
from datetime import datetime

from context import root_dir, data_dir
import warnings

# Suppress runtime warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


# https://medium.com/@khadijamahanga/using-latitude-and-longitude-data-in-my-machine-learning-problem-541e2651e08c


year = "2021"
method = "hfi"
spatially_averaged = True
norm_fwi = False
file_list = sorted(Path(f"/Volumes/WFRT-Ext23/fire/{method}").glob(year + "*"))
static_ds = salem.open_xr_dataset(
    str(data_dir) + "/static/static-rave-3km.nc"
).drop_vars(["time", "xtime"])

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

    return (ds["FWI"] - fwi_min_roi) / (fwi_max_roi - fwi_min_roi)


ds_list = []
for file in file_list:
    try:
        ds = xr.open_zarr(file)
        if (
            (np.all(np.isnan(ds["FRP"].values)) == True)
            or (np.all(np.isnan(ds["NDVI"].values)) == True)
            or (np.all(np.isnan(ds["LAI"].values)) == True)
        ):
            pass
        else:
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
                static_roi[var] = xr.where(
                    np.isnan(ds["FRP"].values) == True, np.nan, static_roi[var]
                )
                ds[var] = static_roi[var]

            for var in list(fuels_roi):
                fuels_roi[var] = xr.where(
                    np.isnan(ds["FRP"].values) == True, np.nan, fuels_roi[var]
                )
                ds[var] = fuels_roi[var]
            print("Passed")
            if spatially_averaged == False:
                ds_list.append(
                    ds.stack(z=("time", "x", "y"))
                    .reset_index("z")
                    .dropna("z")
                    .reset_coords()
                )
            else:
                ds_list.append(ds.mean(("x", "y")).dropna("time"))
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


save_dir = f"/Volumes/WFRT-Ext23/mlp-data/{year}-fires-ffmc"
if spatially_averaged == True:
    save_dir += "-spatially-averaged"


if norm_fwi == True:
    save_dir += "-norm-fwi"
print(save_dir)
final_ds, encoding = compressor(final_ds)
final_ds.to_netcdf(f"{save_dir}.nc", encoding=encoding, mode="w")


# def mod_ds(file):
#   ds = xr.open_zarr(file)
#   if (np.all(np.isnan(ds['NDVI'].values)) == True) or ( np.all(np.isnan(ds['LAI'].values)) == True):
#     pass
#   else:
#     print('Passed')
#     return ds.stack(z=('time','x', 'y')).reset_index('z').dropna('z').to_dataframe()


# df = pd.concat([ mod_ds(file) for file in file_list[:15]], axis=0)

# df.to_csv('/Volumes/WFRT-Ext23/mlp-data/2021-fires.csv')

# ds['FRP'].mean('time').plot(cmap = 'jet')
# ds['NDVI'].mean(('x', 'y')).plot()

# ds_flat = ds.stack(z=('time','x', 'y')).reset_index('z').dropna('z')


# def mod_ds(ds):
