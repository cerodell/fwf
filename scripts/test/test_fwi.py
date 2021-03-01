import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.ndimage as ndimage
from scipy.ndimage.filters import gaussian_filter

from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta

np.seterr(divide="ignore", invalid="ignore")


domain = "d03"
# date = pd.Timestamp("today")
date = pd.Timestamp(2018, 7, 20)
forecast_date = date.strftime("%Y%m%d06")

file_dir = str(fwf_zarr_dir) + f"/fwf-hourly-{domain}-{forecast_date}.zarr"


hourly_ds = xr.open_zarr(file_dir)

loop_time = datetime.now()
shape = np.shape(hourly_ds.T[0, :, :])

# # self.e_full    = np.full(shape,e, dtype=float)
zero_full = np.zeros(shape, dtype=float)


# Eqs. 28b, 28a, 29
bb < -ifelse(
    bui > 80,
    0.1 * isi * (1000 / (25 + 108.64 / exp(0.023 * bui))),
    0.1 * isi * (0.626 * (bui ^ 0.809) + 2),
)
# Eqs. 30b, 30a
fwi < -ifelse(bb <= 1, bb, exp(2.72 * ((0.434 * log(bb)) ^ 0.647)))

# def solve_isi(hourly_ds, fbp = False):
#   ### Call on initial conditions
#   W, F, m_o = hourly_ds.W, hourly_ds.F, hourly_ds.m_o


#   ########################################################################
#   ### (24) Solve for wind function (f_W) with condition for fbp
#   f_W  = xr.where((W >= 40) & (fbp==True),
#                   12 * (1 - np.exp(-0.0818 * (W - 28))),
#                   np.exp(0.05039 * W))

#   ########################################################################
#   ### (25) Solve for fine fuel moisture function (f_F)
#   f_F = 91.9 * np.exp(-0.1386 * m_o) * (1 + np.power(m_o,5.31) / 4.93e7)

#   ########################################################################
#   ### (26) Solve for initial spread index (R)
#   R = 0.208 * f_W * f_F
#   R = xr.DataArray(R, name="R", dims=("time", "south_north", "west_east"))

#   return R


R = solve_isi(hourly_ds, fbp=False)


W, F, m_o = hourly_ds.W, hourly_ds.F, hourly_ds.m_o


########################################################################
### (24) Solve for wind function (f_W)
# a = 0.05039 * W
# f_W = np.power(e_full, a)
## TODO need to rethink this....incluce both ISI and ISI_fbp
# This modification is Equation 53a in FCFDG (1992) (Lawson 2008)
W_limit = 40.0

f_W_low = xr.where(W > W_limit, zero_full, np.exp(0.05039 * W))
f_W_high = xr.where(W <= W_limit, zero_full, 12 * (1 - np.exp(-0.0818 * (W - 28))))
f_W = f_W_low + f_W_low

########################################################################
### (25) Solve for fine fuel moisture function (f_F)
# a = -0.1386 * m_o
# # b = np.power(e_full, a)
# b = np.exp(a)
# c = (1 + np.power(m_o, 5.31) / (4.93e7))
# f_F = 91.9 * b * c

f_F = 91.9 * np.exp(-0.1386 * m_o) * (1 + np.power(m_o, 5.31) / (4.93e7))
########################################################################
### (26) Solve for initial spread index (R)

R_old = 0.208 * f_W * f_F

R_old = xr.DataArray(R_old, name="R", dims=("time", "south_north", "west_east"))


# def solve_ffmc(hourly_ds):
#   startTime = datetime.now()
#   W, T, H, r_o, m_o, F = (
#       hourly_ds.W,
#       hourly_ds.T,
#       hourly_ds.H,
#       hourly_ds.r_o_hourly,
#       hourly_ds.m_o,
#       hourly_ds.F,
#   )


#   ########################################################################
#   ### Solve for the effective rainfall routine (r_f)
#   r_f = xr.where(r_o > 0.5, (r_o - 0.5), xr.where(r_o < 1e-7, 1e-5, r_o))
#   ########################################################################
#   ### (1) Solve the Rainfall routine as defined in  Van Wagner 1985 (m_r)
#   m_o = xr.where(
#       m_o <= 150,
#       m_o + (42.5 * r_f * np.exp((-100 / (251 - m_o))) * (1 - np.exp((-6.93 / r_f)))),
#       m_o + (42.5 * r_f * np.exp((-100 / (251 - m_o))) * (1 - np.exp((-6.93 / r_f))))
#       + (0.0015 * np.power((m_o - 150), 2) * np.power(r_f, 0.5))
#   )

#   m_o = np.where(m_o > 250, 250, np.where(m_o < 0, 1e-5, m_o))

#   ########################################################################
#   ### (2a) Solve Equilibrium Moisture content for drying (E_d)

#   E_d = 0.942 * np.power(H, 0.679) + (11 * np.exp(((H - 100) / 10))) + (0.18 * (21.1 - T) * (1 - np.exp((-0.115 * H))))


#   ########################################################################
#   ### (2b) Solve Equilibrium Moisture content for wetting (E_w)

