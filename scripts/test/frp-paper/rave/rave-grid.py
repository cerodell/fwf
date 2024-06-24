#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import context
import salem
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime
from sklearn.neighbors import KDTree

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

rave_ds = xr.open_dataset(str(rave_pl[int(doi.strftime("%d")) - 1]))


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


# lon_rave = rave_ds['frp_ds_lon'].values
# lat_rave = rave_ds['frp_ds_lat'].values
# lon, lat = frp_ds.ll_coordinates
FRP_MEAN = xr.where(rave_ds["QA"] != 3, rave_ds["PM25"], np.nan)

frp_ds["FRP_MEAN"] = (
    ("y", "x"),
    np.nan_to_num(FRP_MEAN)[int(doi.strftime("%H")) - 1, ::-1],
)

frp_ds["FRP_MEAN"].attrs = frp_ds.attrs

frp_ds = frp_ds.sel(x=slice(-180, -27))

frp_ds["FRP_MEAN"].salem.quick_map(vmax=100, cmap="Reds")


# df_wmo = {
#     "wmo": ds_bias.wmo.values,
#     "lats": ds_bias.lats.values,
#     "lons": ds_bias.lons.values,
#     "elev": ds_bias.elev.values.astype(float),
#     "name": ds_bias.name.values,
#     "tz_correct": ds_bias.tz_correct.values,
# }
# for name in list(ds_bias):
#     df_wmo.update({name: ds_bias[name].values})

# df_wmo = pd.DataFrame(df_wmo)

# smap.set_points(lon.flatten(), lat.flatten())

# smap.visualize(addcbar=False)
