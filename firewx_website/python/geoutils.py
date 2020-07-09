#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import numpy as np
import xarray as xr
import geojsoncontour
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta

from wrf import getvar




def contourf_to_geojson(cmaps, var, ds, index, folderdate):
    """
    This makes a gejson file from a matplot lib countourf

    """
    timestamp  = str(np.array(ds.Time[index], dtype ='datetime64[h]'))
    timestamp = datetime.strptime(str(timestamp), '%Y-%m-%dT%H').strftime('%Y%m%d%H')
    vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
    name, colors = str(cmaps[var]["name"]), cmaps[var]["colors15"]
    geojson_filepath = str(name + "-" + timestamp)
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
        unit=timestamp, 
        geojson_filepath = f'/bluesky/fireweather/fwf/data/geojson/{folderdate}/{geojson_filepath}.geojson')

    print(f'wrote geojson to: /bluesky/fireweather/fwf/data/geojson/{folderdate}/{geojson_filepath}.geojson')
    return

def mask(ds_unmasked, wrf_file_dir):
    LANDMASK, LAKEMASK, SNOWC = wrfmasks(wrf_file_dir)
    SNOWC[:,:600]   = 0
    ds = xr.where(LANDMASK == 1, ds_unmasked, np.nan)
    ds = ds.transpose("time", "south_north", "west_east")
    # ds = xr.where(LAKEMASK == 0, ds, np.nan)
    # ds = ds.transpose("time", "south_north", "west_east")
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
    SNOWC[:,:600]   = 0

    return LANDMASK, LAKEMASK, SNOWC



def jsonmask(ds_unmasked, wrf_file_dir):
    LANDMASK, LAKEMASK, SNOWC = wrfmasks(wrf_file_dir)
    SNOWC[:,:600]   = 0
    ds = xr.where(LANDMASK == 1, ds_unmasked, '')
    ds = ds.transpose("time", "south_north", "west_east")
    # ds = xr.where(LAKEMASK == 0, ds, np.nan)
    # ds = ds.transpose("time", "south_north", "west_east")
    ds = xr.where(SNOWC == 0, ds, '')
    ds = ds.transpose("time", "south_north", "west_east")
    ds['Time'] = ds_unmasked['Time']
    return ds
