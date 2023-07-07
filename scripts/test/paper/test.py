import context
import json
import salem
import numpy as np
import xarray as xr
import pandas as pd
import geopandas as gpd
from scipy import stats
from pathlib import Path
import plotly.express as px
import cartopy.crs as ccrs
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1 import make_axes_locatable


from context import data_dir, root_dir


ds = xr.open_dataset(
    "/Users/crodell/Downloads/HDF5_LSASAF_MSG_FTA-FRP-GRID_MSG-Disk_202305180000"
)
