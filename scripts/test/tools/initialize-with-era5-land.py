#!/Users/crodell/miniconda3/envs/fwf/bin/python

import context

import salem
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
import json
import zarr

from datetime import datetime
import matplotlib.pyplot as plt

from utils.compressor import compressor, file_size

from context import data_dir, root_dir


with open(str(root_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)


model = "adda"
domain = "d01"
doi = pd.Timestamp("2000-12-31")
trial_name = "01"
target_grid = salem.open_xr_dataset(str(data_dir) + f"/{model}/{domain}-grid.nc")
save_dir = Path(f"/Volumes/WFRT-Ext21/fwf-data/{model}/{domain}/{trial_name}/")
save_dir.mkdir(parents=True, exist_ok=True)

filein_era5 = f"/Volumes/WFRT-Ext23/fwf-data/ecmwf/era5-land/04/{doi.strftime('%Y%m')}/"
era5_hourly = salem.open_xr_dataset(
    filein_era5 + f"/fwf-hourly-era5-land-{doi.strftime('%Y%m%d%H')}.nc"
)

hourly_ds = target_grid.salem.transform(
    era5_hourly,
)

# # fig = plt.figure(figsize=(12, 6))
# # ax = fig.add_subplot(1, 1, 1)
# # hourly_ds.isel(time=0)["F"].salem.quick_map(ax=ax, cmap="jet")

# ds_fill = ds.interpolate_na(dim="south_north", method = 'linear', fill_value="extrapolate")
hourly_fill = hourly_ds  # .chunk('auto')
hourly_fill = hourly_fill.fillna(85)
hourly_fill = hourly_fill.drop("time")
# fig = plt.figure(figsize=(12, 6))
# ax = fig.add_subplot(1, 1, 1)
# hourly_fill.isel(time=0)["F"].salem.quick_map(ax=ax, cmap="jet")

# write = datetime.now()
# print("Writing netcdf at: ", write)
# hourly_fill, encoding = compressor(hourly_fill, var_dict)
# hourly_fill.to_netcdf(
#     str(save_dir) + f"/fwf-hourly-{domain}-{doi.strftime('%Y%m%d00')}.nc",
#     mode="w",
# )
# print("Time write netcdf: ", datetime.now() - write)

hourly_fill = hourly_fill.chunk("auto")
zarr_compressor = zarr.Blosc(cname="zstd", clevel=3, shuffle=2)
write = datetime.now()
print("Writing zarr at: ", write)
hourly_fill.to_zarr(
    str(save_dir) + f"/fwf-hourly-{domain}-{doi.strftime('%Y%m%d00')}.zarr",
    encoding={x: {"compressor": zarr_compressor} for x in hourly_fill},
    mode="w",
)
print("Time write zarr: ", datetime.now() - write)


era5_daily = salem.open_xr_dataset(
    filein_era5 + f"/fwf-daily-era5-land-{doi.strftime('%Y%m%d%H')}.nc"
)

daily_ds = target_grid.salem.transform(
    era5_daily,
)

# fig = plt.figure(figsize=(12, 6))
# ax = fig.add_subplot(1, 1, 1)
# daily_ds.isel(time=0)["D"].salem.quick_map(ax=ax, cmap="jet")

# ds_fill = ds.interpolate_na(dim="south_north", method = 'linear', fill_value="extrapolate")
daily_fill = daily_ds
daily_fill["F"] = daily_fill["F"].fillna(85)
daily_fill["P"] = daily_fill["P"].fillna(6)
daily_fill["D"] = daily_fill["D"].fillna(15)
daily_fill = daily_fill.fillna(0)
daily_fill = daily_fill.drop("time")

# fig = plt.figure(figsize=(12, 6))
# ax = fig.add_subplot(1, 1, 1)
# daily_fill.isel(time=0)["D"].salem.quick_map(ax=ax, cmap="jet")

# write = datetime.now()
# print("Writing netcdf at: ", write)
# daily_fill, encoding = compressor(daily_fill, var_dict)
# daily_fill.to_netcdf(
#     str(save_dir) + f"/fwf-daily-{domain}-{doi.strftime('%Y%m%d00')}.nc",
#     mode="w",
# )
# print("Time write netcdf: ", datetime.now() - write)

daily_fill = daily_fill.chunk("auto")
zarr_compressor = zarr.Blosc(cname="zstd", clevel=3, shuffle=2)
write = datetime.now()
print("Writing zarr at: ", write)
daily_fill.to_zarr(
    str(save_dir) + f"/fwf-daily-{domain}-{doi.strftime('%Y%m%d00')}.zarr",
    encoding={x: {"compressor": zarr_compressor} for x in daily_fill},
    mode="w",
)
print("Time write zarr: ", datetime.now() - write)
