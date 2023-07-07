obs_ds = xr.open_dataset(
    "/Users/crodell/fwf/data/obs/observations-all-20191231-20221231.nc"
)
obs_ds1 = obs_ds.sel(wmo=1305, time=slice("2021-06-20", "2021-07-01")).load()
import salem

ds = salem.open_xr_dataset("/Users/crodell/fwf/data/static/static-vars-wrf-d03.nc")


import context
import io
import json
import requests
import salem

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from glob import glob
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from wrf import ll_to_xy, xy_to_ll
from datetime import datetime, date, timedelta
from utils.compressor import compressor, file_size


ds = xr.open_dataset("/Users/crodell/fwf/data/intercomp/02/wrf/20210101-20221231.nc")
ds1 = xr.open_dataset("/Users/crodell/fwf/data/intercomp/02/wrf/20210101-20221231.nc")

## convert lat lon coordinate in master obs to meter base x y as define by wrf polar stere projection
df = pd.DataFrame(
    data={
        "lons": obs_ds.lons.values,
        "lats": obs_ds.lats.values,
        "wmo": obs_ds.wmo.values,
    }
)


############################### Functions #############################


def get_locs(pyproj_srs):
    # get_locs_time = datetime.now()
    gpm25 = gpd.GeoDataFrame(
        df,
        crs="EPSG:4326",
        #  crs="+init=epsg:4326",
        geometry=gpd.points_from_xy(df["lons"], df["lats"]),
    ).to_crs(pyproj_srs)

    x = xr.DataArray(
        np.array(gpm25.geometry.x),
        dims="wmo",
        coords=dict(wmo=gpm25.wmo.values),
    )
    y = xr.DataArray(
        np.array(gpm25.geometry.y),
        dims="wmo",
        coords=dict(wmo=gpm25.wmo.values),
    )
    # print("Locs Time: ", datetime.now() - get_locs_time)

    return x, y


x, y = get_locs(ds.attrs["pyproj_srs"])

ds_elev = ds["HGT"].interp(west_east=x, south_north=y, method="nearest")
