import context
import numpy as np
import sys
sys.path.insert(0, 'folium')
sys.path.insert(0, 'branca')

import branca
import folium
from datetime import datetime, date, timedelta
startTime = datetime.now()

from context import data_dir,leaflet_dir, xr_dir

from branca.element import MacroElement

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


lats = 20 * np.cos(np.linspace(0, 2*np.pi, 300))
lons = 20 * np.sin(np.linspace(0, 2*np.pi, 300))
colors = np.sin(5 * np.linspace(0, 2*np.pi, 300))


cm1 = branca.colormap.LinearColormap(['y','orange','r'], vmin=-1, vmax=1, caption='cm1')
cm2 = branca.colormap.LinearColormap(['b','c','g','y','r'], vmin=70, vmax=100, caption='cm2')

cl1 = folium.features.ColorLine(
    list(zip(lats, lons - 30)),
    colors=colors,
    colormap=cm1,
    weight=10,
    overlay=True,
    name='cl1')
cl2 = folium.features.ColorLine(
    list(zip(lats, lons + 30)),
    colors=colors,
    colormap=cm2,
    weight=10,
    overlay=True,
    name='cl2')

m = folium.Map([0, 0], zoom_start=3)
m.add_child(cl1).add_child(cl2)
m.add_child(folium.map.LayerControl())
m.add_child(cm1).add_child(cm2)
m.add_child(BindColormap(cl1, cm1)).add_child(BindColormap(cl2, cm2))


# # # Plot the data
m.save(str(leaflet_dir) + '/html/colormaps.html')

# ### Timer
print("Run Time: ", datetime.now() - startTime)