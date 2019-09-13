#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 19:17:45 2019

@author: rodell
"""


""" ####################################################################### """
""" ############ Canadian Forest Fire Weather Index System ################ """

import os
import math
import errno
import numpy as np
from netCDF4 import Dataset
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors
import cartopy.crs as crs
from pathlib import Path
#import cartopy as cart
import cartopy.feature as cfeature
from datetime import datetime
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
#from cartopy.feature import NaturalEarthFeature
#from matplotlib.cm import get_cmap
#from mpl_toolkits.axes_grid1 import make_axes_locatable


from wrf import (to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ALL_TIMES)


	


"######################  Adjust for user/times of interest/plot customization ######################"
user     = "crodell"
wrf_date = "20190819" 

Plot_Title = 'Fine Fuel Moisture Code'
label      = 15
fig_size   = 20
tick_size  = 12
title_size = 15
plt_fig    = 11



# Function for creating filepaths if the path does not already exist
def make_sure_path_exists(path):
    if os.path.isdir(path):
        return
    else:
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

#filein = '/Volumes/Scratch/ALBERTA_2019080500/'
#filein  = '/Users/'+user+'/Desktop/WRF/Data/wrfout/'
#filein ='/Volumes/WFRT-Data02/Data/wrfout/'+wrf_date+'/'
#make_sure_path_exists(filein)
filein  = '/home/'+user+'/Data/'


now = datetime.now() # current date and time
date_time = now.strftime("%Y%m%d_%H%M")
print("date and time:",date_time)

save = '/home/'+user+'/Images/FFMC/Contourf/'
#save = '/Users/rodell/Google Drive File Stream/Shared drives/Research/CRodell/Model/Images/FFMC/Contour/'+wrf_date +'/'+date_time+'/'
#save = '/Volumes/WFRT-Data02/Images/'+date_time+'/'
#make_sure_path_exists(save)

file =	"wrfout_d03_"




""" ####################################################################### """
""" ###################### Grab WRF Variables ####################### """

rh, temp, wsp, qpf_list, path_str = [], [], [], [], []

#print(path_str[0][-8:-3])
pathlist = sorted(Path(filein).glob(file+'*'))
#print(pathlist)
for path in pathlist:

    path_in_str = str(path)
    path_str.append(path_in_str)
    wrf_file = Dataset(path_in_str,'r')
#    print(wrf_file.variables.keys())
    
    

    rh_i        = np.array(getvar(wrf_file, "rh2"))
    temp_i      = np.array(getvar(wrf_file, "T2"))-273.15
    lats_i      = np.array(getvar(wrf_file, "lat"))
    lons_i      = np.array(getvar(wrf_file, "lon"))
    wsp_wdir_i  = np.array(g_uvmet.get_uvmet10_wspd_wdir(wrf_file,units='km h-1'))
    wsp_i       = wsp_wdir_i[0,:,:] 
    
    ##varied parameterization scheme to forecast rain..note this is a sum of rain from the starts of the model run  
    rain_c_i    = np.array(getvar(wrf_file, "RAINC"))
    rain_sh_i   = np.array(getvar(wrf_file, "RAINSH"))
    rain_nc_i   = np.array(getvar(wrf_file, "RAINNC"))
    qpf_i       = rain_c_i + rain_sh_i + rain_nc_i
    qpf_ii      = np.where(qpf_i>0,qpf_i, qpf_i*0)
    cord        = getvar(wrf_file, "rh2")   
    shape = np.shape(temp_i)
    rh.append(rh_i)
    temp.append(temp_i)
    wsp.append(wsp_i)
    qpf_list.append(qpf_ii)
    
    
# Get the latitude, longitude and projection of wrfout...doesnt matter what variable you use
#cord = getvar(filein+file+'*', "rh2", timeidx=ALL_TIMES)
lats, lons = latlon_coords(cord)
cart_proj = get_cartopy(cord)

""" ####################################################################### """
""" ############ Mathematical Constants and Usefull Arrays ################ """
######Math Constants
e = math.e
ln_ = np.log
length = len(temp)  ##nice for looping below

e_full    = np.full(shape,e, dtype=float)
zero_full = np.zeros(shape, dtype=float)

######Initial FFMC Values
F_o      = 85.0   #Previous day's F becomes F_o
F_o_full = np.full(shape,F_o, dtype=float)



""" ####################################################################### """
""" ################## Fine Fuel Moisture Code (FFMC) ##################### """

##(1)
m_o = 205.2 * (101 - F_o_full) / (82.9 + F_o_full)  

ffmc = []

for i in range(length):