#   E_w = (0.618 * (np.power(H, 0.753))) + (10 * np.exp(((H - 100) / 10))) + (0.18 * (21.1 - T) * (1 - np.exp((-0.115 * H))))


#   ########################################################################
#   ### (3a) intermediate step to k_d (k_a)
#   k_a = 0.424 * (1 - np.power(H / 100, 1.7)) + 0.0694 * (np.power(W, 0.5)) * (1 - np.power(H / 100, 8))


#   ########################################################################
#   ### (3b) Log drying rate for hourly computation, log to base 10 (k_d)
#   k_d =  0.0579 * k_a * np.exp(0.0365 * T)

#   ########################################################################
#   ### (4a) intermediate steps to k_w (k_b)
#   k_b = 0.424 * (1 - np.power(((100 - H) / 100), 1.7)) + 0.0694 * np.power(W, 0.5) * (1 - np.power(((100 - H) / 100), 8))

#   ########################################################################
#   ### (4b)  Log wetting rate for hourly computation, log to base 10 (k_w)
#   k_w = 0.0579 * k_b * np.exp(0.0365 * T)

#   ########################################################################
#   ### (5a) intermediate dry moisture code (m_d)
#   m_d = E_d + ((m_o - E_d) * np.exp(-2.303 * (k_d)))

#   ########################################################################
#   ### (5b) intermediate wet moisture code (m_w)
#   m_w = E_w - ((E_w - m_o) * np.exp(-2.303 * (k_w)))

#   ########################################################################
#   ### (5c) combine dry, wet, neutral moisture codes
#   m = xr.where(m_o > E_d, m_d, m_w)
#   m = xr.where((E_d >= m_o) & (m_o >= E_w), m_o, m)

#   ########################################################################
#   ### (6) Solve for FFMC
#   F = (59.5 * (250 - m)) / (147.27723 + m)  ## Van 1985

#   ### Recast initial moisture code for next time stamp
#   m_o = (147.27723 * (101 - F)) / (59.5 + F)  ## Van 1985

#   F = F.to_dataset(name="F")
#   F["m_o"] = m_o

#   F_ds_new = F

#   print("New FFMC Time: ", datetime.now() - startTime)

#   return F_ds_new

# FFMC = [solve_ffmc(hourly_ds.isel(time=i)) for i in range(len(hourly_ds.time))]

# blah  = xr.combine_nested(FFMC, "time")

# # hourly_ds = hourly_ds.isel(time = 0)

# print("Loop FFMC Time: ", datetime.now() - loop_time)


# startTime = datetime.now()

# W, T, H, r_o, m_o, F = (
#     hourly_ds.W,
#     hourly_ds.T,
#     hourly_ds.H,
#     hourly_ds.r_o_hourly,
#     hourly_ds.m_o,
#     hourly_ds.F,
# )

# shape = np.shape(hourly_ds.T)

# # self.e_full    = np.full(shape,e, dtype=float)
# zero_full = np.zeros(shape, dtype=float)

# ########################################################################
# ### (1b) Solve for the effective rain (r_f)
# ## Van/Pick define as 0.5
# r_limit = 0.5
# r_fi = xr.where(r_o < r_limit, r_o, (r_o - r_limit))
# r_f = xr.where(r_fi > 1e-7, r_fi, 1e-7)

# ########################################################################
# ### (1c) Solve the Rainfall routine as defined in  Van Wagner 1985 (m_r)
# m_o_limit = 150
# # a =  (-100 / (251 - m_o))
# # b = (-6.93 / r_f)
# # m_r_low = xr.where(m_o >= m_o_limit, zero_full, m_o + \
# #                     (42.5 * r_f * np.power(e_full,a) * (1- np.power(e_full,b))))

# m_r_low = xr.where(
#     m_o >= m_o_limit,
#     zero_full,
#     m_o
#     + (42.5 * r_f * np.exp((-100 / (251 - m_o))) * (1 - np.exp((-6.93 / r_f)))),
# )

# ########################################################################
# ### (1d) Solve the RainFall routine as defined in  Van Wagner 1985 (m_r)
# # m_r_high = xr.where(m_o < m_o_limit, zero_full, m_o + \
# #                     (42.5 * r_f * np.power(e_full, a) * (1 - np.power(e_full, b))) + \
# #                         (0.0015 * np.power((m_o - 150),2) * np.power(r_f, 0.5)))

# m_r_high = xr.where(
#     m_o < m_o_limit,
#     zero_full,
#     m_o
#     + (42.5 * r_f * np.exp((-100 / (251 - m_o))) * (1 - np.exp((-6.93 / r_f))))
#     + (0.0015 * np.power((m_o - 150), 2) * np.power(r_f, 0.5)),
# )

# ########################################################################
# ### (1e) Set new m_o with the rainfall routine (m_o)
# m_o = m_r_low + m_r_high
# m_o = np.where(m_o < 250, m_o, 250)  # Set upper limit of 250
# m_o = np.where(m_o > 0, m_o, 1e4)  # Set lower limit of 0

