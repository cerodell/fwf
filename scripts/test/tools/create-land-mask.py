import context
import math
import salem
import numpy as np
import pandas as pd
import xarray as xr


from datetime import datetime, date, timedelta
from context import data_dir

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


model = "wrf"
domain = "d03"


filein = str(data_dir) + f"/{model}/{domain}-grid.nc"

ocean_shp = str(data_dir) + "/shp/buffed_oceans/buffed_oceans.shp"

## Open datasets
ds = salem.open_xr_dataset(filein)
pyproj_srs = ds.attrs["pyproj_srs"]
df = salem.read_shapefile(ocean_shp)

static_ds = salem.open_xr_dataset(str(data_dir) + f"/static/static-vars-wrf-d03.nc")

static_ds["LAND"].salem.quick_map(prov=True)
