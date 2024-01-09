#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import salem
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt

from utils.compressor import compressor

from context import root_dir

save_dir = Path(str(root_dir) + "/data/ecmwf/era5-land/")
save_dir.mkdir(parents=True, exist_ok=True)
data_dir = "/Volumes/WFRT-Ext25/ecmwf/era5-land/"
start = "1991-01-01"
stop = "2020-12-31"
# vars = ["pev", "t2m"]


t2m = salem.open_xr_dataset(
    str(save_dir)
    + f"/t2m-climatology-{start.replace('-','')}-{stop.replace('-','')}.nc"
)
t2m["t2m"] = ((t2m["t2m"] - 273.15) * (9 / 5)) + 32
t2m["t2m"].attrs = t2m.attrs


pev = salem.open_xr_dataset(
    str(save_dir)
    + f"/pev-climatology-{start.replace('-','')}-{stop.replace('-','')}.nc"
)
pev["pev"] = (pev["pev"] * 39.3701) * -1 / 0.1
pev["pev"].interp(longitude=-120.3, latitude=50).plot()

pev["S"] = (pev["pev"] - ((1 / 5) * (t2m["t2m"] - 32))) * -1

pev["S"].attrs = pev.attrs

pev["S"].isel(month=5).salem.quick_map()
pev["S"].isel(month=5).mean()

# # t2m['t2m'].interp(longitude = -120.3, latitude = 50).plot()


# plt.scatter(pev['pev'].isel(month = 5).values.ravel(),t2m['t2m'].isel(month = 5).values.ravel() )
