#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import salem

import numpy as np
import xarray as xr
import pandas as pd


fuel_dir = f"/Volumes/ThunderBay/CRodell/ecmwf/fuel-load/"

moi = pd.Timestamp("2010-06-15")
fuels_2010 = salem.open_xr_dataset(
    fuel_dir + f'{moi.strftime("%Y")}/CFUEL_timemean_{moi.strftime("%Y_%m")}.nc'
).sel(lat=slice(75, 20), lon=slice(-170, -50))
fuels_2010.coords["time"] = moi


moi = pd.Timestamp("2020-06-15")
fuels_2020 = salem.open_xr_dataset(
    fuel_dir + f'{moi.strftime("%Y")}/CFUEL_timemean_{moi.strftime("%Y_%m")}.nc'
).sel(lat=slice(75, 20), lon=slice(-170, -50))
fuels_2020.coords["time"] = moi


fuels_diff = fuels_2020 - fuels_2010


for var in list(fuels_2010):
    fuels_diff[var].attrs = fuels_2010[var].attrs
fuels_diff.attrs = fuels_2010.attrs


fuels_2020["Live_Wood"].salem.quick_map(oceans=True)

fuels_diff["Dead_Wood"].salem.quick_map(oceans=True, vmin=-1, vmax=1, cmap="coolwarm")

fuels_diff["Live_Wood"].salem.quick_map(oceans=True, vmin=-1, vmax=1, cmap="coolwarm")

fuels_diff["Dead_Foliage"].salem.quick_map(
    oceans=True, vmin=-1, vmax=1, cmap="coolwarm"
)

fuels_diff["Live_Leaf"].salem.quick_map(
    oceans=True, vmin=-0.1, vmax=0.1, cmap="coolwarm"
)
