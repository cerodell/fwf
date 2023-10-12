#!/Users/crodell/miniconda3/envs/fwf/bin/python

import context
import salem
import json
import gc

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go

from pykrige.ok import OrdinaryKriging
from pykrige.uk import UniversalKriging

from pathlib import Path
from datetime import datetime
from context import data_dir, root_dir

# import time
# time.sleep(60*70)

startTime = datetime.now()
print(f"Start Time: {startTime}")

##################################################################
##################### Define Inputs   ###########################
model = "wrf"
domain = "d03"
var = "H"
var_range = [-6, 6]
date = pd.Timestamp("2021-04-01")
trail_name = "02"
days = 6
krig_type = "uk"

##################################################################


fwf_ds = salem.open_xr_dataset(
    f"/Volumes/WFRT-Ext24/fwf-data/{model}/{domain}/{trail_name}/fwf-daily-{domain}-{date.strftime('%Y%m%d')}06.nc"
).isel(time=0)

krig_ds = salem.open_xr_dataset(str(data_dir) + f"/krig/fwf-krig-{domain}-elev.nc")
krig_ds[f"elev_bias"] = krig_ds[f"elev_bias"] * -1
krig_ds[f"elev_bias"].attrs = krig_ds.attrs
krig_ds[f"T_bias"] = krig_ds[f"elev_bias"] * (9.8 / 1000)
krig_ds[f"T_bias"].attrs = krig_ds.attrs
krig_ds["T_bias"].salem.quick_map()


# temp.salem.quick_map()

temp_corrected = fwf_ds["T"].values + (krig_ds[f"elev_bias"].values * (9.8 / 1000))
fwf_ds["T_Corrected"] = (("south_north", "west_east"), temp_corrected)
fwf_ds["T_Corrected"].attrs = fwf_ds.attrs
fwf_ds["T_Corrected"].salem.quick_map()

temp_diff = fwf_ds["T_Corrected"].values - fwf_ds["T"].values
fwf_ds["T_Diff"] = (("south_north", "west_east"), temp_diff)
fwf_ds["T_Diff"].attrs = fwf_ds.attrs
fwf_ds["T_Diff"].salem.quick_map(cmap="coolwarm", vmin=-0.5, vmax=0.5)
