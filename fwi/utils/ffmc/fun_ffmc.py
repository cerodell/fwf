import context
import math
import errno
import numpy as np
import xarray as xr

from context import data_dir, xr_dir, wrf_dir
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime


 

class FFMC:
    """
    Class to solve the Fire Weather Indices 



    """



    ######################################################################
    ######################################################################
    def __init__(self, wrf_file_dir, fwi_file_dir):
        """
        Initialize conditions


        """
        ds_wrf = xr.open_zarr(wrf_file_dir)
        self.ds_wrf = ds_wrf

        if fwi_file_dir == None:
            print("No prior FFMC")
            pass
        else:
            print("Found previous FFMC, will merge with ds_wrf")
            ds_ffmc = xr.open_zarr(fwi_file_dir)
            F = np.array(ds_ffmc.F[-1])
            m_o = np.array(ds_ffmc.m_o[-1])
            self.ds_wrf['F'] = (('south_north', 'west_east'), F)
            self.ds_wrf['m_o'] = (('south_north', 'west_east'), m_o)


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
            print("Again found previous FFMC, will initialize with last FFMC :)")

        else:
            print("Again no prior FFMC, initialize with 85s")
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
        E_d:    Equilibrium Moisture content for drying
        E_w:    Equilibrium Moisture content for wetting 
        k_a:    intermediate steps to k_d 
        k_b:    intermediate steps to k_w
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
        ### (2a) Solve Equilibrium Moisture content for drying (E_d)
        ## define powers
        a = 0.679
        b = ((H-100)/ 10)
        c = (-0.115 * H)

        E_d = (0.942 * np.power(H,a)) + (11 * np.power(e_full,b)) \
                    + (0.18 * (21.1 - T) * (1 - np.power(e_full,c)))


        ########################################################################
        ### (2b) Solve Equilibrium Moisture content for wetting (E_w)
        ## define powers (will use b and c from 2a)
        d = 0.753

        E_w  = xr.where(m_o > E_d, zero_full,(0.618 * (np.power(H, d))) +  \
                            (10 * np.power(e_full, b)) + (0.18 * (21.1 - T)  * \
                            (1 - np.power(e_full, c))))


        ########################################################################
        ### (3a) intermediate step to k_d (k_a)
        # a = ((100 - H) / 100)   ## Van Wagner 1987
        a = H/100               ## Van Wagner 1977

        k_a = xr.where(m_o < E_d, zero_full, 0.424 * (1 - np.power(a,1.7)) \
                        + 0.0694 * (np.power(W, 0.5)) * (1 - np.power(a,8)) )


        ########################################################################
        ### (3b) Log drying rate for hourly computation, log to base 10 (k_d)
        b = 0.0579    

        k_d = xr.where(m_o < E_d, zero_full, b * k_a * np.power(e_full,(0.0365 * T)))


        ########################################################################
        ### (4a) intermediate steps to k_w (k_b)
        a = ((100 - H) / 100)

        k_b = xr.where(m_o > E_w, zero_full, 0.424 * (1 - np.power(a,1.7)) + 0.0694 * \
                    np.power(W,0.5) * (1 - np.power(a,8)))


        ########################################################################
        ### (4b)  Log wetting rate for hourly computation, log to base 10 (k_w)
        b = 0.0579    

        k_w = xr.where(m_o > E_w, zero_full, b * k_b * np.power(e_full,(0.0365 * T)))


        ########################################################################
        ### (5a) intermediate dry moisture code (m_d)

        m_d = xr.where(m_o < E_d, zero_full, E_d + ((m_o - E_d) * np.power(e_full, -2.303*(k_d))))


        ########################################################################
        ### (5b) intermediate wet moisture code (m_w)

        m_w = xr.where(m_o > E_w, zero_full, E_w - ((E_w - m_o) * np.power(e_full, -2.303*(k_w))))


        ########################################################################
        ### (5c) intermediate neutral moisture code (m_neutral)

        m_neutral = xr.where((E_d<=m_o),zero_full, xr.where((m_o<=E_w) ,zero_full,m_o))


        ########################################################################
        ### (6) combine dry, wet, neutral moisture codes

        m = m_d + m_w + m_neutral
        m = xr.where(m<=250,m, 250)
        
        ### Solve for FFMC 
        F = (82.9 * (250 - m)) / (205.2 + m)

        ### Recast initial moisture code for next time stamp  
        m_o = (205.2 * (101 - F)) / (82.9 + F)  
        
        ### Add FFMC and moisture code to xarray 
        self.ds_wrf['F']   = F
        self.ds_wrf['m_o'] = m_o

        ### Return xarray 
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


        # ### Name file after initial time of wrf 
        file_name = np.datetime_as_string(ds_ffmc.Time[0], unit='h')

        print("FFMC initialized at :", file_name)

        # # ## Write and save DataArray (.zarr) file
        make_dir = Path(str(xr_dir) + str('/') + file_name + str(f"_ds_ffmc.zarr"))

        ### Check if file exists....else write file
        if make_dir.exists():
            the_size = make_dir.stat().st_size
            print(
                ("\n{} already exists\n" "and is {} bytes\n" "will not overwrite\n").format(
                    file_name, the_size
                )
            )
        else:
            make_dir.mkdir(parents=True, exist_ok=True)
            ds_ffmc.compute()
            ds_ffmc.to_zarr(make_dir, "w")
            print(f"wrote {make_dir}")
        
        ## return path to xr file to open
        return str(make_dir)
