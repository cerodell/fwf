#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 15:01:30 2019

@author: rodell
"""

import os
import math
import errno
import numpy as np
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import DateFormatter

from wrf import (getvar, g_uvmet, ll_to_xy)

"######################  Adjust for user/times of interest/plot customization ######################"
user     = "rodell"
wrf_date = "20190819" 

Plot_Title = 'Duff Moisture Code'
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

save = '/Users/rodell/Google Drive File Stream/Shared drives/Research/CRodell/Model/Images/DMC/Line/'+wrf_date +'/'
#save = '/Volumes/WFRT-Data02/Images/'+date_time+'/'
make_sure_path_exists(save)

file =	"wrfout_d03_"





""" ####################################################################### """
""" ###################### Grab WRF Variables ####################### """
##initialize list (array) 
rh, temp, wdir, wsp, path_str, qpf_list, utc = [], [], [], [], [], [], []


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
    rain_c_i    = np.array(getvar(wrf_file, "RAINC"))
    rain_sh_i   = np.array(getvar(wrf_file, "RAINSH"))
    rain_nc_i   = np.array(getvar(wrf_file, "RAINNC"))
    qpf_i       = rain_c_i + rain_sh_i + rain_nc_i
    qpf_ii      = np.where(qpf_i>0,qpf_i, qpf_i*0)

    rh_ii   = rh_i[xy_np[0],xy_np[0]]
    temp_ii = temp_i[xy_np[0],xy_np[0]]
    lats_ii = lats_i[xy_np[0],xy_np[0]]
    lons_ii = lons_i[xy_np[0],xy_np[0]]
    wdir_ii = wdir_i[xy_np[0],xy_np[0]]
    wsp_ii  = wsp_i[xy_np[0],xy_np[0]]
    qpf_iii = qpf_ii[xy_np[0],xy_np[0]]


    
    shape = np.shape(temp_ii)
    rh.append(rh_ii)
    temp.append(temp_ii)
    wdir.append(wdir_ii)
    wsp.append(wsp_ii)
    utc.append(utc_i)
    qpf_list.append(qpf_iii)

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
    ##(10)





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

fig, ax = plt.subplots(5,1, figsize=(14,10))
fig.suptitle('Baldy \n Fire Lookout Tower', fontsize=16)
fig.subplots_adjust(hspace=0.18)

ax[0].plot(utc,dmc_, color = 'black')
#ax[0].set_ylim(60,101)  
#ax[0].set_xlabel("Datetime (PDT)", fontsize = ylabel)
ax[0].set_ylabel("DMC", fontsize = label)
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
#ax[3].set_xlabel("Datetime (PDT)", fontsize = label)
ax[3].set_ylabel("Wsp (km/hr)", fontsize = label)
ax[3].xaxis.grid(color='gray', linestyle='dashed')
ax[3].yaxis.grid(color='gray', linestyle='dashed')
ax[3].tick_params(axis='both', which='major', labelsize=tick_size)
ax[3].set_facecolor('lightgrey') 
ax[3].set_xticklabels([])
#ax[3].tick_params(axis='x', rotation=30)
#xfmt = DateFormatter('%m-%d %H:%M')
#ax[3].xaxis.set_major_formatter(xfmt)
 
ax[4].plot(utc, qpf, color ="blue")  
#ax[4].set_ylim(0,360)
ax[4].set_xlabel("Datetime (UTC)", fontsize = label)
ax[4].set_ylabel("QPF", fontsize = label)
ax[4].xaxis.grid(color='gray', linestyle='dashed')
ax[4].yaxis.grid(color='gray', linestyle='dashed')
ax[4].tick_params(axis='both', which='major', labelsize=tick_size)
ax[4].set_facecolor('lightgrey')
xfmt = DateFormatter('%m-%d %H:%M')
ax[4].tick_params(axis='x', rotation=30)
ax[4].xaxis.set_major_formatter(xfmt)

#fig.legend(loc = (0.5, 0), ncol=5 )  
#fig.savefig(save + 'Station_vs_HOBO_Pre_Corrected')
##label = date[4:6]+"/"+date[6:8] + '/' + date[2:4] +'  ' + radar +'   ' 

fig.savefig(save + 'Baldy_Tower')  
    
    
#plt.close("all")
    







