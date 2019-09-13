#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 24 18:29:08 2019

@author: rodell
"""
import os
import math
import errno
import numpy as np
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.dates import DateFormatter

from wrf import (to_np, getvar, g_uvmet, ll_to_xy)

"######################  Adjust for user/times of interest/plot customization ######################"
user     = "rodell"
wrf_date = "20190819" 

Plot_Title = 'Fine Fuel Moisture Code'
label      = 12
fig_size   = 20
tick_size  = 12
title_size = 15
plt_fig    = 11

##Baldy BY Station lookouttower
lat, lon = 52.53152, -116.12549



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

save = '/Users/rodell/Google Drive File Stream/Shared drives/Research/CRodell/Model/Images/FFMC/Line/'+wrf_date +'/'
#save = '/Volumes/WFRT-Data02/Images/'+date_time+'/'
make_sure_path_exists(save)

file =	"wrfout_d03_"





""" ####################################################################### """
""" ###################### Grab WRF Variables ####################### """
##initialize list (array) 
rh, temp, wdir, wsp, path_str, utc = [], [], [], [], [], []


#print(path_str[0][-8:-3])
pathlist = sorted(Path(filein).glob(file+'*'))
#print(pathlist)
for path in pathlist:

    path_in_str = str(path)
    path_str.append(path_in_str)
    wrf_file = Dataset(path_in_str,'r')
#    print(wrf_file.variables.keys())
    utc_i        = np.array(getvar(wrf_file, "times"))
    
    xy_np       = np.array(ll_to_xy(wrf_file, lat, lon, meta= False))
    rh_i        = np.array(getvar(wrf_file, "rh2"))
    temp_i      = np.array(getvar(wrf_file, "T2"))-273.15
    lats_i      = np.array(getvar(wrf_file, "lat"))
    lons_i      = np.array(getvar(wrf_file, "lon"))
    wsp_wdir_i  = np.array(g_uvmet.get_uvmet10_wspd_wdir(wrf_file,units='km h-1'))
    wdir_i      = wsp_wdir_i[1,:,:] 
    wsp_i       = wsp_wdir_i[0,:,:] 

    rh_ii   = rh_i[xy_np[0],xy_np[0]]
    temp_ii = temp_i[xy_np[0],xy_np[0]]
    lats_ii = lats_i[xy_np[0],xy_np[0]]
    lons_ii = lons_i[xy_np[0],xy_np[0]]
    wdir_ii = wdir_i[xy_np[0],xy_np[0]]
    wsp_ii  = wsp_i[xy_np[0],xy_np[0]]


    
    shape = np.shape(temp_ii)
    rh.append(rh_ii)
    temp.append(temp_ii)
    wdir.append(wdir_ii)
    wsp.append(wsp_ii)
    utc.append(utc_i)

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

ffmc, m_, m_o_                     = [], [], []
m_d_, m_w_, m_nutral_              = [], [], []
E_d_, E_w_, k_o_, k_d_, k_i_, k_w_ = [], [], [], [], [], []
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
#    m = np.where(m<=250,m, 250)
    m_.append(m)
#    print(np.average(m))
    
    
    F = 82.9 * ((250 - m) / (205.2 + m))
    ffmc.append(F)

    print(path_str[i][-19:-6]+"   "+str(np.average(F)))
    
    m_o = 205.2 * (101 - F) / (82.9 + F)  
    m_o_.append(m_o)

    E_d_.append(E_d)
    E_w_.append(E_w)
    k_o_.append(k_o)
    k_d_.append(k_d)
    k_i_.append(k_i)
    k_w_.append(k_w)
    m_d_.append(m_d)
    m_w_.append(m_w)
    m_nutral_.append(m_nutral)


"############################# Make Plots #############################"

fig, ax = plt.subplots(4,1, figsize=(14,10))
fig.suptitle('Baldy \n Fire Lookout Tower', fontsize=16)
fig.subplots_adjust(hspace=0.18)

ax[0].plot(utc,ffmc, color = 'black')
ax[0].set_ylim(74,101)  
#ax[0].set_xlabel("Datetime (PDT)", fontsize = ylabel)
ax[0].set_ylabel("FFMC", fontsize = label)
ax[0].xaxis.grid(color='gray', linestyle='dashed')
ax[0].yaxis.grid(color='gray', linestyle='dashed')
ax[0].tick_params(axis='both', which='major', labelsize=tick_size)
ax[0].set_facecolor('lightgrey')
ax[0].set_xticklabels([])


ax[1].plot(utc, temp, color = 'red')
ax[1].set_ylim(0,30)  
#ax[0].set_xlabel("Datetime (PDT)", fontsize = ylabel)
ax[1].set_ylabel("Temp (\N{DEGREE SIGN}C)", fontsize = label)
ax[1].xaxis.grid(color='gray', linestyle='dashed')
ax[1].yaxis.grid(color='gray', linestyle='dashed')
ax[1].tick_params(axis='both', which='major', labelsize=tick_size)
ax[1].set_facecolor('lightgrey')
ax[1].set_xticklabels([])
#chartBox = ax[0].get_position()
#ax[0].legend(loc='upper center', bbox_to_anchor=(1.06,0.95), shadow=True, ncol=1)


ax[2].plot(utc, rh, color = 'green')  
ax[2].set_ylim(0,100)
#ax[2].set_xlabel("Datetime (UTC)", fontsize = label)
ax[2].set_ylabel("RH (%)", fontsize = label)
ax[2].xaxis.grid(color='gray', linestyle='dashed')
ax[2].yaxis.grid(color='gray', linestyle='dashed')
ax[2].tick_params(axis='both', which='major', labelsize=tick_size)
ax[2].set_facecolor('lightgrey')
ax[2].set_xticklabels([])


ax[3].plot(utc, wsp, color = 'blue')
ax[3].set_ylim(0,40)  
ax[3].set_xlabels_top = False
ax[3].set_xlabel("Datetime (PDT)", fontsize = label)
ax[3].set_ylabel("Wsp (km/hr)", fontsize = label)
ax[3].xaxis.grid(color='gray', linestyle='dashed')
ax[3].yaxis.grid(color='gray', linestyle='dashed')
ax[3].tick_params(axis='both', which='major', labelsize=tick_size)
ax[3].set_facecolor('lightgrey') 
ax[3].set_xticklabels([])
ax[3].tick_params(axis='x', rotation=30)
xfmt = DateFormatter('%m-%d %H:%M')
ax[3].xaxis.set_major_formatter(xfmt)
 
#ax[4].plot(utc, wdir, color ="blue")  
#ax[4].set_ylim(0,360)
#ax[4].set_xlabel("Datetime (UTC)", fontsize = label)
#ax[4].set_ylabel("Wdir", fontsize = label)
#ax[4].xaxis.grid(color='gray', linestyle='dashed')
#ax[4].yaxis.grid(color='gray', linestyle='dashed')
#ax[4].tick_params(axis='both', which='major', labelsize=tick_size)
#ax[4].set_facecolor('lightgrey')
#xfmt = DateFormatter('%m-%d %H:%M')
#ax[4].tick_params(axis='x', rotation=30)
#ax[4].xaxis.set_major_formatter(xfmt)

#fig.legend(loc = (0.5, 0), ncol=5 )  
#fig.savefig(save + 'Station_vs_HOBO_Pre_Corrected')
##label = date[4:6]+"/"+date[6:8] + '/' + date[2:4] +'  ' + radar +'   ' 

fig.savefig(save + 'Baldy_Tower')  
    
    
    
    







