import context
import json
import salem
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
from affine import Affine
from pathlib import Path
from netCDF4 import Dataset
from osgeo import osr, gdal, ogr

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.ndimage as ndimage
from scipy.ndimage.filters import gaussian_filter

from context import data_dir, wrf_dir, fwf_zarr_dir, vol_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))


filein_anderson = (
    str(vol_dir)
    + "/fuels/converter/lf71723740_AK_140FBFM13/AK_140FBFM13\AK_140FBFM13.tif"
)
filein_cfbp = (
    str(vol_dir)
    + "/fuels/converter/lf05582407_AK_140CFFDRS/AK_140CFFDRS\AK_140CFFDRS.tif"
)
## Open all files mentioned above
anderson_ds = salem.open_xr_dataset(filein_anderson)
cfbp_ds = salem.open_xr_dataset(filein_cfbp)


def getunique(array):
    unique, count = np.unique(array[~np.isnan(array)], return_counts=True)
    unique = np.unique(array[~np.isnan(array)]).astype(int)
    return unique, count


anderson_array = anderson_ds.data.values
cfbp_array = cfbp_ds.data.values
anderson_unique, anderson_count = getunique(anderson_array)
cfbp_unique, cfbp_count = getunique(cfbp_array)


array = cfbp_array[anderson_array == val]
array = anderson_array[cfbp_array == cfbp_unique[2]]


con_dict = {}
for val in anderson_unique:
    array = cfbp_array[anderson_array == val]
    unique, count = np.unique(array, return_counts=True)
    try:
        con_dict.update(
            {
                str(val): {
                    "most_unique": list(unique[count == count.max()]),
                    "unique": list(unique),
                    "count": list(count),
                }
            }
        )
    except:
        con_dict.update(
            {
                str(val): {
                    "most_unique": list(unique),
                    "unique": list(unique),
                    "count": list(count),
                }
            }
        )


con_df = pd.DataFrame([con_dict])
test = pd.concat({k: pd.DataFrame(v).T for k, v in con_dict.items()}, axis=0)
