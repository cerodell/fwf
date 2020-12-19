#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
from netCDF4 import Dataset
import cartopy.crs as crs
import geopandas as gpd
import seaborn as sns
from glob import glob

from datetime import datetime

from datetime import datetime, date, timedelta
from context import data_dir, root_dir

def read_zarr(files, dim):
    # glob expands paths with * to a list of files, like the unix shell
    if files[-8:-2]== 'hourly':
        paths = sorted(glob(files))
        ds = [xr.open_zarr(p).sel(time=slice(0 ,24)) for p in paths]
    else:
        paths = sorted(glob(files))
        ds = [xr.open_zarr(p).sel(time=slice(0 ,1)) for p in paths]
    combined = xr.concat(ds, dim)
    return combined


def firestats(df):
    mins, growth, timediff = [], [], []
    for i in range(len(df['FIRSTDATE'])):
        first= datetime.fromisoformat(df['FIRSTDATE'][i])
        last= datetime.fromisoformat(df['LASTDATE'][i])
        total_i = last-first
        minutes_diff = total_i.total_seconds() / 60.0
        growth_i = np.linspace(0,df['AREA'][i],minutes_diff)
        mins_i = np.arange(0,minutes_diff,1)
        growth.append(growth_i)
        mins.append(mins_i)
        timediff.append(minutes_diff)
    # df['minutes'] = mins
    # df['growth'] = growth
    df['timediff_min'] = timediff
    return df





def extract_poly_coords(geom):
    if geom.type == 'Polygon':
        exterior_coords = geom.exterior.coords[:]
        interior_coords = []
        for interior in geom.interiors:
            interior_coords += interior.coords[:]
    elif geom.type == 'MultiPolygon':
        exterior_coords = []
        interior_coords = []
        for part in geom:
            epc = extract_poly_coords(part)  # Recursive call
            exterior_coords += epc['exterior_coords']
            interior_coords += epc['interior_coords']
    else:
        raise ValueError('Unhandled geometry type: ' + repr(geom.type))
    return {'exterior_coords': np.asarray(exterior_coords),
            'interior_coords': np.asarray(interior_coords)}