#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import numpy as np
import xarray as xr
import geojsoncontour
# from cr_geocontour.contour import contourf_to_geojson
import geojsoncontour
from pathlib import Path
from netCDF4 import Dataset
import branca.colormap as cm
import scipy.ndimage as ndimage
from scipy.ndimage.filters import gaussian_filter

import matplotlib.pyplot as plt
import matplotlib.colors 

from datetime import datetime, date, timedelta

from wrf import getvar



def mycontourf_to_geojson(cmaps, var, ds, index, folderdate, colornumber):
    """
    This makes a gejson file from a matplot lib countourf

    """
    timestamp  = str(np.array(ds.Time[index], dtype ='datetime64[h]'))
    timestamp = datetime.strptime(str(timestamp), '%Y-%m-%dT%H').strftime('%Y%m%d%H')
    vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
    name, colors, sigma = str(cmaps[var]["name"]), cmaps[var][colornumber], cmaps[var]["sigma"]
    if name == 'dmc':
        timestamp = timestamp[:-2]
    elif name == 'dc':
        timestamp = timestamp[:-2]
    elif name == 'bui':
        timestamp = timestamp[:-2]
    else:
        pass

    lngs = np.array(ds.XLONG)
    lats = np.array(ds.XLAT)
    fillarray = np.round(np.array(ds[var][index]),0)
    fillarray = ndimage.gaussian_filter(fillarray, sigma=sigma)
    
    geojson_filepath = str(name + "-" + timestamp)
    lenght = len(colors)
    lngs, lats = lngs[10:,47:], lats[10:,47:]
    fillarray = fillarray[10:,47:]
    levels = cmaps[var]["levels"]
    Cnorm = matplotlib.colors.Normalize(vmin= vmin, vmax =vmax+1)
    contourf = plt.contourf(lngs, lats, fillarray, levels = levels, \
                            linestyles = 'None', norm = Cnorm, colors = colors, extend = 'both')
    plt.close()

    geojsoncontour.contourf_to_geojson(
        contourf=contourf,
        min_angle_deg=None,
        ndigits=2,
        stroke_width=None,
        fill_opacity=None,
        geojson_properties=None,
        unit='', 
        geojson_filepath = f'/bluesky/fireweather/fwf/data/geojson/{folderdate}/{geojson_filepath}.geojson')

    print(f'wrote geojson to: /bluesky/fireweather/fwf/data/geojson/{folderdate}/{geojson_filepath}.geojson')
    
    return




def mask(ds_unmasked, wrf_file_dir):
    LANDMASK, LAKEMASK, SNOWC = wrfmasks(wrf_file_dir)
    # SNOWC[:,:600]   = 0
    ds = xr.where(LANDMASK == 1, ds_unmasked, np.nan)
    ds = ds.transpose("time", "south_north", "west_east")
    # ds = xr.where(LAKEMASK == 0, ds, np.nan)
    # ds = ds.transpose("time", "south_north", "west_east")
    # ds = xr.where(SNOWC == 0, ds, np.nan)
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
    # ds = xr.where(SNOWC == 0, ds, '')
    # ds = ds.transpose("time", "south_north", "west_east")
    ds['Time'] = ds_unmasked['Time']
    return ds

# def jsonmask(array, wrf_file_dir):
#     LANDMASK, LAKEMASK, SNOWC = wrfmasks(wrf_file_dir)
#     LANDMASK= LANDMASK[:,50:1210]
#     ds = np.where(LANDMASK == 1, array, '')

#     return ds


def latlngmask(array, wrf_file_dir):
    LANDMASK, LAKEMASK, SNOWC = wrfmasks(wrf_file_dir)
    SNOWC[:,:600]   = 0
    arraymasked = np.where(LANDMASK == 1, array, '')
    arraymasked = np.where(SNOWC == 0, arraymasked, '')
    return arraymasked


def delete3D(array3D):
    x = array3D.shape
    array2D = np.reshape(array3D, (x[0],(x[1]*x[2])))
    y_list = []
    for i in range(x[0]):
        index = np.argwhere(array2D[i,:]=='')
        y = np.delete(array2D[i,:], index)
        y_list.append(y)
    final = np.stack(y_list)
    # final = np.float32(final)
    return final

def delete2D(array2D):
    x = array2D.shape
    array1D = np.reshape(array2D, (x[0]*x[1]))
    index = np.argwhere(array1D=='')
    final = np.delete(array1D, index)
    # final = np.float32(final)
    return final


def colormaps(cmaps, var):
    vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
    name, colors = cmaps[var]["name"], cmaps[var]["colors18"]
    levels = cmaps[var]["levels"]
    # cmap  = cm.LinearColormap(colors, vmin = vmin, vmax = vmax, caption = name).to_step(levels)
    cmap  = cm.StepColormap(colors, index = cmaps[var]["levels"], vmin = vmin, vmax = vmax, caption = name)
    cmap.caption = cmaps[var]["title"]
    return cmap