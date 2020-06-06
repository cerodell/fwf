import context
import math
import pickle
import numpy as np
import pandas as pd
import xarray as xr
import cartopy.crs as crs
import cartopy.feature as cfeature
import timezonefinder, pytz
from datetime import datetime
import matplotlib as mpl
import matplotlib.colors
import matplotlib.pyplot as plt
from wrf import (to_np, getvar, get_cartopy, latlon_coords, g_uvmet)
from bson import json_util

import json
import geojson
from fwi.utils.ubc_fwi.fwf import FWF
from fwi.utils.wrf.read_wrfout import readwrf
from context import data_dir, xr_dir, wrf_dir, tzone_dir, root_dir

startTime = datetime.now()

"""######### get directory to yesterdays hourly/daily .zarr files.  #############"""
# yesterday = date.today() - timedelta(days=1)
# zarr_filein = yesterday.strftime('%Y-%m-%dT00.zarr')
zarr_filein = "2019-08-20T00_hourly_ds.zarr"
# hourly_file_dir = str(xr_dir) + str("/hourly/") + zarr_filein

##### Personal Comp path 
 
hourly_file_dir = str(data_dir) + str("/xr/") + zarr_filein
ds = xr.open_zarr(hourly_file_dir)


d = ds.F.to_dict()

# with open(str(data_dir) + '/json/test.json', 'w') as json_file:
#     json.dump(d, json_file, default=json_util.default)

with open(str(data_dir) + '/json/ffmc_timeseires.geojson', 'w') as outfile:
    geojson.dump(d, outfile, sort_keys=True, default=json_util.default)

    print("Run Time: ", datetime.now() - startTime)