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


years = ["2021", "2022"]
# cluster = LocalCluster(
#     n_workers=3,
#     #    threads_per_worker=,
#     memory_limit="10GB",
#     processes=False,
# )
# client = Client(cluster)
# ### # On workstation
# ### http://137.82.23.185:8787/status
# ### # On personal
# ###  http://10.0.0.88:8787/status
# print(client)


def tranform_ds(ds, rave_roi, fire_i, margin):
    ds = ds.salem.subset(shape=fire_i, margin=margin, all_touched=True)
    ds = rave_roi.salem.transform(
        ds, interp="linear"
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


def create_case_ds(config, fire_i, file_dir):
    FIREloopTime = datetime.now()
    fire_ID = fire_i["id"].values[0]
    print(f"Start {fire_ID}")
    config.update(
        date_range=[
            fire_i["initialdat"].to_list()[0],
            fire_i["finaldate"].to_list()[0],
        ],
        fire_i=fire_i,
    )
    print(f"{i}/{file_len}")

    try:
        rave = RAVE(config=config)
        rave_ds = rave.open_rave(var_list=["FRP_MEAN", "PM25"])

        fwx = FWX(config=config)
        fwx_ds = fwx.open_fwx()

        viirs = VIIRS(config=config)
        ndvi_ds = viirs.open_ndvi()
        lai_ds = viirs.open_lai()
        ### Subset the datasets for the region of interest (ROI) and compute the result
        rave_roi = rave_ds.salem.subset(shape=fire_i, margin=1, all_touched=True)

        rave_roi = rave_roi.salem.roi(shape=fire_i, all_touched=True).compute()
        if np.all(np.isnan(rave_roi["FRP_MEAN"].values)) == True:
            print(f"NO FRP FOR: {fire_ID}")
        else:
            print(f"HAS FRP FOR: {fire_ID}")
            # static_roi = static_ds.salem.subset(shape=fire_i, margin=10, all_touched=True)
            # static_roi = static_roi.salem.roi(shape=fire_i, all_touched=True).drop_vars(['time', 'xtime'])
            # rave_roi = rave_roi.compute()
            # static_roi = add_index(static_roi, rave_roi)
            fwx_roi = tranform_ds(fwx_ds, rave_roi, fire_i, margin=2)
            ndvi_roi = re_index_ds(
                tranform_ds(ndvi_ds["NDVI"], rave_roi, fire_i, margin=10), rave_roi
            )
            lai_roi = re_index_ds(
                tranform_ds(lai_ds["LAI"], rave_roi, fire_i, margin=20), rave_roi
            )

            # fwx_roi = xr.where(fwx_roi<0, 0, fwx_roi)
            lai_roi = xr.where(lai_roi < 0, 0, lai_roi)
            ndvi_roi = xr.where(ndvi_roi < -1, -1, ndvi_roi)
            ndvi_roi = xr.where(ndvi_roi > 1, 1, ndvi_roi)

            # # static_roi = xr.where(rave_roi == 0, np.nan, static_roi)
            # fwx_roi = xr.where(rave_roi == 0, np.nan, fwx_roi).rename('FWI')
            # ndvi_roi = xr.where(rave_roi == 0, np.nan, ndvi_roi).rename('NDVI')
            # lai_roi = xr.where(rave_roi == 0, np.nan, lai_roi).rename('LAI')
            rave_roi = xr.where(rave_roi == 0, np.nan, rave_roi).rename(
                {"FRP_MEAN": "FRP"}
            )

            first_valid_index = (
                rave_roi["FRP"]
                .notnull()
                .any(dim=[dim for dim in rave_roi["FRP"].dims if dim != "time"])
                .argmax("time")
            )

            # final_ds = static_roi
            # final_ds['FWI'] = fwx_roi
            final_ds = fwx_roi  # .rename({'S':'FWI', 'F': 'FFMC'})
            final_ds["NDVI"] = ndvi_roi.rename("NDVI")
            final_ds["LAI"] = lai_roi.rename("LAI")
            for var in rave_roi:
                final_ds[var] = rave_roi[var]

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
            bashComand = "rm -rf " + file_dir
            os.system(bashComand)
            bashComand = "rm -rf /Volumes/WFRT-Ext23/fire/all/._*"
            os.system(bashComand)
            zarr_compressor = zarr.Blosc(cname="zstd", clevel=3, shuffle=2)
            encoding = {x: {"compressor": zarr_compressor} for x in final_ds}
            print(f"WRITING AT: {datetime.now()}")
            final_ds.to_zarr(file_dir, encoding=encoding, mode="w")
            print(f"Wrote: {file_dir}")

            del rave
            del fwx
            del viirs

            del rave_ds
            del fwx_ds
            del ndvi_ds
            del lai_ds

            del rave_roi
            del fwx_roi
            del lai_roi
            del ndvi_roi

            del final_ds
            del fire_i
            gc.collect()
            print(f"FIRE {fire_ID} run time: {datetime.now() - FIREloopTime}")

    except:
        raise ValueError("BAD")
        # print(f"FAILED: {fire_ID}")
    return


static_ds = salem.open_xr_dataset(str(data_dir) + "/static/static-rave-3km.nc")

for year in years:
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
    for i in range(file_len):
        fire_i = firep_df.iloc[i : i + 1]
        file_dir = (
            "/Volumes/WFRT-Ext23/fire/all/"
            + year
            + "-"
            + str(fire_i["id"].values[0])
            + ".zarr"
        )
        if os.path.isdir(file_dir) == True:
            print("TESTING FILE")
            try:
                ds = xr.open_zarr(file_dir)
                if (
                    (np.all(np.isnan(ds["NDVI"].values)) == False)
                    | (np.all(np.isnan(ds["LAI"].values)) == False)
                    | (np.all(np.isnan(ds["FRP"].values)) == False)
                ):
                    print(
                        year
                        + "-"
                        + str(fire_i["id"].values[0])
                        + ".zarr"
                        + " Is a valid file"
                    )
                else:
                    print("FAILED FILE TEST")
                    create_case_ds(config, fire_i, file_dir)
            except:
                ("FILE IS BAD CREATE IT")
                bashComand = "rm -rf " + file_dir
                os.system(bashComand)
                bashComand = "rm -rf /Volumes/WFRT-Ext23/fire/all/._*"
                os.system(bashComand)
                create_case_ds(config, fire_i, file_dir)
        else:
            ("NO FILE WILL CREATE IT")
            create_case_ds(config, fire_i, file_dir)
