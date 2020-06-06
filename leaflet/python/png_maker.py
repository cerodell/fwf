import context
import math
import numpy as np
import pandas as pd
import xarray as xr
import folium
# from branca.colormap import linear
import branca.colormap as cm
import geojsoncontour
import matplotlib.pyplot as plt
import cartopy.crs as crs
from folium import plugins
import geojson
# from folium.plugins import TimestampedGeoJson
from datetime import datetime, date, timedelta
startTime = datetime.now()

from fwi.utils.ubc_fwi.fwf import FWF
from context import data_dir,leaflet_dir, xr_dir

"""######### get directory to yesterdays hourly/daily .zarr files.  #############"""
# yesterday = date.today() - timedelta(days=1)
# zarr_filein = yesterday.strftime('%Y-%m-%dT00.zarr')
zarr_filein = "2020-06-05T00.zarr"
hourly_file_dir = str(xr_dir) + str("/hourly/") + zarr_filein
ds = xr.open_zarr(hourly_file_dir)
lats, lons = ds.XLAT, ds.XLONG



# levels = np.arange(70,101,1)
vmin , vmax = 70, 100
# cmap  = cm.LinearColormap(colors, vmin = vmin, vmax = vmax).to_step(len(levels))

contourf = plt.pcolormesh(np.array(lons), np.array(lats), np.array(ds.F[18]), \
                        alpha = 0.5, vmin = vmin, vmax = vmax)
plt.savefig("/bluesky/fireweather/fwf/Images/test.png")
# ### Timer
print("Run Time: ", datetime.now() - startTime)