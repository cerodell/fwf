#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

"""
Class to solve the Fire Weather Indices using output from a numerical weather model
"""

import context
import math
import numpy as np
import pandas as pd
import xarray as xr


from pathlib import Path

# from netCDF4 import Dataset
from datetime import datetime
from utils.read_wrfout import readwrf
from context import tzone_dir, fwf_zarr_dir

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


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

    def __init__(self, wrf_file_dir, domain, initialize):
        """
        Initialize Fire Weather Index Model


        """
        ### Read then open WRF dataset
        if wrf_file_dir.endswith(".zarr"):
            print("Re-run using zarr file")
            wrf_ds = xr.open_zarr(wrf_file_dir)
        else:
            print("New-run, use readwrf to get vars from nc files")
            wrf_ds = readwrf(wrf_file_dir, domain, wright=False)
        ## Get dataset attributes
        self.attrs = wrf_ds.attrs

        ############ Mathematical Constants and Usefull Arrays ################
        ### Math Constants
        # e = math.e
        self.F_initial = 85.0
        self.P_initial = 6.0
        self.D_initial = 15.0
        self.snowfract = 0.6

        ### Shape of Domain make useful fill arrays
        shape = np.shape(wrf_ds.T[0, :, :])
        self.shape = shape
        self.domain = domain
        print("Domain shape:  ", shape)

        # self.e_full    = np.full(shape,e, dtype=float)
        self.zero_full = np.zeros(shape, dtype=float)
        self.ones_full = np.full(shape, 1, dtype=float)

        ### Daylength factor in Duff Moisture Code
        month = np.datetime_as_string(wrf_ds.Time[0], unit="h")
        print("Current Month:  ", month[5:7])
        month = int(month[5:7]) - 1
        L_e = [6.5, 7.5, 9.0, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8.0, 7.0, 6.0]
        L_e = L_e[month]
        self.L_e = L_e

        ### Daylength adjustment in Drought Code
        L_f = [-1.6, -1.6, -1.6, 0.9, 3.8, 5.8, 6.4, 5.0, 2.4, 0.4, -1.6, -1.6]
        L_f = L_f[month]
        self.L_f = L_f

        ### Open time zones dataset...each grids offset from utc time
        tzone_ds = xr.open_dataset(str(tzone_dir) + f"/tzone_wrf_{self.domain}.nc")
        self.tzone_ds = tzone_ds

        # ### Create an hourly datasets for use with their respected codes/indices
        self.hourly_ds = wrf_ds
        wrf_ds = wrf_ds.drop_vars(["SNW", "SNOWH", "U10", "V10"])

        ### Create an hourly and daily datasets for use with their respected codes/indices
        self.daily_ds = self.create_daily_ds(wrf_ds)
        for var in self.hourly_ds.data_vars:
            if var in {"SNW", "SNOWH", "U10", "V10"}:
                pass
            else:
                self.daily_ds[var].attrs = self.hourly_ds[var].attrs
        self.daily_ds["r_o_tomorrow"].attrs = self.daily_ds["r_o"].attrs

        ### Solve for hourly rain totals in mm....will be used in ffmc calculation
        r_oi = np.array(self.hourly_ds.r_o)
        r_o_plus1 = np.dstack((self.zero_full.T, r_oi.T)).T
        r_hourly_list = []
        for i in range(len(self.hourly_ds.Time)):
            r_hour = self.hourly_ds.r_o[i] - r_o_plus1[i]
            r_hourly_list.append(r_hour)
        r_hourly = np.stack(r_hourly_list)
        r_hourly = xr.DataArray(
            r_hourly, name="r_o_hourly", dims=("time", "south_north", "west_east")
        )
        self.hourly_ds["r_o_hourly"] = r_hourly
        # self.hourly_ds['r_o_hourly'].attrs = self.daily_ds['r_o'].attrs

        if initialize == True:
            int_time = np.array(wrf_ds.Time.dt.strftime("%Y-%m-%dT%H"))
            int_time = datetime.strptime(str(int_time[0]), "%Y-%m-%dT%H").strftime(
                "%Y%m%d%H"
            )
            print(f"{initialize}: Initialize FFMC on date {int_time}, with 85s")
            # """ ################## Fine Fuel Moisture Code (FFMC) ##################### """
            F_o = self.F_initial  # Previous day's F becomes F_o
            F_o_full = np.full(shape, F_o, dtype=float)

            ### (1)
            ### Solve for fine fuel moisture content (m_o)
            # m_o = (205.2 * (101 - F_o_full)) / (82.9 + F_o_full)  ## Van 1977
            m_o = (147.27723 * (101 - F_o_full)) / (59.5 + F_o_full)  ## Van 1985

            ### Create dataarrays for F and m_m
            F = xr.DataArray(F_o_full, name="F", dims=("south_north", "west_east"))
            m_o = xr.DataArray(m_o, name="m_o", dims=("south_north", "west_east"))

            ### Add dataarrays to hourly dataset
            self.hourly_ds["F"] = F
            self.hourly_ds["m_o"] = m_o

            # """ ####################   Duff Moisture Code (DMC)    ##################### """
            previous_time = np.array(wrf_ds.Time.dt.strftime("%Y-%m-%dT%H"))
            previous_time = datetime.strptime(
                str(previous_time[0]), "%Y-%m-%dT%H"
            ).strftime("%Y%m%d%H")
            print(f"{initialize}: Initialize DMC on date {previous_time}, with 6s")
            P_o = self.P_initial
            P_o_full = np.full(shape, P_o, dtype=float)

            ### Solve for initial log drying rate (K_o)
            K_o = (
                1.894
                * (self.daily_ds.T[0] + 1.1)
                * (100 - self.daily_ds.H[0])
                * (L_e * 10 ** -6)
            )

            ### Solve for initial duff moisture code (P_o)
            P_o = P_o_full + (100 * K_o)

            ### Create dataarrays for P
            P = xr.DataArray(P_o, name="P", dims=("south_north", "west_east"))

            ### Add dataarrays to daily dataset
            self.daily_ds["P"] = P

            # """ #####################     Drought Code (DC)       ########################### """
            print(f"{initialize}: Initialize DC on date {previous_time}, with 15s")
            D_o = self.D_initial

            D_o_full = np.full(shape, D_o, dtype=float)

            D = xr.DataArray(D_o_full, name="D", dims=("south_north", "west_east"))
            self.daily_ds["D"] = D

        elif initialize == False:

            int_time = wrf_ds.Time.values
            try:
                retrive_time = pd.to_datetime(str(int_time[0] - np.timedelta64(1, "D")))
                retrive_time = retrive_time.strftime("%Y%m%d%H")
                hourly_file_dir = (
                    str(fwf_zarr_dir) + f"/fwf-hourly-{domain}-{retrive_time}.zarr"
                )
                daily_file_dir = (
                    str(fwf_zarr_dir) + f"/fwf-daily-{domain}-{retrive_time}.zarr"
                )

                previous_hourly_ds = xr.open_zarr(hourly_file_dir)
                previous_daily_ds = xr.open_zarr(daily_file_dir)
                print(
                    f"{Path(hourly_file_dir).exists()}: Found previous FFMC on date {retrive_time}, will merge with hourly_ds"
                )
                print(
                    f"{Path(daily_file_dir).exists()}: Found previous DMC on date {retrive_time}, will merge with daily_ds"
                )
                print(
                    f"{Path(daily_file_dir).exists()}: Found previous DC on date {retrive_time}, will merge with daily_ds"
                )
            except:
                try:
                    retrive_time = pd.to_datetime(
                        str(int_time[0] - np.timedelta64(2, "D"))
                    )
                    retrive_time = retrive_time.strftime("%Y%m%d%H")
                    hourly_file_dir = (
                        str(fwf_zarr_dir) + f"/fwf-hourly-{domain}-{retrive_time}.zarr"
                    )
                    daily_file_dir = (
                        str(fwf_zarr_dir) + f"/fwf-daily-{domain}-{retrive_time}.zarr"
                    )

                    previous_hourly_ds = xr.open_zarr(hourly_file_dir)
                    previous_daily_ds = xr.open_zarr(daily_file_dir)
                    print(
                        f"{Path(hourly_file_dir).exists()}: Found previous FFMC on date {retrive_time}, will merge with hourly_ds"
                    )
                    print(
                        f"{Path(daily_file_dir).exists()}: Found previous DMC on date {retrive_time}, will merge with daily_ds"
                    )
                    print(
                        f"{Path(daily_file_dir).exists()}: Found previous DC on date {retrive_time}, will merge with daily_ds"
                    )
                except:
                    raise FileNotFoundError(
                        "ERROR: Can Not Find Previous dataset to initialize model, consider running with initialize as True"
                    )

            # """ ################## Fine Fuel Moisture Code (FFMC) ##################### """
            ### Open previous days hourly_ds
            previous_hourly_ds = xr.open_zarr(hourly_file_dir)
            previous_time = np.array(previous_hourly_ds.Time.dt.strftime("%Y-%m-%dT%H"))
            previous_time = datetime.strptime(
                str(previous_time[0]), "%Y-%m-%dT%H"
            ).strftime("%Y%m%d%H")

            ### Get time step of F and m_o that coincides with the initialization time of current model run
            # current_time = np.datetime_as_string(self.hourly_ds.Time[0], unit="h")
            int_time = pd.to_datetime(
                str(self.hourly_ds.Time.values[0] - np.timedelta64(1, "h"))
            )
            int_time = int_time.strftime("%Y-%m-%dT%H")
            previous_times = np.datetime_as_string(previous_hourly_ds.Time, unit="h")
            (index,) = np.where(previous_times == int_time)
            index = int(index[0])
            F = np.array(previous_hourly_ds.F[index])
            m_o = np.array(previous_hourly_ds.m_o[index])

            ### Create dataarrays for F and m_m
            F = xr.DataArray(F, name="F", dims=("south_north", "west_east"))
            m_o = xr.DataArray(m_o, name="m_o", dims=("south_north", "west_east"))

            ### Add dataarrays to hourly dataset
            self.hourly_ds["F"] = F
            self.hourly_ds["m_o"] = m_o

            # """ ####################   Duff Moisture Code (DCM)    ##################### """
            ### Open previous days daily_ds
            previous_daily_ds = xr.open_zarr(daily_file_dir)
            previous_time = np.array(previous_daily_ds.Time.dt.strftime("%Y-%m-%dT%H"))
            try:
                previous_time = datetime.strptime(
                    str(previous_time[0]), "%Y-%m-%dT%H"
                ).strftime("%Y%m%d%H")
            except:
                previous_time = datetime.strptime(
                    str(previous_time), "%Y-%m-%dT%H"
                ).strftime("%Y%m%d%H")

            ### Get last time step of P and r_o_previous (carry over rain)
            ### that coincides with the initialization time of current model run
            try:
                # current_time = np.datetime_as_string(self.daily_ds.Time[0], unit="D")
                int_time = pd.to_datetime(
                    str(self.daily_ds.Time.values[0] - np.timedelta64(1, "D"))
                )
                int_time = int_time.strftime("%Y-%m-%dT%H")
            except:
                # current_time = np.datetime_as_string(self.daily_ds.Time, unit="D")
                int_time = pd.to_datetime(
                    str(self.daily_ds.Time.values - np.timedelta64(1, "D"))
                )
                int_time = int_time.strftime("%Y-%m-%dT%H")
            print("looking for initialize time", int_time)
            previous_times = np.datetime_as_string(previous_daily_ds.Time, unit="D")
            print("available time options to initialize", previous_times)
            (index,) = np.where(previous_times == int_time)
            if not index:
                index = 0
            else:
                index = int(index[0])
            print(f"Using {previous_times[index]} to initialize")
            P = np.array(previous_daily_ds.P[index])
            r_o_previous = np.array(previous_daily_ds.r_o_tomorrow[0])

            ### Create dataarrays for P
            P = xr.DataArray(P, name="P", dims=("south_north", "west_east"))

            ### Add dataarrays to daily dataset
            self.daily_ds["P"] = P
            ### Add carry over rain to first time step
            self.daily_ds["r_o"][0] = self.daily_ds["r_o"][0] + np.array(r_o_previous)

            # """ #####################     Drought Code (DC)       ########################### """
            ### Get last time step of D that coincides with the
            ### initialization time of current model run
            D = np.array(previous_daily_ds.D[index])

            ### Create dataarrays for D
            D = xr.DataArray(D, name="D", dims=("south_north", "west_east"))

            ### Add dataarrays to daily dataset
            self.daily_ds["D"] = D

        else:
            raise ValueError(
                "ERROR: Can Not Run FWF Model With initialize Option Provided"
            )

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
        W, T, H, r_o, m_o, F = (
            hourly_ds.W,
            hourly_ds.T,
            hourly_ds.H,
            hourly_ds.r_o_hourly,
            hourly_ds.m_o,
            hourly_ds.F,
        )

        # e_full, zero_full = self.e_full, self.zero_full
        zero_full = self.zero_full

        ########################################################################
        ### (1b) Solve for the effective rain (r_f)
        ## Van/Pick define as 0.5
        r_limit = 0.5
        r_fi = xr.where(r_o < r_limit, r_o, (r_o - r_limit))
        r_f = xr.where(r_fi > 1e-7, r_fi, 1e-7)

        ########################################################################
        ### (1c) Solve the Rainfall routine as defined in  Van Wagner 1985 (m_r)
        m_o_limit = 150
        # a =  (-100 / (251 - m_o))
        # b = (-6.93 / r_f)
        # m_r_low = xr.where(m_o >= m_o_limit, zero_full, m_o + \
        #                     (42.5 * r_f * np.power(e_full,a) * (1- np.power(e_full,b))))

        m_r_low = xr.where(
            m_o >= m_o_limit,
            zero_full,
            m_o
            + (42.5 * r_f * np.exp((-100 / (251 - m_o))) * (1 - np.exp((-6.93 / r_f)))),
        )

        ########################################################################
        ### (1d) Solve the RainFall routine as defined in  Van Wagner 1985 (m_r)
        # m_r_high = xr.where(m_o < m_o_limit, zero_full, m_o + \
        #                     (42.5 * r_f * np.power(e_full, a) * (1 - np.power(e_full, b))) + \
        #                         (0.0015 * np.power((m_o - 150),2) * np.power(r_f, 0.5)))

        m_r_high = xr.where(
            m_o < m_o_limit,
            zero_full,
            m_o
            + (42.5 * r_f * np.exp((-100 / (251 - m_o))) * (1 - np.exp((-6.93 / r_f))))
            + (0.0015 * np.power((m_o - 150), 2) * np.power(r_f, 0.5)),
        )

        ########################################################################
        ### (1e) Set new m_o with the rainfall routine (m_o)
        m_o = m_r_low + m_r_high
        m_o = np.where(m_o < 250, m_o, 250)  # Set upper limit of 250
        m_o = np.where(m_o > 0, m_o, 1e4)  # Set lower limit of 0

        ########################################################################
        ### (2a) Solve Equilibrium Moisture content for drying (E_d)
        ## define powers
        a = 0.679
        # b = ((H-100)/ 10)
        # c = (-0.115 * H)

        # E_d = (0.942 * np.power(H,a)) + (11 * np.power(e_full,b)) \
        #             + (0.18 * (21.1 - T) * (1 - np.power(e_full,c)))

        E_d = (
            (0.942 * np.power(H, a))
            + (11 * np.exp(((H - 100) / 10)))
            + (0.18 * (21.1 - T) * (1 - np.exp((-0.115 * H))))
        )

        ########################################################################
        ### (2b) Solve Equilibrium Moisture content for wetting (E_w)
        ## define powers (will use b and c from 2a)
        d = 0.753

        # E_w  = xr.where(m_o > E_d, zero_full,(0.618 * (np.power(H, d))) +  \
        #                     (10 * np.power(e_full, b)) + (0.18 * (21.1 - T)  * \
        #                     (1 - np.power(e_full, c))))

        E_w = xr.where(
            m_o > E_d,
            zero_full,
            (0.618 * (np.power(H, d)))
            + (10 * np.exp(((H - 100) / 10)))
            + (0.18 * (21.1 - T) * (1 - np.exp((-0.115 * H)))),
        )

        ########################################################################
        ### (3a) intermediate step to k_d (k_a)
        # a = ((100 - H) / 100)   ## Van Wagner 1987
        # a = H/100               ## Van Wagner 1977

        k_a = xr.where(
            m_o < E_d,
            zero_full,
            0.424 * (1 - np.power(H / 100, 1.7))
            + 0.0694 * (np.power(W, 0.5)) * (1 - np.power(H / 100, 8)),
        )

        ########################################################################
        ### (3b) Log drying rate for hourly computation, log to base 10 (k_d)
        b = 0.0579

        # k_d = xr.where(m_o < E_d, zero_full, b * k_a * np.power(e_full,(0.0365 * T)))
        k_d = xr.where(m_o < E_d, zero_full, b * k_a * np.exp(0.0365 * T))

        ########################################################################
        ### (4a) intermediate steps to k_w (k_b)
        # a = ((100 - H) / 100)

        k_b = xr.where(
            m_o > E_w,
            zero_full,
            0.424 * (1 - np.power(((100 - H) / 100), 1.7))
            + 0.0694 * np.power(W, 0.5) * (1 - np.power(((100 - H) / 100), 8)),
        )

        ########################################################################
        ### (4b)  Log wetting rate for hourly computation, log to base 10 (k_w)
        b = 0.0579

        # k_w = xr.where(m_o > E_w, zero_full, b * k_b * np.power(e_full,(0.0365 * T)))
        k_w = xr.where(m_o > E_w, zero_full, b * k_b * np.exp(0.0365 * T))

        ########################################################################
        ### (5a) intermediate dry moisture code (m_d)

        # m_d = xr.where(m_o < E_d, zero_full, E_d + ((m_o - E_d) * np.power(e_full, -2.303*(k_d))))  ## Van Wagner 1977
        # m_d = xr.where(m_o < E_d, zero_full, E_d + ((m_o - E_d) * np.power(10, -(k_d))))            ## Van Wagner 1985

        m_d = xr.where(
            m_o < E_d, zero_full, E_d + ((m_o - E_d) * np.exp(-2.303 * (k_d)))
        )  ## Van Wagner 1977

        ########################################################################
        ### (5b) intermediate wet moisture code (m_w)

        # m_w = xr.where(m_o > E_w, zero_full, E_w - ((E_w - m_o) * np.power(e_full, -2.303*(k_w))))  ## Van Wagner 1977
        # m_w = xr.where(m_o > E_w, zero_full, E_w - ((E_w - m_o) * np.power(10, -(k_w))))            ## Van Wagner 1985

        m_w = xr.where(
            m_o > E_w, zero_full, E_w - ((E_w - m_o) * np.exp(-2.303 * (k_w)))
        )  ## Van Wagner 1977

        ########################################################################
        ### (5c) intermediate neutral moisture code (m_neutral)

        m_neutral = xr.where(
            (E_d <= m_o), zero_full, xr.where((m_o <= E_w), zero_full, m_o)
        )

        ########################################################################
        ### (6) combine dry, wet, neutral moisture codes

        m = m_d + m_w + m_neutral
        m = xr.where(m <= 250, m, 250)

        ### Solve for FFMC
        # F = (82.9 * (250 - m)) / (205.2 + m)    ## Van 1977
        F = (59.5 * (250 - m)) / (147.27723 + m)  ## Van 1985

        ### Recast initial moisture code for next time stamp
        # m_o = (205.2 * (101 - F)) / (82.9 + F)  ## Van 1977
        m_o = (147.27723 * (101 - F)) / (59.5 + F)  ## Van 1985

        self.hourly_ds["F"] = F
        self.hourly_ds["m_o"] = m_o

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
        daily_ds: DataSet
            - Adds DMC to DataSet
        """

        W, T, H, r_o, P_o, L_e, SNOWC = (
            daily_ds.W,
            daily_ds.T,
            daily_ds.H,
            daily_ds.r_o,
            daily_ds.P,
            self.L_e,
            daily_ds.SNOWC,
        )

        # e_full, zero_full, ones_full = self.e_full, self.zero_full, self.ones_full
        zero_full, ones_full = self.zero_full, self.ones_full

        #### HOPEFULLY SOLVES RUNTIME WARNING
        P_o = xr.where(P_o > 0, P_o, 0.1)

        ########################################################################
        ### (11) Solve for the effective rain (r_e)
        r_total = 1.5
        r_ei = xr.where(r_o < r_total, r_o, (0.92 * r_o) - 1.27)
        r_e = xr.where(r_ei > 1e-7, r_ei, 1e-7)

        ########################################################################
        ### (12) Recast moisture content after rain (M_o)
        ##define power
        # a = (5.6348 - (P_o / 43.43))
        # M_o = xr.where(r_o < r_total, zero_full, 20 + np.power(e_full,a))
        # M_o = xr.where(r_o < r_total, zero_full, 20 + np.exp(a))

        ## Alteration to Eq. 12 to calculate more accurately (Lawson 2008)
        M_o = 20 + 280 / np.exp(0.023 * P_o)

        ########################################################################
        ### (13a) Solve for coefficients b where P_o <= 33 (b_low)
        b_low = xr.where(
            r_o < r_total,
            zero_full,
            xr.where(P_o >= 33, zero_full, 100 / (0.5 + (0.3 * P_o))),
        )

        ########################################################################
        ### (13b) Solve for coefficients b where 33 < P_o <= 65 (b_mid)

        b_mid = xr.where(
            r_o < r_total,
            zero_full,
            xr.where((P_o > 33) & (P_o <= 65), zero_full, 14 - (1.3 * np.log(P_o))),
        )

        ########################################################################
        ### (13c) Solve for coefficients b where  P_o > 65 (b_high)

        b_high = xr.where(
            r_o < r_total,
            zero_full,
            xr.where(P_o < 65, zero_full, (6.2 * np.log(P_o)) - 17.2),
        )

        ########################################################################
        ### (14a) Solve for moisture content after rain where P_o <= 33 (M_r_low)

        M_r_low = xr.where(
            r_o < r_total,
            zero_full,
            xr.where(P_o >= 33, zero_full, M_o + (1000 * r_e) / (48.77 + b_low * r_e)),
        )

        ########################################################################
        ### (14b) Solve for moisture content after rain where 33 < P_o <= 65 (M_r_mid)

        M_r_mid = xr.where(
            r_o < r_total,
            zero_full,
            xr.where(
                P_o < 33,
                zero_full,
                xr.where(
                    P_o >= 65, zero_full, M_o + (1000 * r_e) / (48.77 + b_mid * r_e)
                ),
            ),
        )

        ########################################################################
        ### (14c)  Solve for moisture content after rain where P_o > 65 (M_r_high)

        M_r_high = xr.where(
            r_o < r_total,
            zero_full,
            xr.where(P_o < 65, zero_full, M_o + (1000 * r_e) / (48.77 + b_high * r_e)),
        )

        ########################################################################
        ### (14d) Combine all moisture content after rain (M_r)

        M_r = M_r_low + M_r_mid + M_r_high
        M_r = xr.where(r_o < r_total, zero_full, xr.where(M_r > 20, M_r, 20.0001))

        ########################################################################
        ### (15) Duff moisture code after rain but prior to drying (P_r_pre_K)

        # P_r_pre_K = xr.where(r_o < r_total, zero_full, 244.72 - (43.43 * np.log(M_r - 20)))

        ## Alteration to Eq. 15 to calculate more accurately  (Lawson 2008)
        P_r_pre_K = xr.where(
            r_o < r_total, zero_full, 43.43 * (5.6348 - np.log(M_r - 20))
        )

        P_r_pre_K = xr.where(P_r_pre_K > 0, P_r_pre_K, 1e-6)

        ########################################################################
        ### (16) Log drying rate (K)
        T = np.where(T > -1.1, T, -1.1)

        K = 1.894 * (T + 1.1) * (100 - H) * (L_e * 10 ** -6)

        ########################################################################
        ### (17a) Duff moisture code dry (P_d)
        P_d = xr.where(r_o > r_total, zero_full, P_o + 100 * K)

        ########################################################################
        ### (17b) Duff moisture code dry (P_r)
        P_r = xr.where(r_o < r_total, zero_full, P_r_pre_K + 100 * K)

        ########################################################################
        ##(18) Combine Duff Moisture Codes accross domain (P)

        P_i = P_d + P_r

        ########################################################################
        ## keep grid to P initial (start up value) if grid
        ## is covered by more than 50% snow
        P = xr.where(SNOWC < self.snowfract, P_i, self.P_initial)
        P = xr.where(P > 0.0, P, 0.1)

        self.daily_ds["P"] = P

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
        W, T, H, r_o, D_o, L_f, SNOWC = (
            daily_ds.W,
            daily_ds.T,
            daily_ds.H,
            daily_ds.r_o,
            daily_ds.D,
            self.L_f,
            daily_ds.SNOWC,
        )

        # e_full, zero_full, ones_full = self.e_full, self.zero_full, self.ones_full
        zero_full, ones_full = self.zero_full, self.ones_full

        ########################################################################
        ### (18) Solve for the effective rain (r_d)
        r_limit = 2.8
        r_di = xr.where(r_o < r_limit, r_o, (0.83 * r_o) - 1.27)
        r_d = xr.where(r_di > 1e-7, r_di, 1e-7)

        ########################################################################
        ### (19) Solve for initial moisture equivalent (Q_o)
        # a = (-D_o/400)
        # Q_o = xr.where(r_o < r_limit, zero_full, 800 * np.power(e_full,a))
        Q_o = xr.where(r_o < r_limit, zero_full, 800 * np.exp((-D_o / 400)))

        ########################################################################
        ### (20) Solve for moisture equivalent (Q_r)

        # Q_r = xr.where(r_o < r_limit, zero_full, Q_o + (3.937 * r_d))

        #### HOPEFULLY SOLVES RUNTIME WARNING
        # Q_r = xr.where(Q_r > 0, Q_r, 1e-6)

        ########################################################################
        ### (21) Solve for DC after rain (D_r)
        # a = (800/Q_r)
        # D_r = xr.where(r_o < r_limit, zero_full, 400 * np.log(a))

        ## Alteration to Eq. 21 (Lawson 2008)\
        # a = 1 + 3.937 * r_d/Q_o
        D_r = xr.where(
            r_o < r_limit, zero_full, D_o - 400 * np.log(1 + 3.937 * r_d / Q_o)
        )
        D_r = xr.where(D_r > 0, D_r, 0.1)

        ########################################################################
        ### (22) Solve for potential evapotranspiration (V)
        T = np.where(T > -2.8, T, -2.8)

        V = (0.36 * (T + 2.8)) + L_f

        ### V can not go negative, if V does go negative raise to zero
        V = xr.where(V > 0, V, 0.1)

        ########################################################################
        ### (23) Combine dry and moist D and Solve for Drought Code (D)
        D_d = xr.where(r_o > r_limit, zero_full, D_o)
        D_combine = D_d + D_r
        # D_i = D_combine + (0.5 * V)

        ## Alteration to Eq. 23 (Lawson 2008)
        D_i = D_combine + V

        ########################################################################
        ## keep grid to D initial (start up value) if grid
        ## is covered by more than 50% snow
        D = xr.where(SNOWC < self.snowfract, D_i, self.D_initial)

        ### D can not go negative, if D does go negative raise to zero
        D = xr.where(D > 0.0, D, 0.1)

        self.daily_ds["D"] = D

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

        # e_full, zero_full = self.e_full, self.zero_full
        zero_full = self.zero_full

        ########################################################################
        ### (24) Solve for wind function (f_W)
        # a = 0.05039 * W
        # f_W = np.power(e_full, a)

        # This modification is Equation 53a in FCFDG (1992) (Lawson 2008)
        W_limit = 40.0
        f_W_low = xr.where(W > W_limit, zero_full, np.exp(0.05039 * W))
        f_W_high = xr.where(
            W <= W_limit, zero_full, 12 * (1 - np.exp(-0.0818 * (W - 28)))
        )
        f_W = f_W_low + f_W_low

        ########################################################################
        ### (25) Solve for fine fuel moisture function (f_F)
        # a = -0.1386 * m_o
        # # b = np.power(e_full, a)
        # b = np.exp(a)
        # c = (1 + np.power(m_o, 5.31) / (4.93e7))
        # f_F = 91.9 * b * c

        f_F = 91.9 * np.exp(-0.1386 * m_o) * (1 + np.power(m_o, 5.31) / (4.93e7))
        ########################################################################
        ### (26) Solve for initial spread index (R)

        R = 0.208 * f_W * f_F

        R = xr.DataArray(R, name="R", dims=("time", "south_north", "west_east"))

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
        zero_full = self.zero_full

        ### Call on initial conditions
        P, D = daily_ds.P, daily_ds.D

        ########################################################################
        ### (27a) Solve for build up index where P =< 0.4D (U_a)
        P_limit = 0.4 * D
        # U_a = (0.8 * P * D) / (P + (0.4 * D))
        U_a = xr.where(P >= P_limit, zero_full, 0.8 * P * D / (P + (0.4 * D)))

        ########################################################################
        ### (27b) Solve for build up index where P > 0.4D (U_b)

        # a   = 0.92 + np.power((0.0114 * P), 1.7)
        # U_b = P - ((1 - (0.8 * D)) / (P + (0.4 * D))) * a
        U_b = xr.where(
            P < P_limit,
            zero_full,
            P - (1 - 0.8 * D / (P + (0.4 * D))) * (0.92 + np.power((0.0114 * P), 1.7)),
        )

        ########################################################################
        ### (27c) Combine build up index (U)

        U = U_a + U_b

        U = np.where(U > 0, U, 0.1)  # Set lower limit of 0

        U = xr.DataArray(U, name="U", dims=("time", "south_north", "west_east"))

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
        # e_full, zero_full = self.e_full, self.zero_full
        zero_full = self.zero_full

        ########################################################################
        ### (28a) Solve for duff moisture function where U =< 80(f_D_a)
        U_limit = 80
        # f_D_a = (0.626 * np.power(U, 0.809)) + 2
        f_D_a = xr.where(U >= U_limit, zero_full, (0.626 * np.power(U, 0.809)) + 2)

        ########################################################################
        ### (28b) Solve for duff moisture function where U > 80 (f_D_b)
        # a = np.power(e_full, (-0.023 * U))
        # a = np.exp(-0.023 * U)
        # f_D_b = 1000 / (25 + 108.64 * a)
        f_D_b = xr.where(
            U < U_limit, zero_full, 1000 / (25 + 108.64 * np.exp(-0.023 * U))
        )

        ########################################################################
        ### (28c) Combine duff moisture functions (f_D)
        f_D = f_D_a + f_D_b

        ########################################################################

        index = [i for i in range(1, len(R) + 1) if i % 24 == 0]
        if len(index) == 1:
            ### (29a) Solve FWI intermediate form  for day 1(B_a)
            B = 0.1 * R[:] * f_D[0]
        elif len(index) == 2:
            # print("fwi index", index[0])
            B_a = 0.1 * R[: index[0]] * f_D[0]
            ### (29b) Solve FWI intermediate form for day 2 (B_b)
            B_b = 0.1 * R[index[0] :] * f_D[1]
            ### (29c) COmbine FWI intermediate (B)
            B = xr.combine_nested([B_a, B_b], "time")
        else:
            raise ValueError(
                "ERROR: Rodell was lazy and needs to rethink indexing of multi length wrf runs"
            )

        #### HOPEFULLY SOLVES RUNTIME WARNING
        B = xr.where(B > 0, B, 1e-6)

        ########################################################################
        ### (30a) Solve FWI where B > 1 (S_a)
        B_limit = 1
        # a = np.power((0.434 * np.log(B)), 0.647)
        # S_a = np.power(e_full,2.72 * a)
        # S_a = np.exp(2.72 * a)
        S_a = xr.where(
            B < B_limit, zero_full, np.exp(2.72 * np.power((0.434 * np.log(B)), 0.647))
        )

        ########################################################################
        ### (30b) Solve FWI where B =< 1 (S_b)

        S_b = xr.where(B >= B_limit, zero_full, B)
        ########################################################################
        ### (30) Combine for FWI (S)

        S = S_a + S_b
        S = xr.DataArray(S, name="S", dims=("time", "south_north", "west_east"))

        ########################################################################
        ### (31) Solve for daily severity rating (DSR)

        DSR = 0.0272 * np.power(S, 1.77)
        DSR = xr.DataArray(DSR, name="DSR", dims=("time", "south_north", "west_east"))

        return S, DSR

    """########################################################################"""
    """ ###################### Create Daily Dataset ###########################"""
    """########################################################################"""

    def create_daily_ds(self, wrf_ds):
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
        tzone_ds = self.tzone_ds
        tzone = tzone_ds.Zone.values

        ## create I, J for quick indexing
        I, J = np.ogrid[: self.shape[0], : self.shape[1]]

        ## determine index for looping based on length of time array and initial time
        time_array = wrf_ds.Time.values
        int_time = int(pd.Timestamp(time_array[0]).hour)
        length = len(time_array) + 1
        num_days = [i - 12 for i in range(1, length) if i % 24 == 0]
        index = [
            i - int_time if 12 - int_time >= 0 else i + 24 - int_time for i in num_days
        ]
        print(f"index of times {index} with initial time {int_time}Z")

        ## loop every 24 hours at noon local
        files_ds = []
        for i in index:
            # print(i)
            ## loop each variable
            mean_da = []
            for var in wrf_ds.data_vars:
                if var == "SNOWC":
                    var_array = wrf_ds[var].values
                    noon = var_array[(i + tzone), I, J]
                    day = np.array(wrf_ds.Time[i + 1], dtype="datetime64[D]")
                    var_da = xr.DataArray(
                        noon,
                        name=var,
                        dims=("south_north", "west_east"),
                        coords=wrf_ds.isel(time=i).coords,
                    )
                    var_da["Time"] = day
                    mean_da.append(var_da)
                else:
                    var_array = wrf_ds[var].values
                    noon_minus = var_array[(i + tzone - 1), I, J]
                    noon = var_array[(i + tzone), I, J]
                    noon_pluse = var_array[(i + tzone + 1), I, J]
                    noon_mean = (noon_minus + noon + noon_pluse) / 3
                    day = np.array(wrf_ds.Time[i + 1], dtype="datetime64[D]")
                    var_da = xr.DataArray(
                        noon_mean,
                        name=var,
                        dims=("south_north", "west_east"),
                        coords=wrf_ds.isel(time=i).coords,
                    )
                    var_da["Time"] = day
                    mean_da.append(var_da)

            mean_ds = xr.merge(mean_da)
            files_ds.append(mean_ds)

        daily_ds = xr.combine_nested(files_ds, "time")

        ## create datarray for carry over rain, this will be added to the next days rain totals
        ## NOTE: this is rain that fell from noon local until 24 hours past the model initial time ie 00Z, 06Z..
        r_o_tomorrow_i = wrf_ds.r_o.values[23] - daily_ds.r_o.values[0]
        r_o_tomorrow = [r_o_tomorrow_i for i in range(len(num_days))]
        r_o_tomorrow = np.stack(r_o_tomorrow)
        r_o_tomorrow_da = xr.DataArray(
            r_o_tomorrow,
            name="r_o_tomorrow",
            dims=("time", "south_north", "west_east"),
            coords=daily_ds.coords,
        )
        r_o_tomorrow_da = xr.where(r_o_tomorrow_da > 1e-4, r_o_tomorrow_da, 0.0)

        daily_ds["r_o_tomorrow"] = r_o_tomorrow_da

        ## create daily 24 accumulated precipitation totals
        x_prev = 0
        for i, x_val in enumerate(daily_ds.r_o):
            daily_ds.r_o[i] -= x_prev
            x_prev = x_val

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
            FFMC = self.solve_ffmc(self.hourly_ds.isel(time=i))
            hourly_list.append(FFMC)
        print("Hourly loop done")
        # hourly_ds = self.combine_by_time(hourly_list)
        hourly_ds = xr.combine_nested(hourly_list, "time")

        ISI = self.solve_isi(hourly_ds)
        hourly_ds["R"] = ISI
        self.R = ISI
        FWI, DSR = self.solve_fwi()
        hourly_ds["S"] = FWI
        hourly_ds["DSR"] = DSR

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

        daily_list = []
        print("Start Daily loop length: ", length)
        for i in range(length):
            DMC = self.solve_dmc(self.daily_ds.isel(time=i))
            DC = self.solve_dc(self.daily_ds.isel(time=i))
            DMC["D"] = DC["D"]
            daily_list.append(DMC)

        print("Daily loop done")
        # daily_ds = self.combine_by_time(daily_list)
        daily_ds = xr.combine_nested(daily_list, "time")
        U = self.solve_bui(daily_ds)
        daily_ds["U"] = U
        self.U = U
        return daily_ds

    """#######################################"""
    """ ######### Combine Datasets ###########"""
    """#######################################"""

    def combine_by_time(self, dict_list):
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
            ds = xr.Dataset(index)
            files_ds.append(ds)
        combined_ds = xr.combine_nested(files_ds, "time")
        return combined_ds

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

        hourly_ds.F.attrs = hourly_ds.T.attrs
        del hourly_ds.F.attrs["units"]
        hourly_ds.F.attrs["description"] = "FINE FUEL MOISTURE CODE"

        hourly_ds.m_o.attrs = hourly_ds.T.attrs
        del hourly_ds.m_o.attrs["units"]
        hourly_ds.m_o.attrs["description"] = "FINE FUEL MOISTURE CONTENT"

        hourly_ds.R.attrs = hourly_ds.T.attrs
        del hourly_ds.R.attrs["units"]
        hourly_ds.R.attrs["description"] = "INITIAL SPREAD INDEX"

        hourly_ds.S.attrs = hourly_ds.T.attrs
        del hourly_ds.S.attrs["units"]
        hourly_ds.S.attrs["description"] = "FIRE WEATHER INDEX"

        hourly_ds.DSR.attrs = hourly_ds.T.attrs
        del hourly_ds.DSR.attrs["units"]
        hourly_ds.DSR.attrs["description"] = "DAILY SEVERITY RATING"

        hourly_ds.r_o_hourly.attrs = hourly_ds.r_o.attrs
        hourly_ds.r_o_hourly.attrs["description"] = "HOURLY PRECIPITATION TOTALS"

        for var in hourly_ds.data_vars:
            hourly_ds[var] = hourly_ds[var].astype(dtype="float32")

        # ### Name file after initial time of wrf
        file_date = str(np.array(self.hourly_ds.Time[0], dtype="datetime64[h]"))
        file_date = datetime.strptime(str(file_date), "%Y-%m-%dT%H").strftime(
            "%Y%m%d%H"
        )
        print("Hourly zarr initialized at :", file_date)

        # # ## Write and save DataArray (.zarr) file
        make_dir = Path(
            str(fwf_zarr_dir)
            + str("/fwf-hourly-")
            + self.domain
            + str(f"-{file_date}.zarr")
        )
        make_dir.mkdir(parents=True, exist_ok=True)
        hourly_ds = hourly_ds.compute()
        hourly_ds.to_zarr(make_dir, mode="w")
        print(f"wrote working {make_dir}")

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

        daily_ds.P.attrs = daily_ds.T.attrs
        del daily_ds.P.attrs["units"]
        daily_ds.P.attrs["description"] = "DUFF MOISTURE CODE"

        daily_ds.D.attrs = daily_ds.T.attrs
        del daily_ds.D.attrs["units"]
        daily_ds.D.attrs["description"] = "DROUGHT CODE"

        daily_ds.U.attrs = daily_ds.T.attrs
        del daily_ds.U.attrs["units"]
        daily_ds.U.attrs["description"] = "BUILD UP INDEX"

        for var in daily_ds.data_vars:
            daily_ds[var] = daily_ds[var].astype(dtype="float32")

        daily_ds.r_o.attrs["description"] = "24 HOUR ACCUMULATED PRECIPITATION"

        # ### Name file after initial time of wrf
        file_date = str(np.array(self.hourly_ds.Time[0], dtype="datetime64[h]"))
        file_date = datetime.strptime(str(file_date), "%Y-%m-%dT%H").strftime(
            "%Y%m%d%H"
        )

        print("Daily zarr initialized at :", file_date)

        # # ## Write and save DataArray (.zarr) file
        make_dir = Path(
            str(fwf_zarr_dir)
            + str("/fwf-daily-")
            + self.domain
            + str(f"-{file_date}.zarr")
        )
        make_dir.mkdir(parents=True, exist_ok=True)
        daily_ds = daily_ds.compute()
        daily_ds.to_zarr(make_dir, mode="w")
        print(f"wrote working {make_dir}")

        return str(make_dir)
