import math
import numpy as np
import pandas as pd
import xarray as xr





da = xr.DataArray(np.random.rand(4, 3),
                    [('time', pd.date_range('2000-01-01', periods=4)),
                         ('space', ['IA', 'IL', 'IN'])])
da[:2]