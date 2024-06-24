#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import salem
import json

import numpy as np
import pandas as pd
import xarray as xr

from context import data_dir

import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.cm as cm

from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm


ds = salem.open_xr_dataset(str(data_dir) + "/fwf-data/fwf-hourly-d02-2024060406.nc")


# %%
frp_i = ds.isel(time=18)
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1)
var = "FRP"
cmap_name = "custom"
# vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
# levels = cmaps[var]["levels"]
vmin, vmax = 0, 2500
# levels = [0,15,50,100,150,200,250,300,400,500,600,700,1000,1400,1800,2200,2500]
levels = [
    0,
    15,
    30,
    50,
    100,
    125,
    150,
    200,
    250,
    300,
    350,
    400,
    500,
    700,
    1000,
    1500,
    2000,
    2500,
]
# colors = np.vstack(([1, 1, 1, 1], plt.get_cmap(cmap_name)(np.linspace(0, 1, 256))))
# custom_cmap = LinearSegmentedColormap.from_list("custom_YlOrRd", colors)

# custom_cmap = LinearSegmentedColormap.from_list('custom_cmap', ['#ffffff','#fff602', '#f88d00', '#FA7000',  '#fc4f00', '#cf352e', '#FF5349',  '#ff0200','#f415c2'])
# custom_cmap = LinearSegmentedColormap.from_list('custom_cmap', ['#ffffff','#fff602', '#f88d00', '#FA7000',  '#fc4f00', '#cf352e', '#FF5349', '#ff0200',  '#BE0A01','#f415c2'])
# custom_cmap = LinearSegmentedColormap.from_list('custom_cmap', ['#ffffff','#fff832', '#fae83b', '#fcda3d',  '#fdc93a', '#FA7000', '#fcb535', '#f99f34',  '#ff8533','#fd7533', '#fe4832', '#fa3e33', '#f5474d', '#f5468d', '#f545ce', '#e140aa' ])


custom_cmap = LinearSegmentedColormap.from_list(
    "custom_cmap", ["#ffffff", "#FAFA33", "#FA7000", "#ff0e00", "#8b0000", "#f545ce"]
)

# custom_cmap = cm.get_cmap(cmap_name)
norm = BoundaryNorm(levels, custom_cmap.N)
frp_i[var].attrs["units"] = ""
frp_i[var].salem.quick_map(
    cmap=custom_cmap, ax=ax, norm=norm, oceans=True, lakes=True, extend="max"
)
ax.set_title(f"Fire Radiative Power (MW) \n")
plt.savefig(str(data_dir) + f"/images/frp-paper/camp-{cmap_name}.png", dpi=250)

# %%
# colors = hex_colors
# # title, colors = str(cmaps[var]["title"]), cmaps[var]["colors"]


import matplotlib.colors as mcolors


def get_hex_colors(cmap, n_colors=10):
    """
    Get a list of hex color codes from a colormap.

    Parameters:
    cmap_name (str): The name of the colormap.
    n_colors (int): The number of colors to extract from the colormap.

    Returns:
    list: A list of hex color codes.
    """
    colors = [mcolors.rgb2hex(cmap(i / n_colors)) for i in range(n_colors)]
    return colors


hex_colors = get_hex_colors(custom_cmap, n_colors=len(levels))
custom_cmap2 = LinearSegmentedColormap.from_list(
    "custom_cmap", [matplotlib.colors.hex2color(color) for color in hex_colors]
)

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1)
var = "FRP"
cmap_name = "custom"
vmin, vmax = 0, 2500
levels = [
    0,
    15,
    30,
    50,
    100,
    125,
    150,
    200,
    250,
    300,
    350,
    400,
    500,
    700,
    1000,
    1500,
    2000,
    2500,
]
# custom_cmap = cm.get_cmap(cmap_name)
norm = BoundaryNorm(levels, custom_cmap2.N)
frp_i[var].attrs["units"] = ""
frp_i[var].salem.quick_map(
    cmap=custom_cmap2, ax=ax, norm=norm, oceans=True, lakes=True, extend="max"
)
ax.set_title(f"Fire Radiative Power (MW) \n")

# %%
