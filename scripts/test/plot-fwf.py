import context
import json

import salem
import numpy as np
import xarray as xr
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors


from context import data_dir, root_dir, wrf_dir


ds = salem.open_mf_wrf_dataset("/NASPANGEA/WRF/BCWS_forecast/all_wrfsfc_d03_2025030600PT.nc")


