#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import os
import context
import salem
import dask
import joblib
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime

from utils.ml_data import MLDATA
from utils.firep import FIREP
from utils.plot_fire_case import plot_fire, drop_outside_std
from utils.solar_hour import get_solar_hours
import matplotlib.dates as mdates

from scipy import stats
from utils.stats import MBE, RMSE, MAE
from sklearn.metrics import r2_score

import geopandas as gpd
import rasterio
import matplotlib.pyplot as plt
import matplotlib
from rasterio.plot import show  # This will be replaced by imshow
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
from matplotlib_scalebar.scalebar import ScaleBar

from context import root_dir, data_dir

# Update Matplotlib parameters for better aesthetics
matplotlib.rcParams.update({"font.size": 16})
plt.rc("font", family="sans-serif")
plt.rc("text", usetex=True)

######################################################
# ID = 25723697
# year = 2022
# fig_title = "McFarland Fire, California, United States"
######################################################
ID = 26695902
year = 2023
fig_title = "Northwest Territories, Canada"
hour_interval = 3
tiff_file_path = "/Users/crodell/fwf/data/fires/nwt-fire-2023.tif"
######################################################
save_fig = True
paper_fig = True
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense-Main"
method = "averaged-v19"
ml_pack = "tf"
target_vars = "FRP"
plot_method = "mean"
persist = True
dt = 12
model_dir = str(data_dir) + f"/mlp/{ml_pack}/{method}/{target_vars}/{mlp_test_case}"
with open(f"{model_dir}/config.json", "r") as json_data:
    config = json.load(json_data)["user_config"]
config["ID"] = ID
config["year"] = year
firep = FIREP(config=config)
firep_df = firep.open_firep()
jj = firep_df[firep_df["id"] == ID].index[0]
fire_i = firep_df.iloc[jj : jj + 1]


# Function to convert degrees to meters at a given latitude
def degrees_to_meters(resolution, latitude):
    meters_per_degree_lat = 111320  # constant for latitude
    meters_per_degree_lon = 111320 * np.cos(
        np.radians(latitude)
    )  # varies with latitude
    return resolution * meters_per_degree_lat, resolution * meters_per_degree_lon


# Assuming `fire_i` is your GeoDataFrame that contains the fire perimeter
# Extract the geometry directly from the `fire_i` GeoDataFrame
fire_perimeter = gpd.GeoDataFrame({"geometry": fire_i["geometry"]})

# Open the GeoTIFF image and read it into memory
with rasterio.open(tiff_file_path) as tif:
    # Read RGB bands and convert to float for processing
    img_data = tif.read([1, 2, 3]).astype(float)
    bounds = tif.bounds
    tif_transform = tif.transform
    tif_crs = tif.crs
    resolution = tif.res[0]  # Get resolution of the raster, likely in degrees

# Convert resolution to meters at the latitude of the image
latitude_center = (bounds.top + bounds.bottom) / 2  # Midpoint of the image latitude
res_lat_meters, res_lon_meters = degrees_to_meters(resolution, latitude_center)

# Average the two resolutions (latitude and longitude) to use for the scale bar
average_resolution_meters = (res_lat_meters + res_lon_meters) / 2

# Reproject the fire perimeter to match the CRS of the TIFF (if needed)
fire_perimeter = fire_perimeter.to_crs(tif_crs)

# ------------------- Enhanced Color Plotting -------------------
# Function to normalize the image data
def normalize_image(img):
    img_min = img.min(axis=(1, 2), keepdims=True)
    img_max = img.max(axis=(1, 2), keepdims=True)
    img_norm = (img - img_min) / (img_max - img_min)
    return img_norm


# Normalize the image data
img_normalized = normalize_image(img_data)

# Apply gamma correction
gamma = 1.2  # Adjust gamma as needed ( >1 darkens the image, <1 brightens it)
img_gamma_corrected = np.power(img_normalized, gamma)

