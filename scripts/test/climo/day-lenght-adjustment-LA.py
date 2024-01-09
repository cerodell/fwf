#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import salem
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
from utils.open import read_dataset

from utils.compressor import compressor

from context import root_dir

save_dir = Path(str(root_dir) + "/data/ecmwf/era5-land/")
save_dir.mkdir(parents=True, exist_ok=True)
data_dir = "/Volumes/WFRT-Ext25/ecmwf/era5-land/"
start = "1991-01-01"
stop = "2020-12-31"
doi = pd.Timestamp("2002-08-03-T00")

config = dict(
    model="ecmwf",
    domain="era5-land",
    trail_name="04",
    initialize=False,
    initialize_hffmc=False,
    overwinter=False,
    fbp_mode=False,
    correctbias=False,
    root_dir="/Volumes/WFRT-Ext25/ecmwf/era5-land/202202/",
    doi=doi,
)


# import numpy as np
# import matplotlib.pyplot as plt

# # Generate an example array with an abrupt shift
# original_array = np.concatenate([np.linspace(0, 10, 50), np.linspace(20, 10, 50)])

# # Apply a Hann window to smooth the transition
# window_size = 20
# hann_window = np.hanning(window_size * 2)
# smoothed_array = np.convolve(original_array, hann_window / hann_window.sum(), mode='same')

# # Plot the original and smoothed arrays
# plt.plot(original_array, label='Original Array')
# plt.plot(smoothed_array, label='Smoothed Array')
# plt.legend()
# plt.show()


int_ds = read_dataset(config)

# int_ds = salem.open_xr_dataset("/Volumes/WFRT-Ext22/fwf-data/ecmwf/era5/02/fwf-daily-era5-2022122900.nc")
test = salem.open_xr_dataset(
    f"/Volumes/WFRT-Ext25/ecmwf/era5-land/{doi.strftime('%Y%m')}/era5-land-{doi.strftime('%Y%m%d00')}.nc"
)
shape = np.shape(int_ds.T[0, :, :])
shape = shape
zero_full = np.zeros(shape, dtype=float)


# #Reference latitude for DMC day length adjustment
# #46N: Canadian standard, latitude >= 30N   (Van Wagner 1987)
# ell01 <- c(6.5, 7.5, 9, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8, 7, 6)
# #20N: For 30 > latitude >= 10
# ell02 <- c(7.9, 8.4, 8.9, 9.5, 9.9, 10.2, 10.1, 9.7, 9.1,8.6, 8.1, 7.8)
# #20S: For -10 > latitude >= -30
# ell03 <- c(10.1, 9.6, 9.1, 8.5, 8.1, 7.8, 7.9, 8.3, 8.9, 9.4, 9.9, 10.2)
# #40S: For -30 > latitude
# ell04 <- c(11.5, 10.5, 9.2, 7.9, 6.8, 6.2, 6.5, 7.4, 8.7, 10, 11.2, 11.8)
# #For latitude near the equator, we simple use a factor of 9 for all months
# %%
### Day length factor in Duff Moisture Code
month = np.datetime_as_string(int_ds.Time[0], unit="h")
print("Current Month:  ", month[5:7])
month = int(month[5:7]) - 1
L_e_n90_30 = [6.5, 7.5, 9.0, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8.0, 7.0, 6.0][month]
L_e_n30_10 = [7.9, 8.4, 8.9, 9.5, 9.9, 10.2, 10.1, 9.7, 9.1, 8.6, 8.1, 7.8][month]
L_e_e = 9.0
L_e_s30_10 = [10.1, 9.6, 9.1, 8.5, 8.1, 7.8, 7.9, 8.3, 8.9, 9.4, 9.9, 10.2][month]
L_e_s90_30 = [11.5, 10.5, 9.2, 7.9, 6.8, 6.2, 6.5, 7.4, 8.7, 10, 11.2, 11.8][month]

L_e = np.where(int_ds.XLAT.values <= 30, zero_full, L_e_n90_30)
L_e = np.where((int_ds.XLAT.values > 30) | (int_ds.XLAT.values < 10), L_e, L_e_n30_10)
L_e = np.where((int_ds.XLAT.values > 10) | (int_ds.XLAT.values < -10), L_e, L_e_e)
L_e = np.where((int_ds.XLAT.values < -30) | (int_ds.XLAT.values > -10), L_e, L_e_s30_10)
L_e = np.where(int_ds.XLAT.values >= -30, L_e, L_e_s90_30)

# int_ds['L_e'] = (('south_north', 'west_east'), L_e)
# int_ds['L_e'].attrs = int_ds.attrs
# int_ds['L_e'].salem.quick_map()

test["L_e"] = (("latitude", "longitude"), L_e)
test["L_e"].attrs = test.attrs
test["L_e"].salem.quick_map()

# %%

# ### Daylength adjustment in Drought Code
L_f_n = [-1.6, -1.6, -1.6, 0.9, 3.8, 5.8, 6.4, 5.0, 2.4, 0.4, -1.6, -1.6][month]
L_f_e = 1.4
L_f_s = [6.4, 5, 2.4, 0.4, -1.6, -1.6, -1.6, -1.6, -1.6, 0.9, 3.8, 5.8][month]

L_f = np.where(int_ds.XLAT.values <= 20, zero_full, L_f_n)
L_f = np.where((int_ds.XLAT.values > 20) | (int_ds.XLAT.values < -20), L_f, L_f_e)
L_f = np.where(int_ds.XLAT.values >= -20, L_f, L_f_s)

# int_ds['L_f'] = (('south_north', 'west_east'), L_f)
# int_ds['L_f'].attrs = int_ds.attrs
# int_ds['L_f'].salem.quick_map()


test["L_f"] = (("latitude", "longitude"), L_f)
test["L_f"].attrs = test.attrs
test["L_f"].salem.quick_map()
# # t2m['t2m'] = ((t2m['t2m'] -273.15) * (9/5)) + 32
# t2m['t2m'] = t2m['t2m'] -273.15

# t2m['t2m'].attrs = t2m.attrs


# pet = salem.open_xr_dataset(str(save_dir) + f"/pet-climatology-19900101-20201231.nc")

# pet['pet'] = xr.where(pet['pet'] < 1000,pet['pet'], np.nan)
# pet['pet'] = xr.where(pet['pet'] > 0,pet['pet'], 0)

# pet['pet'] = pet['pet']/24
# pet['pet'].isel(month = 5).salem.quick_map()

# pet['pet'] = (pet['pet'] * 39.3701)
# pet['pet'].interp(longitude = -118.3, latitude = 60).plot()

# # pet['S'] = (pet['pet'] - ((1/5) * (t2m['t2m'] - 32)))
# pet['S'] = pet['pet'] - t2m['t2m']

# pet['S'].attrs = pet.attrs

# pet['S'].isel(month = 5).salem.quick_map()
# pet['S'].isel(month = 5).mean()
# pet['S'].interp(longitude = -120.3, latitude = 50).plot()

# # t2m['t2m'].interp(longitude = -120.3, latitude = 50).plot()


# plt.scatter(pet['pet'].isel(month = 5).values.ravel(),t2m['t2m'].isel(month = 5).values.ravel() )
# %%
