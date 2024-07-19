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
import cartopy
import matplotlib.colors as mcolors

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
ds_final = salem.open_xr_dataset(str(data_dir) + "/static/static-rave-3km.nc")

rave_ds = xr.open_dataset(
    "/Volumes/ThunderBay/CRodell/rave/2023/10/RAVE-HrlyEmiss-3km_v2r0_blend_s202310310000000_e202310312359590_c202312011700470.nc"
)
var = "land_cover"
ds[var] = (
    ("y", "x"),
    np.nan_to_num(rave_ds[var].data[::-1]),
)  # Invert and fill NaN values
ds[var].attrs = ds.attrs  # Copy attributes
data[::-1, :, 1] = np.where(data[::-1, :, 1] == 255, np.nan, data[::-1, :, 1])
data[::-1, :, 1] = np.where(data[::-1, :, 1] == 30, np.nan, data[::-1, :, 1])
data[::-1, :, 1] = np.where(data[::-1, :, 1] == 16, np.nan, data[::-1, :, 1])
# data[::-1, :, 1] = np.where(data[::-1, :, 1] == 15, np.nan, data[::-1, :, 1])
# data[::-1,:,1] = np.where(data[::-1,:,1] == 14, np.nan, data[::-1,:,1])
# data[::-1, :, 1] = np.where(data[::-1, :, 1] == 1, np.nan, data[::-1, :, 1])
# data[::-1,:,1] = np.where(data[::-1,:,1] == 2, np.nan, data[::-1,:,1])


ds["ecoregions"] = (
    ("y", "x"),
    data[::-1, :, 1],
)  # Invert and fill NaN values
ds["ecoregions"].attrs = ds.attrs  # Copy attributes
ds = ds.sel(x=slice(-180, -27), y=slice(20, 75))  # Select a specific spatial region

for var in ds:
    ds_final[var] = ds[var]


ds_final = ds_final.sel(x=slice(-170, -50), y=slice(20, 75))
# ds_cali = ds.sel(
#     x=slice(-128, -95), y=slice(32, 58)
# )  # Select a specific spatial region

# %%

eco_dict = {
    "eco_code": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "eco_name": [
        "water snow ice",
        "arctic",
        "tundra",
        "boreal",
        "hudson plain",
        "northern forest",
        "forested mountains",
        "west coast mountains",
        "temperate forest",
        "great plains",
        "desert",
        "med. cali.",
        "semiarid highlands",
        "temperate sierras",
        "dry forest",
        "tropical forest",
    ],
    "eco_hex": [
        "#ffffff",
        "#6a91cb",
        "#9fabd7",
        "#91c5eb",
        "#3db1be",
        "#afdee5",
        "#60bc56",
        "#45c1bd",
        "#bcdb8e",
        "#f8cd9c",
        "#f9dc6b",
        "#d2e5b8",
        "#dbd492",
        "#bcdb8e",
        "#ef8265",
        "#c774af",
    ],
    "land_code": [0, 1, 2, 3, 4, 5],
    "land_name": [
        "water snow ice",
        "forest",
        "shrubland",
        "savanna",
        "grassland",
        "cropland",
    ],
    "land_hex": [
        "#ffffff",
        "#00aa41",
        "#c1b568",
        "#ffb500",
        "#85f3a5",
        "#fcff88",
        "#b6b7b7",
    ],
}


fig = plt.figure(figsize=(14, 4))
ax = fig.add_subplot(1, 1, 1, projection=ds.salem.cartopy())

# Create a colormap from the hex colors in eco_dict
hex_colors = eco_dict["eco_hex"]
levels = eco_dict["eco_code"]

cmap = mcolors.ListedColormap(hex_colors)
bounds = np.arange(len(levels) + 1) - 0.5
norm = mcolors.BoundaryNorm(bounds, cmap.N)

# Plot the pcolormesh using the hex colors
pc = ax.pcolormesh(
    ds_final["x"], ds_final["y"], ds_final["ecoregions"], cmap=cmap, norm=norm
)

# Add coastlines and borders
ax.coastlines()
ax.add_feature(cartopy.feature.BORDERS)
ax.set_title("Ecoregions", fontsize=20)

# Create custom colorbar with eco_name labels
cbar = plt.colorbar(
    pc, ax=ax, boundaries=bounds, ticks=np.arange(len(levels)), pad=0.01
)
cbar.ax.set_yticklabels([name.title() for name in eco_dict["eco_name"]])
cbar.ax.tick_params(size=0)  # Remove tick lines

# save as png
fig.savefig(
    str(data_dir) + f"/images/frp-paper/map-eco.png",
    bbox_inches="tight",
    dpi=240,
)


# %%

fig = plt.figure(figsize=(14, 4))
ax = fig.add_subplot(1, 1, 1, projection=ds.salem.cartopy())

# Create a colormap from the hex colors in eco_dict
hex_colors = eco_dict["land_hex"]
levels = eco_dict["land_code"]

cmap = mcolors.ListedColormap(hex_colors)
bounds = np.arange(len(levels) + 1) - 0.5
norm = mcolors.BoundaryNorm(bounds, cmap.N)

# Plot the pcolormesh using the hex colors
pc = ax.pcolormesh(
    ds_final["x"], ds_final["y"], ds_final["land_cover"], cmap=cmap, norm=norm
)

# Add coastlines and borders
ax.coastlines()
ax.add_feature(cartopy.feature.BORDERS)
ax.set_title("Land Cover", fontsize=20)

# Create custom colorbar with eco_name labels
cbar = plt.colorbar(
    pc, ax=ax, boundaries=bounds, ticks=np.arange(len(levels)), pad=0.01
)
cbar.ax.set_yticklabels([name.title() for name in eco_dict["land_name"]])
cbar.ax.tick_params(size=0)  # Remove tick lines


## save as png
fig.savefig(
    str(data_dir) + f"/images/frp-paper/map-land-cover.png",
    bbox_inches="tight",
    dpi=240,
)


# df_forest = pd.read_csv(str(data_dir) + "/frp/curves/boreal.csv").T[2:]
# df_forest['datetime'] = pd.date_range('2024-07-04', '2024-07-05', freq='10min')[:-1]
# df_forest.set_index('datetime', inplace=True)
# df_hourly = df_forest.resample('h').mean()
# df_hourly = df_hourly.astype(float).round(3)
# df_hourly.index = df_hourly.index.hour
# df_hourly = df_hourly.T
# df_hourly.to_csv(str(data_dir) + "/frp/curves/boreal-hourly.csv", index=False)


# %%
