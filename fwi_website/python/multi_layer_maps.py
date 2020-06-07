import context
import numpy as np
import xarray as xr
import sys
sys.path.insert(0, 'folium')
sys.path.insert(0, 'branca')

import branca
import folium
from datetime import datetime, date, timedelta
startTime = datetime.now()
import branca.colormap as cm
import geojsoncontour

from context import data_dir,leaflet_dir, xr_dir

from branca.element import MacroElement
import matplotlib.pyplot as plt

from jinja2 import Template

class BindColormap(MacroElement):
    """Binds a colormap to a given layer.

    Parameters
    ----------
    colormap : branca.colormap.ColorMap
        The colormap to bind.
    """
    def __init__(self, layer, colormap):
        super(BindColormap, self).__init__()
        self.layer = layer
        self.colormap = colormap
        self._template = Template(u"""
        {% macro script(this, kwargs) %}
            {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
            {{this._parent.get_name()}}.on('overlayadd', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
                }});
            {{this._parent.get_name()}}.on('overlayremove', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'none';
                }});
        {% endmacro %}
        """)  # noqa





# # # Convert matplotlib contourf to geojson
def contourf_to_geojson(contourf):
    geojson = geojsoncontour.contourf_to_geojson(
        contourf=contourf,
        min_angle_deg=3.0,
        ndigits=2,
        stroke_width=0.2,
        fill_opacity=0.95)
    return geojson



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


"""######### get .zarr files.  #############"""

zarr_filein = "2019-08-20T00_hourly_ds.zarr" 
hourly_file_dir = str(data_dir) + str("/xr/") + zarr_filein

ds = xr.open_zarr(hourly_file_dir)
lats, lons = ds.XLAT, ds.XLONG

colors = ["#004ddb", "#0057c8", "#0162b4", "#016ca0", "#01778d", "#028179", "#028c65", "#029651", "#19a045", "#37a93a", "#55b22f", "#73bb25", "#91c51a", "#afce10", "#ccd705", "#d9d200", "#d4c000", "#cfae00", "#ca9c00", "#c58a00", "#c07801", "#bb6601", "#b75501", "#b64902", "#b43d03", "#b33105", "#b22406", "#b01807", "#af0c08", "#ae0009"]

levels = len(colors)
print(levels)
cm_FFMC  = cm.LinearColormap(colors, vmin = 70, vmax = 100, caption='FFMC').to_step(len(colors))
cm_FWI  = cm.LinearColormap(colors, vmin = 0, vmax = 30, caption='FWI').to_step(len(colors))

FFMC = plt.contourf(np.array(lons), np.array(lats), np.array(ds.F[18]), levels = levels, \
                        linestyles = 'None', vmin = 70, vmax = 100, colors = colors)
plt.close()
FWI = plt.contourf(np.array(lons), np.array(lats), np.array(ds.S[18]), levels = levels, \
                        linestyles = 'None', vmin = 0, vmax = 30, colors = colors)
plt.close()
# # # Convert matplotlib contourf to geojson
ffmc = contourf_to_geojson(FFMC)
fwi = contourf_to_geojson(FWI)


ffmc_layer = folium.GeoJson(
    ffmc,
    style_function=lambda x: {
        'color':     x['properties']['stroke'],
        'weight':    x['properties']['stroke-width'],
        'fillColor': x['properties']['fill'],
        'opacity':   0.95,
    }, name='FFMC', overlay=True)

fwi_layer = folium.GeoJson(
    fwi,
    style_function=lambda x: {
        'color':     x['properties']['stroke'],
        'weight':    x['properties']['stroke-width'],
        'fillColor': x['properties']['fill'],
        'opacity':   0.95,
    }, name='FWI', overlay=True)




fwimap = folium.Map(
         location=[float(ds.CEN_LAT), float(ds.CEN_LON)], 
         zoom_start = 3)
for key in dictionary.keys():
    folium.TileLayer(dictionary[key]["tiles"], attr = dictionary[key]["attrs"], name = key).add_to(fwimap)
    
fwimap.add_child(ffmc_layer).add_child(fwi_layer)

fwimap.add_child(folium.map.LayerControl())
fwimap.add_child(cm_FFMC).add_child(cm_FWI)
fwimap.add_child(BindColormap(ffmc_layer, cm_FFMC)).add_child(BindColormap(fwi_layer, cm_FWI))




# # # Plot the data
fwimap.save(str(leaflet_dir) + '/html/multi_layer.html')

# ### Timer
print("Run Time: ", datetime.now() - startTime)