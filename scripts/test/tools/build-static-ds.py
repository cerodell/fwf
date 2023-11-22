#!/Users/crodell/miniconda3/envs/fwf/bin/python

"""
Runs the FWF model for each model domain.
Saves dataset as nc file containing all fwi/fbp and associated met products

"""
import context
import math
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path

from datetime import datetime, date, timedelta

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

from utils.static import build_static


__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

model = "ecmwf"
domain = "era5-land"

coeff = build_static(model, domain)

coeff.build_grid()
coeff.timezone_mask()
coeff.static_ds_maker()
