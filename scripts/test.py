import context
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
from netCDF4 import Dataset
import cartopy.crs as crs
import geopandas as gpd

from datetime import datetime
import matplotlib.colors
import matplotlib.pyplot as plt

from datetime import datetime, date, timedelta

from context import fwf_dir, root_dir

from glob import glob


ds = xr.open_dataset("/Users/rodell/Downloads/2022271.00.nc")

# pm25 = ds.PM25
list(ds)
