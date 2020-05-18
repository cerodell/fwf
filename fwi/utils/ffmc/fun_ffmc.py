import context
import math
import numpy as np
import xarray as xr
from context import data_dir, xr_dir, wrf_dir


 
# full_dir = readwrf(filein)

full_dir = str(data_dir) +str('/xr/20200126/20200126_23_ds_wrf.zarr')
ds_wrf = xr.open_zarr(full_dir)


# scp -r /Volumes/CER/WFRT/FWI/Data/20190819 crodell@bluesky2.eoas.ubc.ca:/home/crodell/fwf/data/wrf 

""" ####################################################################### """
""" ############ Mathematical Constants and Usefull Arrays ################ """

######Math Constants
e = math.e
ln_ = np.log

length = len(ds_wrf.Time) 
shape = np.shape(ds_wrf.T[0,:,:])
e_full    = np.full(shape,e, dtype=float)
zero_full = np.zeros(shape, dtype=float)

# ######Initial FFMC Values
F_o      = 85.0   #Previous day's F becomes F_o
F_o_full = np.full(shape,F_o, dtype=float)



# """ ####################################################################### """
# """ ################## Fine Fuel Moisture Code (FFMC) ##################### """

# ##(1)
m_o = 205.2 * (101 - F_o_full) / (82.9 + F_o_full)  

FFMC, list_m = [], []

FFMC_list, F_list, M_list = [], [], []

def FFMC(W,T,H,m_o):

    """
    This function calculates the Fine Fuel Moisture Code at a one-hour interval writes/outputs as an xarray
    
    Parameters
    ----------
    T:    temp (degC)
    W:    wind speed (km h-1)
    H:    relative humidity (%)
    m_o:  Inital fine fuel MC

    Variables
    ----------
    m_o:    initial fine fule MC
    m:      final MC
    F_o:    initial FFMC
    F:      final FFMC
    E_d:    EMC for drying
    E_w:    EMC for wetting 
    k_a:    intermediate steps to k_d and k_w
    k_b:    intermediate steps to k_d and k_w
    k_d:    log drying rate for hourly computation, log to base 10
    k_w:    log wetting rate for hourly computation, log to base 10
    H:      relative humidity, %
    W:      wind, km/hr
    T:      temperature, C    

    Returns
    -------
    
    ds_F: an xarray of FFMC
    """


    ########################################################################
    ##(2a) 
    # define powers
    a = 0.679
    b = ((H-100)/ 10)
    c = (-0.115 * H)
    print(H.shape)
    print(T.shape)

    E_d = (0.942 * np.power(H[i],a)) + (11 * np.power(e_full,b)) \
                   + (0.18 * (21.1 - T) * (1 - np.power(e_full,c)))
    
    ########################################################################
    ##(2b)
    
    E_w  = xr.where(m_o > E_d, zero_full,(0.618 * (np.power(H,0.753))) +  \
                        (10 * np.power(e_full,((H - 100) / 10))) + (0.18 * (21.1 - T)  * \
                         (1 - np.power(e_full,(-0.115 * H)))))
    
    
    ########################################################################
    ##(3a)
    k_a = xr.where(m_o < E_d, zero_full, 0.424 * (1 - ((H / 100)** 1.7)) \
                     + 0.0694 * (np.power(W, 0.5)) * (1 - ((H / 100)** 8)) )
    
    #    k_a = 0.424 * (1 - ((H[i] / 100)** 1.7)) + 0.0694 * (np.power(wsp[i], 0.5)) * (1 - ((H[i] / 100)** 8))
    
    
    ########################################################################
    ##(3b)
    k_d = xr.where(m_o < E_d, zero_full,k_a * (0.579 * np.power(e_full,(0.0365 * T))))
    
    
    ########################################################################
    ##(4a)
    
    a = ((100 - H) / 100)
    k_b = xr.where(m_o > E_w, zero_full, 0.424 * (1 - np.power(a,1.7)) + 0.0694 * \
                   np.power(W,0.5) * (1 - np.power(a,8)))
    
    
    ########################################################################
    ###(4b)    
    k_w = xr.where(m_o > E_w, zero_full, k_b * 0.579 * np.power(e_full,(0.0365 * T)))
    
    
    ########################################################################
    ##(5a)
    m_d = xr.where(m_o < E_d, zero_full, E_d + ((m_o - E_d) * np.power(e_full, -2.303*(k_d))))
        
    
    
    ########################################################################
    ##(5b)
    m_w = xr.where(m_o > E_w, zero_full, E_w - ((E_w - m_o) * np.power(e_full, -2.303*(k_w))))

    ########################################################################
    ##(5c)  
    m_nutral = xr.where((E_d<=m_o),zero_full, xr.where((m_o<=E_w) ,zero_full,m_o))
    

    ########################################################################
    ##(6)
    m = m_d + m_w + m_nutral
    m = xr.where(m<=250,m, 250)
        
    F = 82.9 * ((250 - m) / (205.2 + m))    
    m_o = 205.2 * (101 - F) / (82.9 + F)  
    
    F = xr.DataArray(F, name='FFMC', dims=('south_north', 'west_east'))
    m_o = xr.DataArray(m_o, name='m_o',dims=('south_north', 'west_east'))

    # F_list.append(F)
    # M_list.append(m_o)
    var_list = [F,m_o]
    ds = xr.merge(var_list)
    return ds
    FFMC_list.append(ds)    




