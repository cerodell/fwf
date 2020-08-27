#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import math
import errno
import pickle
import numpy as np
import xarray as xr
from timezonefinder import TimezoneFinder


from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from utils.read_wrfout import readwrf
from context import xr_dir, wrf_dir, tzone_dir



 

class FWF:
    """
    Class to solve the Fire Weather Indices using output from a numerical weather model

    Parameters
    ----------

    wrf_file_dir: str
        - File directory to (zarr) file of WRF met variables to calculate FWI
    hourly_file_dir: str
        - File directory to (zarr) file of yestersdays hourly FWI codes
        - Needed for carry over to intilaze the model
    daily_file_dir: str
        - File directory to (zarr) file of yestersdays daily FWI codes
        - Needed for carry over to intilaze the model


    Returns
    -------
        
    daily_ds: DataSet 
        Writes a DataSet (zarr) of daily FWI indeces/codes 
        - Duff Moisture Code
        - Drought Code
        - Build Up Index

    hourly_ds: DataSet 
        Writes a DataSet (zarr) of daily FWI indeces/codes 
        - Fine Fuel Moisture Code
        - Initial Spread index
        - Fire Weather Index

    """



    """########################################################################"""
    """ ######################## Initialize FWI model #########################"""
    """########################################################################"""
    def __init__(self, wrf_file_dir, hourly_file_dir, daily_file_dir):
        """
        Initialize Fire Weather Index Model


        """
        ### Read then open WRF dataset
        wrf_ds, xy_np = readwrf(wrf_file_dir)
        self.attrs    = wrf_ds.attrs


        ############ Mathematical Constants and Usefull Arrays ################ 
        ### Math Constants
        e = math.e

        ### Shape of Domain make useful fill arrays
        shape = np.shape(wrf_ds.T[0,:,:])
        print("Domain shape:  ",shape)
        self.e_full    = np.full(shape,e, dtype=float)
        self.zero_full = np.zeros(shape, dtype=float)
        self.ones_full = np.full(shape,1, dtype=float)

        ### Daylength factor in Duff Moisture Code
        month = np.datetime_as_string(wrf_ds.Time[0], unit='h')
        print("Current Month:  ", month[5:7])
        month = (int(month[5:7]) - 1)
        L_e = [6.5, 7.5, 9.0, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8.0, 7.0, 6.0]
        L_e = L_e[month]
        self.L_e = L_e

        ### Daylength adjustment in Drought Code
        L_f = [-1.6, -1.6, -1.6, 0.9, 3.8, 5.8, 6.4, 5.0, 2.4, 0.4, -1.6, -1.6]
        L_f = L_f[month]
        self.L_f = L_f

        ### Time Zone classification method
        tzdict  = {"AKDT": {'zone_id':8, 'noon':20 , 'plus': 21, 'minus':19},
                    "PDT": {'zone_id':7, 'noon':19 , 'plus': 20, 'minus':18},
                    "MDT": {'zone_id':6, 'noon':18 , 'plus': 19, 'minus':17},
                    "CDT": {'zone_id':5, 'noon':17 , 'plus': 18, 'minus':16},
                    "EDT": {'zone_id':4, 'noon':16 , 'plus': 17, 'minus':15},
                    "ADT": {'zone_id':3, 'noon':15 , 'plus': 16, 'minus':14}}
        self.tzdict = tzdict

        ### Open time zones dataset
        tzone_ds = xr.open_zarr(str(tzone_dir) + "/ds_tzone.zarr")
        self.tzone_ds = tzone_ds

        # ### Create an hourly datasets for use with their respected codes/indices 
        self.hourly_ds = wrf_ds

        ### Create an hourly and daily datasets for use with their respected codes/indices 
        self.daily_ds = self.create_daily_ds(wrf_ds)
        for var in self.hourly_ds.data_vars:
            # print(var)
            self.daily_ds[var].attrs = self.hourly_ds[var].attrs
        self.daily_ds['r_o_tomorrow'].attrs = self.daily_ds['r_o'].attrs      


        ### Solve for hourly rain totals in mm....will be used in ffmc calculation 
        r_oi = np.array(self.hourly_ds.r_o)
        r_o_pluse1 = np.dstack((self.zero_full.T,r_oi.T)).T
        r_hourly_list = []
        for i in range(len(self.hourly_ds.Time)):
            r_hour =  self.hourly_ds.r_o[i] - r_o_pluse1[i]
            r_hourly_list.append(r_hour)
        r_hourly = np.stack(r_hourly_list)
        r_hourly = xr.DataArray(r_hourly, name='r_o_hourly', dims=('time','south_north', 'west_east'))
        self.hourly_ds['r_o_hourly'] = r_hourly
        # self.hourly_ds['r_o_hourly'].attrs = self.daily_ds['r_o'].attrs


        if hourly_file_dir == None:
            # """ ################## Fine Fuel Moisture Code (FFMC) ##################### """
            print("No prior FFMC, initialize with 85s")
            F_o      = 85.0   #Previous day's F becomes F_o
            F_o_full = np.full(shape,F_o, dtype=float)

            ### (1)
            ### Solve for fine fuel moisture content (m_o)
            # m_o = (205.2 * (101 - F_o_full)) / (82.9 + F_o_full)  ## Van 1977
            m_o = (147.27723 * (101 - F_o_full))/(59.5 + F_o_full)  ## Van 1985

            ### Create dataarrays for F and m_m
            F = xr.DataArray(F_o_full, name='F', dims=('south_north', 'west_east'))
            m_o = xr.DataArray(m_o, name='m_o', dims=('south_north', 'west_east'))
            
            ### Add dataarrays to hourly dataset
            self.hourly_ds['F']   = F
            self.hourly_ds['m_o'] = m_o

        else:
            # """ ################## Fine Fuel Moisture Code (FFMC) ##################### """
            ### Open previous days hourly_ds
            previous_hourly_ds = xr.open_zarr(hourly_file_dir)
            print("Found previous FFMC, will merge with hourly_ds")
            
            ### Get time step of F and m_o that coincides with the initialization time of current model run
            current_time = np.datetime_as_string(self.hourly_ds.Time[0], unit='h')
            previous_times = np.datetime_as_string(previous_hourly_ds.Time, unit='h')
            index, = np.where(previous_times == current_time)
            index = int(index[0]-1)
            F = np.array(previous_hourly_ds.F[index])
            m_o = np.array(previous_hourly_ds.m_o[index])

            ### Create dataarrays for F and m_m
            F = xr.DataArray(F, name='F', dims=('south_north', 'west_east'))
            m_o = xr.DataArray(m_o, name='m_o', dims=('south_north', 'west_east'))
            
            ### Add dataarrays to hourly dataset
            self.hourly_ds['F']   = F
            self.hourly_ds['m_o'] = m_o


        if daily_file_dir == None:
            # """ ####################   Duff Moisture Code (DMC)    ##################### """
            print("No prior DMC, initialize with 6s")
            P_o      = 6.0   
            P_o_full = np.full(shape, P_o, dtype=float)

            ### Solve for initial log drying rate (K_o)
            K_o      = 1.894 * (self.daily_ds.T[0] + 1.1)* (100 - self.daily_ds.H[0]) * (L_e * 10**-6)

            ### Solve for initial duff moisture code (P_o)
            P_o = P_o_full + (100 * K_o)

            ### Create dataarrays for P
            P = xr.DataArray(P_o, name='P', dims=('south_north', 'west_east'))

            ### Add dataarrays to daily dataset
            self.daily_ds['P'] = P

            # """ #####################     Drought Code (DC)       ########################### """
            print("No prior DC, initialize with 15s")
            D_o      = 15.0   #Previous day's P becomes P_o
            D_o_full = np.full(shape, D_o, dtype=float)

            D = xr.DataArray(D_o_full, name='D', dims=('south_north', 'west_east'))
            self.daily_ds['D'] = D

        else:
            # """ ####################   Duff Moisture Code (DCM)    ##################### """
            ### Open previous days daily_ds
            previous_daily_ds = xr.open_zarr(daily_file_dir)
            print("Found previous DMC, will merge with daily_ds")

            ### Get last time step of P and r_o_previous (carry over rain)
            ### that coincides with the initialization time of current model run
            current_time = np.datetime_as_string(self.daily_ds.Time[0], unit='D')
            previous_times = np.datetime_as_string(previous_daily_ds.Time, unit='D')
            index, = np.where(previous_times == current_time)
            index = int(index[0]-1)

            P = np.array(previous_daily_ds.P[index])
            r_o_previous = np.array(previous_daily_ds.r_o_tomorrow[index])

            ### Create dataarrays for P
            P = xr.DataArray(P, name='P', dims=('south_north', 'west_east'))

            ### Add dataarrays to daily dataset
            self.daily_ds['P']  = P
             ### Add carry over rain to first time step
            self.daily_ds['r_o'][index] = self.daily_ds['r_o'][index] + np.array(r_o_previous)
            
            # """ #####################     Drought Code (DC)       ########################### """
            print("Found previous DC, will merge with daily_ds")

            ### Get last time step of D that coincides with the
            ### initialization time of current model run
            D = np.array(previous_daily_ds.D[index])

            ### Create dataarrays for D
            D = xr.DataArray(D, name='D', dims=('south_north', 'west_east'))

            ### Add dataarrays to daily dataset
            self.daily_ds['D'] = D

        return



    """########################################################################"""
    """ #################### Fine Fuel Moisture Code #########################"""
    """########################################################################"""
    def solve_ffmc(self, hourly_ds):

        """
        Calculates the Fine Fuel Moisture Code at a one-hour interval writes/outputs as an xarray
        
        Parameters
        ----------

        hourly_ds: DataSet 
            Dataset of hourly forecast variables
                - m_o: float
                    - Initial fine fuel moisture content
                - m: float
                    - Final fine fuel moisture content
                - F_o: float
                    - Initial FFMC
                - F: float
                    - Final FFMC
                - E_d: float
                    - Equilibrium Moisture content for drying
                - E_w: float    
                    - Equilibrium Moisture content for wetting 
                - k_a: float
                    - Intermediate steps to k_d 
                - k_b:float
                    - Intermediate steps to k_w
                - k_d:float
                    - Log drying rate for hourly computation, log to base 10
                - k_w: float
                    - Log wetting rate for hourly computation, log to base 10
                - H: float
                    - Relative humidity, %
                - W: float
                    - Wind speed km/hr
                - T: float
                    - Temperature, C    

        Returns
        -------
        
        hourly_ds: DataSet
            - Adds FFMC and m_o dataset
        """

        ### Call on initial conditions
        W, T, H, r_o, m_o, F = hourly_ds.W, hourly_ds.T, hourly_ds.H, hourly_ds.r_o_hourly, hourly_ds.m_o, hourly_ds.F

        e_full, zero_full = self.e_full, self.zero_full

        ########################################################################
        ### (1b) Solve for the effective rain (r_f) 
        ## Van/Pick define as 0.5
        r_limit = 0.5 
        r_fi  = xr.where(r_o < r_limit, r_o, (r_o - r_limit))
        r_f    = xr.where(r_fi > 1e-7, r_fi, 1e-7)


        ########################################################################
        ### (1c) Solve the Rainfall routine as defiend in  Van Wagner 1985 (m_r)
        m_o_limit = 150
        a = -(100 / (251 - m_o))
        b = -(6.93 / r_f)
        m_r_low = xr.where(m_o >= m_o_limit, zero_full, m_o + \
                            (42.5 * r_f * np.power(e_full,a) * (1- np.power(e_full,b))))


        ########################################################################
        ### (1d) Solve the RainFall routine as defiend in  Van Wagner 1985 (m_r)
        m_r_high = xr.where(m_o < m_o_limit, zero_full, m_o + \
                            (42.5 * r_f * np.power(e_full, a) * (1 - np.power(e_full, b))) + \
                                (0.0015 * np.power((m_o - 150),2) * np.power(r_f, 0.5)))


        ########################################################################
        ### (1e) Set new m_o with the rainfall routine (m_o)
        m_o = m_r_low + m_r_high
        m_o = np.where(m_o < 250, m_o, 250)  # Set upper limit of 250 
        m_o = np.where(m_o > 0, m_o, 1e4)    # Set lower limit of 0 


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
        # F = (82.9 * (250 - m)) / (205.2 + m)    ## Van 1977
        F =  (59.5 * (250 - m)) / (147.27723 + m)  ## Van 1985

        ### Recast initial moisture code for next time stamp  
        # m_o = (205.2 * (101 - F)) / (82.9 + F)  ## Van 1977
        m_o = (147.27723 * (101 - F))/(59.5 + F)  ## Van 1985

        self.hourly_ds['F']   = F
        self.hourly_ds['m_o'] = m_o

        ### Return dataarray 
        return hourly_ds


    """########################################################################"""
    """ ########################## Duff Moisture Code #########################"""
    """########################################################################"""
    def solve_dmc(self, daily_ds):

        """
        Calculates the Duff Moisture Code at noon local daily and outputs as an xarray
        
        Notes
        -----
        The dataset of daily variables at noon local are averaged from (1100-1300) local 
        the averageing was done as a buffer for any frontal passage.
        
        Parameters
        ----------
        daily_ds: DataSet
            dataset of daily forecast variables
                - M_o: DataArray
                    - Initial duff moisture content
                - M_r: DataArray
                    - Duff moisture content after rain
                - M: DataArray
                    - Final duff moisture content
                - P_o: DataArray
                    - Initial DMC
                - P_r: DataArray
                    - DMC after rain
                - P: DataArray
                    - Final DMC
                - b: DataArray
                    - Three coefficient with their own empirical equation for diff range of P_o
                - K: DataArray
                    - Log drying rate
                - H: DataArray
                    - Noon local relative humidity, %
                - W: DataArray
                    - Noon local wind, km/hr
                - T: DataArray
                    - Noon local temperature, C    
                - r_o: DataArray
                    - Noon local 24 hour accumulated precipitation
                - r_e: DataArray
                    - Effective rain
                - L_e: DataArray
                    - Effective day-lengths 

        Returns
        -------
        dialy_ds: DataSet
            - Adds DMC to DataSet
        """

        W, T, H, r_o, P_o, L_e = daily_ds.W, daily_ds.T, daily_ds.H, daily_ds.r_o, daily_ds.P, self.L_e

        e_full, zero_full, ones_full = self.e_full, self.zero_full, self.ones_full

        tzdict = self.tzdict

        #### HOPEFULLY SOLVES RUNTIME WARNING
        P_o = xr.where(P_o > 0, P_o, 1e-6)

        ########################################################################
        ### (11) Solve for the effective rain (r_e) 
        r_total = 1.5  
        r_ei  = xr.where(r_o < r_total, r_o, (0.92*r_o) - 1.27) ### Im confusing myself here
       
        r_e    = xr.where(r_ei > 1e-7, r_ei, 1e-7)

        ########################################################################
        ### (12) Recast moisture content after rain (M_o)
        ##define power
        a = (5.6348 - (P_o / 43.43))
        M_o = xr.where(r_o < r_total, zero_full, 20 + np.power(e_full,a))
        

        ########################################################################
        ### (13a) Solve for coefficients b where P_o <= 33 (b_low)
        b_low = xr.where(r_o < r_total, zero_full, 
                        xr.where(P_o >= 33, zero_full, 100 / (0.5 + (0.3 * P_o))))
        

        ########################################################################
        ### (13b) Solve for coefficients b where 33 < P_o <= 65 (b_mid)
        
        b_mid = xr.where(r_o < r_total, zero_full,
                        xr.where((P_o > 33) & (P_o <= 65), zero_full, 14 - (1.3* np.log(P_o))))


        ########################################################################
        ### (13c) Solve for coefficients b where  P_o > 65 (b_high)
        
        b_high = xr.where(r_o < r_total, zero_full, 
                    xr.where(P_o < 65, zero_full, (6.2 * np.log(P_o)) - 17.2))


        ########################################################################
        ### (14a) Solve for moisture content after rain where P_o <= 33 (M_r_low)
        
        M_r_low = xr.where(r_o < r_total, zero_full, 
                        xr.where(P_o >= 33, zero_full, M_o + (1000 * r_e) / (48.77 + b_low * r_e)))


        ########################################################################
        ### (14b) Solve for moisture content after rain where 33 < P_o <= 65 (M_r_mid)

        M_r_mid = xr.where(r_o < r_total, zero_full, 
                        xr.where(P_o < 33, zero_full, 
                                    xr.where(P_o >= 65, zero_full, M_o + (1000 * r_e) / (48.77 + b_mid * r_e))))


        ########################################################################
        ### (14c)  Solve for moisture content after rain where P_o > 65 (M_r_high)
                     
        M_r_high = xr.where(r_o < r_total, zero_full, 
                        xr.where(P_o < 65, zero_full, M_o + (1000 * r_e) / (48.77 + b_high * r_e)))
        
        
        ########################################################################
        ### (14d) Combine all moisture content after rain (M_r)
                   
        M_r = M_r_low + M_r_mid + M_r_high
        M_r = xr.where(r_o < r_total, zero_full, \
                        xr.where(M_r>20,M_r, 20.0001))

        
        ########################################################################
        ### (15) Duff moisture code after rain but prior to drying (P_r_pre_K)
        
        P_r_pre_K = xr.where(r_o < r_total, zero_full, 244.72 - (43.43 * np.log(M_r - 20)))
        # P_r_pre_K = xr.where(r_o < r_total, zero_full, \
        #                         xr.where(P_r_pre_K>0,P_r_pre_K, 1e-6))
        P_r_pre_K = xr.where(P_r_pre_K > 0, P_r_pre_K, 1e-6)


        ########################################################################
        ### (16) Log drying rate (K)
        T = np.where(T>-1.1,T, -1.1)

        K = 1.894 * (T + 1.1)* (100 - H) * (L_e * 10**-6)


        ########################################################################
        ### (17a) Duff moisture code dry (P_d)   
        P_d = xr.where(r_o > r_total, zero_full, P_o + 100 * K)


        ########################################################################
        ### (17b) Duff moisture code dry (P_r)  
        P_r = xr.where(r_o < r_total, zero_full, P_r_pre_K + 100 * K)


        ########################################################################
        ##(18) Combine Duff Moisture Codes accross domain (P)
                    
        P = P_d + P_r
        self.daily_ds['P'] = P

        ### Return dataarray
        return daily_ds


    """########################################################################"""
    """ ############################ Drought Code #############################"""
    """########################################################################"""
    def solve_dc(self, daily_ds):

        """
        Calculates the Drought Code at noon local daily and outputs as an xarray
        
        Notes
        -----
        The dataset of daily variables at noon local are averaged from (1100-1300) local 
        the averageing was done as a buffer for any frontal passage.
        
        Parameters
        ----------
        daily_ds: DataSet
            dataset of daily forecast variables
                Q_o: DataArray
                    - Initial moisture equivalent of DC, units 0.254 mm 
                Q: DataArray
                    - Moisture equivalent of DC, units 0.254 mm 
                Q_r: DataArray
                    - Moisture equivalent of DC after rain, units 0.254 mm 
                V: DataArray
                    - Potential evapotranspiration, units of 0.254 mm water/day
                D_o: DataArray
                    - Initial DC
                D_r: DataArray
                    - DC after rain
                D: DataArray
                    - Final DC
                H: DataArray
                    - Noon local relative humidity, %
                W: DataArray 
                    - Noon local wind, km/hr
                T: DataArray 
                    - Noon local temperature, C    
                r_o: DataArray
                    - Noon local 24 hour accumulated precipitation
                r_d: DataArray
                    - Effective rain
                L_f: DataArray
                    - Day-length factor

        Returns
        -------
        daily_ds: DataSet
            - Adds DC dataset
        """
        ### Call on initial conditions
        W, T, H, r_o, D_o, L_f = daily_ds.W, daily_ds.T, daily_ds.H, daily_ds.r_o, daily_ds.D, self.L_f

        e_full, zero_full, ones_full = self.e_full, self.zero_full, self.ones_full

        tzdict = self.tzdict


        ########################################################################
        ### (18) Solve for the effective rain (r_d) 
        r_limit = 2.8  
        r_di  = xr.where(r_o < r_limit, r_o, (0.83*r_o) - 1.27)
        r_d    = xr.where(r_di > 1e-7, r_di, 1e-7)

        ########################################################################
        ### (19) Solve for initial moisture equivalent (Q_o) 
        a = (-D_o/400)
        Q_o = xr.where(r_o < r_limit, zero_full, 800 * np.power(e_full,a))


        ########################################################################
        ### (20) Solve for moisture equivalent (Q_r) 

        Q_r = xr.where(r_o < r_limit, zero_full, Q_o + (3.937 * r_d))
        
        #### HOPEFULLY SOLVES RUNTIME WARNING
        Q_r = xr.where(Q_r > 0, Q_r, 1e-6)

        ########################################################################
        ### (21) Solve for DC after rain (D_r) 
        a = (800/Q_r)
        D_r = xr.where(r_o < r_limit, zero_full, 400 * np.log(a))
        D_r = xr.where(D_r > 0, D_r, 1e-6)


        ########################################################################
        ### (21) Solve for potential evapotranspiration (V) 
        T = np.where(T>-2.8,T, -2.8)

        V = (0.36 * (T + 2.8)) + L_f

        ########################################################################
        ### (21) Combine dry and moist D and Solve for Drought Code (D) 
        D_d = xr.where(r_o > r_limit, zero_full, D_o)
        D_combine = D_d + D_r
        D = D_combine + (0.5 * V)

        self.daily_ds['D'] = D

        return daily_ds


    """########################################################################"""
    """ #################### Initial Spread Index #############################"""
    """########################################################################"""
    def solve_isi(self, hourly_ds):

        """
        Calculates the hourly initial spread index
        
        Parameters
        ----------
        hourly_ds: DataSet
            - Dataset of hourly forecast variables
                - W: DataArray
                    - Wind speed, km/hr
                - F: DataArray
                    - Fine fuel moisture code    
                - R: DataArray
                    - Initial spread index

        Returns
        -------
        R: DataArray
            - Datarray of ISI
        """
        ### Call on initial conditions
        W, F, m_o = hourly_ds.W, hourly_ds.F, hourly_ds.m_o

        e_full, zero_full = self.e_full, self.zero_full

        ########################################################################
        ### (24) Solve for wind function (f_W) 
        a = 0.05039 * W
        f_W = np.power(e_full, a)

        ########################################################################
        ### (25) Solve for fine fuel moisture function (f_F) 
        a = -0.1386 * m_o
        b = np.power(e_full, a)
        c = (1 + np.power(m_o, 5.31) / (4.93e7))
        f_F = 91.9 * b * c
        ########################################################################
        ### (26) Solve for initial spread index (R) 

        R = 0.208 * f_W * f_F

        R = xr.DataArray(R, name='R', dims=('time', 'south_north', 'west_east'))
        
        # self.hourly_ds['R']   = R

        return R


    """########################################################################"""
    """ ########################## Build up Index #############################"""
    """########################################################################"""
    def solve_bui(self, daily_ds):

        """
        Calculates the Build up Index at noon local daily and outputs as an xarray

        Notes
        -----
        The dataset of daily variables at noon local are averaged from (1100-1300) local 
        the averageing was done as a buffer for any frontal passage.
        
        Parameters
        ----------
        daily_ds: DataSet
            dataset of daily forecast variables
                - P: DataArray
                    - Duff moisture code
                - D: DataArray
                    - Drought code  
                - U: DataArray
                    - Build up index

        Returns
        -------
        U: DataArray
            - An DataArray of BUI
        """
        zero_full  =  self.zero_full

        ### Call on initial conditions
        P, D  = daily_ds.P, daily_ds.D

        ########################################################################
        ### (27a) Solve for build up index where P =< 0.4D (U_a) 
        P_limit = 0.4 * D
        U_a = (0.8 * P * D) / (P + (0.4 * D))
        U_a = xr.where(P >= P_limit, zero_full, U_a)

        ########################################################################
        ### (27b) Solve for build up index where P > 0.4D (U_b) 

        a   = 0.92 + np.power((0.0114 * P), 1.7)
        U_b = P - ((1 - (0.8 * D)) / ((P + (0.4 * D)) * a))
        U_b = xr.where(P < P_limit, zero_full, U_b)


        ########################################################################
        ### (27c) Combine build up index (U) 

        U = U_a + U_b

        U = xr.DataArray(U, name='U', dims=('time', 'south_north', 'west_east'))

        return U





    """########################################################################"""
    """ ###################### Fire Weather Index #############################"""
    """########################################################################"""
    def solve_fwi(self):

        """
        Calculates the hourly fire weather index and daily severity rating
        
        
        ----------
            W: datarray     
                - Wind speed, km/hr
            F: datarray
                - Fine fuel moisture code    
            R: datarray    
                - Initial spread index
            S: datarray
                - Fire weather index
            DSR: datarray
                - Daily severity rating

        Returns
        -------
        S: datarray
            - An datarray of FWI
        DSR datarray
            - An datarray of DSR
        """
        ### Call on initial conditions

        U, R = self.U, self.R
        e_full, zero_full = self.e_full, self.zero_full

        ########################################################################
        ### (28a) Solve for duff moisture function where U =< 80(f_D_a) 
        U_limit = 80
        f_D_a = (0.626 * np.power(U, 0.809)) + 2
        f_D_a = xr.where(U >= U_limit, zero_full, f_D_a)

        ########################################################################
        ### (28b) Solve for duff moisture function where U > 80 (f_D_b) 
        a = np.power(e_full, (-0.023 * U))
        f_D_b = 1000 / (25 + 108.64 * a)
        f_D_a = xr.where(U < U_limit, zero_full, f_D_b)

        ########################################################################
        ### (28c) Combine duff moisture functions (f_D) 
        f_D = f_D_a + f_D_b

        ########################################################################
        ### (29a) Solve FWI intermediate form  for day 1(B_a)
        B_a = 0.1 * R[:36] * f_D[0]

        ########################################################################
        ### (29b) Solve FWI intermediate form for day 2 (B_b)
        B_b = 0.1 * R[36:] * f_D[1]

        ########################################################################
        ### (29c) COmbine FWI intermediate (B)
        B   = xr.combine_nested([B_a,B_b], 'time')

        #### HOPEFULLY SOLVES RUNTIME WARNING
        B = xr.where(B > 0, B, 1e-6)

        ########################################################################
        ### (30a) Solve FWI where B > 1 (S_a)
        B_limit = 1
        a = np.power((0.434 * np.log(B)), 0.647)
        S_a = np.power(e_full,2.72 * a)
        S_a = xr.where(B < B_limit, zero_full, S_a)

        ########################################################################
        ### (30b) Solve FWI where B =< 1 (S_b)

        S_b = xr.where(B >= B_limit, zero_full, B)
        ########################################################################
        ### (30) Combine for FWI (S)

        S = S_a + S_b
        S = xr.DataArray(S, name='S', dims=('time', 'south_north', 'west_east'))

        ########################################################################
        ### (31) Solve for daily severity rating (DSR)

        DSR = 0.0272 * np.power(S,1.77) 
        DSR = xr.DataArray(DSR, name='DSR', dims=('time', 'south_north', 'west_east'))

        return S, DSR



    """########################################################################"""
    """ ###################### Create Daily Dataset ###########################"""
    """########################################################################"""
    def create_daily_ds(self,wrf_ds):
        """
        Creates a dataset of forecast variables averaged from
        (1100-1300) local to act as the noon local conditions for daily index/codes 
        calculations
        
        Parameters
        ----------
            wrf_ds: DataSet
                WRF dataset at 4-km spatial resolution and one hour tempolar resolution
                    - tzdict:  dictionary
                        - Dictionary of all times zones in North America and their respective offsets to UTC
                    - zone_id: in
                        - ID of model domain with hours off set from UTC
                    - noon: int
                        - 1200 local index based on ID
                    - plus: int
                        - 1300 local index based on ID
                    - minus: int
                        - 1100 local index based on ID
                    - tzone_ds: dataset 
                        - Gridded 2D array of zone_id 

        Returns
        -------
            daily_ds: DataSet
                Dataset of daily variables at noon local averaged from (1100-1300)
                local the averageing was done as a buffer for any frontal passage.
        """
        
        print("Create Daily ds")

        ### Call on variables 
        zero_full = self.zero_full
        tzdict = self.tzdict
        tzone_ds = self.tzone_ds

        files_ds = []
        for i in range(0,48,24):

            sum_list = []
            for key in tzdict.keys():
                zone_id, noon, plus, minus = tzdict[key]['zone_id'], tzdict[key]['noon'], tzdict[key]['plus'], tzdict[key]['minus']

                mean_da = []
                for var in wrf_ds.data_vars:
                    # print(wrf_ds[var])
                    var_mean = wrf_ds[var][minus+i:plus+i].mean(axis=0)
                    var_da = xr.where(tzone_ds != zone_id, zero_full, var_mean)
                    var_da = np.array(var_da.Zone)
                    day    = np.array(wrf_ds.Time[noon + i], dtype ='datetime64[D]')
                    var_da = xr.DataArray(var_da, name=var, 
                            dims=('south_north', 'west_east'), coords= wrf_ds.isel(time = i).coords)
                    var_da["Time"] = day
                    mean_da.append(var_da)

                    if var == 'r_o':
                        r_o_tom_mean  = wrf_ds[var][noon:24].mean(axis=0)
                        r_o_tom       = xr.where(tzone_ds != zone_id, zero_full, r_o_tom_mean)
                        r_o_tom       = np.array(r_o_tom.Zone)
                        r_o_tom_da    = r_o_tom - np.array(var_da)
                        day           = np.array(wrf_ds.Time[noon + i], dtype ='datetime64[D]')
                        r_o_tom_da    = xr.DataArray(r_o_tom_da, name="r_o_tomorrow", 
                                dims=('south_north', 'west_east'),coords= wrf_ds.isel(time = i).coords)
                        r_o_tom_da["Time"] = day
                        mean_da.append(r_o_tom_da)
                    else:
                        pass

                mean_ds = xr.merge(mean_da)
                sum_list.append(mean_ds)
            sum_ds = sum(sum_list)
            files_ds.append(sum_ds)
        
            daily_ds = xr.combine_nested(files_ds, 'time')
        
        print("Daily ds done")

        return daily_ds




    """#######################################"""
    """ ######## Hourly Dataset Loop ########"""
    """#######################################"""
    def hourly_loop(self):
        """
        Loops through each hourly time step and solves hourly fwi(s)

        Returns
        -------
        daily_ds: DataSet
            A xarray DataSet with all the houlry FWI codes/indices solved
        """

        length = len(self.hourly_ds.time)
        hourly_list = []
        print("Start Hourly loop lenght: ", length)
        for i in range(length):
            FFMC = self.solve_ffmc(self.hourly_ds.isel(time = i))
            hourly_list.append(FFMC)
        print("Hourly loop done")
        hourly_ds = self.combine_by_time(hourly_list)
        ISI  = self.solve_isi(hourly_ds)
        hourly_ds['R'] = ISI
        self.R = ISI
        FWI, DSR  = self.solve_fwi()
        hourly_ds['S']   = FWI
        hourly_ds['DSR'] = DSR

        return hourly_ds


    """#######################################"""
    """ ######## Daily Dataset Loop ########"""
    """#######################################"""
    def daily_loop(self):
        """
        Loops through each daily time step and solves daily fwi(s)

        Returns
        -------
        daily_ds: DataSet
            A xarray DataSet with all the daily FWI codes/indices solved

        """

        length = len(self.daily_ds.time)
        r_o_list = []
        r_o_list.append(self.zero_full)
        r_o_list.append(np.array(self.daily_ds.r_o[0]))
        r_o_list.append(np.array(self.daily_ds.r_o[1]))
        for j in range(length):
            r_o = r_o_list[j+1] - r_o_list[j]
            self.daily_ds.r_o[j] = r_o
        daily_list = []
        print("Start Daily loop length: ", length)
        for i in range(length):
            DMC = self.solve_dmc(self.daily_ds.isel(time = i))
            DC  = self.solve_dc(self.daily_ds.isel(time = i))
            DMC['D'] = DC['D']
            daily_list.append(DMC)
        
        print("Daily loop done")
        daily_ds = self.combine_by_time(daily_list)
        U  = self.solve_bui(daily_ds)
        daily_ds['U'] = U
        self.U = U
        return daily_ds


    """#######################################"""
    """ ######### Combine Datasets ###########"""
    """#######################################"""
    def combine_by_time(self,dict_list):
        """
        Combine datsets by time coordinate

        Parameters
        ----------
        dict_list: list
            List of xarray datasets

        Returns
        -------
        combined_ds: DataSet
            Single xarray DataSet with a dimension time
        """
        files_ds = []
        for index in dict_list:
            ds  = xr.Dataset(index)
            files_ds.append(ds)
        combined_ds = xr.combine_nested(files_ds, 'time')
        return(combined_ds)


    # def merge_by_coords(self,dict_list):
    #     xarray_files = []
    #     for index in dict_list:
    #         ds  = xr.Dataset(index)
    #         xarray_files.append(ds)
    #     # ds_final = xr.merge(xarray_files,compat='override')
    #     # ds_final = xr.concat(xarray_files)
    #     return(ds_final)


    """#######################################"""
    """ ######## Write Hourly Dataset ########"""
    """#######################################"""
    def hourly(self):
        """
        Writes hourly_ds (.zarr) and adds the appropriate attributes to each variable 

        Returns
        -------
        make_dir: str
            - File directory to (zarr) file of todays hourly FWI codes
            - Needed for carry over to intilaze tomorrow's model run
        """
        hourly_ds = self.hourly_loop()
        hourly_ds.attrs = self.attrs

        hourly_ds.F.attrs   = hourly_ds.T.attrs
        del hourly_ds.F.attrs['units']
        hourly_ds.F.attrs['description'] = "FINE FUEL MOISTURE CODE"

        hourly_ds.m_o.attrs = hourly_ds.T.attrs
        del hourly_ds.m_o.attrs['units']
        hourly_ds.m_o.attrs['description'] = "FINE FUEL MOISTURE CONTENT"

        hourly_ds.R.attrs = hourly_ds.T.attrs
        del hourly_ds.R.attrs['units']
        hourly_ds.R.attrs['description'] = "INITIAL SPREAD INDEX"

        hourly_ds.S.attrs   = hourly_ds.T.attrs
        del hourly_ds.S.attrs['units']
        hourly_ds.S.attrs['description'] = "FIRE WEATHER INDEX"

        hourly_ds.DSR.attrs   = hourly_ds.T.attrs
        del hourly_ds.DSR.attrs['units']
        hourly_ds.DSR.attrs['description'] = "DAILY SEVERITY RATING"

        hourly_ds.r_o_hourly.attrs   = hourly_ds.r_o.attrs
        hourly_ds.r_o_hourly.attrs['description'] = "HOURLY PRECIPITATION TOTALS"

        for var in hourly_ds.data_vars:
            del hourly_ds[var].attrs['coordinates']
            hourly_ds[var].attrs['projection'] = str(hourly_ds[var].projection)


        # ### Name file after initial time of wrf 
        file_name  = str(np.array(self.hourly_ds.Time[0], dtype ='datetime64[h]'))
        file_name = datetime.strptime(str(file_name), '%Y-%m-%dT%H').strftime('%Y%m%d%H')
        print("Hourly zarr initialized at :", file_name)

        # # ## Write and save DataArray (.zarr) file
        make_dir = Path(str(xr_dir) + str('/fwf-hourly-') + file_name + str(f".zarr"))
        make_dir.mkdir(parents=True, exist_ok=True)
        hourly_ds = hourly_ds.compute()
        hourly_ds.to_zarr(make_dir, "w")
        print(f"wrote archive {make_dir}")
    
        current_dir_hourly = str(xr_dir) + str('/current/hourly.zarr')
        hourly_ds.to_zarr(current_dir_hourly, "w")
        print(f"wrote working {current_dir_hourly}")

        # ## return path to hourly_ds file to open
        return str(make_dir)


    """#######################################"""
    """ ######## Write Daily Dataset ########"""
    """#######################################"""
    def daily(self):
        """
        Writes daily_ds (.zarr) and adds the appropriate attributes to each variable

        Returns
        -------
        make_dir: str
            - File directory to (zarr) file of todays daily FWI codes
            - Needed for carry over to intilaze tomorrow's model run
        """
        daily_ds = self.daily_loop()
        daily_ds.attrs = self.attrs

        daily_ds.P.attrs   = daily_ds.T.attrs
        del daily_ds.P.attrs['units']
        daily_ds.P.attrs['description'] = "DUFF MOISTURE CODE"

        daily_ds.D.attrs   = daily_ds.T.attrs
        del daily_ds.D.attrs['units']
        daily_ds.D.attrs['description'] = "DROUGHT CODE"

        daily_ds.U.attrs   = daily_ds.T.attrs
        del daily_ds.U.attrs['units']
        daily_ds.U.attrs['description'] = "BUILD UP INDEX"


        for var in daily_ds.data_vars:
        #     print(var)
            del daily_ds[var].attrs['coordinates']
            daily_ds[var].attrs['projection'] = str(daily_ds[var].projection)

        daily_ds.r_o.attrs['description'] = "24 HOUR ACCUMULATED PRECIPITATION"


        # ### Name file after initial time of wrf 
        file_name  = str(np.array(self.hourly_ds.Time[0], dtype ='datetime64[h]'))
        file_name = datetime.strptime(str(file_name), '%Y-%m-%dT%H').strftime('%Y%m%d%H')

        print("Daily zarr initialized at :", file_name)

        # # ## Write and save DataArray (.zarr) file
        make_dir = Path(str(xr_dir) + str('/fwf-daily-') + file_name + str(f".zarr"))
        make_dir.mkdir(parents=True, exist_ok=True)
        daily_ds = daily_ds.compute()
        daily_ds.to_zarr(make_dir, "w")
        print(f"wrote archive {make_dir}")

        current_dir_daily = str(xr_dir) + str('/current/daily.zarr')
        daily_ds.to_zarr(current_dir_daily, "w")
        print(f"wrote working {current_dir_daily}")

        ## return path to daily_ds file to open
        return str(make_dir)