# ########################################################################
# ### (2a) Solve Equilibrium Moisture content for drying (E_d)
# ## define powers
# a = 0.679
# # b = ((H-100)/ 10)
# # c = (-0.115 * H)

# # E_d = (0.942 * np.power(H,a)) + (11 * np.power(e_full,b)) \
# #             + (0.18 * (21.1 - T) * (1 - np.power(e_full,c)))

# E_d = (
#     (0.942 * np.power(H, a))
#     + (11 * np.exp(((H - 100) / 10)))
#     + (0.18 * (21.1 - T) * (1 - np.exp((-0.115 * H))))
# )

# ########################################################################
# ### (2b) Solve Equilibrium Moisture content for wetting (E_w)
# ## define powers (will use b and c from 2a)
# d = 0.753

# # E_w  = xr.where(m_o > E_d, zero_full,(0.618 * (np.power(H, d))) +  \
# #                     (10 * np.power(e_full, b)) + (0.18 * (21.1 - T)  * \
# #                     (1 - np.power(e_full, c))))

# E_w = xr.where(
#     m_o > E_d,
#     zero_full,
#     (0.618 * (np.power(H, d)))
#     + (10 * np.exp(((H - 100) / 10)))
#     + (0.18 * (21.1 - T) * (1 - np.exp((-0.115 * H)))),
# )

# ########################################################################
# ### (3a) intermediate step to k_d (k_a)
# # a = ((100 - H) / 100)   ## Van Wagner 1987
# # a = H/100               ## Van Wagner 1977

# k_a = xr.where(
#     m_o < E_d,
#     zero_full,
#     0.424 * (1 - np.power(H / 100, 1.7))
#     + 0.0694 * (np.power(W, 0.5)) * (1 - np.power(H / 100, 8)),
# )

# ########################################################################
# ### (3b) Log drying rate for hourly computation, log to base 10 (k_d)
# b = 0.0579

# # k_d = xr.where(m_o < E_d, zero_full, b * k_a * np.power(e_full,(0.0365 * T)))
# k_d = xr.where(m_o < E_d, zero_full, b * k_a * np.exp(0.0365 * T))

# ########################################################################
# ### (4a) intermediate steps to k_w (k_b)
# # a = ((100 - H) / 100)

# k_b = xr.where(
#     m_o > E_w,
#     zero_full,
#     0.424 * (1 - np.power(((100 - H) / 100), 1.7))
#     + 0.0694 * np.power(W, 0.5) * (1 - np.power(((100 - H) / 100), 8)),
# )

# ########################################################################
# ### (4b)  Log wetting rate for hourly computation, log to base 10 (k_w)
# b = 0.0579

# # k_w = xr.where(m_o > E_w, zero_full, b * k_b * np.power(e_full,(0.0365 * T)))
# k_w = xr.where(m_o > E_w, zero_full, b * k_b * np.exp(0.0365 * T))

# ########################################################################
# ### (5a) intermediate dry moisture code (m_d)

# # m_d = xr.where(m_o < E_d, zero_full, E_d + ((m_o - E_d) * np.power(e_full, -2.303*(k_d))))  ## Van Wagner 1977
# # m_d = xr.where(m_o < E_d, zero_full, E_d + ((m_o - E_d) * np.power(10, -(k_d))))            ## Van Wagner 1985

# m_d = xr.where(
#     m_o < E_d, zero_full, E_d + ((m_o - E_d) * np.exp(-2.303 * (k_d)))
# )  ## Van Wagner 1977

# ########################################################################
# ### (5b) intermediate wet moisture code (m_w)

# # m_w = xr.where(m_o > E_w, zero_full, E_w - ((E_w - m_o) * np.power(e_full, -2.303*(k_w))))  ## Van Wagner 1977
# # m_w = xr.where(m_o > E_w, zero_full, E_w - ((E_w - m_o) * np.power(10, -(k_w))))            ## Van Wagner 1985

# m_w = xr.where(
#     m_o > E_w, zero_full, E_w - ((E_w - m_o) * np.exp(-2.303 * (k_w)))
# )  ## Van Wagner 1977

# ########################################################################
# ### (5c) intermediate neutral moisture code (m_neutral)

# m_neutral = xr.where(
#     (E_d <= m_o), zero_full, xr.where((m_o <= E_w), zero_full, m_o)
# )

# ########################################################################
# ### (6) combine dry, wet, neutral moisture codes

# m = m_d + m_w + m_neutral
# m = xr.where(m <= 250, m, 250)

# ### Solve for FFMC
# # F = (82.9 * (250 - m)) / (205.2 + m)    ## Van 1977
# F = (59.5 * (250 - m)) / (147.27723 + m)  ## Van 1985

# ### Recast initial moisture code for next time stamp
# # m_o = (205.2 * (101 - F)) / (82.9 + F)  ## Van 1977
# m_o = (147.27723 * (101 - F)) / (59.5 + F)  ## Van 1985

# F = F.to_dataset(name="F")
# F["m_o"] = m_o

# F_ds = F
# print("Old FFMC Time: ", datetime.now() - startTime)
