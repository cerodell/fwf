import context
import math
import errno
import numpy as np
import xarray as xr


from read_wrfout import readwrf
from wrf import (to_np, get_cartopy, latlon_coords)

filein ='/Volumes/CER/WFRT/FWI/Data/20190819/'
 
ds_wrf = readwrf(filein)


""" ####################################################################### """
""" ############ Mathematical Constants and Usefull Arrays ################ """
# Get the latitude, longitude and projection
lats, lons = latlon_coords(ds_wrf.rh2)
cart_proj = get_cartopy(ds_wrf.rh2)

######Math Constants
e = math.e
ln_ = np.log

length = len(ds_wrf.Time) 
shape = np.shape(ds_wrf.T2[0,:,:])
e_full    = np.full(shape,e, dtype=float)
zero_full = np.zeros(shape, dtype=float)

# ######Initial FFMC Values
F_o      = 85.0   #Previous day's F becomes F_o
F_o_full = np.full(shape,F_o, dtype=float)



# """ ####################################################################### """
# """ ################## Fine Fuel Moisture Code (FFMC) ##################### """

# ##(1)
m_o = 205.2 * (101 - F_o_full) / (82.9 + F_o_full)  

# ffmc, list_m = [], []

ffmc_list = []

for i in range(length):
#i = 1
    
    ########################################################################
    ##(4) 
    a = ((ds_wrf.rh2[i,:,:]-100)/ 10)
    b = (-0.115 * ds_wrf.rh2[i,:,:])
    
    E_d = (0.942 * np.power(ds_wrf.rh2[i,:,:],0.679)) + (11 * np.power(e_full,a)) \
                   + (0.18 * (21.1 - ds_wrf.T2[i,:,:]) * (1 - np.power(e_full,b)))
    
    ########################################################################
    ##(5)
    
    E_w    = xr.where(m_o > E_d, zero_full,(0.618 * (np.power(ds_wrf.rh2[i,:,:],0.753))) +  \
                        (10 * np.power(e_full,((ds_wrf.rh2[i,:,:] - 100) / 10))) + (0.18 * (21.1 - ds_wrf.T2[i,:,:])  * \
                         (1 - np.power(e_full,(-0.115 * ds_wrf.rh2[i,:,:])))))
    
    
    ########################################################################
    ##(6a)
    k_o = xr.where(m_o < E_d, zero_full, 0.424 * (1 - ((ds_wrf.rh2[i,:,:] / 100)** 1.7)) \
                     + 0.0694 * (np.power(ds_wrf.uvmet10_wspd_wdir[i,:,:], 0.5)) * (1 - ((ds_wrf.rh2[i,:,:] / 100)** 8)) )
    
    #    k_o = 0.424 * (1 - ((rh[i] / 100)** 1.7)) + 0.0694 * (np.power(wsp[i], 0.5)) * (1 - ((rh[i] / 100)** 8))
    
    
    ########################################################################
    ##(6b)
    k_d = xr.where(m_o < E_d, zero_full,k_o * (0.579 * np.power(e_full,(0.0365 * ds_wrf.T2[i,:,:]))))
    
    
    ########################################################################
    ##(7a)
    
    a = ((100 - ds_wrf.rh2[i,:,:]) / 100)
    k_i = xr.where(m_o > E_w, zero_full, 0.424 * (1 - np.power(a,1.7)) + 0.0694 * \
                   np.power(ds_wrf.uvmet10_wspd_wdir[i,:,:],0.5) * (1 - np.power(a,8)))
    
    
    ########################################################################
    ###(7b)    
    k_w = xr.where(m_o > E_w, zero_full, k_i * 0.579 * np.power(e_full,(0.0365 * ds_wrf.T2[i,:,:])))
    
    
    ########################################################################
    ##(8)
    m_d = xr.where(m_o < E_d, zero_full, E_d + ((m_o - E_d) * np.power(e_full, -2.303*(k_d))))
        
    
    
    ########################################################################
    ##(9)
    m_w = xr.where(m_o > E_w, zero_full, E_w - ((E_w - m_o) * np.power(e_full, -2.303*(k_w))))
    
    m_nutral = xr.where((E_d<=m_o),zero_full, xr.where((m_o<=E_w) ,zero_full,m_o))
    
    ########################################################################
    ##(10)
    m = m_d + m_w + m_nutral
    m = xr.where(m<=250,m, 250)
    
#    print(np.average(m))
    
    
    F = 82.9 * ((250 - m) / (205.2 + m))
    m_o = 205.2 * (101 - F) / (82.9 + F)  
    
    # F = xr.DataArray(F, name='ffmc', dims=('time', 'south_north', 'west_east'))
    # m_o = xr.DataArray(m_o, name='m_o', dims=('time', 'south_north', 'west_east'))



    var_dict={}
    dims = ('time', 'south_north', 'west_east')
    def dict_xarry(var):
        var_dict.update({'ffmc' : (dims,np.array(F, dtype=float))})
        var_dict.update({'m_o' : (dims,np.array(m_o, dtype=float))})
    var_dict.update({'time' : (dims,F.Time)})
    var_dict.update({'ffmc' : (dims,np.array(F, dtype=float))})
    var_dict.update({'m_o' : (dims,np.array(m_o, dtype=float))})






    # var_list = [F,m_o]
    # ds = xr.merge(var_list)
    ffmc_list.append(var_dict)    


# ds_ffmc = xr.combine_nested(ffmc_list, "time")
