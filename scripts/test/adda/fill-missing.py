import os
import context
import salem
import dask
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from context import data_dir


# TD2_2003-01-23_23.nc
# TD2_2003-06-13_13.nc
# TD2_2003-06-16_09.nc*
# TD2_2003-06-18_14.nc

# TD2_2003-06-19_09.nc


doi, model, domain, trial = pd.Timestamp("2004-07-10T22"), "adda", "d01", "01"
adda_dir = f"/Volumes/WFRT-Ext20/ADDA_V2/TD2/{doi.strftime('%Y')}/"


td_1 = xr.open_dataset(
    adda_dir + f"TD2_{(doi-pd.Timedelta(hours=1)).strftime('%Y-%m-%d_%H')}.nc"
)
td_1.to_netcdf(adda_dir + f"TD2_{(doi).strftime('%Y-%m-%d_%H')}.nc")
# for doi in pd.date_range("2004-04-01T00", "2004-04-02T00", freq='h'):
#   # print(xr.open_dataset(adda_dir + f"TD2_{(doi).strftime('%Y-%m-%d_%H')}.nc").dims)
#   print((doi).strftime('%Y-%m-%d_%H'))
#   print(xr.open_dataset(f"/Volumes/ThunderBay/CRodell/ADDA_V2/2004/cstm_d01_{(doi).strftime('%Y-%m-%d_%H')}_00_00.nc")['time'].values)

# td_0 = xr.open_dataset(f"/Volumes/ThunderBay/CRodell/ADDA_V2/2004/cstm_d01_{(doi).strftime('%Y-%m-%d_%H')}_00_00.nc").rename({'times':'time'}).drop_vars('time')
# td_0.to_netcdf(f"/Volumes/ThunderBay/CRodell/ADDA_V2/2004/cstm_d01_{(doi).strftime('%Y-%m-%d_%H')}_00_00-copy.nc", mode= 'w')
# td_0['Time'] = [0]
# td_1 = xr.open_dataset(adda_dir + f"TD2_{(doi-pd.Timedelta(hours=1)).strftime('%Y-%m-%d_%H')}.nc")
# td_1['TD2'] = (('Time', 'south_north', 'west_east'), np.full_like(td_1['TD2'], np.nan))
# td_1['Time'] = [1]
# td_2 = xr.open_dataset(adda_dir + f"TD2_{(doi+pd.Timedelta(hours=1)).strftime('%Y-%m-%d_%H')}.nc")
# td_2['Time'] = [2]


# td_final = xr.combine_nested([td_0, td_1, td_2], concat_dim='Time')
# td_final = td_final.interpolate_na(dim = 'Time')

# td_write = xr.open_dataset(adda_dir + f"TD2_{(doi-pd.Timedelta(hours=1)).strftime('%Y-%m-%d_%H')}.nc")
# td_write['TD2'] = (('Time', 'south_north', 'west_east'), td_final.isel(Time = 1))

# td_final_test = td_final.drop_vars('Time').isel(Time = 1)
# td_final_test = td_final_test.expand_dims('Time')
