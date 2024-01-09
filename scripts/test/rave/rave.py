#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import context
import salem
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime

from utils.compressor import compressor

from context import root_dir

from herbie import Herbie
import pandas as pd

import matplotlib.pyplot as plt
import cartopy.crs as ccrs


## open case study json file
with open(str(root_dir) + f"/json/fire-cases.json", "r") as fp:
    case_dict = json.load(fp)

# ds_13km = xr.open_dataset("/Volumes/WFRT-Ext24/rave/RAVE-HrlyEmiss-13km_v1r3_blend_s202309271500000_e202309271559590_c202309271702540.nc")
ds_3km = xr.open_dataset(
    "/Volumes/WFRT-Ext24/rave/RAVE-HrlyEmiss-3km_v1r3_blend_s202309271500000_e202309271559590_c202309271702540.nc"
)


grid = salem.Grid(
    nxny=(len(ds_3km["grid_xt"]), len(ds_3km["grid_yt"])),
    dxdy=(
        ds_3km.attrs["geospatial_lon_resolution"],
        ds_3km.attrs["geospatial_lat_resolution"],
    ),
    x0y0=(ds_3km.attrs["geospatial_lon_min"] - 360, ds_3km.attrs["geospatial_lat_min"]),
    proj=salem.wgs84,
)


# lon_rave = ds_3km['grid_lon'].values
# lat_rave = ds_3km['grid_lat'].values
# lon, lat = grid.ll_coordinates
grid_ds = grid.to_dataset()
grid_ds["FRP_MEAN"] = (("y", "x"), np.nan_to_num(ds_3km["FRP_MEAN"])[0, ::-1])

grid_ds["FRP_MEAN"].attrs = grid_ds.attrs

grid_ds = grid_ds.sel(x=slice(-180, -27))

grid_ds["FRP_MEAN"].salem.quick_map()


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
