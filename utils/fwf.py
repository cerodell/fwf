#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

"""
Class to solve the Fire Weather Indices using output from a numerical weather model
"""

import context
import os
import math
import json
import numpy as np
import pandas as pd
import xarray as xr


from pathlib import Path

# from netCDF4 import Dataset
from datetime import datetime
from utils.bias_correct import bias_correct
from utils.compressor import compressor, file_size
from utils.era5 import read_era5
from utils.open import read_dataset

from context import data_dir, root_dir


__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


class FWF:
    """
    Class to solve the Fire Weather Index System and the Fire Behavior Predictions System using output from a numerical weather model

    Parameters
    ----------

    filein_dir: str
        - File directory to (nc) file of WRF met variables to calculate FWI
    domain: str
        - the wrf domain tag, examples d03 or d02
    wrf_model: str
        - the wrf version, this will be removed in future versions assuming WRFv4 is being used

    fbp_mode: boolean
        - True, FBP will be resolved with FWI and both returned
        - False, Only FWI will be resolved and returned

    initialize: boolean
        - True, initializing FWI iterations with default start-up values
        - False, will search and use yesterdays forecast to initialize the FWI iterations


    Returns
    -------

    daily_ds: DataSet
        Writes a DataSet (nc) of daily
        - FWI indices/codes
        - Associated Meterology

    hourly_ds: DataSet
        Writes a DataSet (nc) of hourly
        - FWI indices/codes
        - Associated Meterology
        - FBP products (if fbp_mode is True)

    """

    """########################################################################"""
    """ ######################## Initialize FWI model #########################"""
    """########################################################################"""

    def __init__(self, config):
        """
        Initialize Fire Weather Index Model

        """

        self.int_ds = read_dataset(config)

        ############ Set up dataset and get attributes ################
        self.attrs = self.int_ds.attrs
        self.model = config["model"]
        self.domain = config["domain"]
        self.trail_name = config["trail_name"]
        self.fbp_mode = config["fbp_mode"]
        self.overwinter = config["overwinter"]
        self.initialize = config["initialize"]
        self.correctbias = config["correctbias"]
        self.root_dir = config["root_dir"]
        self.initialize_hffmc = config["initialize_hffmc"]

        ## NOTE this will be adjusted when made operational
        self.iterator_dir = f"/Volumes/WFRT-Ext24/fwf-data/{self.model}/{self.domain}/{self.trail_name}/"
        self.filein_dir = f"{self.root_dir}/{self.model}/{self.domain}"
        self.save_dir = Path(self.iterator_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

        ############ Mathematical Constants and UsefulArrays ################
        ### Math Constants
        # e = math.e
        self.F_initial = 85.0
        self.P_initial = 6.0
        self.D_initial = 15.0
        self.snowfract = 0.6
        self.date = str(np.datetime_as_string(self.int_ds.Time.values[0], unit="D"))

        ### Shape of Domain make useful fill arrays
        shape = np.shape(self.int_ds.T[0, :, :])
        self.shape = shape
        self.domain = config["domain"]
        print("Domain shape:  ", shape)
        self.zero_full = np.zeros(shape, dtype=float)
        self.ones_full = np.full(shape, 1, dtype=float)

        ### Day length factor in Duff Moisture Code
        month = np.datetime_as_string(self.int_ds.Time[0], unit="h")
        print("Current Month:  ", month[5:7])
        month = int(month[5:7]) - 1
        L_e = [6.5, 7.5, 9.0, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8.0, 7.0, 6.0]
        L_e = L_e[month]
        self.L_e = L_e

        ### Daylength adjustment in Drought Code
        L_f = [-1.6, -1.6, -1.6, 0.9, 3.8, 5.8, 6.4, 5.0, 2.4, 0.4, -1.6, -1.6]
        L_f = L_f[month]
        self.L_f = L_f

        ## Open Data Attributes for writing
        with open(str(root_dir) + f"/json/fwf-attrs.json", "r") as fp:
            self.var_dict = json.load(fp)

        ## Open gridded static
        static_ds = xr.open_dataset(
            str(data_dir) + f"/static/static-vars-{self.model.lower()}-{self.domain}.nc"
        )

        ## Print Over wintering status
        print(f"Overwintering {self.overwinter}")

        ## Define Static Variables for FPB
        # landmask = static_ds['LAND']
        # for var in static_ds:
        #     masked_array = static_ds[var].to_masked_array()
        #     masked_array.mask = landmask
        #     static_ds[var] = (('south_north', 'west_east'), masked_array)
        #     static_ds[var].attrs['pyproj_srs'] = static_ds.attrs['pyproj_srs']
        print(f"FBP Mode {self.fbp_mode}")
        if self.fbp_mode == True:
            (
                self.ELV,
                self.LAT,
                self.LON,
                self.FUELS,
                self.GS,
                self.SAZ,
                self.tzone,
                self.PC,
                # self.landmask
            ) = (
                static_ds.HGT.values,
                static_ds.XLAT.values,
                static_ds.XLONG.values * -1,
                static_ds.FUELS.values.astype(int),
                static_ds.GS.values,
                static_ds.SAZ.values,
                static_ds.ZoneST.values,
                static_ds.PC.values,
                # static_ds.LAND
            )
        elif self.fbp_mode == False:
            self.tzone = static_ds.ZoneST.values
            # self.landmask = static_ds.LAND
        else:
            raise ValueError(
                f"Invalided fbp_mode option: {self.fbp_mode}. Only supports boolean inputs \n Please try with True or False :)"
            )

        ################################################################################
        ## TODO remove all this all, will be required for int_ds
        # ### Create an hourly datasets for use with their respected codes/indices

        # maskTime = datetime.now()
        # landmask = static_ds['LAND']
        # for var in self.int_ds:
        #     masked_array = self.int_ds[var].to_masked_array()
        #     masked_array.mask = landmask
        #     self.int_ds[var] = (('time','south_north', 'west_east'), masked_array)
        #     self.int_ds[var].attrs['pyproj_srs'] = self.int_ds.attrs['pyproj_srs']
        # print("Mask: ", datetime.now() - maskTime)

        self.hourly_ds = self.int_ds
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
        ################################################################################
        ################################################################################
        ## TODO remove all this all, will be required for int_ds
        try:
            self.int_ds = self.int_ds.drop_vars(["SNW", "SNOWH", "U10", "V10"])
        except:
            self.int_ds = self.int_ds.drop_vars(["U10", "V10"])

        ### Create an hourly and daily datasets for use with their respected codes/indices
        self.daily_ds = self.create_daily_ds(self.int_ds)

        for var in self.hourly_ds.data_vars:
            if var in {"SNW", "SNOWH", "U10", "V10"}:
                pass
            else:
                self.daily_ds[var].attrs = self.hourly_ds[var].attrs
        self.daily_ds["r_o_tomorrow"].attrs = self.daily_ds["r_o"].attrs

        # test = self.daily_ds.H.values
        if self.correctbias == True:
            self.daily_ds = bias_correct(self.daily_ds, self.domain, self.config)
        elif self.correctbias == False:
            pass
        else:
            raise ValueError(
                f"Invalided correctbias option: {self.correctbias}. Only supports boolean inputs \n Please try with True or False :)"
            )

        ################################################################################
        ## NOTE this could be a solution for allowing FWF to solve FWI from daily on datasets. Issue will be the TMAX for over wintering.
        ## TODO figure out a solution for TMAX when using daily datasets. I guess just use the noon local values?
        # time_interval = self.int_ds.Time.values
        # # Calculate the time delta
        # if time_interval.size == 1:
        #     self.daily_ds = self.int_ds
        #     print("This is dataset is a has a daily time step, will solve FWI without finding noon local")
        # else:
        #     delta = time_interval[1] - time_interval[0]
        #     hours = delta.astype('timedelta64[h]')
        #     print('Time interval in hours:', hours)
        #     if hours == 1:
        #         print("This is dataset is a has a hourly time interval, will solve FWI by finding noon local")
        #         self.hourly_ds = self.int_ds
        #         ### Solve for hourly rain totals in mm....will be used in ffmc calculation
        #         r_oi = np.array(self.hourly_ds.r_o)
        #         r_o_plus1 = np.dstack((self.zero_full.T, r_oi.T)).T
        #         r_hourly_list = []
        #         for i in range(len(self.hourly_ds.Time)):
        #             r_hour = self.hourly_ds.r_o[i] - r_o_plus1[i]
        #             r_hourly_list.append(r_hour)
        #         r_hourly = np.stack(r_hourly_list)
        #         r_hourly = xr.DataArray(
        #             r_hourly, name="r_o_hourly", dims=("time", "south_north", "west_east")
        #         )
        #         self.hourly_ds["r_o_hourly"] = r_hourly
        #         try:
        #             self.int_ds = self.int_ds.drop_vars(["SNW", "SNOWH", "U10", "V10"])
        #         except:
        #             self.int_ds = self.int_ds.drop_vars(["U10", "V10"])

        #         ### Create an hourly and daily datasets for use with their respected codes/indices
        #         self.daily_ds = self.create_daily_ds(self.int_ds)

        #         for var in self.hourly_ds.data_vars:
        #             if var in {"SNW", "SNOWH", "U10", "V10"}:
        #                 pass
        #             else:
        #                 self.daily_ds[var].attrs = self.hourly_ds[var].attrs
        #         self.daily_ds["r_o_tomorrow"].attrs = self.daily_ds["r_o"].attrs

        #         if self.correctbias == True:
        #             self.daily_ds = bias_correct(self.daily_ds, self.domain, self.config)
        #         elif self.correctbias == False:
        #             pass
        #         else:
        #             raise ValueError(
        #                 f"Invalided correctbias option: {self.correctbias}. Only supports boolean inputs \n Please try with True or False :)"
        #             )
        #     elif hours == 24:
        #         self.daily_ds = self.int_ds
        #         print("This is dataset is a has a daily time interval, will solve FWI without finding noon local")
        #     else:
        #         raise ValueError(f"Sadly this is an incompatible time interval of {hours}. FWF currently only works with hourly or daily time intervals")
        #     ################################################################################
        return

    def iteration(self, timestep):
        int_time = self.int_ds.Time.values
        if timestep == "hourly":
            if self.initialize_hffmc == False:
                previous_hourly_ds = self.ds_retriever(int_time, timestep)
                # """ ################## Fine Fuel Moisture Code (FFMC) ##################### """
                ### Open previous days hourly_ds
                previous_time = np.array(
                    previous_hourly_ds.Time.dt.strftime("%Y-%m-%dT%H")
                )
                previous_time = datetime.strptime(
                    str(previous_time[0]), "%Y-%m-%dT%H"
                ).strftime("%Y%m%d%H")

                ### Get time step of F and m_o that coincides with the initialization time of current model run
                # current_time = np.datetime_as_string(self.hourly_ds.Time[0], unit="h")
                int_time = pd.to_datetime(
                    str(self.hourly_ds.Time.values[0] - np.timedelta64(1, "h"))
                )
                int_time = int_time.strftime("%Y-%m-%dT%H")
                previous_times = np.datetime_as_string(
                    previous_hourly_ds.Time, unit="h"
                )
                (index,) = np.where(previous_times == int_time)
                index = int(index[0])

                F = np.array(previous_hourly_ds.F[index])
                F = xr.DataArray(F, name="F", dims=("south_north", "west_east"))
                self.F = F
            elif self.initialize_hffmc == True:
                print(
                    f"{self.initialize_hffmc}: Initialize FFMC on date {int_time[0]}, with 85s"
                )
                # """ ################## Fine Fuel Moisture Code (FFMC) ##################### """
                F_o = self.F_initial  # Previous day's F becomes F_o
                F_o_full = np.full(self.shape, F_o, dtype=float)
                F = xr.DataArray(F_o_full, name="F", dims=("south_north", "west_east"))
                self.F = F
            else:
                raise ValueError(
                    f"Invalided initialize_hffmc option: {self.initialize_hffmc}. Only supports boolean inputs \n Please try with True or False :)"
                )

        elif timestep == "daily":
            previous_daily_ds = self.ds_retriever(int_time, timestep)
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

            # """ ####################   Carry over precipitation (r_o_previous)    ##################### """
            r_o_previous = np.array(previous_daily_ds.r_o_tomorrow[0])
            ### Add carry over rain to first time step
            self.daily_ds["r_o"][0] = self.daily_ds["r_o"][0] + np.array(r_o_previous)

            # """ ####################   Fine Fuel Moisture Code (FFMC)    ##################### """
            ### Get last time step of F that coincides with the
            ### initialization time of current model run
            F = np.array(previous_daily_ds.F[index])
            F = xr.DataArray(F, name="F", dims=("south_north", "west_east"))
            self.F = F

            # """ ####################   Duff Moisture Code (DCM)    ##################### """
            ### Get last time step of D that coincides with the
            ### initialization time of current model run
            P = np.array(previous_daily_ds.P[index])
            P = xr.DataArray(P, name="P", dims=("south_north", "west_east"))
            self.P = P

            # """ #####################     Drought Code (DC)       ########################### """
            ### Get last time step of D that coincides with the
            ### initialization time of current model run
            D = np.array(previous_daily_ds.D[index])
            D = xr.DataArray(D, name="D", dims=("south_north", "west_east"))
            self.D = D

            if self.overwinter == True:
                # """ #####################    Fall Drought Code (DC)       ########################### """
                ### Get last time step of Df that coincides with the
                ### initialization time of current model run
                Df = np.array(previous_daily_ds.Df[index])
                Df = xr.DataArray(Df, name="Df", dims=("south_north", "west_east"))
                self.Df = Df

                # """ #####################     Winter Rain Fall (r_w)       ########################### """
                ### Get last time step of r_w that coincides with the
                ### initialization time of current model run
                r_w = np.array(previous_daily_ds.r_w[index])
                r_w = xr.DataArray(r_w, name="r_w", dims=("south_north", "west_east"))
                self.r_w = r_w

                # """ #####################     Fire Season Mask (FSy)       ########################### """
                ### Get last time step of FS that coincides with the
                ### initialization time of current model run
                FSy = np.array(previous_daily_ds.FS[index])
                FSy = xr.DataArray(FSy, name="FSy", dims=("south_north", "west_east"))
                self.FSy = FSy

                # """ #####################     Fire Season Day (FS_days)     ########################### """
                ### Get last time step of FS_days that coincides with the
                ### initialization time of current model run
                FS_days = np.array(previous_daily_ds.FS_days[index])
                FS_days = xr.DataArray(
                    FS_days, name="FS_days", dims=("south_north", "west_east")
                )
                self.FS_days = FS_days

            else:
                pass

        else:
            raise ValueError(
                f"ERROR: {timestep} is not a valid option for timestep, only hourly or daily are supported at this time. If you want sub-hourly let me know and I will try tyo add this feature :)"
            )

        if self.overwinter == True:
            self.FS_mask(self.int_ds.Time.values, "hourly")
        else:
            pass

        return

    def ds_retriever(self, int_time, timestep):
        domain = self.domain
        try:
            retrieve_time = pd.to_datetime(str(int_time[0] - np.timedelta64(1, "D")))
            retrieve_time = retrieve_time.strftime("%Y%m%d%H")

            int_file_dir = (
                str(self.iterator_dir) + f"/fwf-{timestep}-{domain}-{retrieve_time}.nc"
            )
            previous_int_ds = xr.open_dataset(int_file_dir)
            print(
                f"{Path(int_file_dir).exists()}: Found previous moisture codes on date {retrieve_time}, will merge with int_ds"
            )
        except:
            try:
                retrieve_time = pd.to_datetime(
                    str(int_time[0] - np.timedelta64(2, "D"))
                )
                retrieve_time = retrieve_time.strftime("%Y%m%d%H")

                int_file_dir = (
                    str(self.iterator_dir)
                    + f"/fwf-{timestep}-{domain}-{retrieve_time}.nc"
                )

                previous_int_ds = xr.open_dataset(int_file_dir)
                print(
                    f"{Path(int_file_dir).exists()}: Found previous moisture codes on for two day forecast  {retrieve_time}, will merge with int_ds"
                )
            except:
                raise FileNotFoundError(
                    "ERROR: Can Not Find Previous dataset to initialize model, consider running with initialize as True"
                )
        return previous_int_ds

    def initializer(self, timestep):
        initialize = self.initialize
        shape = self.shape

        if initialize == True:
            int_time = np.array(self.int_ds.Time.dt.strftime("%Y-%m-%dT%H"))
            int_time = datetime.strptime(str(int_time[0]), "%Y-%m-%dT%H").strftime(
                "%Y%m%d%H"
            )
            print(f"{initialize}: Initialize FFMC on date {int_time}, with 85s")
            # """ ################## Fine Fuel Moisture Code (FFMC) ##################### """
            F_o = self.F_initial  # Previous day's F becomes F_o
            F_o_full = np.full(shape, F_o, dtype=float)
            F = xr.DataArray(F_o_full, name="F", dims=("south_north", "west_east"))
            self.F = F

            # """ ####################   Duff Moisture Code (DMC)    ##################### """
            print(f"{initialize}: Initialize DMC on date {int_time}, with 6s")
            P_o = self.P_initial
            P_o_full = np.full(shape, P_o, dtype=float)
            P = xr.DataArray(P_o_full, name="P", dims=("south_north", "west_east"))
            self.P = P

            # """ #####################     Drought Code (DC)       ########################### """
            print(f"{initialize}: Initialize DC on date {int_time}, with 15s")
            D_o = self.D_initial
            D_o_full = np.full(shape, D_o, dtype=float)
            D = xr.DataArray(D_o_full, name="D", dims=("south_north", "west_east"))
            self.D = D
            if self.overwinter == True:
                # """ #####################    Fall Drought Code (DC)       ########################### """
                print(f"{initialize}: Initialize DCf on date {int_time}, with 15s")
                D_f = self.D_initial
                D_f_full = np.full(shape, D_f, dtype=float)
                Df = xr.DataArray(
                    D_f_full, name="Df", dims=("south_north", "west_east")
                )
                self.Df = Df

                # """ #####################     Winter Rain Fall (r_w)       ########################### """
                print(f"{initialize}: Initialize r_w on date {int_time}, with zeros")
                r_w = np.full(shape, 0, dtype=float)
                r_w = xr.DataArray(r_w, name="r_w", dims=("south_north", "west_east"))
                self.r_w = r_w

                # """ #####################     Fire Season Mask (FSy)       ########################### """
                print(f"{initialize}: Initialize FSy on date {int_time}, with zeros")
                FSy = np.full(shape, 0, dtype=float)
                FSy = xr.DataArray(FSy, name="FSy", dims=("south_north", "west_east"))
                self.FSy = FSy

                # """ #####################     Fire Season Day (FS_days)     ########################### """
                print(f"{initialize}: Initialize FS_days on date {int_time}, with 30s")
                FS_days = np.full(shape, 30, dtype=float)
                FS_days = xr.DataArray(
                    FS_days, name="FS_days", dims=("south_north", "west_east")
                )
                self.FS_days = FS_days

            else:
                pass
            # """ #####################     Temperature Maximum (TMAX)       ########################### """
            print(
                f"{initialize}: Initialize TMAX on date {int_time}, with Max Temps on that date"
            )
            if self.overwinter == True:
                self.FS_mask(self.int_ds.Time.values, "hourly")
            else:
                pass

        elif initialize == False:

            self.iteration(timestep)

        else:
            raise ValueError(
                f"Invalided initialize option: {initialize}. Only supports boolean inputs \n Please try with True or False :)"
            )

        return

    """########################################################################"""
    """ ####### Creat and fire season mask and based on tmax condition ########"""
    """########################################################################"""

    def FS_mask(self, time_array, timestep):

        FSy = self.FSy
        r_w = self.r_w
        FS_days = self.FS_days

        XLAT = self.daily_ds.XLAT.values
        XLONG = self.daily_ds.XLONG.values

        ## define time slicing based on hourly or daily data
        if timestep == "daily":
            tslice = 0
        elif timestep == "hourly":
            tslice = slice(0, 24)
        else:
            raise ValueError(
                f"ERROR: {timestep} is not a valid option for timestep, only hourly or daily are supported at this time. If you want sub-hourly let me know and I will try tyo add this feature :)"
            )

        ## loop and try and open datasets from today to four days in the past
        previous_dss, days_of_max = [], []
        for i in range(4, -1, -1):
            retrieve_time_np = time_array[0] - np.timedelta64(i, "D")
            retrieve_time = pd.to_datetime(retrieve_time_np).strftime("%Y%m%d%H")
            try:
                if (self.model == "wrf") or (self.model == "eccc"):
                    int_file_dir = (
                        str(self.filein_dir)
                        + f"/{pd.to_datetime(retrieve_time_np).strftime('%Y%m')}/fwf-{timestep}-{self.domain}-{retrieve_time}.nc"
                    )
                    da = xr.open_dataset(int_file_dir)
                elif self.model == "ecmwf":
                    da = read_era5(
                        pd.to_datetime(retrieve_time_np), self.model, self.domain
                    )
                else:
                    raise ValueError("Bad model input")
                if i == 0:
                    da = da.chunk("auto").T
                else:
                    da = da.isel(time=tslice).chunk("auto").T
                previous_dss.append(da)
                days_of_max.append(retrieve_time_np.astype("datetime64[D]"))
            except:
                pass
        ## combine the dataset into one continuous dataarray
        cont_ds = xr.concat(
            previous_dss, dim="time", coords="minimal", compat="override"
        ).load()
        ## find all index of 00Z in the continuous dataarray based on the inital time
        time_array = cont_ds.Time.values
        int_time = int(pd.Timestamp(time_array[0]).hour)
        length = len(time_array) + 1
        num_days = [i for i in range(1, length) if i % 24 == 0]
        if int_time == 0:
            num_days = [0] + num_days
        else:
            pass
        index = [
            i - int_time if 12 - int_time >= 0 else i + 24 - int_time for i in num_days
        ]
        if (len(cont_ds.time) - index[-1]) < (24 + float(np.max(self.tzone))):
            if (len(cont_ds.time) - index[-1]) < (float(np.max(self.tzone))):
                index = index[:-2]
            else:
                index = index[:-1]
        else:
            pass

        print(f"index of 00Z times {index} with initial time {int_time}Z")
        ## loop every 00Z index and find daily max temps between local midnight to midnight using an array of utc offsets
        da_j_list = []
        for j in range(len(index)):
            da_i_list = []
            for i in range(index[j], index[j] + 24):
                ind_a = xr.DataArray(i + self.tzone, dims=["south_north", "west_east"])
                da_i = cont_ds.isel(time=ind_a)
                try:
                    da_i = da_i.drop(["time"])
                except:
                    pass
                da_i_list.append(da_i)
            da_j = xr.concat(da_i_list, dim="time").max(dim="time")
            da_j = da_j.assign_coords(
                {
                    "Time": days_of_max[j],
                    "XLAT": (("south_north", "west_east"), XLAT),
                    "XLONG": (("south_north", "west_east"), XLONG),
                }
            )
            da_j_list.append(da_j)

        TMAX_da = xr.concat(da_j_list, dim="time")

        ## apply a try condition for when data in the past doesn't exist
        ## TODO this is hacky, needs to be more robust for longer NWP forecast (only good for two day forecasts)
        try:
            TMAX_yesterday = (
                TMAX_da.isel(time=slice(0, 3))
                .max(dim="time")
                .assign_coords({"Time": days_of_max[-2]})
            )
            TMAX_today = (
                TMAX_da.isel(time=slice(1, 4))
                .max(dim="time")
                .assign_coords({"Time": days_of_max[-1]})
            )
            TMAX = xr.concat([TMAX_yesterday, TMAX_today], dim="time")
        except:
            TMAX = xr.concat(
                [
                    TMAX_da.assign_coords(
                        {"Time": days_of_max[0] - np.timedelta64(1, "D")}
                    ),
                    TMAX_da.assign_coords({"Time": days_of_max[0]}),
                ],
                dim="time",
            )
        if len(self.daily_ds.time) == 1:
            TMAX = xr.concat([TMAX_yesterday], dim="time")
        else:
            pass

        ## apply fire season onset condtions and create binary mask
        dFS_list, FS_list, r_w_list, FS_days_list = [], [], [], []
        for i in range(len(TMAX)):
            FS_days = FS_days + 1
            TMAXi = TMAX.isel(time=i)
            nan_full = np.full(TMAXi.shape, np.nan)
            # FSi = xr.where(TMAXi < 5, 1, nan_full)
            # FSi = xr.where(TMAXi > 12, 0, FSi)
            FSi = xr.where((TMAXi < 5) & (FS_days > 30), 1, nan_full)
            FSi = xr.where((TMAXi > 12) & (FS_days > 30), 0, FSi)

            ## take dif of yesterdays FS mask minus intermediate FS mask
            dFS = FSy - FSi
            dFS = xr.DataArray(dFS, name="dFS", dims=("south_north", "west_east"))
            dFS_list.append(dFS)

            FS_days = np.where((dFS == -1) | (dFS == 1), 0, FS_days)
            FS_days = xr.DataArray(
                FS_days, name="FS_days", dims=("south_north", "west_east")
            )
            FS_days_list.append(FS_days)

            ## create todays FS binary mask
            FS = xr.where(dFS == -1, 1, FSy)
            FS = xr.where(dFS == 1, 0, FS)
            FS = xr.DataArray(FS, name="FS", dims=("south_north", "west_east"))
            FS_list.append(FS)

            ## replace FSy with FS for next day's forecast
            FSy = FS

            ## accumualte preciptaiton on model grids that are in winter
            r_w = r_w + self.daily_ds["r_o"].isel(time=i)

            ## Apply dFS mask to zero out r_w if winter oneset occured
            # r_w = np.where(dFS == -1, 0, r_w)
            r_w = np.where((dFS == -1) | (dFS == 1), 0, r_w)

            ## create dataarray of winter accumulated preciptaiton
            r_w = xr.DataArray(r_w, name="r_w", dims=("south_north", "west_east"))
            r_w_list.append(r_w)

        dFS = xr.concat(dFS_list, dim="time")
        FS = xr.concat(FS_list, dim="time")
        FS_days = xr.concat(FS_days_list, dim="time")
        r_w = xr.concat(r_w_list, dim="time")

        self.daily_ds["TMAX"] = TMAX
        self.daily_ds["dFS"] = dFS
        self.daily_ds["FS"] = FS
        self.daily_ds["FS_days"] = FS_days
        self.daily_ds["r_w"] = r_w

        return

    """########################################################################"""
    """ #################### Fine Fuel Moisture Code #########################"""
    """########################################################################"""

    def solve_hourly_ffmc(self, hourly_ds):

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
        W, T, H, r_o, F_o = (
            hourly_ds.W,
            hourly_ds.T,
            hourly_ds.H,
            hourly_ds.r_o_hourly,
            self.F,
        )
        # maskTime = datetime.now()
        # landmask = self.landmask
        # W, T, H, r_o, F_o = (
        #     hourly_ds.W.to_masked_array(),
        #     hourly_ds.T.to_masked_array(),
        #     hourly_ds.H.to_masked_array(),
        #     hourly_ds.r_o_hourly.to_masked_array(),
        #     self.F.to_masked_array(),
        # )
        # W.mask, T.mask, H.mask, r_o.mask, F_o.mask = landmask, landmask, landmask, landmask, landmask

        # #Eq. 1
        m_o = 147.2 * (101 - F_o) / (59.5 + F_o)

        ########################################################################
        ### Solve for the effective rainfall routine (r_f)
        r_f = np.where(r_o > 0.5, (r_o - 0.5), np.where(r_o < 1e-7, 1e-5, r_o))

        ########################################################################
        ### (1) Solve the Rainfall routine as defined in  Van Wagner 1985 (m_r)
        m_o = np.where(
            m_o <= 150,
            m_o
            + (42.5 * r_f * np.exp((-100 / (251 - m_o))) * (1 - np.exp((-6.93 / r_f)))),
            m_o
            + (42.5 * r_f * np.exp((-100 / (251 - m_o))) * (1 - np.exp((-6.93 / r_f))))
            + (0.0015 * np.power((m_o - 150), 2) * np.power(r_f, 0.5)),
        )

        m_o = np.where(m_o > 250, 250, np.where(m_o < 0, 0.1, m_o))
        #

        ########################################################################
        ### (2a) Solve Equilibrium Moisture content for drying (E_d)

        E_d = (
            0.942 * np.power(H, 0.679)
            + 11 * np.exp((H - 100) / 10)
            + 0.18 * (21.1 - T) * (1 - np.exp((-0.115 * H)))
        )

        ########################################################################
        ### (2b) Solve Equilibrium Moisture content for wetting (E_w)

        E_w = (
            0.618 * (np.power(H, 0.753))
            + 10 * np.exp((H - 100) / 10)
            + 0.18 * (21.1 - T) * (1 - np.exp((-0.115 * H)))
        )

        ########################################################################
        ### (3a) intermediate step to k_d (k_a)
        k_a = 0.424 * (1 - np.power(H / 100, 1.7)) + 0.0694 * (np.power(W, 0.5)) * (
            1 - np.power(H / 100, 8)
        )

        ########################################################################
        ### (3b) Log drying rate for hourly computation, log to base 10 (k_d)
        k_d = 0.0579 * k_a * np.exp(0.0365 * T)

        ########################################################################
        ### (4a) intermediate steps to k_w (k_b)
        k_b = 0.424 * (1 - np.power(((100 - H) / 100), 1.7)) + 0.0694 * np.power(
            W, 0.5
        ) * (1 - np.power(((100 - H) / 100), 8))

        ########################################################################
        ### (4b)  Log wetting rate for hourly computation, log to base 10 (k_w)
        k_w = 0.0579 * k_b * np.exp(0.0365 * T)

        ########################################################################
        ### (5a) intermediate dry moisture code (m_d)
        m_d = E_d + ((m_o - E_d) * np.exp(-2.303 * (k_d)))

        ########################################################################
        ### (5b) intermediate wet moisture code (m_w)
        m_w = E_w - ((E_w - m_o) * np.exp(-2.303 * (k_w)))

        ########################################################################
        ### (5c) combine dry, wet, neutral moisture codes
        m = np.where(m_o > E_d, m_d, m_w)
        m = np.where((E_d >= m_o) & (m_o >= E_w), m_o, m)

        ########################################################################
        ### (6) Solve for FFMC
        F = (59.5 * (250 - m)) / (147.27723 + m)  ## Van 1985
        F = np.where(F < 0, 1.0, F)

        ## Recast initial moisture code for next time stamp
        # m_o = 147.27723 * (101 - F) / (59.5 + F)  ## Van 1985

        m_o = xr.DataArray(m_o, name="m_o", dims=("south_north", "west_east"))
        F = xr.DataArray(F, name="F", dims=("south_north", "west_east"))
        # F = F.to_dataset(name="F")

        # F["m_o"] = m_o
        F_ds = F.to_dataset(name="F")
        F_ds["m_o"] = m_o
        self.F = F
        # self.m_o =

        ### Return dataarray
        return F_ds

    def solve_ffmc(self, daily_ds):

        W, T, H, r_o, F_o = (
            daily_ds.W,
            daily_ds.T,
            daily_ds.H,
            daily_ds.r_o,
            self.F,
        )

        if self.overwinter == True:
            dFS = daily_ds.dFS
            ## Apply delta FS mask to initalize F with the default start up values F_initial  (dFS = 1 mean onset of summer)
            F_o = np.where(dFS == 1, self.F_initial, F_o)
        else:
            pass
        # #Eq. 1
        m_o = 147.2 * (101 - F_o) / (59.5 + F_o)

        ########################################################################
        ### Solve for the effective raut
        r_f = np.where(r_o > 0.5, (r_o - 0.5), np.where(r_o < 1e-7, 1e-5, r_o))

        ########################################################################
        ### (1) Solve the Rautfagner 1985 (m_r)
        m_o = np.where(
            m_o <= 150,
            m_o
            + (42.5 * r_f * np.exp((-100 / (251 - m_o))) * (1 - np.exp((-6.93 / r_f)))),
            m_o
            + (42.5 * r_f * np.exp((-100 / (251 - m_o))) * (1 - np.exp((-6.93 / r_f))))
            + (0.0015 * np.power((m_o - 150), 2) * np.power(r_f, 0.5)),
        )

        m_o = np.where(m_o > 250, 250, np.where(m_o < 0, 0.1, m_o))

        ########################################################################
        ### (2a) Solve Equilibrium Moisture content for dry

        E_d = (
            0.942 * np.power(H, 0.679)
            + 11 * np.exp((H - 100) / 10)
            + 0.18 * (21.1 - T) * (1 - np.exp((-0.115 * H)))
        )

        ########################################################################
        ### (2b) Solve Equilibrium Moisture content for wett

        E_w = (
            0.618 * (np.power(H, 0.753))
            + 10 * np.exp((H - 100) / 10)
            + 0.18 * (21.1 - T) * (1 - np.exp((-0.115 * H)))
        )
        ########################################################################
        ### (3a) ate step to k_d (k_a)
        k_a = 0.424 * (1 - np.power(H / 100, 1.7)) + 0.0694 * (np.power(W, 0.5)) * (
            1 - np.power(H / 100, 8)
        )

        ########################################################################
        ### (3b) Log dry for hourly computation, log to base 10 (k_d)
        k_d = k_a * 0.581 * np.exp(0.0365 * T)

        ########################################################################
        ### (4a) ate steps to k_w (k_b)
        k_b = 0.424 * (1 - np.power(((100 - H) / 100), 1.7)) + 0.0694 * np.power(
            W, 0.5
        ) * (1 - np.power(((100 - H) / 100), 8))

        ########################################################################
        ### (4b)  Log wettfor hourly computation, log to base 10 (k_w)
        k_w = k_b * 0.581 * np.exp(0.0365 * T)

        ########################################################################
        ### (5a) ate dry moisture code (m_d)
        m_d = E_d + (m_o - E_d) * 10 ** (-k_d)

        ########################################################################
        ### (5b) ate wet moisture code (m_w)
        m_w = E_w - (E_w - m_o) * 10 ** (-k_w)

        ########################################################################
        ### (5c) combine dry, wet, neutral moisture codes
        m = np.where(m_o > E_d, m_d, m_w)
        m = np.where((E_d >= m_o) & (m_o >= E_w), m_o, m)

        ########################################################################
        ### (6) Solve for FFMC
        F = (59.5 * (250 - m)) / (147.2 + m)  ## Van 1985

        ########################################################################
        ## constrain F to be non negative
        F = np.where(F < 1, 1.0, F)
        F = xr.DataArray(F, name="F", dims=("south_north", "west_east"))
        self.F = F

        return F

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

        T, H, r_o, P_o, L_e = (
            daily_ds.T,
            daily_ds.H,
            daily_ds.r_o,
            self.P,
            self.L_e,
        )

        if self.overwinter == True:
            dFS = daily_ds.dFS
            ## Apply delta FS mask to initalize P with the default start up values P_initial  (dFS = 1 mean onset of summer)
            P_o = np.where(dFS == 1, self.P_initial, P_o)
        else:
            pass

        zero_full = self.zero_full
        ##  Constrain temp
        ##    - The log drying rate K is proportional to temperature, becoming negligible at about -1.1°C (Van Wagner 1985) .
        T = np.where(T < -1.1, -1.1, T)

        ########################################################################
        ### (11) Solve for the effective rain (r_e)
        r_e = (0.92 * r_o) - 1.27

        ########################################################################
        ### (12) NOTE Alteratered for more accurate calculation (Lawson 2008)
        M_o = 20 + 280 / np.exp(0.023 * P_o)

        ########################################################################
        ### (13a) Solve for coefficients b where P_o <= 33 (b_low)
        b_low = np.where(P_o <= 33, 100 / (0.5 + 0.3 * P_o), zero_full)

        ########################################################################
        ### (13b) Solve for coefficients b where 33 < P_o <= 65 (b_mid)

        b_mid = np.where((P_o > 33) & (P_o <= 65), 14 - 1.3 * np.log(P_o), zero_full)

        ########################################################################
        ### (13c) Solve for coefficients b where  P_o > 65 (b_high)

        b_high = np.where(P_o > 65, 6.2 * np.log(P_o) - 17.2, zero_full)
        ########################################################################
        ### Combine (13a 13b 13c) for coefficients b
        b = b_low + b_mid + b_high

        ########################################################################
        ### (14) Solve for moisture content
        M_r = M_o + 1000 * r_e / (48.77 + b * r_e)

        ########################################################################
        ### (15) Duff moisture code (P_r) Alteration more accurate calculation (Lawson 2008)
        P_r = 43.43 * (5.6348 - np.log(M_r - 20))
        ## Apply rain condition if precip is less than 2.8 then use yesterday's DC
        P_r = np.where(r_o <= 1.5, P_o, P_r)
        P_r = np.where(P_r < 0, 0, P_r)

        ########################################################################
        ### (16) Log drying rate (K)
        K = (
            1.894 * (T + 1.1) * (100 - H) * (L_e * 1e-4)
        )  ## NOTE they use 1e-04 in the R but in the paper is 1e-06 code not sure what to use.

        ########################################################################
        ### (17) Duff moisture
        P = P_r + K

        ########################################################################
        ## constrain P to default start up and convert to dataarray
        P = np.where(P < self.P_initial, self.P_initial, P)
        P = xr.DataArray(P, name="P", dims=("south_north", "west_east"))

        self.P = P
        return P

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
        T, r_o, L_f, = (
            daily_ds.T,
            daily_ds.r_o,
            self.L_f,
        )
        if self.overwinter == True:
            D_o, Df = self.overwinter_dc(daily_ds)
        else:
            D_o = self.D

        ##  Constrain temp
        ##    - The log drying rate K is proportional to temperature, becoming negligible at about -2.8°C (Van Wagner 1985) .
        T = np.where(T < (-2.8), -2.8, T)

        ########################################################################
        ### (18) Solve for the effective rain (r_d)
        r_d = 0.83 * r_o - 1.27

        ########################################################################
        ### (19) Solve for initial moisture equivalent (Q_o)
        Q_o = 800 * np.exp(-1 * D_o / 400)

        ########################################################################
        ### (20) Solve for moisture equivalent (Q_r)
        Q_r = Q_o + 3.937 * r_d

        ########################################################################
        ### (21) Solve for DC after rain (D_r)
        ## Alteration to Eq. 21 (Lawson 2008)
        D_r = D_o - 400 * np.log(1 + 3.937 * r_d / Q_o)
        # D_r = 400 * np.log(800 / Q_r)
        D_r = np.where(D_r < 0, 0.0, D_r)
        D_r = np.where(r_o <= 2.8, D_o, D_r)

        ########################################################################
        ### (22) Solve for potential evapotranspiration (V)
        V = (0.36 * (T + 2.8)) + L_f
        V = np.where(V < 0, 0.0, V)

        ########################################################################
        ## Alteration to Eq. 23 (Lawson 2008)
        D = D_r + V * 0.5

        ########################################################################
        ## constrain P to default start up and convert to dataarray
        D = np.where(D < self.D_initial, self.D_initial, D)
        D = xr.DataArray(D, name="D", dims=("south_north", "west_east"))

        self.D = D
        if self.overwinter == True:
            self.Df = Df
        else:
            Df = None

        return D, Df

    """########################################################################"""
    """ ###################### Overwinter Drought Code ########################"""
    """########################################################################"""

    def overwinter_dc(self, daily_ds):
        Df, D, r_w, dFS = (self.Df, self.D, daily_ds.r_w, daily_ds.dFS)
        ## TODO update coefficients, these are the defaults as suggested by Lawson and Armitage (2008) and Anderson and Otway (2003)
        a, b = 1, 0.75

        ## Eq. 3 - Final fall moisture equivalent of the DC
        Qf = 800 * np.exp(-Df / 400)
        ## Eq. 2 - Starting spring moisture equivalent of the DC
        Qs = a * Qf + b * (3.94 * r_w)

        ## Eq. 4 - Spring start-up value for the DC
        Ds = 400 * np.log(800 / Qs)

        ## Apply delta FS mask to fill Ds at start up locations (dFS = 1 mean onset of summer)
        D = np.where(dFS == 1, Ds, D)

        ## Constrain DC and make into DataArray
        D = np.where(D < self.D_initial, self.D_initial, D)
        D = xr.DataArray(D, name="D", dims=("south_north", "west_east"))

        ## Apply delta FS mask to save D as Df if winter onset occurred (dFS = -1 mean onset of winter)
        Df = np.where(dFS == -1, D, Df)
        Df = xr.DataArray(Df, name="Df", dims=("south_north", "west_east"))

        return D, Df

    """########################################################################"""
    """ #################### Initial Spread Index #############################"""
    """########################################################################"""

    def solve_isi(self, hourly_ds, W, fbp=False):
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
        W, F = W, hourly_ds.F

        # #Eq. 1
        m_o = 147.2 * (101 - F) / (59.5 + F)

        ########################################################################
        ### (24) Solve for wind function (f_W) with condition for fbp
        f_W = np.where(
            (W >= 40) & (fbp == True),
            12 * (1 - np.exp(-0.0818 * (W - 28))),
            np.exp(0.05039 * W),
        )

        ########################################################################
        ### (25) Solve for fine fuel moisture function (f_F)
        f_F = 91.9 * np.exp(-0.1386 * m_o) * (1 + np.power(m_o, 5.31) / 4.93e7)

        ########################################################################
        ### (26) Solve for initial spread index (R)
        R = 0.208 * f_W * f_F
        R = xr.DataArray(R, name="R", dims=("time", "south_north", "west_east"))

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

        ### Call on initial conditions
        P, D = daily_ds.P, daily_ds.D
        zero_full = self.zero_full

        ########################################################################
        ### (27a and 27b) Solve for build up index where P =< 0.4D (U_a)
        U_low = np.where(P <= 0.4 * D, 0.8 * P * D / (P + (0.4 * D)), zero_full)

        U_high = np.where(
            P > 0.4 * D,
            P - (1 - 0.8 * D / (P + (0.4 * D))) * (0.92 + np.power((0.0114 * P), 1.7)),
            zero_full,
        )

        U = U_low + U_high
        U = np.where(U < 0, 1.0, U)
        U = xr.DataArray(U, name="U", dims=("time", "south_north", "west_east"))

        return U

    """########################################################################"""
    """ ###################### Fire Weather Index #############################"""
    """########################################################################"""

    def solve_fwi(self, hourly):

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
        ### (28 & 29) Solve for duff moisture function where U =< 80(f_D_a)
        # U_limit = 80
        f_D = np.where(
            U > 80,
            1000 / (25 + 108.64 * np.exp(-0.023 * U)),
            (0.626 * np.power(U, 0.809)) + 2,
        )

        ########################################################################
        if hourly == True:
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
                    "ERROR: Rodell was lazy and needs to rethink indexing of multi length nwp runs, he will bet better in the next version!"
                )
        else:
            B = 0.1 * R * f_D

        #### HOPEFULLY SOLVES RUNTIME WARNING
        B = np.where(B > 0, B, 1e-6)

        ########################################################################
        ### (30) Solve FWI
        S = np.where(B <= 1, B, np.exp(2.72 * np.power((0.434 * np.log(B)), 0.647)))

        S = xr.DataArray(S, name="S", dims=("time", "south_north", "west_east"))

        ########################################################################
        ### (31) Solve for daily severity rating (DSR)
        DSR = 0.0272 * np.power(S, 1.77)
        DSR = xr.DataArray(DSR, name="DSR", dims=("time", "south_north", "west_east"))

        return S, DSR

    def solve_fbp(self, hourly_ds):
        """
        Solves the Fire Behavior Predictions System at hourly intervals

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
        hourly_ds: DataSet
            - Datarray of
                - FMC: DataArray
                    - Foliar Moisture Content, %
                - SFC: DataArray
                    - Surface Fuel Consumption, kg m^{-2}
                - TFC: DataArray
                    - Total Fuel Consumption, kg m^{-2}
                - CFB: DataArray
                    - Crown Fraction Burned, %
                - ROS: DataArray
                    - Rate of Spread, m min^{-1}
                - HFI: DataArray
                    - Head Fire Intensity, kW m^{-1}
        """
        FBPloopTime = datetime.now()
        print("Start of FBP")
        ## Open fuels converter
        hourly_ds = self.rechunk(hourly_ds)
        ELV, LAT, LON, FUELS, GS, SAZ, PC = (
            self.ELV,
            self.LAT,
            self.LON,
            self.FUELS,
            self.GS,
            self.SAZ,
            self.PC,
        )
        unique = np.unique(FUELS)

        fc_df = pd.read_csv(str(data_dir) + "/fbp/fuel_converter.csv")
        fc_df = fc_df.drop_duplicates(subset=["CFFDRS"])
        fc_df["Code"] = fc_df["FWF_Code"]
        drop_fuels = list(set(fc_df["Code"].values) - set(unique))
        for code in drop_fuels:
            fc_df = fc_df[fc_df["Code"] != code]
        fc_df.loc[fc_df["CFFDRS"] == "M1 C25%", "CFFDRS"] = "M1"
        fc_df = fc_df[~fc_df["CFFDRS"].str.contains("M1/")]
        fc_df = fc_df.set_index("CFFDRS")
        fc_dict = fc_df.transpose().to_dict()

        daily_ds = self.daily_ds
        daily_ds = self.rechunk(daily_ds)

        ## Define new wind direction varible
        WD = hourly_ds.WD

        zero_full3D, zero_full = (
            np.zeros(hourly_ds.F.shape, dtype=float),
            self.zero_full,
        )
        ## Convert Wind Direction from degrees to radians
        WD = WD * np.pi / 180

        ## Reorient to Wind Azimuth (WAZ)
        WAZ = WD + np.pi
        WAZ = np.where(WAZ > 2 * np.pi, WAZ - 2 * np.pi, WAZ)
        print("WAZ", type(WAZ))
        ###################    Foliar Moisture Content:  #######################
        ########################################################################
        ## Solve Normalized latitude (degrees) with terrain data (3)
        LATN = 43 + 33.7 * np.exp(-0.0351 * (150 - LON))

        ## Solve Julian date of minimum FMC with terrain data (4)
        D_o = 142.1 * (LAT / LATN) + 0.0172 * ELV

        ## Get day of year or Julian date
        date = pd.Timestamp(self.date)

        D_j = int(date.strftime("%j"))

        ## Solve Number of days between the current date and D_o (5)
        ND = abs(D_j - D_o)

        ## Solve Foliar moisture content(%) where ND < 30 (6)
        FMC = zero_full
        FMC = np.where(ND < 30.0, 85 + 0.0189 * ND ** 2, FMC)
        ## Solve Foliar moisture content(%) where 30 <= ND < 50 (7)
        FMC = np.where((ND >= 30) & (ND < 50), 32.9 + 3.17 * ND - 0.0288 * ND ** 2, FMC)
        ## Solve Foliar moisture content(%) where ND >= 50 (8)
        FMC = np.where(ND >= 50, 120, FMC)
        FMC = xr.DataArray(FMC, name="FMC", dims=("south_north", "west_east"))
        hourly_ds["FMC"] = FMC.astype(dtype="float32")

        ###################    Surface Fuel Consumption  #######################
        ########################################################################
        ## Define frequently used variables
        FFMC, BUI, GFL, PH = hourly_ds.F, daily_ds.U, 0.3, 50
        index = [i for i in range(1, len(FFMC) + 1) if i % 24 == 0]
        ## Build a BUI datarray fo equal length to hourly forecast bisecting is by day
        BUI_i = BUI.values
        try:
            BUI_day1 = np.stack([BUI_i[0]] * index[0])
            BUI_day2 = np.stack([BUI_i[1]] * (len(FFMC) - index[0]))
            BUI = np.vstack([BUI_day1, BUI_day2])
        except:
            BUI = np.stack([BUI_i[0]] * len(FFMC))
            print(len(BUI))

        BUI = xr.DataArray(BUI, name="BUI", dims=("time", "south_north", "west_east"))
        # hourly_ds["BUI"] = BUI

        ## Solve Surface Fuel Consumption for C1 Fuels adjusted from (Wotton et. al. 2009) (9)
        SFC = zero_full3D
        SFC = np.where(
            FUELS == fc_dict["C1"]["Code"],
            np.where(
                FFMC > 84,
                0.75 + 0.75 * (1 - np.exp(-0.23 * (FFMC - 84))) ** 0.5,
                0.75 - 0.75 * (1 - np.exp(-0.23 * (84 - FFMC))) ** 0.5,
            ),
            SFC,
        )

        ## Solve Fuel Consumption for C2, M3, and M4 Fuels  (10)
        SFC = np.where(
            (FUELS == fc_dict["C2"]["Code"]),
            # | (FUELS == fc_dict["M3"]["Code"])
            # | (FUELS == fc_dict["M4"]["Code"]),
            5.0 * (1 - np.exp(-0.0115 * BUI)),
            SFC,
        )

        ## Solve Fuel Consumption for C3, C4 Fuels  (11)
        SFC = np.where(
            (FUELS == fc_dict["C3"]["Code"]) | (FUELS == fc_dict["C4"]["Code"]),
            5.0 * (1 - np.exp(-0.0164 * BUI)) ** 2.24,
            SFC,
        )

        ## Solve Fuel Consumption for C5, C6 Fuels  (12)
        SFC = np.where(
            (FUELS == fc_dict["C5"]["Code"]) | (FUELS == fc_dict["C6"]["Code"]),
            5.0 * (1 - np.exp(-0.0149 * BUI)) ** 2.48,
            SFC,
        )

        ## Solve Fuel Consumption for C7 Fuels  (13, 14, 15)
        SFC = np.where(
            (FUELS == fc_dict["C7"]["Code"]),
            np.where(FFMC > 70, 2 * (1 - np.exp(-0.104 * (FFMC - 70))), 0)
            + 1.5 * (1 - np.exp(-0.0201 * BUI)),
            SFC,
        )

        ## Solve Fuel Consumption for D1 Fuels  (16)
        SFC = np.where(
            (FUELS == fc_dict["D1"]["Code"]), 1.5 * (1 - np.exp(-0.0183 * BUI)), SFC
        )

        ## Solve Fuel Consumption for M1, M2 Fuels  (17)
        SFC = np.where(
            (FUELS == fc_dict["M1"]["Code"]),  # | (FUELS == fc_dict["M2"]["Code"]),
            PC / 100 * (5.0 * (1 - np.exp(-0.0115 * BUI)))
            + ((100 - PC) / 100 * (1.5 * (1 - np.exp(-0.0183 * BUI)))),
            SFC,
        )

        ## Solve Fuel Consumption for O1a, O1b Fuels  (18)
        SFC = np.where(
            (FUELS == fc_dict["O1a"]["Code"]) | (FUELS == fc_dict["O1b"]["Code"]),
            GFL,
            SFC,
        )

        # ## Solve Fuel Consumption for S1 Fuels  (19, 20, 25)
        # SFC = np.where(
        #     (FUELS == fc_dict["S1"]["Code"]),
        #     4.0 * (1 - np.exp(-0.025 * BUI)) + 4.0 * (1 - np.exp(-0.034 * BUI)),
        #     SFC,
        # )

        # ## Solve Fuel Consumption for S2 Fuels  (21, 22, 25)
        # SFC = np.where(
        #     (FUELS == fc_dict["S2"]["Code"]),
        #     10.0 * (1 - np.exp(-0.013 * BUI)) + 6.0 * (1 - np.exp(-0.060 * BUI)),
        #     SFC,
        # )

        # ## Solve Fuel Consumption for S3 Fuels  (23, 24, 25)
        # SFC = np.where(
        #     (FUELS == fc_dict["S3"]["Code"]),
        #     12.0 * (1 - np.exp(-0.0166 * BUI)) + 20.0 * (1 - np.exp(-0.0210 * BUI)),
        #     SFC,
        # )

        # Remove negative SFC value
        SFC = np.where(SFC <= 0, 0.01, SFC)
        SFC = xr.DataArray(SFC, name="SFC", dims=("time", "south_north", "west_east"))
        hourly_ds["SFC"] = SFC.astype(dtype="float32")

        ## Define frequently used variables
        PDF = 35  # percent dead balsam fir default
        C = 80  # degree of curing(%)
        # ISI = hourly_ds.R
        ISZ = self.solve_isi(hourly_ds, W=0, fbp=True)
        # hourly_ds["ISZ"] = ISZ.astype(dtype="float32")

        ## (O-1A grass) grass curing coefficient (Wotton et. al. 2009)
        CF = np.where(
            C < 58.8, 0.005 * (np.exp(0.061 * C) - 1), 0.176 + 0.02 * (C - 58.8)
        )

        ## General Rate of Spread Equation for C-1 to C-5, and C-7 (26)
        def solve_gen_ros(ROS, fueltype, ISI):
            ROS = np.where(
                FUELS == fc_dict[fueltype]["Code"],
                fc_dict[fueltype]["a"]
                * (
                    (1 - np.exp(-fc_dict[fueltype]["b"] * ISI))
                    ** fc_dict[fueltype]["c"]
                ),
                ROS,
            )
            return ROS

        ## General Rate of Spread Equation for C-1 to C-5, and C-7 (26)
        # def solve_gen_ros(ROS, fueltype, ISI):
        #     func = lambda ROS, fueltype, ISI: np.where(FUELS == fc_dict[fueltype]["Code"],
        #                                     fc_dict[fueltype]["a"]
        #                                     * (
        #                                         (1 - np.exp(-fc_dict[fueltype]["b"] * ISI))
        #                                         ** fc_dict[fueltype]["c"]
        #                                     ),
        #                                     ROS,
        #                                 )
        #     return xr.apply_ufunc(func, ROS, fueltype, ISI)

        def solve_M_ros(fueltype, ISI):
            ROS = fc_dict[fueltype]["a"] * (
                (1 - np.exp(-fc_dict[fueltype]["b"] * ISI)) ** fc_dict[fueltype]["c"]
            )
            return ROS

        def solve_ros(ISI, FMC, PDF, fc_dict, *args):
            # ##  (M-3)
            # fc_dict["M3"]["a"] = 170 * np.exp(-35.0 / PDF)  # (29)
            # fc_dict["M3"]["b"] = 0.082 * np.exp(-36 / PDF)  # (30)
            # fc_dict["M3"]["c"] = 1.698 - 0.00303 * PDF  # (31)

            # ##  (M-4)
            # fc_dict["M4"]["a"] = 140 * np.exp(-35.5 / PDF)  # (22)
            # fc_dict["M4"]["b"] = 0.0404  # (33)
            # fc_dict["M4"]["c"] = 3.02 * np.exp(-0.00714 * PDF)  # (34)

            ROS = zero_full3D
            for fueltype in [
                "C1",
                "C2",
                "C3",
                "C4",
                "C5",
                "C7",
                "D1",
                # "S1",
                # "S2",
                # "S3",
                # "M3",
                # "M4",
            ]:
                ROS = solve_gen_ros(ROS, fueltype, ISI)

            ## Fuel Type Specific Rate of Spread Equations
            ##  (M-1 leaftess) (27)
            ROS_M1 = np.where(
                FUELS == fc_dict["M1"]["Code"],
                ((PC / 100) * solve_M_ros("C2", ISI))
                + ((PC / 100) * solve_M_ros("D1", ISI)),
                zero_full3D,
            )

            # ##  (M-2 green)   (28)
            # ROS_M2 = np.where(
            #     FUELS == fc_dict["M2"]["Code"],
            #     ((PC / 100) * solve_M_ros("C2", ISI))
            #     + (0.2 * ((PC / 100) * solve_M_ros("D1", ISI))),
            #     zero_full3D,
            # )

            ROS_O1a = np.where(
                (FUELS == fc_dict["O1a"]["Code"]),
                fc_dict["O1a"]["a"]
                * ((1 - np.exp(-fc_dict["O1a"]["b"] * ISI)) ** fc_dict["O1a"]["c"])
                * CF,
                zero_full3D,
            )

            ## (O-1B grass) grass curing coefficient (Wotton et. al. 2009)
            ROS_O1b = np.where(
                (FUELS == fc_dict["O1b"]["Code"]),
                fc_dict["O1b"]["a"]
                * ((1 - np.exp(-fc_dict["O1b"]["b"] * ISI)) ** fc_dict["O1b"]["c"])
                * CF,
                zero_full3D,
            )
            if args:
                ## Surface spread rate
                ROS = ROS + ROS_M1 + ROS_O1a + ROS_O1b
                # ROS = ROS + ROS_M1 + ROS_M2 + ROS_O1a + ROS_O1b
                ROS = ROS * BE
            else:
                ROS = ROS + ROS_M1 + ROS_O1a + ROS_O1b
                # ROS = ROS + ROS_M1 + ROS_M2 + ROS_O1a + ROS_O1b

            return ROS

        def solve_c6(ISI, FMC, fc_dict, *args):
            ##  (C-6) Conifer plantation spread rate
            T = 1500 - 2.75 * FMC  # (59)
            h = 460 + 25.9 * FMC  # (60)
            FME = (((1.5 - 0.00275 * FMC) ** 4.0) / (460 + (25.9 * FMC))) * 1000  # (61)

            ROS_C6 = np.where(
                (FUELS == fc_dict["C6"]["Code"]),
                30 * (1 - np.exp(-0.08 * ISI)) ** 3.0,
                zero_full3D,
            )

            if args:
                ## (63)
                RSS = ROS_C6 * BE
                ## (64)
                RSC = np.where(
                    (FUELS == fc_dict["C6"]["Code"]),
                    60 * (1 - np.exp(-0.0497 * ISI)) ** 1.0 * (FME / 0.778),
                    zero_full3D,
                )
                ## (56)
                CSI = 0.001 * (fc_dict["C6"]["CBH"] ** 1.5) * (460 + 25.9 * FMC) ** 1.5
                ## (57)
                RSO = CSI / (300 * SFC)
                RSO = xr.DataArray(
                    np.transpose(RSO.values, (2, 0, 1)),
                    name="RSO",
                    dims=("time", "south_north", "west_east"),
                )

                ## (58)
                CFB = np.where(RSS > RSO, 1 - np.exp(-0.23 * (RSS - RSO)), 0)
                CFB = np.where(CFB < 0, 0.0, CFB)
                # CFB = 1 - np.exp(-0.23 * (ROS_C6 - RSO))
                ## (65)
                ROS = np.where(
                    FUELS == fc_dict["C6"]["Code"], RSS + CFB * (RSC - RSS), zero_full3D
                )
            else:
                ROS = ROS_C6

            return ROS

        ## Surface spread rate with zero wind on level terrain
        RSZ = solve_ros(ISZ, FMC, PDF, fc_dict)
        RSZ_C6 = solve_c6(ISZ, FMC, fc_dict)
        RSZ = RSZ + RSZ_C6
        # hourly_ds["RSZ"] = RSZ

        ###################   Effect of Slope on Rate of Spread  #######################
        ################################################################################
        WS = hourly_ds.W

        ## Solve Factor, Upslope (39)
        ## NOTE they use have another condition in the R code: if GS >= 70 SF = 10
        ## Also they don't have the GS<60 condition in the code..not sure why
        SF = np.where(GS < 60, np.exp(3.533 * ((GS / 100) ** 1.2)), zero_full)

        ## Surface spread rate with zero wind, upslope (40)
        RSF = RSZ * SF
        # hourly_ds["RSF"] = RSF.astype(dtype="float32")

        ## Solve ISF (ie ISI, with zero wind upslope) for the majority of fuels (41)
        ## NOTE adjusted base don 41a, 41b (Wotton 2009)
        def solve_isf(ISF, fueltype, RSF):
            ISF = np.where(
                FUELS == fc_dict[fueltype]["Code"],
                np.where(
                    (1 - (RSF / fc_dict[fueltype]["a"]) ** (1 / fc_dict[fueltype]["c"]))
                    >= 0.01,
                    np.log(
                        1
                        - (RSF / fc_dict[fueltype]["a"]) ** (1 / fc_dict[fueltype]["c"])
                    )
                    / -fc_dict[fueltype]["b"],
                    np.log(0.01) / -fc_dict[fueltype]["b"],
                ),
                ISF,
            )
            return ISF

        # def solve_isf(ISF, fueltype, RSF):
        #     func = lambda ISF, fueltype, RSF:  np.where(
        #         FUELS == fc_dict[fueltype]["Code"],
        #         np.where(
        #             (1 - (RSF / fc_dict[fueltype]["a"]) ** (1 / fc_dict[fueltype]["c"]))
        #             >= 0.01,
        #             np.log(
        #                 1
        #                 - (RSF / fc_dict[fueltype]["a"]) ** (1 / fc_dict[fueltype]["c"])
        #             )
        #             / -fc_dict[fueltype]["b"],
        #             np.log(0.01) / -fc_dict[fueltype]["b"],
        #         ),
        #         ISF,
        #     )
        #     return xr.apply_ufunc(func, ISF, fueltype, RSF)

        ISF = zero_full3D
        for fueltype in [
            "C1",
            "C2",
            "C3",
            "C4",
            "C5",
            "C6",
            "C7",
            "D1",
            # "S1",
            # "S2",
            # "S3",
        ]:
            ISF = solve_isf(ISF, fueltype, RSF)

        ## Solve ISF (ie ISI, with zero wind upslope) for M1 and M2 (42)
        ISF_M1M2 = np.where(
            (FUELS == fc_dict["M1"]["Code"]),  # | (FUELS == fc_dict["M2"]["Code"]),
            np.log(
                1
                - ((100 - RSF) / (PC * fc_dict["C2"]["a"])) ** (1 / fc_dict["C2"]["c"])
            )
            / -fc_dict["C2"]["b"],
            zero_full3D,
        )

        ## Solve ISF (ie ISI, with zero wind upslope) for O1a and O1b (grass)(43)
        ISF_O1a = np.where(
            (FUELS == fc_dict["O1a"]["Code"]),
            np.log(1 - (RSF / (CF * fc_dict["O1a"]["a"])) ** (1 / fc_dict["O1a"]["c"]))
            / -fc_dict["O1a"]["b"],
            zero_full3D,
        )

        ISF_O1b = np.where(
            (FUELS == fc_dict["O1b"]["Code"]),
            np.log(1 - (RSF / (CF * fc_dict["O1b"]["a"])) ** (1 / fc_dict["O1b"]["c"]))
            / -fc_dict["O1b"]["b"],
            zero_full3D,
        )

        ## Combine all ISFs (ie ISI, with zero wind upslope)
        ISF = ISF + ISF_M1M2 + ISF_O1a + ISF_O1b
        # hourly_ds["ISF"] = ISF.astype(dtype="float32")

        ### (25) Solve for fine fuel moisture function (f_F)
        m_o = hourly_ds.m_o
        f_F = 91.9 * np.exp(-0.1386 * m_o) * (1 + ((m_o ** 5.31) / 4.93e7))
        f_F = np.where(f_F < 0.0, 0.1, f_F)

        ## Compute the slope equivalent wind speed (WSE) (44)
        WSE = np.where(ISF > 0.1, np.log(ISF / (0.208 * f_F)) / 0.05039, zero_full3D)
        # print('WSE ',np.mean(WSE.values))

        # NOTE Adjusted Slope equivalent wind speed (44b 44e) (Wotton 2009)
        WSE = np.where(
            (WSE > 40) & (ISF < (0.999 * 2.496 * f_F)),
            28 - (1 / 0.0818 * np.log(1 - ISF / (2.496 * f_F))),
            WSE,
        )

        # NOTE Adjusted Slope equivalent wind speed (44c) (Wotton 2009)
        WSE = np.where((WSE > 40) & (ISF >= (0.999 * 2.496 * f_F)), 112.45, WSE)
        # print('WSE ',np.mean(WSE.values))

        ## Net vectored wind speed in the x-direction (47)
        WSX = (WS * np.sin(WAZ)) + (WSE * np.sin(SAZ * (np.pi / 180)))

        ## Net vectored wind speed in they-direction (48)
        WSY = (WS * np.cos(WAZ)) + (WSE * np.cos(SAZ * (np.pi / 180)))

        ## Net vectored wind speed (49)
        WSV = np.sqrt(WSX ** 2 + WSY ** 2)
        WSV = np.where((GS > 0) & (FFMC > 0), WSV, WS)

        ## Spread direction azimuth and convert from radians to degrees (50)
        RAZ = np.arccos(WSY / WSV) * 180 / np.pi
        ## Convert RAZ values at locations of negative WSX to account for the full compass circle. (51)
        RAZ = np.where(WSX < 0, 360 - RAZ, RAZ)

        ## Solve ISI equation (from the FWI System) (52, 53, 53a)
        ISI = self.solve_isi(hourly_ds, WSV, fbp=True)

        hourly_ds["ISI"] = ISI.astype(dtype="float32")

        ###########   BUI Effect on Surface Fire Rate of Spread  #############
        #######################################################################
        ## Buildup effect on spread rate (54)
        def solve_be(BE, fueltype, BUI):
            BE = np.where(
                FUELS == fc_dict[fueltype]["Code"],
                np.where(
                    (BUI > 0) & (fc_dict[fueltype]["BUI_o"] > 0),
                    np.exp(
                        50
                        * np.log(fc_dict[fueltype]["q"])
                        * ((1 / BUI) - (1 / fc_dict[fueltype]["BUI_o"]))
                    ),
                    1,
                ),
                BE,
            )
            return BE

        # def solve_be(BE, fueltype, BUI):
        #     func = lambda BE, fueltype, BUI: np.where(
        #         FUELS == fc_dict[fueltype]["Code"],
        #         np.where(
        #             (BUI > 0) & (fc_dict[fueltype]["BUI_o"] > 0),
        #             np.exp(
        #                 50
        #                 * np.log(fc_dict[fueltype]["q"])
        #                 * ((1 / BUI) - (1 / fc_dict[fueltype]["BUI_o"]))
        #             ),
        #             1,
        #         ),
        #         BE,
        #     )
        #     return xr.apply_ufunc(func, BE, fueltype, BUI)

        BE = zero_full3D
        for fueltype in fc_df.index.values[:-8]:
            BE = solve_be(BE, fueltype, BUI)

        ROS = solve_ros(ISI, FMC, PDF, fc_dict, BE)
        ROS_C6 = solve_c6(ISI, FMC, fc_dict, BE)
        ROS = ROS + ROS_C6
        ROS = np.where(ROS < 0, 0.0, ROS)
        ROS = xr.DataArray(ROS, name="ROS", dims=("time", "south_north", "west_east"))
        hourly_ds["ROS"] = ROS.astype(dtype="float32")

        ################   Critical Surface Fire Intensity  ###################
        #######################################################################

        def solve_cfb(CFB, ROS, fueltype, FMC):
            if fc_dict[fueltype]["CBH"] == -99:
                CFB = CFB
            else:
                ## Solve Critical surface intensity for crowning (56)
                CSI = (
                    0.001
                    * (fc_dict[fueltype]["CBH"] ** 1.5)
                    * (460 + 25.9 * FMC) ** 1.5
                )
                ## Solve Critical spread rate for crowning (57)
                RSO = CSI / (300 * SFC)
                # Solve Crown fraction burned (58)
                CFB_i = np.where(ROS > RSO, 1 - np.exp(-0.23 * (ROS - RSO)), CFB)
                # CFB_i = 1 - np.exp(-0.23 * (ROS - RSO))
                CFB_i = np.where(CFB_i < 0, 0.0, CFB_i)
                CFB = np.where(FUELS == fc_dict[fueltype]["Code"], CFB_i, CFB)
            return CFB

        CFB = zero_full3D
        for fueltype in fc_df.index.values[:-8]:
            CFB = solve_cfb(CFB, ROS, fueltype, FMC)
        CFB = xr.DataArray(CFB, name="CFB", dims=("time", "south_north", "west_east"))
        hourly_ds["CFB"] = CFB.astype(dtype="float32")

        #####################   Total Fuel Consumption  #######################
        #######################################################################

        def solve_tfc(TFC, fueltype, CFB):
            if fc_dict[fueltype]["CFL"] == -99:
                TFC = np.where(FUELS == fc_dict[fueltype]["Code"], SFC, TFC)
            else:
                CFC = fc_dict[fueltype]["CFL"] * CFB
                TFC = np.where(FUELS == fc_dict[fueltype]["Code"], SFC + CFC, TFC)
            return TFC

        TFC = zero_full3D
        for fueltype in fc_df.index.values[:-8]:
            TFC = solve_tfc(TFC, fueltype, CFB)
        TFC = xr.DataArray(TFC, name="TFC", dims=("time", "south_north", "west_east"))
        hourly_ds["TFC"] = TFC.astype(dtype="float32")

        #########################   Fire Intensity  ###########################
        #######################################################################

        HFI = 300 * TFC * ROS
        # print('HFI', np.max(HFI.values))
        HFI = xr.DataArray(HFI, name="HFI", dims=("time", "south_north", "west_east"))
        hourly_ds["HFI"] = HFI.astype(dtype="float32")
        print(f"End of FBP with run time of {datetime.now() - FBPloopTime}")

        return hourly_ds

    """########################################################################"""
    """ ###################### Create Daily Dataset ###########################"""
    """########################################################################"""

    def create_daily_ds(self, int_ds):
        """
        Creates a dataset of forecast variables averaged from
        (1100-1300) local to act as the noon local conditions for daily index/codes
        calculations

        Parameters
        ----------
            int_ds: DataSet
                WRF dataset at 4/12-km spatial resolution and one hour temporal resolution

        Returns
        -------
            daily_ds: DataSet
                Dataset of daily variables at noon local averaged from (1100-1300)
                local the averaging was done as a buffer for any frontal passage.
        """

        print("Create Daily ds")

        ### Call on variables
        tzone = self.tzone
        # correct for places on int dateline
        tzone[tzone <= -12] *= -1

        ## create I, J for quick indexing
        I, J = np.ogrid[: self.shape[0], : self.shape[1]]

        ## determine index for looping based on length of time array and initial time
        time_array = int_ds.Time.values
        print(time_array[0])
        int_time = int(pd.Timestamp(time_array[0]).hour)
        length = len(time_array) + 1
        num_days = [i - 12 for i in range(1, length) if i % 24 == 0]
        index = [
            i - int_time if 12 - int_time >= 0 else i + 24 - int_time for i in num_days
        ]
        print(f"index of 12Z times {index} with initial time {int_time}Z")

        ## loop every 24 hours at noon local
        files_ds = []
        for i in index:
            # print(i)
            ## loop each variable
            mean_da = []
            for var in int_ds.data_vars:
                var_array = int_ds[var].values
                noon = var_array[(i + tzone), I, J]
                day = np.array(int_ds.Time[i + 1], dtype="datetime64[D]")
                var_da = xr.DataArray(
                    noon,
                    name=var,
                    dims=("south_north", "west_east"),
                    coords=int_ds.isel(time=i).coords,
                )
                var_da["Time"] = day
                mean_da.append(var_da)
            mean_ds = xr.merge(mean_da)
            files_ds.append(mean_ds)

        daily_ds = xr.combine_nested(files_ds, "time")

        ## create datarray for carry over rain, this will be added to the next days rain totals
        ## NOTE: this is rain that fell from noon local until 24 hours past the model initial time ie 00Z, 06Z..
        r_o_tomorrow_i = int_ds.r_o.values[23] - daily_ds.r_o.values[0]
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
        hourly_ds: DataSet
            A xarray DataSet with all the hourly FWI codes/indices solved
        """

        length = len(self.hourly_ds.time)
        loopTime = datetime.now()
        print("Start Hourly loop length: ", length)
        FFMC = xr.combine_nested(
            [
                self.solve_hourly_ffmc(self.hourly_ds.isel(time=i))
                for i in range(length)
            ],
            "time",
        )
        print(f"Hourly loop done, Time: {datetime.now() - loopTime}")
        hourly_ds = xr.merge([FFMC, self.hourly_ds])

        ISI = self.solve_isi(hourly_ds, hourly_ds.W, fbp=False)
        hourly_ds["R"] = ISI
        self.R = ISI
        FWI, DSR = self.solve_fwi(hourly=True)
        hourly_ds["S"] = FWI
        hourly_ds["DSR"] = DSR
        if self.fbp_mode == True:
            hourly_ds = self.solve_fbp(hourly_ds)
        else:
            pass

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
            F = self.solve_ffmc(self.daily_ds.isel(time=i))
            P = self.solve_dmc(self.daily_ds.isel(time=i))
            D, Df = self.solve_dc(self.daily_ds.isel(time=i))
            ds = F.to_dataset(name="F")
            ds["P"] = P
            ds["D"] = D
            if self.overwinter == True:
                ds["Df"] = Df
            else:
                pass
            daily_list.append(ds)
        print("Daily loop done")
        daily_ds = xr.combine_nested(daily_list, "time")
        daily_ds = xr.merge([daily_ds, self.daily_ds])

        ISI = self.solve_isi(daily_ds, daily_ds.W, fbp=False)
        self.R = ISI

        U = self.solve_bui(daily_ds)
        self.U = U

        FWI, DSR = self.solve_fwi(hourly=False)

        daily_ds["R"] = ISI
        daily_ds["U"] = U
        daily_ds["S"] = FWI
        daily_ds["DSR"] = DSR
        if self.overwinter == True:
            daily_ds["dFS"] = self.daily_ds.dFS
            daily_ds["FS"] = self.daily_ds.FS
        else:
            pass
        self.U = U
        return daily_ds

    def rechunk(self, ds):
        # ds = ds.load()
        ds = ds.chunk(chunks="auto")
        ds = ds.unify_chunks()
        return ds

    def prepare_ds(self, ds):
        loadTime = datetime.now()
        print("Start Loading ", datetime.now())
        ds = ds.load()
        for var in list(ds):
            ds[var].encoding = {}
        print("Load Time: ", datetime.now() - loadTime)

        return ds

    """#######################################"""
    """ ######## Write Hourly Dataset ########"""
    """#######################################"""

    def hourly(self):
        """
        Writes hourly_ds (.nc) and adds the appropriate attributes to each variable

        Returns
        -------
        make_dir: str
            - File directory to (nc) file of todays hourly FWI codes
            - Needed for carry over to intilaze tomorrow's model run
        """
        self.initializer("hourly")
        hourly_ds = self.hourly_loop()
        hourly_ds.attrs = self.attrs

        ## change all to float32 and give attributes to variabels
        for var in hourly_ds.data_vars:
            hourly_ds[var] = hourly_ds[var].astype(dtype="float32")
            hourly_ds[var].attrs = self.var_dict[var]
            hourly_ds[var].attrs["pyproj_srs"] = hourly_ds.attrs["pyproj_srs"]

        # ### Name file after initial time of wrf
        file_date = str(np.array(self.hourly_ds.Time[0], dtype="datetime64[h]"))
        file_date = datetime.strptime(str(file_date), "%Y-%m-%dT%H").strftime(
            "%Y%m%d%H"
        )
        print("Hourly nc initialized at :", file_date)

        # # ## Write and save DataArray (.nc) file
        make_dir = Path(
            str(self.save_dir)
            + str("/fwf-hourly-")
            + self.domain
            + str(f"-{file_date}.nc")
        )
        hourly_ds = self.prepare_ds(hourly_ds)
        writeTime = datetime.now()
        print("Start Write ", datetime.now())
        # hourly_ds.to_netcdf(make_dir, mode="w")
        keep_vars = ["F", "R", "S"]
        hourly_ds = hourly_ds.drop(
            [var for var in list(hourly_ds) if var not in keep_vars]
        )
        hourly_ds, encoding = compressor(hourly_ds, self.var_dict)
        hourly_ds.to_netcdf(make_dir, encoding=encoding, mode="w")
        print("Write Time: ", datetime.now() - writeTime)
        print(f"Wrote working {make_dir}")

        return str(make_dir)

    """#######################################"""
    """ ######## Write Daily Dataset ########"""
    """#######################################"""

    def daily(self):
        """
        Writes daily_ds (.nc) and adds the appropriate attributes to each variable

        Returns
        -------
        make_dir: str
            - File directory to (nc) file of todays daily FWI codes
            - Needed for carry over to intilaze tomorrow's model run
        """
        self.initializer("daily")
        daily_ds = self.daily_loop()
        daily_ds.attrs = self.attrs

        ## change all to float32 and give attributes to variabels
        for var in daily_ds.data_vars:
            daily_ds[var] = daily_ds[var].astype(dtype="float32")
            daily_ds[var].attrs = self.var_dict[var]
            daily_ds[var].attrs["pyproj_srs"] = daily_ds.attrs["pyproj_srs"]

        # # ### Name file after initial time of wrf
        # try:
        #     file_date = str(np.array(self.daily_ds.Time[0], dtype="datetime64[h]"))
        #     file_date = datetime.strptime(str(file_date), "%Y-%m-%dT%H").strftime(
        #         "%Y%m%d06"
        #     )
        # except:
        #     file_date = str(np.array(self.daily_ds.Time, dtype="datetime64[h]"))
        #     file_date = datetime.strptime(str(file_date), "%Y-%m-%dT%H").strftime(
        #         "%Y%m%d06"
        #     )

        # ### Name file after initial time of wrf
        file_date = str(np.array(self.hourly_ds.Time[0], dtype="datetime64[h]"))
        file_date = datetime.strptime(str(file_date), "%Y-%m-%dT%H").strftime(
            "%Y%m%d%H"
        )
        print("Hourly nc initialized at :", file_date)

        print("Daily nc initialized at :", file_date)

        # # ## Write and save DataArray (.nc) file
        make_dir = Path(
            str(self.save_dir)
            + str("/fwf-daily-")
            + self.domain
            + str(f"-{file_date}.nc")
        )
        daily_ds = self.prepare_ds(daily_ds)
        self.daily_ds = daily_ds
        writeTime = datetime.now()
        print("Start Write ", datetime.now())
        daily_ds, encoding = compressor(daily_ds, self.var_dict)
        daily_ds.to_netcdf(make_dir, encoding=encoding, mode="w")
        # daily_ds.to_netcdf(make_dir, mode="w")
        print("Write Time: ", datetime.now() - writeTime)
        print(f"Wrote working {make_dir}")

        return str(make_dir)
