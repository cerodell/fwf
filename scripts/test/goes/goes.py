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
doi = pd.Timestamp("2020-09-09T20")

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
    f"/Volumes/WFRT-Ext22/ecmwf/era5-land/{var_name}-hourly-climatology-19910101-20201231-compressed.zarr"
)[var_name].sel(dayofyear=int(doi.strftime("%j")) - 1, hour=int(doi.strftime("%H")))

rave_ds = xr.open_dataset(str(rave_pl[int(doi.strftime("%d")) - 1]))

era5_ds = xr.open_dataset(str(era5_pl[int(doi.strftime("%d")) - 1]))

frp_ds = salem.Grid(
    nxny=(len(rave_ds["grid_xt"]), len(rave_ds["grid_yt"])),
    dxdy=(
        rave_ds.attrs["geospatial_lon_resolution"],
        rave_ds.attrs["geospatial_lat_resolution"],
    ),
    x0y0=(
        rave_ds.attrs["geospatial_lon_min"] - 359,
        rave_ds.attrs["geospatial_lat_min"],
    ),
    proj=salem.wgs84,
).to_dataset()
lon, lat = frp_ds.salem.grid.ll_coordinates


frp_ds = frp_ds.assign_coords({"time": rave_ds.time.values})
frp_array = rave_ds["FRP_MEAN"].values
frp_ds["FRP_MEAN"] = (("time", "y", "x"), frp_array)
frp_ds["FRP_MEAN"].attrs = frp_ds.attrs
frp_ds = frp_ds.sel(x=slice(-180, -27))


frp_locs = np.argwhere(~np.isnan(frp_array[int(doi.strftime("%H")) - 1, :, :]))

lon_locs = lon[frp_locs[:, 0], frp_locs[:, 1]]
lat_locs = lat[frp_locs[:, 0], frp_locs[:, 1]]
frp_values = frp_array[int(doi.strftime("%H")) - 1, frp_locs[:, 0], frp_locs[:, 1]]


y, x = make_KDtree("ecmwf", "era5-land", lat_locs, lon_locs)
fwi_array = era5_ds[var_name].values
xlats = era5_ds["XLAT"].values[y, x]
xlons = era5_ds["XLONG"].values[y, x]

fwi_values = fwi_array[int(doi.strftime("%H")) - 1, y, x]
fwi_max = climo_ds.sel(quantile=1).values[y, x]
fwi_min = climo_ds.sel(quantile=0).values[y, x]
# fwi_norm = (fwi_values - fwi_min) / (fwi_max - fwi_min)

# fig = plt.figure(figsize=(6,6))
# ax = fig.add_subplot(2,1,1)
# ax.scatter(fwi_values, fwi_norm)

# ax = fig.add_subplot(2,1,2)
# ax.scatter(fwi_norm, frp_values)

df = pd.DataFrame(
    {
        "lats": lat_locs,
        "lons": lon_locs,
        "frp": frp_values,
        "fwi": fwi_values,
        # 'fwi_norm': fwi_norm,
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
    hover_data=["frp", "fwi", "fwi_max", "fwi_min", "xlats", "xlons"],
    mapbox_style="carto-positron",
    # range_color=[vmin, vmax],
    zoom=1.5,
    # labels={"colorbar": '2m Temperature Bias'}
)
fig.layout.coloraxis.colorbar.title = "Bias"
# fig.update_layout(
#     margin=dict(l=0, r=100, t=30, b=10),
#     autosize=False,
#     # width=700,
#     # height=500,
#     showlegend=False,
# )
fig.show()


# frp_ds["FRP_MEAN"].isel(time = 0).salem.quick_map()
