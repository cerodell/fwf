#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 13:22:03 2019

@author: rodell
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 14:01:24 2019

@author: crodell
"""
""" ####################################################################### """
""" ############ Canadian Forest Fire Weather Index System ################ """


import numpy as np
from netCDF4 import Dataset
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors
import cartopy.crs as crs
from pathlib import Path
import cartopy as cart
from datetime import datetime, timedelta
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

#save = '/Users/rodell/Google Drive File Stream/Shared drives/Research/CRodell/Model/Images/FFMC/Loop/'


file =	"wrfout_d03_"



rh, temp, wsp, qpf_list, path_str = [], [], [], [], []


""" ####################################################################### """
""" ###################### Grab WRF Variables ####################### """
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
    
    shape = np.shape(temp_i)
    rh.append(rh_i)
    temp.append(temp_i)
    wsp.append(wsp_i)
    qpf_list.append(qpf_ii)
    
    
# Get the latitude, longitude and projection of wrfout...doesnt matter what variable you use
cord = getvar(wrf_file, "rh2")
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


######Needed to calculate the differance in qpf from hour to hour
qpf_list.insert(0,zero_full)
qpf = []
for i in range(length):
    qpf_iii = qpf_list[i+1]-qpf_list[i]
    qpf_iv  = np.where(qpf_iii>0,qpf_iii, qpf_iii*0)
    qpf.append(qpf_iv)
#    qpf.append((qpf_iv/24))

#print(np.max(qpf[2]))

""" ####################################################################### """
""" ################## Fine Fuel Moisture Code (FFMC) ##################### """

##(1)
m_o = 147.2 * (101 - F_o_full) / (59.5 + F_o_full)  

ffmc = []

for i in range(length):

#i = 1
    ########################################################################
    ###This could be a source of error, doest make sense to the direction of the greater sign!
    #    qpf_dry = np.where(qpf[i]<=0.5, qpf[i], qpf[i]*0)
    #    qpf_wet_i  = np.where(qpf[i]<0.5, qpf[i],qpf[i] - 0.5)
    qpf_wet_i  = np.where(qpf[i]<(0.5/24), qpf[i],qpf[i] - (0.5/24))
    
    qpf_wet    = np.where(qpf_wet_i>0., qpf_wet_i,0.0000001)
    
                         
    
    ########################################################################
    ###(3a)
    ########Will need to figure out how to apply the other aspect of the m_r
    ########This will also get much more complicated as you begin to loop though each time and run to run!!!!!
    
    m_r_high = np.where(m_o>=150 , zero_full, (m_o + 42.5 * qpf_wet * np.power(e_full,((-100 / (251 - m_o)))) \
                                         * (1 -  np.power(e_full,(-6.93/qpf_wet)))))
    
    #print(np.where(m_r_high<150))
    ###(3b)
    m_r_low = np.where(m_o<150, zero_full, (m_o + 42.5 * qpf_wet * np.power(e_full,((-100 / (251 - m_o)))) \
                                         * (1 -  np.power(e_full,(-6.93/qpf_wet))) \
                                        + 0.0015 * ((m_o - 150)** 2) * (qpf_wet** 2) ))
    
    m_r = m_r_high + m_r_low
    
    m_r = np.where(m_r<=250,m_r, 250)
    
    #print(np.average(m_r))
    
    ########################################################################
    ##(4) 
    a = ((rh[i]-100)/ 10)
    b = (-0.115 * rh[i])
    
    E_d = (0.942 * np.power(rh[i],0.679)) + (11 * np.power(e_full,a)) \
                   + (0.18 * (21.1 - temp[i]) * (1 - np.power(e_full,b)))
    
    ########################################################################
    ##(5)
    
    E_w    = np.where(m_r > E_d, zero_full,(0.618 * (np.power(rh[i],0.753))) +  \
                        (10 * np.power(e_full,((rh[i] - 100) / 10))) + (0.18 * (21.1 - temp[i])  * \
                         (1 - np.power(e_full,(-0.115 * rh[i])))))
    
    
    ########################################################################
    ##(6a)
    k_o = np.where(m_r < E_d, zero_full, 0.424 * (1 - ((rh[i] / 100)** 1.7)) \
                     + 0.0694 * (np.power(wsp[i], 0.5)) * (1 - ((rh[i] / 100)** 8)) )
    
    #    k_o = 0.424 * (1 - ((rh[i] / 100)** 1.7)) + 0.0694 * (np.power(wsp[i], 0.5)) * (1 - ((rh[i] / 100)** 8))
    
    
    ########################################################################
    ##(6b)
    k_d = np.where(m_r < E_d, zero_full,k_o * (0.581 * np.power(e_full,(0.0365 * temp[i]))))
    
    
    ########################################################################
    ##(7a)
    
    a = ((100 - rh[i]) / 100)
    k_i = np.where(m_r > E_w, zero_full, 0.424 * (1 - np.power(a,1.7)) + 0.0694 * \
                   np.power(wsp[i],0.5) * (1 - np.power(a,8)))
    
    
    ########################################################################
    ###(7b)    
    k_w = np.where(m_r > E_w, zero_full, k_i * 0.581 * np.power(e_full,(0.0365 * temp[i])))
    
    
    ########################################################################
    ##(8)
    m_d = np.where(m_r < E_d, zero_full, E_d + ((m_r - E_d) * (10** -(k_d))))
        
    
    
    ########################################################################
    ##(9)
    m_w = np.where(m_r > E_w, zero_full, E_w - ((E_w - m_r) * (10** -(k_w))))
    
    m_nutral = np.where((E_d<=m_r) & (m_r<=E_w) ,zero_full,m_r)
    
    ########################################################################
    ##(10)
    m = m_d + m_w 
    m = np.where(m<=250,m, 250)
    
    #    print(np.average(m))
    
    
    F = 59.5 * ((250 - m) / (147.2 + m))
    ffmc.append(F)

    print(path_str[i][-19:-6]+"   "+str(np.average(F)))
    
    m_o = 147.2 * (101 - F) / (59.5 + F)  
    
    
