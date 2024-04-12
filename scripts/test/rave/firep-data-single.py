#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import context
import salem
import dask
import zarr
import os
import gc
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime

from context import root_dir, data_dir
from utils.rave import RAVE
from utils.fwx import FWX
from utils.viirs import VIIRS
from utils.firep import FIREP
from utils.frp import set_axis_postion
from scipy import stats
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.dates import DateFormatter
from matplotlib.colors import LinearSegmentedColormap

import matplotlib.dates as mdates
import cartopy.crs as ccrs


from dask.distributed import LocalCluster, Client

import warnings

# Suppress runtime warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


year = "2021"
i = 100


def tranform_ds(ds, rave_roi, fire_i, margin):
    ds = ds.salem.subset(shape=fire_i, margin=margin, all_touched=True)
    ds = rave_roi.salem.transform(
        ds, interp="nearest"
    )  # Apply a spatial transform to align datasets
    ds = ds.salem.roi(shape=fire_i, all_touched=True)
    try:
        ds = ds.drop_vars("Time")  # Finalize the FWX dataset
    except:
        pass
    return ds  # .compute()


def re_index_ds(ds, rave_roi):
    ds_date_range = pd.Series(ds.time.values)
    date_range_list = []
    for doi in ds_date_range:
        if doi != ds_date_range.iloc[-1]:
            date_range_list.append(doi)
        else:
            date_range_list.append(doi + pd.Timedelta(days=1))
    ds.coords["time"] = pd.Series(date_range_list)
    return ds.reindex(time=rave_roi.time, method="ffill")


def add_index(ds, rave_roi):
    ds = ds.expand_dims("time")
    ds.coords["time"] = pd.Series(rave_roi.time.values[0])
    return ds.reindex(time=rave_roi.time, method="ffill")


static_ds = salem.open_xr_dataset(str(data_dir) + "/static/static-rave-3km.nc")

# Configuration dictionary for the RAVE and FWX models
config = dict(
    model="wrf",
    trail_name="01",
    method="hourly",
    year=year,
)
# # Initialize RAVE, FWX and VIIRS data with the configuration
firep = FIREP(config=config)
firep_df = firep.open_firep()
file_len = len(firep_df)
fire_i = firep_df.iloc[i : i + 1]
file_dir = (
    "/Volumes/WFRT-Ext23/fire/" + year + "-" + str(fire_i["id"].values[0]) + ".zarr"
)

FIREloopTime = datetime.now()
fire_ID = fire_i["id"].values[0]
print(f"Start {fire_ID}")
config.update(
    date_range=[fire_i["initialdat"].to_list()[0], fire_i["finaldate"].to_list()[0]],
    fire_i=fire_i,
)
print(f"{i}/{file_len}")

rave = RAVE(config=config)
rave_ds = rave.open_rave()

fwx = FWX(config=config)
fwx_ds = fwx.open_fwx(var_list=["S"])

viirs = VIIRS(config=config)
ndvi_ds = viirs.open_ndvi()
lai_ds = viirs.open_lai()

### Subset the datasets for the region of interest (ROI) and compute the result
rave_roi = rave_ds["FRP_MEAN"].salem.subset(shape=fire_i, margin=1, all_touched=True)
rave_roi = rave_roi.salem.roi(shape=fire_i, all_touched=True).compute()
if np.all(np.isnan(rave_roi.values)) == True:
    print(f"NO FRP FOR: {fire_ID}")
else:
    print(f"HAS FRP FOR: {fire_ID}")
    # static_roi = static_ds.salem.subset(shape=fire_i, margin=10, all_touched=True)
    # static_roi = static_roi.salem.roi(shape=fire_i, all_touched=True).drop_vars(['time', 'xtime'])
    # rave_roi = rave_roi.compute()
    # static_roi = add_index(static_roi, rave_roi)
    fwx_roi = tranform_ds(fwx_ds["S"], rave_roi, fire_i, margin=2)
    ndvi_roi = re_index_ds(
        tranform_ds(ndvi_ds["NDVI"], rave_roi, fire_i, margin=10), rave_roi
    )
    lai_roi = re_index_ds(
        tranform_ds(lai_ds["LAI"], rave_roi, fire_i, margin=20), rave_roi
    )

    fwx_roi = xr.where(fwx_roi < 0, 0, fwx_roi)
    lai_roi = xr.where(lai_roi < 0, 0, lai_roi)
    ndvi_roi = xr.where(ndvi_roi < -1, -1, ndvi_roi)
    ndvi_roi = xr.where(ndvi_roi > 1, 1, ndvi_roi)

    # static_roi = xr.where(rave_roi == 0, np.nan, static_roi)
    # fwx_roi = xr.where(rave_roi == 0, np.nan, fwx_roi).rename('FWI')
    # ndvi_roi = xr.where(rave_roi == 0, np.nan, ndvi_roi).rename('NDVI')
    # lai_roi = xr.where(rave_roi == 0, np.nan, lai_roi).rename('LAI')
    rave_roi = xr.where(rave_roi == 0, np.nan, rave_roi).rename("FRP")

    first_valid_index = (
        rave_roi.notnull()
        .any(dim=[dim for dim in rave_roi.dims if dim != "time"])
        .argmax("time")
    )

    # final_ds = static_roi
    # final_ds['FWI'] = fwx_roi
    final_ds = fwx_roi.rename("FWI").to_dataset()
    final_ds["NDVI"] = ndvi_roi.rename("NDVI")
    final_ds["LAI"] = lai_roi.rename("LAI")
    final_ds["FRP"] = rave_roi.rename("FRP")

    final_ds = final_ds.isel(time=slice(first_valid_index.values, None))
    final_ds.attrs = {
        "area_ha": str(fire_i["area_ha"].values[0]),
        "initialdat": str(fire_i["initialdat"].values[0]),
        "finaldate": str(fire_i["finaldate"].values[0]),
        "id": str(fire_i["id"].values[0]),
        "min_x": str(fire_i["min_x"].values[0]),
        "min_y": str(fire_i["min_y"].values[0]),
        "max_x": str(fire_i["max_x"].values[0]),
        "max_y": str(fire_i["max_y"].values[0]),
    }
    # test = xr.where(np.isnan(final_ds['FRP']), np.nan, final_ds)

    # zarr_compressor = zarr.Blosc(cname="zstd", clevel=3, shuffle=2)
    # encoding = {x: {"compressor": zarr_compressor} for x in final_ds}
    # print(f"WRITING AT: {datetime.now()}")
    # final_ds.to_zarr(file_dir , encoding=encoding, mode="w")

    print(f"FIRE {fire_ID} run time: {datetime.now() - FIREloopTime}")
