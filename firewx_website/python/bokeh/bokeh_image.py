import context
import numpy as np
import xarray as xr
from context import  xr_dir, data_dir
from netCDF4 import Dataset
from bokeh.plotting import figure, output_file, save, curdoc, show
from ipywidgets import interact
from bokeh.io import output_notebook, push_notebook, curdoc
from bokeh.models.widgets import Div

from wrf import  ll_to_xy

from bokeh.models.widgets import RadioButtonGroup
from bokeh.layouts import column, layout
output_file("/bluesky/archive/fireweather/test/index_image.html", title="image.py example")

# select = Select(title="Forecasts:", value="20200604", options=["20200604", "20200614"])
# radio_button_group = RadioButtonGroup(labels=['20200604', '20200614'], active=0)

# show(vform(select))

png_dir = '/bluesky/archive/fireweather/test/static/images/20200604.png'

# div_image = Div(text="""<img src="./static/images/20200604.png" alt="div_image">""", width=150, height=150)

# div_image = Div(text="""<img src="./static/images/20200604.png" alt="div_image">""", width=10, height=10)

# def update():
#     div_image.text = """<img src="./static/images/{}.png" alt="div_image">""".format()
#     return div_image
# radio_button_group.on_change('active', lambda attr, old, new: update())
# radio_button_group.active


# interact(update, forecast=["20200604", "20200614"])
# page = column(radio_button_group, div_image)
# save(page)


div_image1 = Div(text="""<img src="./static/images/20200604.png" alt="div_image">""", width=10, height=10)
div_image2 = Div(text="""<img src="./static/images/20200604.png" alt="div_image">""", width=10, height=10)

def update_plot(attrname, old, new):

    if options[button_group.active] == '20200614':
        curdoc().clear()
        curdoc().add_root(lay_out)
        curdoc().add_root(div_image1)

    if options[button_group.active] == '20200614':
        curdoc().clear()
        curdoc().add_root(lay_out)
        curdoc().add_root(div_image2)



options = ['20200614', '20200614']
button_group = RadioButtonGroup(labels=options, active=0)
button_group.on_change("active", update_plot)


# create layout and add to curdoc
lay_out = layout([[button_group]])
# curdoc().add_root(grid)
curdoc().add_root(lay_out)

page = column(lay_out)
save(page)