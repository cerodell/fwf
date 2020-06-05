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


# cm = linear.RdBu_04.scale(float(ds.F.min()), float(ds.F.max()))
# Setup colormap
colors = ['#2b83ba',  '#abdda4',  '#ffffbf',  '#fdae61',  '#d7191c']
levels = len(colors)
cmap  = cm.LinearColormap(colors, vmin=70, vmax=100).to_step(levels)

contourf = plt.contourf(np.array(lons), np.array(lats), np.array(ds.F[18]))
plt.close()

# Convert matplotlib contourf to geojson
geojson = geojsoncontour.contourf_to_geojson(
    contourf=contourf,
    min_angle_deg=3.0,
    ndigits=5,
    stroke_width=1,
    fill_opacity=0.5)


geomap = folium.Map(location=[float(ds.CEN_LAT), float(ds.CEN_LON)], zoom_start = 3)

# Plot the contour plot on folium
folium.GeoJson(
    geojson,
    style_function=lambda x: {
        'color':     x['properties']['stroke'],
        'weight':    x['properties']['stroke-width'],
        'fillColor': x['properties']['fill'],
        'opacity':   0.6,
    }).add_to(geomap)

# Add the colormap to the folium map
cmap.caption = 'FFMC'
geomap.add_child(cmap)

# # Fullscreen mode
plugins.Fullscreen(position='topright', force_separate_button=True).add_to(geomap)

# # Plot the data

geomap.save(str(leaflet_dir) + '/html/index.html')

### Timer
print("Run Time: ", datetime.now() - startTime)



















