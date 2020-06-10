import context
import numpy as np
import xarray as xr
import sys
sys.path.insert(0, 'folium')
sys.path.insert(0, 'branca')

import branca
import folium
from datetime import datetime, date, timedelta
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




############################################
#### Convert matplotlib contourf to geojson
############################################
def contourf_to_geojson(contourf, name):
    geojson = geojsoncontour.contourf_to_geojson(
        contourf=contourf,
        min_angle_deg=3.0,
        ndigits=2,
        stroke_width=0.2,
        fill_opacity=0.95)

    folium_GeoJson = folium.GeoJson(
    geojson,
    style_function=lambda x: {
        'color':     x['properties']['stroke'],
        'weight':    x['properties']['stroke-width'],
        'fillColor': x['properties']['fill'],
        'opacity':   0.95,
    }, name=name, overlay=True)
    return folium_GeoJson


def contourf_cm(cmaps, var, ds, index):
    vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
    name, colors = cmaps[var]["name"], cmaps[var]["colors15"]
    levels = len(colors)
    cmap  = cm.LinearColormap(colors, vmin = vmin, vmax = vmax, caption = name).to_step(levels)
    contourf = plt.contourf(np.array(ds.XLONG), np.array(ds.XLAT), np.array(ds[var][index]), levels = levels, \
                            linestyles = 'None', vmin = vmin, vmax = vmax, colors = colors)
    plt.close()
    return contourf, cmap

def colormaps(cmaps, var):
    vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
    name, colors = cmaps[var]["name"], cmaps[var]["colors15"]
    levels = len(colors)
    cmap  = cm.LinearColormap(colors, vmin = vmin, vmax = vmax, caption = name).to_step(levels)
    cmap.caption = cmaps[var]["title"]
    return cmap