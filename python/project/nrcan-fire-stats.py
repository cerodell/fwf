import context
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
from netCDF4 import Dataset
import cartopy.crs as crs
import geopandas as gpd
import seaborn as sns

from datetime import datetime
import matplotlib.colors
import matplotlib.pyplot as plt

from datetime import datetime, date, timedelta

from context import data_dir, root_dir


filein = str(data_dir) + '/shp/' + "progression.shp"
df = gpd.read_file(filein)
df = df.to_crs(epsg=4326)

df2 = df.loc[df['DATE'] == 20200910.0]



# def firestats(per):
#     mins, growth, timediff = [], [], []
#     for i in range(len(per['AFSDATE'])):
#         print(per['YEAR'][i])
#         if per['AFSDATE'][i] == None:
#             if per['EDATE'][i] == None:
#                 pass
#             else:
#                 first= datetime.fromisoformat(per['SDATE'][i])
#         else:
#             first= datetime.fromisoformat(per['AFSDATE'][i])
#         if per['AFEDATE'][i] == None:
#             if per['EDATE'][i] == None:
#                 pass
#             else:
#                 last= datetime.fromisoformat(per['EDATE'][i])
#         else:
#             last= datetime.fromisoformat(per['AFEDATE'][i])
        
#         total_i = last-first
#         minutes_diff = total_i.total_seconds() / 60.0

#         timediff.append(minutes_diff)

#     # per['minutes'] = mins
#     # per['growth'] = growth
#     per['timediff'] = timediff
#     return per
# per_1986_2020 = firestats(per_1986_2020)

# per_test = per_1986_2020.loc[per_1986_2020['timediff'] < 1000000]
# per_test = per_test.loc[per_test['timediff'] > 0]
# per_test = per_test.loc[per_test['POLY_HA'] > 100]

# sns.jointplot(x=per_test["timediff"], y=per_test["POLY_HA"], kind='scatter')

# corr = per_test["timediff"].corr(per_test["POLY_HA"])