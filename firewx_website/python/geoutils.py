import context
import numpy as np
import xarray as xr
import geojsoncontour
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta

from wrf import getvar




def contourf_to_geojson(cmaps, var, ds, index):
    day  = str(np.array(ds.Time[0], dtype ='datetime64[D]'))
    vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
    name, colors = cmaps[var]["name"], cmaps[var]["colors15"]
    # geojson_filepath = str(name + "_" + day)
    geojson_filepath = str(name)
    levels = len(colors)
    contourf = plt.contourf(np.array(ds.XLONG), np.array(ds.XLAT), np.round(np.array(ds[var][index]),3), levels = levels, \
                            linestyles = 'None', vmin = vmin, vmax = vmax, colors = colors)
    plt.close()

    geojsoncontour.contourf_to_geojson(
        contourf=contourf,
        min_angle_deg=3.0,
        ndigits=2,
        stroke_width=0.2,
        fill_opacity=0.95,
        geojson_filepath = f'/bluesky/fireweather/fwf/data/geojson/{geojson_filepath}.geojson')

    return

def mask(ds_unmasked, wrf_file_dir):
    LANDMASK, LAKEMASK, SNOWC = wrfmasks(wrf_file_dir)
    ds = xr.where(LANDMASK == 1, ds_unmasked, np.nan)
    ds = ds.transpose("time", "south_north", "west_east")
    ds = xr.where(LAKEMASK == 0, ds, np.nan)
    ds = ds.transpose("time", "south_north", "west_east")
    ds = xr.where(SNOWC == 0, ds, np.nan)
    ds = ds.transpose("time", "south_north", "west_east")
    ds['Time'] = ds_unmasked['Time']
    return ds



def wrfmasks(wrf_file_dir):
    wrf_file = Dataset(wrf_file_dir[-1],'r')
    ### Get Land Mask and Lake Mask data
    LANDMASK        = getvar(wrf_file, "LANDMASK")
    LAKEMASK        = getvar(wrf_file, "LAKEMASK")
    SNOWC           = getvar(wrf_file, "SNOWC")
    return LANDMASK, LAKEMASK, SNOWC




# import sys
# sys.path.insert(0, 'folium')
# sys.path.insert(0, 'branca')

# import branca
# import folium
# import branca.colormap as cm
# from jinja2 import Template



# class BindColormap(MacroElement):
#     """Binds a colormap to a given layer.

#     Parameters
#     ----------
#     colormap : branca.colormap.ColorMap
#         The colormap to bind.
#     """
#     def __init__(self, layer, colormap):
#         super(BindColormap, self).__init__()
#         self.layer = layer
#         self.colormap = colormap
#         self._template = Template(u"""
#         {% macro script(this, kwargs) %}
#             {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
#             {{this._parent.get_name()}}.on('overlayadd', function (eventLayer) {
#                 if (eventLayer.layer == {{this.layer.get_name()}}) {
#                     {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
#                 }});
#             {{this._parent.get_name()}}.on('overlayremove', function (eventLayer) {
#                 if (eventLayer.layer == {{this.layer.get_name()}}) {
#                     {{this.colormap.get_name()}}.svg[0][0].style.display = 'none';
#                 }});
#         {% endmacro %}
#         """)  # noqa
############################################
#### Convert matplotlib contourf to geojson
############################################
# def contourf_to_geojson(contourf, name):
#     geojson = geojsoncontour.contourf_to_geojson(
#         contourf=contourf,
#         min_angle_deg=3.0,
#         ndigits=2,
#         stroke_width=0.2,
#         fill_opacity=0.95)

#     folium_GeoJson = folium.GeoJson(
#     geojson,
#     style_function=lambda x: {
#         'color':     x['properties']['stroke'],
#         'weight':    x['properties']['stroke-width'],
#         'fillColor': x['properties']['fill'],
#         'opacity':   0.95,
#     }, name=name, overlay=True)
#     return folium_GeoJson


# def contourf_cm(cmaps, var, ds, index):
#     vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
#     name, colors = cmaps[var]["name"], cmaps[var]["colors15"]
#     levels = len(colors)
#     cmap  = cm.LinearColormap(colors, vmin = vmin, vmax = vmax, caption = name).to_step(levels)
#     contourf = plt.contourf(np.array(ds.XLONG), np.array(ds.XLAT), np.array(ds[var][index]), levels = levels, \
#                             linestyles = 'None', vmin = vmin, vmax = vmax, colors = colors)
#     plt.close()
#     return contourf, cmap

# def colormaps(cmaps, var):
#     vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
#     name, colors = cmaps[var]["name"], cmaps[var]["colors15"]
#     levels = len(colors)
#     cmap  = cm.LinearColormap(colors, vmin = vmin, vmax = vmax, caption = name).to_step(levels)
#     cmap.caption = cmaps[var]["title"]
#     return cmap






