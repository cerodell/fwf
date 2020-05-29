import context
import math
import numpy as np
import pandas as pd
import xarray as xr
import cartopy.crs as crs
import cartopy.feature as cfeature
import timezonefinder, pytz
from datetime import datetime
import matplotlib as mpl
import matplotlib.colors
import matplotlib.pyplot as plt
from wrf import (to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ll_to_xy_proj)


from fwi.utils.ubc_fwi.fwf import FWF
from fwi.utils.wrf.read_wrfout import readwrf
from context import data_dir, xr_dir, wrf_dir, tzone_dir, root_dir




# %%

wrf_file_dir = "/Volumes/CER/WFRT/FWI/Data/20190819_05/"

lat, lon = 49.083, -116.5
wrf_ds, xy_np = readwrf(wrf_file_dir, lat, lon)
print(xy_np)



fwf_file_dir  = str(xr_dir) + "/2019-08-20T00_daily_ds.zarr"

ffmc_ds = xr.open_zarr(fwf_file_dir)

time_ind = -42
time = np.datetime_as_string(ffmc_ds.Time[-18], unit='h')
print(time)


cwfis_file_dir = "/Users/rodell/Google Drive File Stream/Shared drives/Research/CRodell/Model/Data/cwfis/2019/"

filein = "cwfis_fwi2019.csv"
df = pd.read_csv(cwfis_file_dir + filein )
creston = df.loc[df['aes'] == '114B1F0']


obs_08_20 = creston.loc[creston['rep_date'] == '2019-08-20 12:00:00']
obs_08_21 = creston.loc[creston['rep_date'] == '2019-08-21 12:00:00']

ffmc = [obs_08_20["ffmc"], obs_08_21["ffmc"]]


# index_time = [-42, -18]
# obs_time  = np.array([ffmc_ds.Time[index] for index in index_time])

# %%
# # "############################# Make Plots #############################"
Plot_Title = 'Fine Fuel Moisture Code'
label      = 16
fig_size   = 20
tick_size  = 12
title_size = 15
plt_fig    = 11


fig, ax = plt.subplots(5,1, figsize=(14,8))
fig.suptitle(Plot_Title + '\n CRESTON, BC (CWJR)', fontsize=16)
fig.subplots_adjust(hspace=0.1)
ax[0].plot(ffmc_ds.Time[-42],obs_08_20["ffmc"], color = 'firebrick', 
                    marker = "*", linewidth= 5, zorder =10, markersize=12, label = "Observations")
ax[0].plot(ffmc_ds.Time[-18],obs_08_21["ffmc"], color = 'firebrick',
                    marker = "*", linewidth= 5, zorder =10, markersize=12)
ax[0].plot(ffmc_ds.Time,ffmc_ds.F[:,xy_np[1],xy_np[0]], linewidth= 2, color = 'purple', label = "Forcast")
# ax[0].legend() 
ax[0].set_ylabel("FFMC", fontsize = label)
ax[0].xaxis.grid(color='gray', linestyle='dashed')
ax[0].yaxis.grid(color='gray', linestyle='dashed')
ax[0].tick_params(axis='both', which='major', labelsize=tick_size)
ax[0].set_xticklabels([])


ax[1].plot(ffmc_ds.Time[-42],obs_08_20["temp"], color = 'firebrick', 
                    marker = "*", linewidth= 5, zorder =10, markersize=12)
ax[1].plot(ffmc_ds.Time[-18],obs_08_21["temp"], color = 'firebrick',
                    marker = "*", linewidth= 5, zorder =10, markersize=12)
ax[1].plot(ffmc_ds.Time,ffmc_ds.T[:,xy_np[1],xy_np[0]], linewidth= 2, color = 'red')  
# ax[1].set_ylim(0,100)
ax[1].set_ylabel("Temp (\N{DEGREE SIGN}C)", fontsize = label)
ax[1].xaxis.grid(color='gray', linestyle='dashed')
ax[1].yaxis.grid(color='gray', linestyle='dashed')
ax[1].tick_params(axis='both', which='major', labelsize=tick_size)
ax[1].set_xticklabels([])


ax[2].plot(ffmc_ds.Time[-42],obs_08_20["rh"], color = 'firebrick', 
                    marker = "*", linewidth= 5, zorder =10, markersize=12)
ax[2].plot(ffmc_ds.Time[-18],obs_08_21["rh"], color = 'firebrick',
                    marker = "*", linewidth= 5, zorder =10, markersize=12)
ax[2].plot(ffmc_ds.Time,ffmc_ds.H[:,xy_np[1],xy_np[0]], linewidth= 2, color = 'green')  
# ax[2].set_ylim(0,100)
ax[2].set_ylabel("RH (%)", fontsize = label)
ax[2].xaxis.grid(color='gray', linestyle='dashed')
ax[2].yaxis.grid(color='gray', linestyle='dashed')
ax[2].tick_params(axis='both', which='major', labelsize=tick_size)
ax[2].set_xticklabels([])


ax[3].plot(ffmc_ds.Time[-42],obs_08_20["ws"], color = 'firebrick', 
                    marker = "*", linewidth= 5, zorder =10, markersize=12)
ax[3].plot(ffmc_ds.Time[-18],obs_08_21["ws"], color = 'firebrick',
                    marker = "*", linewidth= 5, zorder =10, markersize=12)
ax[3].plot(ffmc_ds.Time,ffmc_ds.W[:,xy_np[1],xy_np[0]], linewidth= 2, color = 'k')  
# ax[3].set_ylim(0,100)
ax[3].set_ylabel(r"WS $\frac{km}{hr}$", fontsize = label)
ax[3].xaxis.grid(color='gray', linestyle='dashed')
ax[3].yaxis.grid(color='gray', linestyle='dashed')
ax[3].tick_params(axis='both', which='major', labelsize=tick_size)
ax[3].set_xticklabels([])

ax[4].plot(ffmc_ds.Time[-42],obs_08_20["precip"], color = 'firebrick', 
                    marker = "*", linewidth= 5, zorder =10, markersize=12)
ax[4].plot(ffmc_ds.Time[-18],obs_08_21["precip"], color = 'firebrick',
                    marker = "*", linewidth= 5, zorder =10, markersize=12)
ax[4].plot(ffmc_ds.Time,ffmc_ds.r_o[:,xy_np[1],xy_np[0]], linewidth= 2, color = 'blue')  
ax[4].set_xlabel("Datetime (UTC)", fontsize = label)
ax[4].set_ylabel("Rain (mm)", fontsize = label)
ax[4].xaxis.grid(color='gray', linestyle='dashed')
ax[4].yaxis.grid(color='gray', linestyle='dashed')
ax[4].tick_params(axis='both', which='major', labelsize=tick_size)


plt.show()

# %%
