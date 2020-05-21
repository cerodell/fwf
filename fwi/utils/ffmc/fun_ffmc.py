import context
import math
import errno
import numpy as np
import xarray as xr

from context import data_dir
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime



# from fwi.utils.read_wrfout import readwrf, dict_xarry
# from wrf import (to_np, get_cartopy, latlon_coords)
 

class FFMC:
    """
    Class to solve the Fire Weather Indices 



    """



    ######################################################################
    ######################################################################
    def __init__(self, file_dir):
        """
        Initialize conditions


        """
        ds_wrf = xr.open_zarr(file_dir)
        self.ds_wrf = ds_wrf


        ############ Mathematical Constants and Usefull Arrays ################ 
        ### Math Constants
        e = math.e

        ### Length of forecast
        self.length = len(ds_wrf.Time)
        print("Time len: ", self.length)

        ### Shape of Domain
        shape = np.shape(ds_wrf.T[0,:,:])
        self.e_full    = np.full(shape,e, dtype=float)
        self.zero_full = np.zeros(shape, dtype=float)

        if "F" in ds_wrf:
            var_exists = True
            print("FFMC exists from last run",var_exists)

        else:
            var_exists = False
            print("FFMC exists from last run",var_exists)
            F_o      = 85.0   #Previous day's F becomes F_o
            F_o_full = np.full(shape,F_o, dtype=float)
            self.ds_wrf['F'] = (('south_north', 'west_east'), F_o_full)

            # """ ################## Fine Fuel Moisture Code (FFMC) ##################### """
            ### (1)
            m_o = 205.2 * (101 - F_o_full) / (82.9 + F_o_full)  
            ### Add to xarry 
            self.ds_wrf['m_o'] = (('south_north', 'west_east'), m_o)
        


        return



    ######################################################################
    ######################################################################
    def solve_ffmc(self, ds_wrf):

        """
        This function calculates the Fine Fuel Moisture Code at a one-hour interval writes/outputs as an xarray
        
        Parameters
        ----------
        T:    temp (degC)
        W:    wind speed (km h-1)
        H:    relative humidity (%)
        m_o:  Initial fine fuel MC

        Variables
        ----------
        m_o:    initial fine fuel MC
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

        ### Call on initial conditions
        W, T, H, m_o = ds_wrf.W, ds_wrf.T, ds_wrf.H, ds_wrf.m_o

        e_full, zero_full = self.e_full, self.zero_full


        ########################################################################
        ##(2a) 
        # define powers
        a = 0.679
        b = ((H-100)/ 10)
        c = (-0.115 * H)
        # print(H.shape)
        print(T.shape)

        E_d = (0.942 * np.power(H,a)) + (11 * np.power(e_full,b)) \
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
        m_neutral = xr.where((E_d<=m_o),zero_full, xr.where((m_o<=E_w) ,zero_full,m_o))
        

        ########################################################################
        ##(6)
        m = m_d + m_w + m_neutral
        m = xr.where(m<=250,m, 250)
            
        F = 82.9 * ((250 - m) / (205.2 + m))    
        m_o = 205.2 * (101 - F) / (82.9 + F)  
        
        self.ds_wrf['F'] = F
        self.ds_wrf['m_o'] = m_o


        # var_list = [F_xr,m_o_xr]
        # ds = xr.merge(var_list)

        return ds_wrf


    def loop_ds(self):
        ds_wrf = self.ds_wrf
        FFMC_list = []
        print("Length: ",self.length)
        for i in range(self.length):
            FFMC = self.solve_ffmc(ds_wrf.isel(time = i))
            FFMC_list.append(FFMC)
        return FFMC_list


    def xarray_unlike(self,dict_list): 
        xarray_files = []
        for index in dict_list:
            ds  = xr.Dataset(index)
            xarray_files.append(ds)
        ds_final = xr.combine_nested(xarray_files, 'time')
        return(ds_final)


    # def xarray_like(self,dict_list):
    #     xarray_files = []
    #     for index in dict_list:
    #         ds  = xr.Dataset(index)
    #         xarray_files.append(ds)
    #     ds_final = xr.merge(xarray_files,compat='override')    
    #     return(ds_final)

    def xr_ffmc(self):
        FFMC_list = self.loop_ds()
        ds_ffmc = self.xarray_unlike(FFMC_list)
        return ds_ffmc