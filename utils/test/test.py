import context
import io
import json
import requests

import numpy as np
import pandas as pd
import xarray as xr
from glob import glob
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from wrf import ll_to_xy, xy_to_ll
from datetime import datetime, date, timedelta

from context import data_dir


wrf_model = "wrf4"
domain = "d03"

static_ds = xr.open_dataset(
    str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}.nc"
)
tzone = static_ds.ZoneDT.values
shape = tzone.shape
