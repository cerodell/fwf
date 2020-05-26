        
import context
import math
import errno
import numpy as np
import xarray as xr

from context import data_dir, xr_dir, wrf_dir
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
  
        
        
        
        
        
        W, T, H, r_o, P_o, L_e = ds_wrf.W, ds_wrf.T, ds_wrf.H, ds_wrf.r_o, self.P, self.L_e

        e_full, zero_full, ones_full = self.e_full, self.zero_full, self.ones_full

        # ln = np.log

        ########################################################################
        ### (11) Solve for the effective rain (r_e) 
        r_total = 1.5  ### This is different from van wanger  (dividing by 24 to make hourly)
        r_ei  = np.where(r_o < r_total, r_o, (0.92*r_o) - 1.27)
        # r_ei  = r_ei  ### This is different from van wanger  (dividing by 24 to make hourly)
       
        r_e    = np.where(r_ei > 1e-7, r_ei, 1e-7)

        print(np.min(np.array(r_e)), "r_e min")

        ########################################################################
        ### (12) Recast moisture content after rain (M_o)
        ##define power
        a = (5.6348 - (P_o / 43.43))
        M_o = xr.where(r_o < r_total, zero_full, 20 + np.power(e_full,a))
        
        print(np.min(np.array(P_o)), "LN issue P_o")
        ########################################################################
        ### (13a) Solve for coefficients b where P_o <= 33 (b_low)
        b_low = xr.where(r_o < r_total, zero_full, 
                        xr.where(P_o >= 33, zero_full, 100 / (0.5 + (0.3 * P_o))))
        
        # print(np.min(np.array(b_low)), "LN issue b_low")

        ########################################################################
        ### (13b) Solve for coefficients b where 33 < P_o <= 65 (b_mid)
        
        b_mid = xr.where(r_o < r_total, zero_full,
                        xr.where((P_o > 33) & (P_o <= 65), zero_full, 14 - (1.3* np.log(P_o))))

                        # xr.where(P_o < 33, zero_full,
                        #         xr.where(P_o >= 65, zero_full, 14 - (1.3* np.log(P_o)))))

        # print(np.min(np.array(b_mid)), "LN issue b_mid")

        ########################################################################
        ### (13c) Solve for coefficients b where  P_o > 65 (b_high)
        
        b_high = xr.where(r_o < r_total, zero_full, 
                    xr.where(P_o < 65, zero_full, (6.2 * np.log(P_o)) - 17.2))


        # print(np.min(np.array(b_high)), "LN issue b_high")

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
        self.P = P
        ### Add to dataarray
        ds_dmc = xr.DataArray(P, name='P', dims=('south_north', 'west_east'))

        print(np.min(np.array(P)), "P final")

        ### Return dataarray
        return ds_dmc