#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 14:01:24 2019

@author: crodell
"""

import numpy as np
from netCDF4 import Dataset
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors
import cartopy.crs as crs
import math
from cartopy.feature import NaturalEarthFeature
from matplotlib.cm import get_cmap
from mpl_toolkits.axes_grid1 import make_axes_locatable


from wrf import (to_np, getvar, smooth2d, get_cartopy, cartopy_xlim,
                 cartopy_ylim, latlon_coords, g_uvmet)

"######################  Adjust for user/times of interest/plot customization ######################"
user = "rodell"

Plot_Title = 'Fine Fuel Moisture Code'
label      = 15
fig_size   = 20
tick_size  = 12
title_size = 15
plt_fig    = 11

#filein = '/Volumes/Scratch/ALBERTA_2019080500/'
filein  = '/Users/'+user+'/Desktop/WRF/Data/wrfout/'

file =	"wrfout_d03_2019-08-05_18:00:00"








wrf_file = Dataset(filein+file,'r')
print(wrf_file.variables.keys())



rh        = np.array(getvar(wrf_file, "rh2"))
temp      = np.array(getvar(wrf_file, "T2"))-273.15
lats      = np.array(getvar(wrf_file, "lat"))
lons      = np.array(getvar(wrf_file, "lon"))
wsp_wdir  = np.array(g_uvmet.get_uvmet10_wspd_wdir(wrf_file,units='km h-1'))
wsp       = wsp_wdir[0,:,:] 

##varied parameterization scheme to forecast rain..note this is a sum of rain from the starts of the model run  
rain_c    = np.array(getvar(wrf_file, "RAINC"))
rain_sh   = np.array(getvar(wrf_file, "RAINSH"))
rain_nc   = np.array(getvar(wrf_file, "RAINNC"))
qpf_i     = rain_c + rain_sh + rain_nc
qpf       = np.where(qpf_i>0,qpf_i, qpf_i*0)

# Get the latitude and longitude points
cord = getvar(wrf_file, "rh2")
#lats, lons = latlon_coords(cord)

cart_proj = get_cartopy(cord)


#qpf       = [ x if x > 0 else 0.0 for x in qpf_i ]


shape = np.shape(temp)

""" ####################################################################### """
""" ############ Canadian Forest Fire Weather Index System ################ """
e = math.e
e_full    = np.full(shape,e, dtype=float)
zero_full = np.zeros(shape)
ln_ = np.log




""" ####################################################################### """
""" ###################### Equations and Procedures ####################### """

####################################
###Fine Fuel Moisture Code (FFMC)
####################################
##Unknowns
F_o      = 72.0   #Previous day's F becomes F_o
F_o_full = np.full(shape,F_o, dtype=float)
r_o = '?'   #rainfall in open, measured once daily at noon, mm
H   = '?'   #Relative Humidity
T   = '?'   #Temperature
W   = '?'   #Wind Speed
k_1 = '?'   #I think it might be k_i 



##(1)
m_o = 147.2 * (101 - F_o_full) / (59.5 + F_o_full)  

########################################################################
###This could be a source of error, doest make sense to the direction of the greater sign!
qpf_f = np.where(qpf<0.5, qpf, qpf-0.5)
                     

########################################################################
###(3a)
########Will need to figure out how to apply the other aspect of the m_r
########This will also get much more complicated as you begin to loop though each time and run to run!!!!!
m_r = np.where(m_o>=150, zero_full, (m_o + 42.5 * qpf_f * np.power(e_full,(-(100 / (251 - m_o)))) \
                                     * (1 -  np.power(e_full,-(6.93/qpf_f)))))

###(3b)
#m_r = np.where(m_o<150, zero_full, (m_o + 42.5 * qpf_f * np.power(e_full,(-(100 / (251 - m_o)))) \
#                                     * (1 -  np.power(e_full,-(6.93/qpf_f))) \
#                                    + 0.0015 * ((m_o - 150)** 2) * (qpf_f** 2) ))


########################################################################
##(4) 
a = ((rh-100)/ 10)
b = (-0.115 * rh)
E_d = (0.942 * np.power(rh,0.679)) + (11 * np.power(e_full,a)) \
               + (0.18 * (21.1 - temp) * (1 - np.power(e_full,b)))

########################################################################
##(5)
E_w = (0.618 * (np.power(rh,0.753))) + (10 * np.power(e_full,((rh - 100) / 10))) + \x
(0.18 * (21.1 - temp) * (1 - np.power(e_full,-(0.115 * rh))))


########################################################################
##(6a)
k_o = 0.424 * (1 - ((rh / 100)** 1.7)) + 0.0694 * (np.power(wsp, 0.5)) * (1 - ((rh / 100)** 8))


########################################################################
##(6b)
k_d = k_o * (0.581 * np.power(e_full,(0.0365 * temp)))


########################################################################
##(7a)
a = ((100 - rh) / 100)
k_i = 0.424 * (1 - np.power(a,1.7)) + 0.0694 * np.power(wsp,0.5) * (1 - np.power(a,8))


########################################################################
###(7b)
#k_w = k_1 * (0.581 * (e** (0.0365 * T)))

#k_w = k_i * 0.581 * np.power(e_full,(0.0365 * temp))


########################################################################
##(8)
m = E_d + (m_o - E_d) * (10** -(k_d))


########################################################################
##(9)
#m = E_w - (E_w - m_o) * (10** -(k_w))


########################################################################
##(10)
F = 59.5 * ((250 - m) / (147.2 + m))


f_ff = np.where(F>=85,F, F *0)



"############################# Make Plots #############################"
#
#fig, ax1, ax2 = plt.subplots(figsize=(16,14))
fig = plt.figure(figsize=(12,10))
ax2 = plt.axes(projection=cart_proj)

# Download and add the states and coastlines
states = NaturalEarthFeature(category="cultural", scale="50m",
                             facecolor="none",
                             name="admin_1_states_provinces_shp")
ax2.add_feature(states, linewidth=.5, edgecolor="black")
ax2.coastlines('50m', linewidth=0.8)


colors = ["#0000FF","#00E000","#FFFF00", "#E0A000", "#FF0000"]
cmap= matplotlib.colors.ListedColormap(colors)
bounds = [0, 74, 84, 88, 91, math.inf]
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

plt.contourf(to_np(lons), to_np(lats),F, 10,
             transform=crs.PlateCarree(), norm = norm, cmap=cmap)
plt.tight_layout()
#plt.colorbar(ax=ax2, orientation="vertical", pad=.01, shrink=.6)


# Add the gridlines
ax2.gridlines(color="black", linestyle="dotted")

#ax2.axis("off")

plt.title(Plot_Title)

plt.show()








































































