
import context
import numpy as np
import xarray as xr
from context import  xr_dir, data_dir
from netCDF4 import Dataset


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




# time_ind = 18
# time = np.datetime_as_string(hourly_ds.Time[time_ind], unit='h')
# initial = np.datetime_as_string(hourly_ds.Time[0], unit='h')
# valid = np.datetime_as_string(hourly_ds.Time[time_ind], unit='h')
# print(time)
time = np.array(hourly_ds.Time)
ffmc = np.array(hourly_ds.F[:,xy_np[1], xy_np[0]])


# output HTML file
output_file('/bluesky/archive/fireweather/test/index.html')

# create a new plot with a title and axis labels
p = figure(title="FFMC", x_axis_label='Time', y_axis_label='FFMC', x_axis_type="datetime")

# add a line renderer with legend and line thickness
p.line(time, ffmc, legend_label="FFMC", line_width=2)
p.xaxis.formatter=DatetimeTickFormatter(days=["%b %d, %Y"])

# # Add Tooltips
# hover = HoverTool()
# hover.tooltips = """
#   <div>
#     <h3>@Car</h3>
#     <div><strong>Price: </strong>@Price</div>
#     <div><strong>HP: </strong>@Horsepower</div>
#     <div><img src="@Image" alt="" width="200" /></div>
#   </div>
# """
# p.add_tools(hover)

# # Show results
# show(p)

# Save file
save(p)

# Print out div and script
# script, div = components(p)
# print(div)
# print(script)