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
from fwi.utils.wrf.read_wrfout import readwrf
from context import data_dir, xr_dir, wrf_dir, tzone_dir



 

class FWF:
    """
    Class to solve the Fire Weather Indices 



    """



    ######################################################################
    ######################################################################
    def __init__(self, wrf_file_dir, fwf_file_dir):
        """
        Initialize conditions


        """
        ### Read then open WRF dataset
        wrf_ds, xy_np = readwrf(wrf_file_dir)
        self.attrs    = wrf_ds.attrs
        ############ Mathematical Constants and Usefull Arrays ################ 
        ### Math Constants
        e = math.e

        ### Shape of Domain
        shape = np.shape(wrf_ds.T[0,:,:])
        print(shape)
        self.e_full    = np.full(shape,e, dtype=float)
        self.zero_full = np.zeros(shape, dtype=float)
        self.ones_full = np.full(shape,1, dtype=float)

        ### Daylength factor in Duff Moisture Code
        month = np.datetime_as_string(wrf_ds.Time[0], unit='h')
        print(month[5:7])
        month = (int(month[5:7]) - 1)
        L_e = [6.5, 7.5, 9.0, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8.0, 7.0, 6.0]
        L_e = L_e[month]
        self.L_e = L_e

        ### Time Zone classification method
        tzdict   = {"PDT": {'zone_id':7, 'noon':19 , 'plus': 20, 'minus':18},
                    "MDT": {'zone_id':6, 'noon':18 , 'plus': 19, 'minus':17},
                    "CDT": {'zone_id':5, 'noon':17 , 'plus': 18, 'minus':16},
                    "EDT": {'zone_id':4, 'noon':16 , 'plus': 17, 'minus':15},
                    "ADT": {'zone_id':3, 'noon':15 , 'plus': 16, 'minus':14}}
        self.tzdict = tzdict

        ### Open time zones dataset
        print(str(tzone_dir) + "/ds_tzone.zarr")
        tzone_ds = xr.open_zarr(str(tzone_dir) + "/ds_tzone.zarr")
        self.tzone_ds = tzone_ds

        ### Create an hourly and daily datasets for use with their respected codes/indices 
        self.hourly_ds = wrf_ds
        self.daily_ds = self.create_daily_ds(wrf_ds)
        for var in self.hourly_ds.data_vars:
            print(var)
            self.daily_ds[var].attrs = self.hourly_ds[var].attrs
        self.daily_ds['r_o_tomorrow'].attrs = self.daily_ds['r_o'].attrs      

 

        if fwf_file_dir == None:
            # """ ################## Fine Fuel Moisture Code (FFMC) ##################### """
            print("No prior FFMC, initialize with 85s")
            F_o      = 85.0   #Previous day's F becomes F_o
            F_o_full = np.full(shape,F_o, dtype=float)
            # self.F = F_o_full

            ### (1)
            m_o = 205.2 * (101 - F_o_full) / (82.9 + F_o_full)  
            # self.m_o = m_o


            F = xr.DataArray(F_o_full, name='F', dims=('south_north', 'west_east'))
            m_o = xr.DataArray(m_o, name='m_o', dims=('south_north', 'west_east'))
            
            self.hourly_ds['F']   = F
            self.hourly_ds['m_o'] = m_o


            # """ ####################   Duff Moisture Code (DCM)    ##################### """
            print("No prior DMC, initialize with 6s")
            P_o      = 6.0   #Previous day's P becomes P_o
            P_o_full = np.full(shape, P_o, dtype=float)

            ### (16)
            K_o      = 1.894 * (self.daily_ds.T[0] + 1.1)* (100 - self.daily_ds.H[0]) * (L_e * 10**-6)

            ##(1)
            P_o = P_o_full + (100 * K_o)
            self.daily_ds['P'] = P_o

            # """ #####################     Drought Code (DC)       ########################### """


        else:
            fwf_ds = xr.open_zarr(fwf_file_dir)


            print("Found previous FFMC, will merge with hourly_ds")
            F = np.array(fwf_ds.F[-1])
            m_o = np.array(fwf_ds.m_o[-1])

            F = xr.DataArray(F, name='F', dims=('south_north', 'west_east'))
            m_o = xr.DataArray(m_o, name='m_o', dims=('south_north', 'west_east'))
            
            self.hourly_ds['F']   = F
            self.hourly_ds['m_o'] = m_o

            
            # print("Found previous DMC, will merge with daily_ds")
            # P = np.array(fwf_ds.P[-1])

            # self.P = P


        return



    ######################################################################
    ######################################################################
    def solve_ffmc(self, hourly_ds):

        """
        This function calculates the Fine Fuel Moisture Code at a one-hour interval writes/outputs as an xarray
        
        Parameters
        ----------
        ds_wrf: dataarray of wrf variables

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
        
        F_ds: an dataset of FFMC and m_o
        """

        ### Call on initial conditions
        # W, T, H, m_o = hourly_ds.W, hourly_ds.T, hourly_ds.H, self.m_o
        W, T, H, m_o, F = hourly_ds.W, hourly_ds.T, hourly_ds.H, hourly_ds.m_o, hourly_ds.F

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

        # self.m_o = m_o

        ### Add FFMC and moisture code to dataarray 
        # F = xr.DataArray(F, name='F', dims=('south_north', 'west_east'))
        # m_o = xr.DataArray(m_o, name='m_o', dims=('south_north', 'west_east'))
        
        # var_list = [F,m_o]
        # ds_ffmc = xr.merge(var_list)

        self.hourly_ds['F']   = F
        self.hourly_ds['m_o'] = m_o

        ### Return dataarray 
        return hourly_ds



    def solve_dmc(self, daily_ds):

        """
        This function calculates the Duff Moisture Code at a one-hour interval writes/outputs as an xarray
        
        Parameters
        ----------
        ds_wrf: dataarray of wrf variables

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
        
        ds_P: an dataarray of DMC
        """

        W, T, H, r_o, P_o, L_e = daily_ds.W, daily_ds.T, daily_ds.H, daily_ds.r_o, daily_ds.P, self.L_e

        e_full, zero_full, ones_full = self.e_full, self.zero_full, self.ones_full

        tzdict = self.tzdict
        

        # ln = np.log
        print(np.max(np.array(r_o)), "WRF RAIN Max")

        ########################################################################
        ### (11) Solve for the effective rain (r_e) 
        r_total = 1.5  ### This is different from van wanger  (dividing by 24 to make hourly)
        r_ei  = np.where(r_o < r_total, r_o, (0.92*r_o) - 1.27)
        # r_ei  = r_ei  ### This is different from van wanger  (dividing by 24 to make hourly)
       
        r_e    = np.where(r_ei > 1e-7, r_ei, 1e-7)

        print(np.max(np.array(r_e)), "r_e max")

        ########################################################################
        ### (12) Recast moisture content after rain (M_o)
        ##define power
        a = (5.6348 - (P_o / 43.43))
        M_o = xr.where(r_o < r_total, zero_full, 20 + np.power(e_full,a))
        
        print(np.min(np.array(P_o)), "Initial P_o")
        ########################################################################
        ### (13a) Solve for coefficients b where P_o <= 33 (b_low)
        b_low = xr.where(r_o < r_total, zero_full, 
                        xr.where(P_o >= 33, zero_full, 100 / (0.5 + (0.3 * P_o))))
        
        print(np.min(np.array(b_low)), "b_low min")

        ########################################################################
        ### (13b) Solve for coefficients b where 33 < P_o <= 65 (b_mid)
        
        b_mid = xr.where(r_o < r_total, zero_full,
                        xr.where((P_o > 33) & (P_o <= 65), zero_full, 14 - (1.3* np.log(P_o))))

                        # xr.where(P_o < 33, zero_full,
                        #         xr.where(P_o >= 65, zero_full, 14 - (1.3* np.log(P_o)))))

        print(np.max(np.array(b_mid)), "b_mid max")

        ########################################################################
        ### (13c) Solve for coefficients b where  P_o > 65 (b_high)
        
        b_high = xr.where(r_o < r_total, zero_full, 
                    xr.where(P_o < 65, zero_full, (6.2 * np.log(P_o)) - 17.2))


        print(np.max(np.array(b_high)), "b_high max")

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
        
        print(np.max(np.array(M_r)), "M_r min")
        
        ########################################################################
        ### (15) Drought moisture code after rain but prior to drying (P_r_pre_K)
        
        P_r_pre_K = xr.where(r_o < r_total, zero_full, 244.72 - (43.43 * np.log(M_r - 20)))
        # P_r_pre_K = xr.where(r_o < r_total, zero_full, 244.72 - (43.43 * (M_r - 20)))



        ########################################################################
        ### (16) Log drying rate (K)

        K = 1.894 * (T + 1.1)* (100 - H) * (L_e * 10**-6)


        ########################################################################
        ### (17a) Drought moisture code dry (P_d)   
        P_d = xr.where(r_o > r_total, zero_full, P_o + 100 * K)


        ########################################################################
        ### (17b) Drought moisture code dry (P_r)  
        P_r = xr.where(r_o < r_total, zero_full, P_r_pre_K + 100 * K)


        ########################################################################
        ##(18) Combine Drought Moisture Codes accross domain (P)
                    
        P = P_d + P_r
        self.daily_ds['P'] = P
        ### Add to dataarray
        # ds_dmc = xr.DataArray(P, name='P', dims=('south_north', 'west_east'))

        print(np.min(np.array(P)), "P final")

        ### Return dataarray
        return daily_ds



    def create_daily_ds(self,wrf_ds):
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
                            dims=('south_north', 'west_east'),coords={'time':day})
                    mean_da.append(var_da)

                    if var == 'r_o':




                        r_o_tom_mean  = wrf_ds[var][noon+i:].mean(axis=0)
                        r_o_tom       = xr.where(tzone_ds != zone_id, zero_full, r_o_tom_mean)
                        r_o_tom       = np.array(r_o_tom.Zone)
                        r_o_tom_da    = r_o_tom - np.array(var_da)
                        day           = np.array(wrf_ds.Time[noon + i], dtype ='datetime64[D]')
                        r_o_tom_da    = xr.DataArray(r_o_tom_da, name="r_o_tomorrow", 
                                dims=('south_north', 'west_east'),coords={'time':day})
                        mean_da.append(r_o_tom_da)
                    else:
                        pass

                
                mean_ds = xr.merge(mean_da)
                sum_list.append(mean_ds)
            sum_ds = sum(sum_list)
            files_ds.append(sum_ds)
        
            daily_ds = xr.combine_nested(files_ds, 'time')
        
        return daily_ds




    def hourly_loop(self):
        # hourly_ds = self.hourly_ds
        length = len(self.hourly_ds.time)
        hourly_list = []
        print("Hourly length: ", length)
        for i in range(length):
            FFMC = self.solve_ffmc(self.hourly_ds.isel(time = i))
            # ISI  = self.solve_isi(self.hourly_ds.isel(time = i))
            # FWI  = self.solve_fwi(self.hourly_ds.isel(time = i))

            hourly_list.append(FFMC)
        print("hourly loop done")
        hourly_ds = self.combine_by_time(hourly_list)
        return hourly_ds

    def daily_loop(self):
        # daily_ds = self.daily_ds
        length = len(self.daily_ds.time)
        daily_list = []
        print("Daily length: ", length)
        for i in range(length):
            DMC = self.solve_dmc(self.daily_ds.isel(time = i))
            daily_list.append(DMC)
        
        print("daily loop done")
        daily_ds = self.combine_by_time(daily_list)

        return daily_ds



    def combine_by_time(self,dict_list): 
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



    def hourly(self):
        hourly_ds = self.hourly_loop()
        hourly_ds.attrs = self.attrs
        hourly_ds.F.attrs   = hourly_ds.T.attrs
        del hourly_ds.F.attrs['units']
        hourly_ds.F.attrs['description'] = "FINE FUEL MOISTURE CODE"
        hourly_ds.m_o.attrs = hourly_ds.T.attrs
        del hourly_ds.m_o.attrs['units']
        hourly_ds.m_o.attrs['description'] = "FINE FUEL MOISTURE CONTENT"
        print(hourly_ds.F.attrs)


        for var in hourly_ds.data_vars:
            print(var)
            del hourly_ds[var].attrs['coordinates']
            # hourly_ds[var].attrs['coordinates'] = 'XLONG XLAT XTIME'
            hourly_ds[var].attrs['projection'] = str(hourly_ds[var].projection)

            # back = pickle.loads(test)
        # ### Name file after initial time of wrf 
        file_name = np.datetime_as_string(hourly_ds.Time[0], unit='h')

        print("FFMC initialized at :", file_name)

        # # ## Write and save DataArray (.zarr) file
        make_dir = Path(str(xr_dir) + str('/') + file_name + str(f"_hourly_ds.zarr"))

        # ### Check if file exists....else write file
        # if make_dir.exists():
        #     the_size = make_dir.stat().st_size
        #     print(
        #         ("\n{} already exists\n" "and is {} bytes\n" "will not overwrite\n").format(
        #             file_name, the_size
        #         )
        #     )
        # else:
        #     make_dir.mkdir(parents=True, exist_ok=True)
        #     # hourly_ds.compute()
        #     # hourly_ds.chunk()
        #     hourly_ds.to_zarr(make_dir, "w")
        #     print(f"wrote {make_dir}")

        make_dir.mkdir(parents=True, exist_ok=True)
        hourly_ds.compute()
        # hourly_ds.chunk()
        # for var in hourly_ds.data_vars:
            # del hourly_ds[var].encoding['chunks']
        hourly_ds.to_zarr(make_dir, "w")
        # hourly_ds.to_netcdf(make_dir)

        print(f"wrote {make_dir}")
        
        ## return path to hourly_ds file to open
        return str(make_dir)



    def daily(self):
        daily_ds = self.daily_loop()
        daily_ds.attrs = self.attrs
        print(daily_ds.T.attrs)
        daily_ds.P.attrs   = daily_ds.T.attrs
        del daily_ds.P.attrs['units']
        daily_ds.P.attrs['description'] = "DUFF MOISTURE CODE"
        print(daily_ds.P.attrs)


        for var in daily_ds.data_vars:
            print(var)
            del daily_ds[var].attrs['coordinates']
            # daily_ds[var].attrs['coordinates'] = 'XLONG XLAT XTIME'
            daily_ds[var].attrs['projection'] = str(daily_ds[var].projection)

            # back = pickle.loads(test)
        # ### Name file after initial time of wrf 
        file_name = np.datetime_as_string(self.hourly_ds.Time[0], unit='h')

        print("DMC initialized at :", file_name)

        # # ## Write and save DataArray (.zarr) file
        make_dir = Path(str(xr_dir) + str('/') + file_name + str(f"_daily_ds.zarr"))

        # ### Check if file exists....else write file
        # if make_dir.exists():
        #     the_size = make_dir.stat().st_size
        #     print(
        #         ("\n{} already exists\n" "and is {} bytes\n" "will not overwrite\n").format(
        #             file_name, the_size
        #         )
        #     )
        # else:
        #     make_dir.mkdir(parents=True, exist_ok=True)
        #     # daily_ds.compute()
        #     # daily_ds.chunk()
        #     daily_ds.to_zarr(make_dir, "w")
        #     print(f"wrote {make_dir}")

        make_dir.mkdir(parents=True, exist_ok=True)
        daily_ds.compute()
        # daily_ds.chunk()
        # for var in daily_ds.data_vars:
            # del daily_ds[var].encoding['chunks']
        daily_ds.to_zarr(make_dir, "w")
        # daily_ds.to_netcdf(make_dir)

        print(f"wrote {make_dir}")
        
        ## return path to daily_ds file to open
        return str(make_dir)