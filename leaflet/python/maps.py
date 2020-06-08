import context
import math
import numpy as np
import pandas as pd
import xarray as xr
import folium
# import json
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


"""######### get directory to hourly/daily .zarr files.  #############"""
hourly_file_dir  = "/Volumes/CER/WFRT/FWI/Data/hourly/2020-06-07T00.zarr"
hourly_ds = xr.open_zarr(hourly_file_dir)

daily_file_dir  = "/Volumes/CER/WFRT/FWI/Data/daily/2020-06-07T00.zarr"
daily_ds = xr.open_zarr(daily_file_dir)
lats, lons = np.array(hourly_ds.XLAT), np.array(hourly_ds.XLONG)

# colors = ["#004ddb", "#004ed9", "#004fd7", "#0050d5", "#0051d2", "#0052d0", "#0054ce", "#0055cc", "#0056ca", "#0057c7", "#0059c5", "#005ac3", "#005bc1", "#005cbe", "#015dbc", "#015fba", "#0160b8", "#0161b5", "#0162b3", "#0163b1", "#0165af", "#0166ac", "#0167aa", "#0168a8", "#0169a6", "#016aa3", "#016ca1", "#016d9f", "#016e9d", "#016f9a", "#017198", "#017296", "#017394", "#017491", "#01758f", "#01778d", "#01788b", "#017988", "#017a86", "#017b84", "#017d82", "#017e80", "#027f7d", "#02807b", "#028179", "#028377", "#028474", "#028572", "#028670", "#02876e", "#02886b", "#028a69", "#028b67", "#028c65", "#028d62", "#028f60", "#02905e", "#02915c", "#029259", "#029357", "#029555", "#029653", "#029750", "#02984e", "#03994c", "#079a4b", "#0a9b4a", "#0d9c49", "#119d47", "#149e46", "#18a045", "#1ba144", "#1ea243", "#22a341", "#25a440", "#29a53f", "#2ca63e", "#2fa73d", "#33a83b", "#36a93a", "#3aaa39", "#3dab38", "#40ac37", "#44ad35", "#47ae34", "#4baf33", "#4eb032", "#52b131", "#55b22f", "#58b32e", "#5cb42d", "#5fb52c", "#63b62b", "#66b729", "#69b928", "#6dba27", "#70bb26", "#74bc25", "#77bd23", "#7abe22", "#7ebf21", "#81c020", "#85c11f", "#88c21d", "#8bc31c", "#8fc41b", "#92c51a", "#96c619", "#99c717", "#9cc816", "#a0c915", "#a3ca14", "#a7cb13", "#aacc11", "#adcd10", "#b1ce0f", "#b4cf0e", "#b8d10d", "#bbd20b", "#bfd30a", "#c2d409", "#c5d508", "#c9d607", "#ccd705", "#d0d804", "#d3d903", "#d6da02", "#dadb01", "#dbda00", "#dbd800", "#dad600", "#d9d400", "#d9d200", "#d8d000", "#d8ce00", "#d7cc00", "#d7ca00", "#d6c800", "#d5c600", "#d5c400", "#d4c200", "#d4c000", "#d3be00", "#d3bc00", "#d2b900", "#d1b700", "#d1b500", "#d0b300", "#d0b100", "#cfaf00", "#cfad00", "#ceab00", "#cda900", "#cda700", "#cca500", "#cca300", "#cba100", "#cb9f00", "#ca9d00", "#ca9b00", "#c99800", "#c89600", "#c89400", "#c79200", "#c79000", "#c68e00", "#c68c00", "#c58a00", "#c48800", "#c48601", "#c38401", "#c38201", "#c28001", "#c27e01", "#c17c01", "#c07a01", "#c07801", "#bf7501", "#bf7301", "#be7101", "#be6f01", "#bd6d01", "#bc6b01", "#bc6901", "#bb6701", "#bb6501", "#ba6301", "#ba6101", "#b95f01", "#b85d01", "#b85b01", "#b75901", "#b75701", "#b75601", "#b75401", "#b75301", "#b65201", "#b65002", "#b64f02", "#b64d02", "#b64c02", "#b64b02", "#b64902", "#b54802", "#b54602", "#b54503", "#b54403", "#b54203", "#b54103", "#b54003", "#b43e03", "#b43d03", "#b43b04", "#b43a04", "#b43904", "#b43704", "#b43604", "#b33504", "#b33304", "#b33204", "#b33005", "#b32f05", "#b32e05", "#b32c05", "#b22b05", "#b22905", "#b22805", "#b22706", "#b22506", "#b22406", "#b22306", "#b12106", "#b12006", "#b11e06", "#b11d06", "#b11c07", "#b11a07", "#b01907", "#b01707", "#b01607", "#b01507", "#b01307", "#b01208", "#b01108", "#af0f08", "#af0e08", "#af0c08", "#af0b08", "#af0a08", "#af0808", "#af0709", "#ae0609", "#ae0409", "#ae0309", "#ae0109", "#ae0009"]
colors = ["#004ddb", "#0057c8", "#0162b4", "#016ca0", "#01778d", "#028179", "#028c65", "#029651", "#19a045", "#37a93a", "#55b22f", "#73bb25", "#91c51a", "#afce10", "#ccd705", "#d9d200", "#d4c000", "#cfae00", "#ca9c00", "#c58a00", "#c07801", "#bb6601", "#b75501", "#b64902", "#b43d03", "#b33105", "#b22406", "#b01807", "#af0c08", "#ae0009"]
# Setup colormap
# colors = ["#0000FF","#00E000","#FFFF00", "#E0A000", "#FF0000"]
# colors = ["#004ddb", "#004ed9", "#004fd7", "#0050d5"]
levels = len(colors)
print(levels)
vmin , vmax = 70, 100
cmap  = cm.LinearColormap(colors, vmin = vmin, vmax = vmax).to_step(len(colors))
contourf = plt.contourf(lons, np.arraylats, np.array(ds.F[18]), levels = levels, \
                        linestyles = 'None', vmin = vmin, vmax = vmax, colors = colors)