# Transpose the image data to match Matplotlib's (Height, Width, Channels) format
img_display = np.transpose(img_gamma_corrected, (1, 2, 0))

# ------------------- Plot the Enhanced TIFF Image -------------------
fig, ax = plt.subplots(
    figsize=(14, 8)
)  # Increase the width from 10 to 14 for a wider image

# Display the image with enhanced colors using imshow
im = ax.imshow(
    img_display,
    origin="upper",
    extent=(bounds.left, bounds.right, bounds.bottom, bounds.top),
    aspect="auto",
    interpolation="nearest",
)

# Overlay the fire perimeter
fire_perimeter.plot(ax=ax, edgecolor="red", linewidth=0.5, facecolor="none")

# Add the scale bar using matplotlib_scalebar
scalebar = ScaleBar(
    dx=average_resolution_meters, units="km", location="lower left"
)  # Now in meters
ax.add_artist(scalebar)
ax.set_ylabel("Latitude")
ax.set_xlabel("Longitude")

# Display the area burned
area_burned = 1678.62  # Area in square kilometers

# Set titles
ax.set_title(
    f"Fire ID: {ID}, Start: 2023-08-04, Stop: 2023-09-23, Area Burned: {area_burned:.2f} "
    + r"$km^{2}$",
    y=1.02,
    fontsize=16,
)
fig.suptitle("Northwest Territories, Canada", fontsize=22, y=0.96)

# ------------------- Inset Map -------------------
# Define the position of the inset axes [left, bottom, width, height] in figure coordinates
# Adjust these values as needed to position the inset appropriately
inset_position = [0.3, 0.675, 0.2, 0.2]  # [left, bottom, width, height]

# Create the inset axes with Cartopy projection
inset_ax = fig.add_axes(inset_position, projection=ccrs.PlateCarree())

# Set the extent to North America
inset_ax.set_extent([-165, -50, 10, 80], crs=ccrs.PlateCarree())

# Add geographic features
# Ocean is added to provide a white background
inset_ax.add_feature(cfeature.OCEAN, color="white", zorder=2)

# Add US states and Canadian provinces shapefiles
states_provinces = cfeature.NaturalEarthFeature(
    category="cultural",
    name="admin_1_states_provinces_shp",
    scale="50m",
    facecolor="none",
)
inset_ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
inset_ax.coastlines("50m", linewidth=0.8, zorder=5)


# Plot the main map location on the inset
# Get the centroid of the main map's bounds
main_map_center_lon = (bounds.left + bounds.right) / 2
main_map_center_lat = (bounds.top + bounds.bottom) / 2

# Plot a red dot or marker
inset_ax.plot(
    main_map_center_lon,
    main_map_center_lat,
    marker="o",
    markersize=7,
    markeredgecolor="black",
    markerfacecolor="red",
    transform=ccrs.PlateCarree(),
    zorder=10,
)

# Optionally, add a label
# inset_ax.text(main_map_center_lon + 5, main_map_center_lat + 5, 'Main Map Location',
#              transform=ccrs.PlateCarree(), fontsize=8, color='black')

# Add a rectangle on the inset to indicate the main map area
# Define the extent of the main map in the inset
inset_extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
inset_ax.add_patch(
    plt.Rectangle(
        (inset_extent[0], inset_extent[2]),
        inset_extent[1] - inset_extent[0],
        inset_extent[3] - inset_extent[2],
        linewidth=1,
        edgecolor="blue",
        facecolor="none",
        transform=ccrs.PlateCarree(),
        zorder=6,
    )
)


# -------------------------------------------------

# Save or display the figure
if save_fig:
    fig.savefig("/Users/crodell/ams-frp/nwt-fire-map.pdf", bbox_inches="tight")
    fig.savefig("/Users/crodell/ams-frp/nwt-fire-map.png", bbox_inches="tight", dpi=200)
else:
    plt.show()
