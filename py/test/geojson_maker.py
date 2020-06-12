import sys
import json
import numpy as np
import xarray as xr
import geojsoncontour
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
from context import data_dir, xr_dir

startTime = datetime.now()


"""######### get directory to hourly/daily .zarr files.  #############"""
# hourly_file_dir  = "/Volumes/CER/WFRT/FWI/Data/hourly/2020-06-07T00.zarr"
hourly_file_dir  = str(xr_dir) + '/current/hourly.zarr'
hourly_ds = xr.open_zarr(hourly_file_dir)

# daily_file_dir  = "/Volumes/CER/WFRT/FWI/Data/daily/2020-06-07T00.zarr"
daily_file_dir  = str(xr_dir) + '/current/daily.zarr'

daily_ds = xr.open_zarr(daily_file_dir)
lats, lons = np.array(hourly_ds.XLAT), np.array(hourly_ds.XLONG)


with open('/bluesky/fireweather/fwf/firewx_website/python/colormaps.json') as f:
  cmaps = json.load(f)



def contourf_to_geojson(cmaps, var, ds, index):
    day  = str(np.array(ds.Time[0], dtype ='datetime64[D]'))
    vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
    name, colors = cmaps[var]["name"], cmaps[var]["colors15"]
    geojson_filepath = str(name)
    levels = len(colors)
    contourf = plt.contourf(np.array(ds.XLONG), np.array(ds.XLAT), np.array(ds[var][index]), levels = levels, \
                            linestyles = 'None', vmin = vmin, vmax = vmax, colors = colors)
    plt.close()

    geojsoncontour.contourf_to_geojson(
        contourf=contourf,
        min_angle_deg=3.0,
        ndigits=2,
        stroke_width=0.2,
        fill_opacity=0.95,
        geojson_filepath = f'/bluesky/fireweather/fwf/firewx_website/json/{geojson_filepath}.geojson')

    return

# ### Make Geojson files
contourf_to_geojson(cmaps, 'F', hourly_ds, 18)
contourf_to_geojson(cmaps, 'P', daily_ds, 0)
contourf_to_geojson(cmaps, 'D', daily_ds, 0)
contourf_to_geojson(cmaps, 'R', hourly_ds, 18)
contourf_to_geojson(cmaps, 'U', daily_ds, 0)
contourf_to_geojson(cmaps, 'S', hourly_ds, 18)


# ### Timer
print("Run Time: ", datetime.now() - startTime)