"############################# Make Plots #############################"
# 
#for i in range(0,len(ffmc),3):  
for i in range(len(ffmc)):  

#i = 5
    #fig, ax1, ax2 = plt.subplots(figsize=(16,14))
    fig = plt.figure(figsize=(12,10))
    ax2 = plt.axes(projection=cart_proj)
    
    # Download and add the states and coastlines
    states = NaturalEarthFeature(category="cultural", scale="50m",
                                 facecolor="none",
                                 name="admin_1_states_provinces_shp")
    ax2.add_feature(states, linewidth=.5, edgecolor="black")
    ax2.add_feature(cart.feature.OCEAN, zorder=100, edgecolor='#A9D0F5')
    ax2.add_feature(cart.feature.LAKES, zorder=100, edgecolor='#A9D0F5')
    ax2.coastlines('50m', linewidth=0.8)
    
    
    colors = ["#0000FF","#00E000","#FFFF00", "#E0A000", "#FF0000"]
    cmap= matplotlib.colors.ListedColormap(colors)
    bounds = [0, 74, 84, 88, 91, math.inf]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    
    plt.contourf(to_np(lons), to_np(lats),ffmc[i], 10,
                 transform=crs.PlateCarree(), norm = norm, cmap=cmap)
    #    plt.tight_layout()
    #plt.colorbar(ax=ax2, orientation="vertical", pad=.01, shrink=.6)
    
    
    # Add the gridlines
    ax2.gridlines(color="black", linestyle="dotted")
    
    #ax2.axis("off")
    
    plt.title(Plot_Title + path_str[i][-19:-3])
#    fig.savefig(save + path_str[i][-19:-6])
#    plt.close('all')
    
    
    print(path_str[i][-19:-6])
    
    
#    
    
    


























































