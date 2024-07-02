#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import os
import context
import salem
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt

from context import data_dir


# Paths to the .hdr and binary data files
hdr_file_path = (
    str(data_dir) + "/maps/ecoregion_ecosystem_pt03degree_NorthAmerica_G2.hdr"
)
binary_file_path = (
    str(data_dir) + "/maps/ecoregion_ecosystem_pt03degree_NorthAmerica_G2.bin"
)


# import spectral


def read_hdr_file(hdr_file_path):
    with open(hdr_file_path, "r") as file:
        lines = file.readlines()

    header_info = {}
    for line in lines:
        if "=" in line:
            key, value = line.split("=")
            header_info[key.strip()] = value.strip()
    return header_info


def read_binary_data(hdr_file_path, binary_file_path):
    header_info = read_hdr_file(hdr_file_path)

    # Extract relevant information from the header
    samples = int(header_info["samples"])
    lines = int(header_info["lines"])
    bands = int(header_info["bands"])
    dtype = header_info["data type"]

    # Determine the numpy dtype
    dtype_map = {
        "0": np.uint8,
        "1": np.uint8,
        "2": np.int16,
        "3": np.int32,
        "4": np.float32,
        "5": np.float64,
        "12": np.uint16,
        "13": np.uint32,
        "14": np.int64,
        "15": np.uint64,
        "16": np.uint64,
    }

    np_dtype = dtype_map[dtype]

    # Read the binary data
    data = np.fromfile(binary_file_path, dtype=np_dtype)

    # Reshape the data to the correct dimensions (lines, samples, bands)
    data = data.reshape((lines, samples, bands))

    return data


# Read the data
data = read_binary_data(hdr_file_path, binary_file_path)


ds = salem.open_xr_dataset(str(data_dir) + "/static/static-rave-3km-grid.nc")
rave_ds = xr.open_dataset(
    "/Volumes/ThunderBay/CRodell/rave/2023/10/RAVE-HrlyEmiss-3km_v2r0_blend_s202310310000000_e202310312359590_c202312011700470.nc"
)
# df_forest = pd.read_csv(str(data_dir) + "/frp/forest_frp_curve.csv")

# ds = grid_ds.assign_coords(
#     {"time": rave_ds.time.values}
# )  # Assign time coordinates from the RAVE dataset to the grid
# Apply spatial selections and calculations to the dataset
# rave_ds = xr.where(rave_ds["QA"] != 3, rave_ds, np.nan)
var = "land_cover"
ds[var] = (
    ("y", "x"),
    np.nan_to_num(rave_ds[var].data[::-1]),
)  # Invert and fill NaN values
ds[var].attrs = ds.attrs  # Copy attributes

ds["eco1"] = (
    ("y", "x"),
    data[::-1, :, 0],
)  # Invert and fill NaN values
ds["eco1"].attrs = ds.attrs  # Copy attributes
data[::-1, :, 1] = np.where(data[::-1, :, 1] == 255, np.nan, data[::-1, :, 1])
data[::-1, :, 1] = np.where(data[::-1, :, 1] == 30, np.nan, data[::-1, :, 1])
# data[::-1, :, 1] = np.where(data[::-1, :, 1] == 16, np.nan, data[::-1, :, 1])
# data[::-1, :, 1] = np.where(data[::-1, :, 1] == 15, np.nan, data[::-1, :, 1])
# data[::-1,:,1] = np.where(data[::-1,:,1] == 14, np.nan, data[::-1,:,1])
# data[::-1, :, 1] = np.where(data[::-1, :, 1] == 1, np.nan, data[::-1, :, 1])
# data[::-1,:,1] = np.where(data[::-1,:,1] == 2, np.nan, data[::-1,:,1])

ds["eco2"] = (
    ("y", "x"),
    data[::-1, :, 1],
)  # Invert and fill NaN values
ds["eco2"].attrs = ds.attrs  # Copy attributes
# ds = ds.sel(
#   x=slice(-180, -27), y=slice(20, 75)
# )  # Select a specific spatial region
# ds = ds.sel(
#   x=slice(-128, -109), y=slice(32, 53)
# )  # Select a specific spatial region
ds = ds.sel(x=slice(-170, -50), y=slice(25, 75))  # Select a specific spatial region


ds_cali = ds.sel(
    x=slice(-128, -95), y=slice(32, 58)
)  # Select a specific spatial region

import cartopy

fig = plt.figure(figsize=(14, 4))
ax = fig.add_subplot(1, 1, 1, projection=ds.salem.cartopy())
ds["eco2"].plot.pcolormesh(levels=np.unique(ds["eco2"]), ax=ax, cmap="tab20c")
ax.coastlines()
ax.add_feature(cartopy.feature.BORDERS)
# save as png
# fig.savefig(
#     str(data_dir) + f"/images/frp-paper/map-eco.png",
#     bbox_inches="tight",
#     dpi=240,
# )


import cartopy

fig = plt.figure(figsize=(14, 4))
ax = fig.add_subplot(1, 1, 1, projection=ds.salem.cartopy())
ds["eco1"].plot.pcolormesh(levels=np.unique(ds["eco1"]), ax=ax, cmap="tab20c")
ax.coastlines()
ax.add_feature(cartopy.feature.BORDERS)
# save as png
# fig.savefig(
#     str(data_dir) + f"/images/frp-paper/map-land-cover.png",
#     bbox_inches="tight",
#     dpi=240,
# )


# df_curve = pd.read_csv(str(data_dir) + "/frp/FRP_diurnal_climatology.csv")

# # # Clean the header row
# df_curve.columns = ['Land Cover', 'Ecoregion', 'hh00', 'hh01', 'hh02', 'hh03', 'hh04', 'hh05', 'hh06', 'hh07', 'hh08', 'hh09', 'hh10', 'hh11', 'hh12', 'hh13', 'hh14', 'hh15', 'hh16', 'hh17', 'hh18', 'hh19', 'hh20', 'hh21', 'hh22', 'hh23']

# # # Remove the first row which is now redundant
# df_curve = df_curve.drop(0).drop(columns=['Land Cover', 'Ecoregion']).dropna().reset_index(drop=True).astype(float)

# df_curve = df_curve.mean()
# grouped_df = df.groupby(['Land Cover'])['Forest']

# crop_curve = pd.read_csv(str(data_dir) + "/frp/cropland_frp_curve.csv")
