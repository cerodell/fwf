import context
import numpy as np
import xarray as xr
import pandas as pd
import salem
import cartopy.crs as crs

from datetime import datetime
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker

from datetime import datetime, date, timedelta


from context import data_dir, root_dir


ds_climo = salem.open_xr_dataset(
    "/Volumes/WFRT-Ext22/atsc413/data/climatology-1991-2021.nc"
)
longitude = slice(-175, -40)
latitude = slice(80, 20)


def convert_longitudes(longitudes):
    converted_longitudes = np.where(longitudes > 180, longitudes - 360, longitudes)
    return converted_longitudes


ds_climo["longitude"] = convert_longitudes(ds_climo["longitude"])

ds_climo = ds_climo.sel(month=7, longitude=longitude, latitude=latitude)

tmax = ds_climo["t2m"].max(dim="hour")

fig = plt.figure(figsize=(12, 4))
ax = fig.add_subplot(1, 1, 1)
(tmax - 273.15).salem.quick_map(prov=True, states=True, oceans=True, cmap="jet", ax=ax)
plt.savefig(
    str(data_dir) + f"/images/norm/max-temp-july.png",
    dpi=250,
    bbox_inches="tight",
)


tpsum = ds_climo["tp"].sum(dim="hour")

fig = plt.figure(figsize=(12, 4))
ax = fig.add_subplot(1, 1, 1)
(tpsum * 1000).salem.quick_map(
    prov=True, states=True, oceans=True, cmap="jet", ax=ax, vmin=0, vmax=8
)
plt.savefig(
    str(data_dir) + f"/images/norm/max-temp-july.png",
    dpi=250,
    bbox_inches="tight",
)
