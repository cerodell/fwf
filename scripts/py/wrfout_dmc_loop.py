#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 13:50:47 2019

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
import cartopy.feature as cfeature
from datetime import datetime



from wrf import (to_np, getvar, get_cartopy, latlon_coords, g_uvmet)


	


"######################  Adjust for user/times of interest/plot customization ######################"
user     = "rodell"
wrf_date = "20190819" 

Plot_Title = 'Duff Moisture Code'
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
filein ='/Volumes/WFRT-Data02/Data/wrfout/'+wrf_date+'/'
#make_sure_path_exists(filein)


now = datetime.now() # current date and time
date_time = now.strftime("%Y%m%d_%H%M")
print("date and time:",date_time)

save = '/Users/rodell/Google Drive File Stream/Shared drives/Research/CRodell/Model/Images/DMC/Contour/'+wrf_date +'/'+date_time+'/'
#save = '/Volumes/WFRT-Data02/Images/'+date_time+'/'
make_sure_path_exists(save)

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



l_e = [6.5, 7.5, 9.0, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8.0, 7.0, 6.0]
index = int(wrf_date[-3])
l_e = l_e[(index-1)]
l_e = np.full(shape, l_e, dtype=float)

######Initial DMC Values
p_o      = 6.0   #Previous day's P becomes P_o
p_o_full = np.full(shape, p_o, dtype=float)

k_o       = 1.894 * (temp[0] + 1.1)* (100 - rh[0]) * (l_e * 10**-6)
######Needed to calculate the differance in qpf from hour to hour
qpf_list.insert(0,zero_full)
qpf = []
for i in range(length):
    qpf_iii = qpf_list[i+1]-qpf_list[i]
    qpf_iv  = np.where(qpf_iii>0,qpf_iii, qpf_iii*0)
    qpf.append(qpf_iv)
#    qpf.append((qpf_iv/24))

""" ####################################################################### """
""" ########################### Duff Moisture Code ######################## """

##(1)
p_o = p_o_full + 100 * k_o


qpf_, m_o_                       = [], []
b_low_, b_mid_, b_high_          = [], [], []
m_r_low_, m_r_mid_, m_r_high_    = [], [], []
m_r_, p_r_, k_                   = [], [], []
dmc_, dmc_dry_, dmc_wet_         = [], [], []
p_o_                             = []
""" ####################################################################### """


for i in range(length):

    #    i = 1
    ########################################################################
    ##(11)

    qpf_wet_i  = np.where(qpf[i]<(1.5), qpf[i],(0.92*qpf[i]) - 1.27)

    qpf_wet    = np.where(qpf_wet_i>0., qpf_wet_i,0.0000001)
    
                         
    
    ########################################################################
    ###(12)
    a = (5.6348 - (p_o/43.43))
    m_o = np.where(qpf_wet < 1.5, zero_full, 20 + np.power(e_full,a))
    
    ########################################################################
    ##(13a) 
    b_low = np.where(qpf_wet < 1.5, zero_full, 
                     np.where(p_o >= 33, zero_full, 100/(0.5 + (0.3 * p_o))))
    
    ########################################################################
    ##(5)
    
    b_mid = np.where(qpf_wet < 1.5, zero_full, 
                     np.where(p_o < 33, zero_full, 
                              np.where(p_o >= 65, zero_full, 14 - (1.3* ln_(p_o)))))

    
    ########################################################################
    ##(6a)
    
    b_high = np.where(qpf_wet < 1.5, zero_full, 
                      np.where(p_o < 65, zero_full, (6.2*ln_(p_o))-17.2))

    
    ########################################################################
    ##(6b)
    m_r_low = np.where(qpf_wet < 1.5, zero_full, 
                       np.where(p_o >= 33, zero_full, m_o + (1000 * qpf_wet) / (48.77 + b_low * qpf_wet)))
    
    m_r_mid = np.where(qpf_wet < 1.5, zero_full, 
                       np.where(p_o < 33, zero_full, 
                                np.where(p_o >= 65, zero_full, m_o + (1000 * qpf_wet) / (48.77 + b_mid * qpf_wet))))
                    
    m_r_high = np.where(qpf_wet < 1.5, zero_full, 
                       np.where(p_o < 65, zero_full, m_o + (1000 * qpf_wet) / (48.77 + b_high * qpf_wet)))
                       
    m_r = m_r_low + m_r_mid + m_r_high
    ########################################################################
    ##(7a)
    
    p_r = np.where(qpf_wet < 1.5, zero_full, 244.72 - (43.43* ln_(m_r-20)))
    ########################################################################
    ###(7b)    

    k = 1.894 * (temp[i] + 1.1)* (100 - rh[i]) * (l_e * 10**-6)
    
    p_d = np.where(qpf_wet > 1.5, zero_full, p_o + 100 * k)

     
    ########################################################################
    ##(8)
    
    dmc_dry = np.where(qpf_wet > 1.5, zero_full, p_d + 100 *k )
    
    dmc_wet = np.where(qpf_wet < 1.5, zero_full, p_r + 100 *k )
    
    dmc = dmc_dry + dmc_wet
    ########################################################################
    p_o = p_r + p_d
    
    ########################################################################


    qpf_.append(qpf_wet)
    m_o_.append(m_o)
    b_low_.append(b_low)
    b_mid_.append(b_mid)
    b_high_.append(b_high)
    m_r_low_.append(m_r_low)
    m_r_mid_.append(m_r_mid)
    m_r_high_.append(m_r_high)
    m_r_.append(m_r)
    p_r_.append(p_r)
    k_.append(k)
    dmc_dry_.append(dmc_dry)
    dmc_wet_.append(dmc_wet)
    dmc_.append(dmc)
    p_o_.append(p_o)

"############################# Make Plots #############################"
for i in range(0,len(dmc_),3):  
#i = 5
    fig = plt.figure(figsize=(12,10))
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
    bounds = [0, 21, 27, 40, 60, math.inf]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    
    plt.contourf(to_np(lons), to_np(lats),dmc_[i], extend = 'both',
                 transform=crs.PlateCarree(), norm = norm, cmap=cmap)
    
                
    #    plt.tight_layout()
    #plt.colorbar(ax=ax2, orientation="vertical", pad=.01, shrink=.6)
    
    
    # Add the gridlines
    ax2.gridlines(color="black", linestyle="dotted")
    
    #ax2.axis("off")
    
    plt.title(Plot_Title + '   ' + path_str[i][-19:-3])
    fig.savefig(save + path_str[i][-19:-6])
    plt.close('all')
    
    
    print(path_str[i][-19:-6])
    
    
    
#plt.close('all')































































