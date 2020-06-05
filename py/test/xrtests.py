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

ztone = str(xr_dir) + "/hourly/2020-06-04T00.zarr"


ds = xr.open_zarr(ztone)


d = ds.F.to_dict()

# with open(str(data_dir) + '/json/test.json', 'w') as json_file:
#     json.dump(d, json_file, default=json_util.default)

with open(str(data_dir) + '/json/test.geojson', 'w') as outfile:
    geojson.dump(d, outfile, sort_keys=True, default=json_util.default)