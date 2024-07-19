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
from utils.solar_hour import get_solar_hours
from scipy.ndimage import convolve

from context import data_dir


wrf_ds = salem.open_xr_dataset(str(data_dir) + "/static/static-vars-wrf-d03.nc")

curve_ds = salem.open_xr_dataset(str(data_dir) + "/static/curves-rave-3km.nc")
curve_ds["CLIMO_FRP"] = curve_ds["OFFSET_NORM"] * curve_ds["MAX"]
curves_roi = wrf_ds.salem.transform(curve_ds, interp="nearest")
curves_roi.to_netcdf(str(data_dir) + "/static/curves-wrf-d03.nc", mode="w")

# fire_time = ds.time.values
# hour_one = pd.Timestamp(fire_time[0]).hour
# curves_roi = curves_roi.roll(time = -hour_one, roll_coords=True)

# CLIMO_FRP = curve_ds['CLIMO_FRP'].values
# CLIMO_FRP = CLIMO_FRP[CLIMO_FRP>0.1]


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


# ds_final = ds_final.sel(
#   x=slice(-170, -50), y=slice(20, 75)
# )


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


df = pd.read_csv(str(data_dir) + "/frp/curves/FRP_diurnal_climatology.csv")
# df_groups = df_curves.groupby('Land Cover')


# Assuming ds_final contains the required 2D arrays for land cover and ecoregions
land_cover = ds_final["land_cover"].values
ecoregions = ds_final["ecoregions"].values

# Check unique values in the arrays
unique_land_cover = np.unique(land_cover)
unique_ecoregions = np.unique(ecoregions)
print(f"Unique land cover codes: {unique_land_cover}")
print(f"Unique ecoregion codes: {unique_ecoregions}")

# Create a complete set of all possible combinations of land cover and ecoregion codes
complete_grid = pd.MultiIndex.from_product(
    [unique_land_cover, unique_ecoregions], names=["Land Cover Code", "Ecoregion Code"]
).to_frame(index=False)

# Merge the complete grid with the CSV DataFrame
merged_df = pd.merge(
    complete_grid, df, on=["Land Cover Code", "Ecoregion Code"], how="left"
)

# Fill missing values with a default value, e.g., NaN or 0
for var in list(df)[4:]:
    merged_df[var] = merged_df[var].fillna(np.nan)

# Create a DataFrame with the 2D arrays to use for merging
grid_df = pd.DataFrame(
    {"Land Cover Code": land_cover.ravel(), "Ecoregion Code": ecoregions.ravel()}
)

# Merge the grid DataFrame with the completed merged DataFrame to get the maximum values
final_df = pd.merge(
    grid_df, merged_df, on=["Land Cover Code", "Ecoregion Code"], how="left"
)

hour_list = []
for var in list(df)[4:]:
    # Extract the 'MAX' column values
    max_values = final_df[var]

    # Reshape the result back to the original grid shape
    max_values_grid = max_values.values.reshape(land_cover.shape)

    # Add the max_values_grid to ds_final
    ds_final[var] = (
        ("y", "x"),
        max_values_grid,
    )
    ds_final[var] = (
        ds_final[var]
        .interpolate_na(dim="x", method="nearest")
        .interpolate_na(
            dim="y",
            method="nearest",
        )
    )
    ds_final[var].attrs = ds_final.attrs  # Copy attributes
    if var[0] == "h":
        hour_list.append(ds_final[var].values)


# ds_final["MAX"].plot()
# # Check the resulting values
# print(ds_final['MAX'].values)

fig = plt.figure(figsize=(14, 4))
ax = fig.add_subplot(1, 1, 1, projection=ds.salem.cartopy())
# Plot the pcolormesh using the hex colors
pc = ax.pcolormesh(ds_final["x"], ds_final["y"], ds_final["hh12"])
# Add coastlines and borders
ax.coastlines()
ax.add_feature(cartopy.feature.BORDERS)
ax.set_title("Max FRP", fontsize=20)
# Create custom colorbar with eco_name labels
cbar = plt.colorbar(pc, ax=ax, pad=0.01)


da = xr.Dataset(
    data_vars=dict(
        NORM_FRP=(["time", "y", "x"], np.stack(hour_list)),
    ),
    coords=dict(
        x=ds_final["x"],
        y=ds_final["y"],
        time=pd.date_range("2024-05-01", "2024-05-02", freq="h")[:-1],
    ),
    attrs=dict(
        description="Normalized FRP",
        units="",
    ),
)

fwf_ds = get_solar_hours(da)


NORM_FRP = da["NORM_FRP"].values
solar_hour = fwf_ds["solar_hour"].round().values.astype(int) - 1
shape = NORM_FRP.shape

fwf_ds["OFFSET_NORM"] = (
    ("time", "y", "x"),
    np.stack(
        [
            NORM_FRP[solar_hour[i], np.arange(shape[1])[:, None], np.arange(shape[2])]
            for i in range(shape[0])
        ]
    ),
)
fwf_ds["OFFSET_NORM"].attrs = ds.attrs

fig = plt.figure(figsize=(14, 4))
ax = fig.add_subplot(1, 1, 1, projection=ds.salem.cartopy())
# Plot the pcolormesh using the hex colors
pc = ax.pcolormesh(fwf_ds["x"], ds_final["y"], fwf_ds["OFFSET_NORM"].isel(time=0))
# Add coastlines and borders
ax.coastlines()
ax.add_feature(cartopy.feature.BORDERS)
ax.set_title("00Z NORM FRP", fontsize=20)
# Create custom colorbar with eco_name labels
cbar = plt.colorbar(pc, ax=ax, pad=0.01)
fwf_ds = fwf_ds.drop("solar_hour")
fwf_ds["MAX"] = ds_final["MAX"]
for var in fwf_ds:
    fwf_ds[var].attrs = ds.attrs
fwf_ds.attrs = ds.attrs
fwf_ds.to_netcdf(str(data_dir) + "/static/curves-rave-3km.nc", mode="w")

# xx =2000
# yy =900
# fwf_ds['OFFSET_NORM'].isel(x=xx,y=yy).plot()
# print('land_cover ', ds_final['land_cover'].isel(x=xx,y=yy).values)
# print('ecoregions ', ds_final['ecoregions'].isel(x=xx,y=yy).values)

# # Resample from hourly to 10-minute intervals
# resampled_data = fwf_ds['OFFSET_NORM'].resample(time='10T').asfreq()

# # Interpolate missing data
# interpolated_data = resampled_data.interpolate_na(dim='time', method='linear')

# mean_hourly_data = interpolated_data.resample(time='h').mean()

# fwf_ds['TEST'] = (("time", "y", "x"), mean_hourly_data.values)

# fwf_ds['TEST'].attrs = ds.attrs


# # Loop through each cell in the 2D arrays
# for i in range(land_cover.shape[0]):
#     for j in range(land_cover.shape[1]):
#         land_code = land_cover[i, j]
#         eco_code = ecoregions[i, j]

#         # Get the rows from the DataFrame that match the land and eco codes
#         matching_rows = df[(df['Land Cover Code'] == land_code) & (df['Ecoregion Code'] == eco_code)]

#         # Find the maximum value from the matching rows
#         if not matching_rows.empty:
#             max_value = matching_rows['MAX'].max()  # Replace 'value' with the correct column name
#             max_values[i, j] = max_value
#         else:
#             max_values[i, j] = 0 # Assign NaN if no matching rows are found

# # Now, max_values contains the maximum values for each grid cell
# print(max_values)


# %%
