#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import context
import salem
import dask
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime
import plotly.express as px

from utils.compressor import compressor
from utils.geoutils import make_KDtree
from context import root_dir
from utils.rave import RAVE

import pandas as pd

import matplotlib.pyplot as plt
import cartopy.crs as ccrs

# doi = pd.Timestamp("2020-09-09T20")
# case_study = 'wildcat'
# ## open case study json file
# with open(str(root_dir) + f"/json/fire-cases.json", "r") as fp:
#     case_dict = json.load(fp)


ds = xr.open_zarr("/Volumes/WFRT-Ext23/fire/hfi/2021-24453150.zarr")

# np.unique(np.isnan(ds['ASPECT'].values))

# # ds['LAI'].isel(time =slice(0,400,50)).plot(x="x", y="y", col="time", col_wrap=3, cmap = 'jet')

# ds['ASPECT'].mean('time').plot(cmap = 'terrain')

# ds['NDVI'].mean(('x', 'y')).plot()
test = xr.open_dataset(
    "/Volumes/WFRT-Ext24/rave/2020/09/RAVE-HrlyEmiss-3km_v2r0_blend_s202009010000000_e202009012359590_c202310260235330.nc"
)

# coeff = RAVE(
#     config=case_dict[case_study],
# )
# rave_ds = coeff.combine_rave()


# rave_ds["FRP_MEAN"].isel(time = 4).salem.quick_map( cmap="Reds")
