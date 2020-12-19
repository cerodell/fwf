#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from context import data_dir, xr_dir, wrf_dir

from wrf import (getvar, g_uvmet,get_cartopy, ll_to_xy, interplevel)



""" ####################################################################### """
""" ###################### Grab WRF Variables ####################### """

def readwrf(filein, domain,  *args):
    """
    This function reads wrfout files and grabs required met variables for fire weather index calculations.  Writes/outputs as a xarray    
    
        - wind speed (km h-1)
        - temp (degC)
        - rh (%)
        - qpf (mm)
        - snw (mm)

    Parameters
    ----------
    
    files: str
        - File directory to NetCDF files

    Returns
    -------
    
    ds_wrf: DataSet
        xarray DataSet
    """
    startTime = datetime.now()
    print("begin readwrf: ", str(startTime))
    ds_list, time_list, attributes = [], [], []
    pathlist = sorted(Path(filein).glob(f'wrfout_{domain}_*00'))
    if domain == 'd02':
        pathlist = pathlist[:61]
    else:
        pass
    for path in pathlist:
        path_in_str = str(path)
        wrf_file = Dataset(path_in_str,'r')

        time         = getvar(wrf_file, "times", timeidx=0)
        Ti           = getvar(wrf_file, "T2")
        T            = Ti-273.15
        T.attrs      = Ti.attrs
        T.attrs['description'] = "2m TEMP"
        T.attrs['units'] = "C"
        Hi           = getvar(wrf_file, "rh2", meta=False)
        H            = xr.DataArray(Hi, name='H', dims=('south_north', 'west_east'))
        H.attrs      = Ti.attrs
        H.attrs['units'] = "(%)"
        H.attrs['description'] = "2m RELATIVE HUMIDITY"
        wsp_wdir     = g_uvmet.get_uvmet10_wspd_wdir(wrf_file,units='km h-1')
        wsp_array    = np.array(wsp_wdir[0])
        wdir_array   = np.array(wsp_wdir[1])
        W            = xr.DataArray(wsp_array, name='W', dims=('south_north', 'west_east'))
        WD           = xr.DataArray(wdir_array, name='WD', dims=('south_north', 'west_east'))
        W.attrs      = wsp_wdir.attrs
        W.attrs['description'] = "10m WIND SPEED"
        WD.attrs      = wsp_wdir.attrs
        WD.attrs['description'] = "10m WIND DIRECTION"
        WD.attrs['units'] = "degrees"

        U10i           = np.array(getvar(wrf_file, "U10")) *1.0
        U10            = xr.DataArray(U10i, name='U10', dims=('south_north', 'west_east'))
        U10.attrs      = Ti.attrs
        U10.attrs['units'] = "m s-1"
        U10.attrs['description'] = "U at 10 M"

        V10i           = np.array(getvar(wrf_file, "V10")) *1.0
        V10            = xr.DataArray(V10i, name='V10', dims=('south_north', 'west_east'))
        V10.attrs      = Ti.attrs
        V10.attrs['units'] = "m s-1"
        V10.attrs['description'] = "V at 10 M"

        ##varied parameterization scheme to forecast rain..note this is a sum of rain from the starts of the model run  
        rain_ci   = getvar(wrf_file, "RAINC")
        rain_c    = rain_ci.values
        rain_sh   = getvar(wrf_file, "RAINSH", meta=False)
        rain_nc   = getvar(wrf_file, "RAINNC", meta=False)
        qpf_i     = rain_c + rain_sh + rain_nc
        qpf       = np.where(qpf_i>0,qpf_i, qpf_i*0)
        r_o       = xr.DataArray(qpf, name='r_o', dims=('south_north', 'west_east'))
        r_o.attrs = rain_ci.attrs
        r_o.attrs['description'] = "ACCUMULATED TOTAL PRECIPITATION"

        SNWi           = getvar(wrf_file, "SNOWNC", meta=False)
        SNW            = xr.DataArray(SNWi, name='SNW', dims=('south_north', 'west_east'))
        SNW.attrs      = Ti.attrs
        SNW.attrs['units'] = "cm"
        SNW.attrs['description'] = "ACCUMULATED TOTAL GRID SCALE SNOW AND ICE"

        SNOWCi           = getvar(wrf_file, "SNOWC", meta=False)
        SNOWC            = xr.DataArray(SNOWCi, name='SNOWC', dims=('south_north', 'west_east'))
        SNOWC.attrs      = Ti.attrs
        SNOWC.attrs['units'] = ""
        SNOWC.attrs['description'] = "FLAG INDICATING SNOW COVERAGE (1 FOR SNOW COVER)"

        SNOWHi           = getvar(wrf_file, "SNOWH", meta=False)
        SNOWH            = xr.DataArray(SNOWHi, name='SNOWH', dims=('south_north', 'west_east'))
        SNOWH.attrs      = Ti.attrs
        SNOWH.attrs['units'] = "m"
        SNOWH.attrs['description'] = "PHYSICAL SNOW DEPTH"

        # # Extract the pressure, geopotential height, and wind variables
        # p = getvar(wrf_file, "pressure")
        # z = getvar(wrf_file, "z", units="dm")
        # ua = getvar(wrf_file, "ua", units="m s-1")
        # va = getvar(wrf_file, "va", units="m s-1")
        # wspd = getvar(wrf_file, "wspd_wdir", units="m s-1")[0,:]

        # # Interpolate geopotential height, u, and v winds to 500 hPa
        # ht_500i = interplevel(z, p, 500)
        # u_500i = interplevel(ua, p, 500)
        # v_500i = interplevel(va, p, 500)
        # wspd_500i = interplevel(wspd, p, 500)

        # ht_500i           = np.array(ht_500i) *1.0
        # HT500            = xr.DataArray(ht_500i, name='HT500', dims=('south_north', 'west_east'))
        # HT500.attrs      = Ti.attrs
        # HT500.attrs['units'] = "m"
        # HT500.attrs['description'] = "500 hPa geopotential height"

        # u_500i           = np.array(u_500i) *1.0
        # U500            = xr.DataArray(u_500i, name='U500', dims=('south_north', 'west_east'))
        # U500.attrs      = Ti.attrs
        # U500.attrs['units'] = "m s-1"
        # U500.attrs['description'] = "500 hPa U winds"

        # v_500i           = np.array(v_500i) *1.0
        # V500            = xr.DataArray(v_500i, name='V500', dims=('south_north', 'west_east'))
        # V500.attrs      = Ti.attrs
        # V500.attrs['units'] = "m s-1"
        # V500.attrs['description'] = "500 hPa U winds"

        # wspd_500i           = np.array(wspd_500i) *1.0
        # WSP500            = xr.DataArray(wspd_500i, name='WSP500', dims=('south_north', 'west_east'))
        # WSP500.attrs      = Ti.attrs
        # WSP500.attrs['units'] = "m s-1"
        # WSP500.attrs['description'] = "500 hPa wind speeds"


        var_list = [H,T,W,WD,r_o, SNW, SNOWC, SNOWH, U10, V10]
        ds = xr.merge(var_list)
        ds_list.append(ds)
        time_list.append(time)
        attributes.append(path_in_str)

    ### Combine xarrays and rename to match van wangers defs 
    wrf_ds = xr.combine_nested(ds_list, 'time')
    wrf_ds = wrf_ds.rename_vars({"T2":"T"})

    wrf_file = Dataset(attributes[0],'r')
    nc_attrs = wrf_file.ncattrs()
    for nc_attr in nc_attrs:
        # print('\t%s:' % nc_attr, repr(wrf_file.getncattr(nc_attr)))
        wrf_ds.attrs[nc_attr] = repr(wrf_file.getncattr(nc_attr))

    if args:
        xy_np    = np.array(ll_to_xy(wrf_file, float(args[0]), float(args[1])))
    else:
        xy_np    = None

    print("readwrf run time: ", datetime.now() - startTime)
    return wrf_ds, xy_np




# def dict_xarry(var1, var2, var3):
#     var_dict={}
#     var3 = np.array(var3, dtype=float)
#     dims = ('time', 'south_north', 'west_east')
#     var_dict.update({'FFMC' : (dims,np.array(var1, dtype=float))})
#     var_dict.update({'m_o' : (dims,np.array(var2, dtype=float))})
#     var_dict.update({'time' : ('time',var3)})
#     return var_dict