# plt.close()

# # # Convert matplotlib contourf to geojson
ffmc = geojsoncontour.contourf_to_geojson(
    contourf=contourf,
    min_angle_deg=3.0,
    ndigits=2,
    stroke_width=0.2,
    fill_opacity=0.95)

# with open(str(data_dir) + '/json/test.geojson', 'w') as outfile:
#     geojson.dump(ffmc, outfile, sort_keys=True)

# geo_dir = str(data_dir) + r'/json/test.geojson'
# with open(r'/Users/rodell/fwf/data/json/test.json') as f:
#     ffmc = geojson.load(f)


dictionary = {"World Imagery":{ "tiles": 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                                "attrs": 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'},
              "NatGeo World Map":{ "tiles": 'https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}',
                                "attrs": 'Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC'},                 
              "Light Gray Base":{ "tiles": 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
                                "attrs": 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'},                  
              "Carto Basemap Light":{ "tiles": 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
                                "attrs": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'},                  
              "Carto Basemap Dark":{ "tiles": 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
                                "attrs": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'},                   
                                
                                }

# dictionary = {"World Imagery":{ "tiles": 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
#                                 "attrs": 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'},
#               "NatGeo World Map":{ "tiles": 'https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}',
#                                 "attrs": 'Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC'},                 
#               "Light Gray Base":{ "tiles": 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
#                                 "attrs": 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'},                  
#               "Carto Basemap Light":{ "tiles": 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
#                                 "attrs": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'},                  
#               "Carto Basemap Dark":{ "tiles": 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
#                                 "attrs": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'},                   
#               "Stamen Toner":{ "tiles": 'https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}{r}.{ext}',
#                                 "attrs": 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'},
#               "Stamen Toner Light":{ "tiles": 'https://stamen-tiles-{s}.a.ssl.fastly.net/toner-lite/{z}/{x}/{y}{r}.{ext}',
#                                 "attrs": 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'},                                
#                                 }

# # dictionary = {"World Imagery":{ "tiles": 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
# #                                 "attrs": 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'},
# #               "NatGeo World Map":{ "tiles": 'https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}',
# #                                 "attrs": 'Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC'},                 
# #               "Light Gray Base":{ "tiles": 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
# #                                 "attrs": 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'},                  
# #               "Carto Basemap Light":{ "tiles": 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
# #                                 "attrs": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'},                            
# #               "Stamen Toner":{ "tiles": 'https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}{r}.{ext}',
# #                                 "attrs": 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'},
# #               "Thunder Forest":{ "tiles": 'https://{s}.tile.thunderforest.com/spinal-map/{z}/{x}/{y}.png?apikey={apikey}',
# #                                 "attrs": '&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>, &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}                                    
# #                                 }


fwimap = folium.Map(
         location=[float(ds.CEN_LAT), float(ds.CEN_LON)], 
         zoom_start = 3)
for key in dictionary.keys():
    folium.TileLayer(dictionary[key]["tiles"], attr = dictionary[key]["attrs"], name = key).add_to(fwimap)
# folium.TileLayer(tiles = tiles[4], attr = attrs[4]).add_to(fwimap)
# Plot the contour plot on folium
folium.GeoJson(
    ffmc,
    style_function=lambda x: {
        'color':     x['properties']['stroke'],
        'weight':    x['properties']['stroke-width'],
        'fillColor': x['properties']['fill'],
        'opacity':   0.95,
    }).add_to(fwimap)


# add the layer control
folium.LayerControl().add_to(fwimap)

# # Add the colormap to the folium map
fwimap.add_child(cmap)

# # # Fullscreen mode
# plugins.Fullscreen(position='topright', force_separate_button=True).add_to(fwimap)

# # # Plot the data
fwimap.save(str(leaflet_dir) + '/html/index.html')

# ### Timer
print("Run Time: ", datetime.now() - startTime)



















