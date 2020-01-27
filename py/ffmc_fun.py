import context
import math
import errno
import numpy as np
import xarray as xr

from context import data_dir
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime



from fwi.utils.read_wrfout import readwrf, dict_xarry
from wrf import (to_np, get_cartopy, latlon_coords)
 
# full_dir = readwrf(filein)

full_dir = str(data_dir) +str('/xr/20200126/20200126_23_ds_wrf.zarr')
ds_wrf = xr.open_zarr(full_dir)



""" ####################################################################### """
""" ############ Mathematical Constants and Usefull Arrays ################ """
# Get the latitude, longitude and projection
# lats, lons = latlon_coords(ds_wrf.rh2)
# cart_proj = get_cartopy(ds_wrf.rh2)

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

ffmc, list_m = [], []

ffmc_list, F_list, M_list = [], [], []

def ffmc(wsp,temp,rh,m_o):
    ########################################################################
    ##(4) 
    a = ((rh-100)/ 10)
    b = (-0.115 * rh)
    print(rh.shape)
    print(temp.shape)
    E_d = (0.942 * np.power(rh[i],0.679)) + (11 * np.power(e_full,a)) \
                   + (0.18 * (21.1 - temp) * (1 - np.power(e_full,b)))
    
    ########################################################################
    ##(5)
    
    E_w    = xr.where(m_o > E_d, zero_full,(0.618 * (np.power(rh,0.753))) +  \
                        (10 * np.power(e_full,((rh - 100) / 10))) + (0.18 * (21.1 - temp)  * \
                         (1 - np.power(e_full,(-0.115 * rh)))))
    
    
    ########################################################################
    ##(6a)
    k_o = xr.where(m_o < E_d, zero_full, 0.424 * (1 - ((rh / 100)** 1.7)) \
                     + 0.0694 * (np.power(wsp, 0.5)) * (1 - ((rh / 100)** 8)) )
    
    #    k_o = 0.424 * (1 - ((rh[i] / 100)** 1.7)) + 0.0694 * (np.power(wsp[i], 0.5)) * (1 - ((rh[i] / 100)** 8))
    
    
    ########################################################################
    ##(6b)
    k_d = xr.where(m_o < E_d, zero_full,k_o * (0.579 * np.power(e_full,(0.0365 * temp))))
    
    
    ########################################################################
    ##(7a)
    
    a = ((100 - rh) / 100)
    k_i = xr.where(m_o > E_w, zero_full, 0.424 * (1 - np.power(a,1.7)) + 0.0694 * \
                   np.power(wsp,0.5) * (1 - np.power(a,8)))
    
    
    ########################################################################
    ###(7b)    
    k_w = xr.where(m_o > E_w, zero_full, k_i * 0.579 * np.power(e_full,(0.0365 * temp)))
    
    
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
        
    F = 82.9 * ((250 - m) / (205.2 + m))    
    m_o = 205.2 * (101 - F) / (82.9 + F)  
    
    F = xr.DataArray(F, name='ffmc', dims=('south_north', 'west_east'))
    m_o = xr.DataArray(m_o, name='m_o',dims=('south_north', 'west_east'))

    # F_list.append(F)
    # M_list.append(m_o)
    var_list = [F,m_o]
    ds = xr.merge(var_list)
    return ds
    ffmc_list.append(ds)    


for i in range(length):
    ffmc = ffmc(ds_wrf.wsp[i],ds_wrf.T2[i],ds_wrf.rh2[i],m_o)
    ffmc_list.append(ffmc)







# def xarray_unlike(dict_list): 
#     xarray_files = []
#     for index in dict_list:
#         ds  = xr.Dataset(index)
#         xarray_files.append(ds)
#     ds_final = xr.combine_nested(xarray_files, 'time')
#     return(ds_final)


# def xarray_like(dict_list):
#     xarray_files = []
#     for index in dict_list:
#         ds  = xr.Dataset(index)
#         xarray_files.append(ds)
#     ds_final = xr.merge(xarray_files,compat='override')    
#     return(ds_final)

# ds_ffmc = xarray_like(ffmc_list)