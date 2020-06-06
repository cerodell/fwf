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


# cm = linear.RdBu_04.scale(float(ds.F.min()), float(ds.F.max()))
# Setup colormap
# colors = ["#0000FF","#00E000","#FFFF00", "#E0A000", "#FF0000"]
# levels = np.arange(70,101,1)
# vmin , vmax = 70, 100
# cmap  = cm.LinearColormap(colors, vmin = vmin, vmax = vmax).to_step(len(levels))

# contourf = plt.contourf(np.array(lons), np.array(lats), np.array(ds.F[18]), levels = levels, \
#                         alpha = 0.5, colors = colors, linestyles = 'None', vmin = vmin, vmax = vmax)
# plt.close()

# # Convert matplotlib contourf to geojson
# ffmc = geojsoncontour.contourf_to_geojson(
#     contourf=contourf,
#     min_angle_deg=3.0,
#     ndigits=2,
#     stroke_width=0.5,
#     fill_opacity=0.5)

# with open(str(data_dir) + '/json/test.geojson', 'w') as outfile:
#     geojson.dump(geofile, outfile, sort_keys=True)


fwimap = folium.Map(
         location=[float(ds.CEN_LAT), float(ds.CEN_LON)], 
         zoom_start = 3,
         tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
	     attr = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, \
            GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community')



# Plot the contour plot on folium
# folium.GeoJson(
#     ffmc,
#     style_function=lambda x: {
#         'color':     x['properties']['stroke'],
#         'weight':    x['properties']['stroke-width'],
#         'fillColor': x['properties']['fill'],
#         'opacity':   0.5,
#     }).add_to(fwimap)



# # Add the colormap to the folium map
# cmap.caption = 'FFMC'
# fwimap.add_child(cmap)

# # # Fullscreen mode
# plugins.Fullscreen(position='topright', force_separate_button=True).add_to(fwimap)


image = plt.imshow(np.array(ds.F[18]))
bounds = [[np.min(lats), np.min(lons)], [np.max(lats), np.min(lons)]]
folium.raster_layers.ImageOverlay(image, bounds, origin='upper', colormap=None, \
            mercator_project=False, pixelated=True, name=None, overlay=True, control=True, show=True)

# # # Plot the data

fwimap.save(str(leaflet_dir) + '/html/index.html')

# ### Timer
print("Run Time: ", datetime.now() - startTime)



















