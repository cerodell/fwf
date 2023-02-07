import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText


from scipy import stats
from sklearn.metrics import mean_squared_error, mean_absolute_error

from context import data_dir


##################################################################
##################### Define Inputs   ###########################
## time of interest
start, stop = "2022-04-01", "2022-10-01"


## models to compare
models = ["_wrf05", "_wrf07", "_wrf08"]

## test case
test_case = "WRF05060708"
## define directory to save figures
save_dir = Path(str(data_dir) + f"/images/stats/{test_case}/")
save_dir.mkdir(parents=True, exist_ok=True)


##################################################################
#################### Open Data Files   ###########################

ds = xr.open_dataset(str(data_dir) + f"/intercomp/d02/{test_case}/20210101-20221031.nc")
