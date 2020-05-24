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
            print("No prior FFMC, DMC or DC")
            pass
        else:
            print("Found previous FFMC, will merge with ds_wrf")
            ds_ffmc = xr.open_zarr(fwi_file_dir)
            F = np.array(ds_ffmc.F[-1])
            m_o = np.array(ds_ffmc.m_o[-1])
            self.ds_wrf['F'] = (('south_north', 'west_east'), F)
            self.ds_wrf['m_o'] = (('south_north', 'west_east'), m_o)
            print("Found previous DMC, will merge with ds_wrf")
            P = np.array(ds_ffmc.P[-1])
            self.ds_wrf['P'] = (('south_north', 'west_east'), P)


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

        ### Daylength factor in Duff Moisture Code
        month = np.datetime_as_string(ds_wrf.Time[0], unit='h')
        print(month[5:7])
        month = (int(month[5:7]) - 1)
        L_e = [6.5, 7.5, 9.0, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8.0, 7.0, 6.0]
        L_e = L_e[month]
        # print(L_e)


        if "F" in ds_wrf:
            print("Again found previous FFMC, will initialize with last FFMC :)")

        else:
            # """ ################## Fine Fuel Moisture Code (FFMC) ##################### """
            print("Again no prior FFMC, initialize with 85s")
            F_o      = 85.0   #Previous day's F becomes F_o
            F_o_full = np.full(shape,F_o, dtype=float)
            self.ds_wrf['F'] = (('south_north', 'west_east'), F_o_full)

            ### (1)
            m_o = 205.2 * (101 - F_o_full) / (82.9 + F_o_full)  
            ### Add to xarry 
            self.ds_wrf['m_o'] = (('south_north', 'west_east'), m_o)
        
            # """ ####################   Duff Moisture Code (DCM)    ##################### """
            print("Again no prior DMC, initialize with 6s")
            L_e = np.full(shape, L_e, dtype=float)
            self.L_e = L_e
            P_o      = 6.0   #Previous day's P becomes P_o
            P_o_full = np.full(shape, P_o, dtype=float)

            ### (16)
            K_o      = 1.894 * (ds_wrf.T[0] + 1.1)* (100 - ds_wrf.H[0]) * (L_e * 10**-6)

            ##(1)
            P_o = P_o_full + (100 * K_o)
            self.ds_wrf['P'] = (('south_north', 'west_east'), P_o)

            # """ #####################     Drought Code (DC)       ########################### """


        return



    ######################################################################
    ######################################################################
    def solve_ffmc(self, ds_wrf):

        """
        This function calculates the Fine Fuel Moisture Code at a one-hour interval writes/outputs as an xarray
        
        Parameters
        ----------
        ds_wrf: xarray of wrf variables

        Variables
        ----------
        m_o:    initial fine fuel moisture content
        m:      final fine fuel moisture content
        F_o:    initial FFMC
        F:      final FFMC
        E_d:    Equilibrium Moisture content for drying
        E_w:    Equilibrium Moisture content for wetting 
        k_a:    intermediate steps to k_d 
        k_b:    intermediate steps to k_w
        k_d:    log drying rate for hourly computation, log to base 10
        k_w:    log wetting rate for hourly computation, log to base 10
        H:      relative humidity, %
        W:      wind speed km/hr
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

        P = ds_wrf.P
        self.ds_wrf['P'] = P * m_o
        ### Return xarray 
        return ds_wrf



    def solve_dmc(self, ds_wrf):

        """
        This function calculates the Duff Moisture Code at a one-hour interval writes/outputs as an xarray
        
        Parameters
        ----------
        ds_wrf: xarray of wrf variables

        r_o:  total qpf

        Variables
        ----------
        M_o:    initial duff moisture content
        M_r:    duff moisture content after rain
        M:      final duff moisture content
        P_o:    initial DMC
        P_r:    DMC after rain
        P:      final DMC
        b:      three coefficient with their own empirical equation for diff range of P_o
        K:      Log drying rate
        H:      relative humidity, %
        W:      wind, km/hr
        T:      temperature, C    
        r_o:    total rain
        r_e:    effective rain

        Returns
        -------
        
        ds_P: an xarray of DMC
        """

        W, T, H, r_o, P_o, L_e = ds_wrf.W, ds_wrf.T, ds_wrf.H, ds_wrf.r_o, ds_wrf.P, self.L_e

        e_full, zero_full = self.e_full, self.zero_full

        ln = np.log

        ########################################################################
        ### (11) Solve for the effective rain (r_e) 

        r_ei  = np.where(r_o<(1.5), r_o,(0.92*r_o) - 1.27)

        r_e    = np.where(r_ei>0., r_ei,0.0000001)


        ########################################################################
        ### (12) 
        a = (5.6348 - (P_o/43.43))
        M_o = xr.where(r_e < 1.5, zero_full, 20 + np.power(e_full,a))
        
        ########################################################################
        ### (13a) Solve for coefficients b where P_o <= 33 (b_low)
        b_low = xr.where(r_e < 1.5, zero_full, 
                        xr.where(P_o >= 33, zero_full, 100/(0.5 + (0.3 * P_o))))
        
        ########################################################################
        ### (13b) Solve for coefficients b where 33 < P_o <= 65 (b_mid)
        
        b_mid = xr.where(r_e < 1.5, zero_full, 
                        xr.where(P_o < 33, zero_full, 
                                xr.where(P_o >= 65, zero_full, 14 - (1.3* ln(P_o)))))

        
        ########################################################################
        ### (13c) Solve for coefficients b where  P_o > 65 (b_high)
        
        b_high = np.where(r_e < 1.5, zero_full, 
                        np.where(P_o < 65, zero_full, (6.2*ln(P_o))-17.2))

        
        ########################################################################
        ##(6b)
        m_r_low = xr.where(r_e < 1.5, zero_full, 
                        xr.where(P_o >= 33, zero_full, M_o + (1000 * r_e) / (48.77 + b_low * r_e)))
        
        m_r_mid = xr.where(r_e < 1.5, zero_full, 
                        xr.where(P_o < 33, zero_full, 
                                    xr.where(P_o >= 65, zero_full, M_o + (1000 * r_e) / (48.77 + b_mid * r_e))))
                        
        m_r_high = xr.where(r_e < 1.5, zero_full, 
                        xr.where(P_o < 65, zero_full, M_o + (1000 * r_e) / (48.77 + b_high * r_e)))
                        
        m_r = m_r_low + m_r_mid + m_r_high
        ########################################################################
        ##(7a)
        
        p_r = xr.where(r_e < 1.5, zero_full, 244.72 - (43.43* ln(m_r-20)))
        ########################################################################
        ###(7b)    

        k = 1.894 * (T + 1.1)* (100 - H) * (L_e * 10**-6)
        
        p_d = xr.where(r_e > 1.5, zero_full, P_o + 100 * k)

        
        ########################################################################
        ##(8)
        
        dmc_dry = xr.where(r_e > 1.5, zero_full, p_d + 100 *k )
        
        dmc_wet = xr.where(r_e < 1.5, zero_full, p_r + 100 *k )
        
        dmc = dmc_dry + dmc_wet

        return



    def loop_ds(self):
        ds_wrf = self.ds_wrf
        test = self.ds_wrf
        # print(ds_wrf.keys())
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
    #     # ds_final = xr.merge(xarray_files,compat='override')
    #     # ds_final = xr.concat(xarray_files)
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