#i = 1
    ########################################################################

    
                         
    
    ########################################################################
    ###(3a)
    
    
    ########################################################################
    ##(4) 
    a = ((rh[i]-100)/ 10)
    b = (-0.115 * rh[i])
    
    E_d = (0.942 * np.power(rh[i],0.679)) + (11 * np.power(e_full,a)) \
                   + (0.18 * (21.1 - temp[i]) * (1 - np.power(e_full,b)))
    
    ########################################################################
    ##(5)
    
    E_w    = np.where(m_o > E_d, zero_full,(0.618 * (np.power(rh[i],0.753))) +  \
                        (10 * np.power(e_full,((rh[i] - 100) / 10))) + (0.18 * (21.1 - temp[i])  * \
                         (1 - np.power(e_full,(-0.115 * rh[i])))))
    
    
    ########################################################################
    ##(6a)
    k_o = np.where(m_o < E_d, zero_full, 0.424 * (1 - ((rh[i] / 100)** 1.7)) \
                     + 0.0694 * (np.power(wsp[i], 0.5)) * (1 - ((rh[i] / 100)** 8)) )
    
    #    k_o = 0.424 * (1 - ((rh[i] / 100)** 1.7)) + 0.0694 * (np.power(wsp[i], 0.5)) * (1 - ((rh[i] / 100)** 8))
    
    
    ########################################################################
    ##(6b)
    k_d = np.where(m_o < E_d, zero_full,k_o * (0.579 * np.power(e_full,(0.0365 * temp[i]))))
    
    
    ########################################################################
    ##(7a)
    
    a = ((100 - rh[i]) / 100)
    k_i = np.where(m_o > E_w, zero_full, 0.424 * (1 - np.power(a,1.7)) + 0.0694 * \
                   np.power(wsp[i],0.5) * (1 - np.power(a,8)))
    
    
    ########################################################################
    ###(7b)    
    k_w = np.where(m_o > E_w, zero_full, k_i * 0.579 * np.power(e_full,(0.0365 * temp[i])))
    
    
    ########################################################################
    ##(8)
    m_d = np.where(m_o < E_d, zero_full, E_d + ((m_o - E_d) * np.power(e_full, -2.303*(k_d))))
        
    
    
    ########################################################################
    ##(9)
    m_w = np.where(m_o > E_w, zero_full, E_w - ((E_w - m_o) * np.power(e_full, -2.303*(k_w))))
    
    m_nutral = np.where((E_d<=m_o),zero_full, np.where((m_o<=E_w) ,zero_full,m_o))
    
    ########################################################################
    ##(10)
    m = m_d + m_w + m_nutral
    m = np.where(m<=250,m, 250)
    
#    print(np.average(m))
    
    
    F = 82.9 * ((250 - m) / (205.2 + m))
    ffmc.append(F)

    print(path_str[i][-19:-6]+"   "+str(np.average(F)))
    
    m_o = 205.2 * (101 - F) / (82.9 + F)  
    
    
"############################# Make Plots #############################"

#for i in range(0,len(ffmc),3):  
plot_start = datetime.now() # current date and time
i = 2
fig = plt.figure(figsize=(16,10))
ax2 = plt.axes(projection=cart_proj)

# Download and create the states, land, and oceans using cartopy features
states = cfeature.NaturalEarthFeature(category='cultural', scale='50m',
                                      facecolor='none',
                                      name='admin_1_states_provinces_shp')
land = cfeature.NaturalEarthFeature(category='physical', name='land',
                                    scale='50m',
                                    facecolor=cfeature.COLORS['land'])
ocean = cfeature.NaturalEarthFeature(category='physical', name='ocean',
                                     scale='50m',
                                     facecolor=cfeature.COLORS['water'])
lake = cfeature.NaturalEarthFeature(category='physical', name='lakes',
                                     scale='50m',
                                     facecolor=cfeature.COLORS['water'])

ax2.add_feature(states, linewidth=.5, edgecolor="black")
#ax2.add_feature(land)
ax2.add_feature(ocean)              
ax2.add_feature(lake, linewidth=.25, edgecolor="black")

#ax2.add_feature(cart.feature.OCEAN, zorder=100, edgecolor='#A9D0F5')
#ax2.add_feature(cart.feature.LAKES, zorder=100, edgecolor='#A9D0F5')
ax2.coastlines('50m', linewidth=0.8)


colors = ["#0000FF","#00E000","#FFFF00", "#E0A000", "#FF0000"]
cmap= matplotlib.colors.ListedColormap(colors)
bounds = [0, 74, 84, 88, 91, math.inf]
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

plt.contourf(to_np(lons), to_np(lats),ffmc[i], extend = 'both',
             transform=crs.PlateCarree(), norm = norm, cmap=cmap)

            
#    plt.tight_layout()
#plt.colorbar(ax=ax2, orientation="vertical", pad=.01, shrink=.6)


# Add the gridlines
#gl = ax2.gridlines(color="black", linestyle="dotted")
#gl.xformatter = LONGITUDE_FORMATTER
#gl.yformatter = LATITUDE_FORMATTER
#gl.xlabel_style = {'size': 15, 'color': 'gray'}

#ax2.axis("off")

plt.xticks([-1772000,-849900,-1125,831400,1737000,2754000],
           ('130'u"\u00b0"" W", '120'u"\u00b0"" W", '110'u"\u00b0"" W", '100'u"\u00b0"" W", '90'u"\u00b0"" W", '80'u"\u00b0"" W"))
plt.yticks([-4520000,-4143000,-3753000,-3372000,-2991000],
           ('45'u"\u00b0"" N", '48'u"\u00b0"" N", '51'u"\u00b0"" N", '54'u"\u00b0"" N", '57'u"\u00b0"" N"))

plt.xlim(-753900,108200)
plt.ylim(-4448000,-2989000)

plt.title(r"Fine Fuel Moisture Code" + "\n" + "Init: " +  path_str[0][-19:-3] + "Z        --->   Valid: " + path_str[i][-19:-3]+"Z")
fig.savefig(save + path_str[i][-19:-6])
#    plt.close('all')
plt.tight_layout(pad=1.08, h_pad=0.4, w_pad=None, rect=None)

print(path_str[i][-19:-6])

plot_stop = datetime.now() # current date and time
diff = plot_stop - plot_start

print(diff)

#zzz___ = 3312000 + 1772000
#zzzzzzzz = np.arange(-1772000,3312000,(5084000/7))
#plt.close('all')

    


























































