#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import context
import salem
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime
import plotly.express as px

from utils.compressor import compressor
from utils.geoutils import make_KDtree

from context import root_dir

import pandas as pd

import matplotlib.pyplot as plt
import cartopy.crs as ccrs

var_name = "S"
doi = pd.Timestamp("2021-07-15T20")

rave_pl = sorted(
    Path(f"/Volumes/WFRT-Ext24/rave/{doi.strftime('%Y')}/{doi.strftime('%m')}/").glob(
        f"RAVE-HrlyEmiss*"
    )
)


era5_pl = sorted(
    Path(
        f"/Volumes/WFRT-Ext23/fwf-data/ecmwf/era5-land/04/{doi.strftime('%Y%m')}/"
    ).glob(f"fwf-hourly*")
)

climo_ds = xr.open_zarr(
    f"/Volumes/WFRT-Ext23/ecmwf/era5-land/{var_name}-hourly-climatology-19910101-20201231-compressed.zarr"
)[var_name].sel(dayofyear=int(doi.strftime("%j")) - 1, hour=int(doi.strftime("%H")))

climo_ds_mean = xr.open_zarr(
    f"/Volumes/WFRT-Ext23/ecmwf/era5-land/{var_name}-hourly-climatology-19910101-20201231-mean.zarr"
)[var_name].sel(dayofyear=int(doi.strftime("%j")) - 1, hour=int(doi.strftime("%H")))

climo_ds_std = xr.open_zarr(
    f"/Volumes/WFRT-Ext23/ecmwf/era5-land/{var_name}-hourly-climatology-19910101-20201231-std.zarr"
)[var_name].sel(dayofyear=int(doi.strftime("%j")) - 1, hour=int(doi.strftime("%H")))


rave_ds = xr.open_dataset(str(rave_pl[int(doi.strftime("%d")) - 1]))

era5_ds = xr.open_dataset(str(era5_pl[int(doi.strftime("%d")) - 1]))
era5_ds["time"] = era5_ds["Time"]


frp_ds = salem.Grid(
    nxny=(len(rave_ds["grid_xt"]), len(rave_ds["grid_yt"])),
    dxdy=(
        rave_ds.attrs["geospatial_lon_resolution"],
        rave_ds.attrs["geospatial_lat_resolution"],
    ),
    x0y0=(
        rave_ds.attrs["geospatial_lon_min"] - 360,
        rave_ds.attrs["geospatial_lat_min"],
    ),
    proj=salem.wgs84,
).to_dataset()


frp_ds = frp_ds.assign_coords({"time": rave_ds.time.values})
# rave_ds = xr.where(rave_ds['QA'] != 3, rave_ds,  np.nan)
FRP_MEAN = xr.where(rave_ds["QA"] != 3, rave_ds["FRP_MEAN"], np.nan)
frp_ds["FRP_MEAN"] = (("time", "y", "x"), FRP_MEAN.data[:, ::-1])

frp_ds["FRP_MEAN"].attrs = frp_ds.attrs
frp_ds = frp_ds.sel(x=slice(-180, -27), y=slice(20, 75)).sel(time=doi)

lon, lat = frp_ds.salem.grid.ll_coordinates

# frp_locs = np.argwhere(~np.isnan(frp_ds["FRP_MEAN"].values))

frp_locs = np.argwhere(frp_ds["FRP_MEAN"].values > 100)


lon_locs = lon[frp_locs[:, 0], frp_locs[:, 1]]
lat_locs = lat[frp_locs[:, 0], frp_locs[:, 1]]
frp_values = frp_ds["FRP_MEAN"].values[frp_locs[:, 0], frp_locs[:, 1]]


y, x = make_KDtree("ecmwf", "era5-land", lat_locs, lon_locs)
fwi_array = era5_ds[var_name].sel(time=doi).values
xlats = era5_ds["XLAT"].values[y, x]
xlons = era5_ds["XLONG"].values[y, x]

fwi_values = fwi_array[y, x]
fwi_max = climo_ds.sel(quantile=0.99).values[y, x]
fwi_min = climo_ds.sel(quantile=0).values[y, x]
fwi_norm = (fwi_values - fwi_min) / (fwi_max - fwi_min)

fwi_mean = climo_ds_mean.values[y, x]
fwi_std = climo_ds_std.values[y, x]
fwi_stand = (fwi_values - fwi_mean) / fwi_std


# fig = plt.figure(figsize=(6, 6))
# ax = fig.add_subplot(3, 1, 1)
# ax.scatter(fwi_values, frp_values)

# ax = fig.add_subplot(3, 1, 2)
# ax.scatter(fwi_norm, frp_values)

# ax = fig.add_subplot(3, 1, 3)
# ax.scatter(fwi_stand, frp_values)

df = pd.DataFrame(
    {
        "lats": lat_locs,
        "lons": lon_locs,
        "frp": frp_values,
        "fwi": fwi_values,
        "fwi_norm": fwi_norm,
        "fwi_stand": fwi_stand,
        "fwi_max": fwi_max,
        "fwi_min": fwi_min,
        "xlats": xlats,
        "xlons": xlons,
    }
)

fig = px.scatter_mapbox(
    df,
    lat="lats",
    lon="lons",
    color="frp",
    # size=f"fwi",
    color_continuous_scale="jet",
    center={"lat": 55.0, "lon": -96.0},
    hover_data=[
        "frp",
        "fwi",
        "fwi_norm",
        "fwi_stand",
        "fwi_max",
        "fwi_min",
        "xlats",
        "xlons",
    ],
    # hover_data=["frp"],
    mapbox_style="carto-positron",
    range_color=[0, 300],
    zoom=1.5,
    labels={"colorbar": "FRP MW"},
)
# fig.layout.coloraxis.colorbar.title = "FRP"
fig.update_layout(
    margin=dict(l=0, r=100, t=30, b=10),
    autosize=False,
    # width=700,
    # height=500,
    showlegend=False,
)
fig.show()


# frp_ds["FRP_MEAN"].isel(time = 0).salem.quick_map()
