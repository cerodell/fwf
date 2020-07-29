import context
import sys
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
startTime = datetime.now()
from PIL import Image

import rasterio as rio
import earthpy as et
from context import data_dir, xr_dir, wrf_dir, root_dir




filein_tif = str(data_dir) + '/tif/ffmc_current.tif'

with rio.open(filein_tif) as ffmc:
    ffmc.bounds

ffmc.meta