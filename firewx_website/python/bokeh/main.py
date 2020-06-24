
import context
import numpy as np
import xarray as xr
import pandas as pd
from context import  xr_dir, data_dir
from netCDF4 import Dataset

from bokeh.layouts import column, row
from bokeh.plotting import figure, output_file, show, save, ColumnDataSource
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models.tools import HoverTool
from bokeh.transform import factor_cmap
from bokeh.palettes import Blues8
from bokeh.embed import components

from wrf import  ll_to_xy

lat, lon = 49.083, -116.5

wrf_file_dir = str(data_dir) + "/wrf/lat_lon.nc"
wrf_file = Dataset(wrf_file_dir,'r')

xy_np  = np.array(ll_to_xy(wrf_file, lat, lon))


hourly_file_dir  = str(xr_dir) + "/current/hourly.zarr"
hourly_ds = xr.open_zarr(hourly_file_dir)

daily_file_dir  = str(xr_dir) + "/current/daily.zarr"
daily_ds = xr.open_zarr(daily_file_dir)


### Make Pandas Dataframe
df_list = []
for var in hourly_ds.data_vars:
    df = hourly_ds[var][:,xy_np[1], xy_np[0]].to_dataframe()
    del df['Time']
    del df['XLAT']
    del df['XLONG']

    df_list.append(df)
df = pd.concat(df_list, axis=1)
df['Time'] = np.array(hourly_ds.Time)


source = ColumnDataSource(df)



# output HTML file
output_file('/bluesky/archive/fireweather/test/index_bokeh.html')

# create a new plot with a title and axis labels
FFMC = figure(title="FINE FUEL MOISTURE CODE", x_axis_label='Time', y_axis_label='FFMC',
            x_axis_type="datetime", plot_width=900, plot_height=200)

# add a line renderer with legend and line thickness
FFMC.line('Time', 'F',  line_width=2, source=source, color="orange")
FFMC.circle('Time', 'F', size=4, source=source, color="orange")

FFMC.xaxis.formatter=DatetimeTickFormatter(days=["%b %d, %Y"])

# Add Tooltips
hover = HoverTool(    tooltips = [
        ("Time", "@Time{%b %d, %Y}"),
        ("FFMC", "@F"),
    ],
    formatters={
        'Time': 'datetime',
        'FFMC' : 'printf',
    },
)
FFMC.add_tools(hover)


# create a new plot with a title and axis labels
ISI = figure(title="INITIAL SPREAD INDEX", x_axis_label='Time', y_axis_label='ISI',
            x_axis_type="datetime", plot_width=900, plot_height=200)

# add a line renderer with legend and line thickness
ISI.line('Time', 'R',  line_width=2, source=source, color="red")
ISI.circle('Time', 'R', size=4, source=source, color="red")

ISI.xaxis.formatter=DatetimeTickFormatter(days=["%b %d, %Y"])

# Add Tooltips
hover = HoverTool(    tooltips = [
        ("Time", "@Time{%b %d, %Y}"),
        ("ISI", "@R"),
    ],
    formatters={
        'Time': 'datetime',
        'ISI' : 'printf',
    },
)
ISI.add_tools(hover)






layout = column(FFMC, ISI)

# Save file
save(layout)

# Print out div and script
# script, div = components(p)
# print(div)
# print(script)