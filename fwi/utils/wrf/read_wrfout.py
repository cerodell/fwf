import context
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from context import data_dir, xr_dir, wrf_dir

from wrf import (getvar, g_uvmet,get_cartopy, ll_to_xy)



""" ####################################################################### """
""" ###################### Grab WRF Variables ####################### """

def readwrf(filein, *args):
    """
    This function reads wrfout files and grabs variables of interest and writes/outputs as an xarray
    
    Parameters
    ----------
    
    files: netcdf files
    Returns
    -------
    
    ds_wrf: an xarray of wind speed (km h-1), temp (degC), rh (%) & qpf (mm)
    """
   
    ds_list, time_list, attributes = [], [], []
    pathlist = sorted(Path(filein).glob('wrfout_d03_*'))
    # print(pathlist)
    for path in pathlist:
        path_in_str = str(path)
        wrf_file = Dataset(path_in_str,'r')

        time         = getvar(wrf_file, "times", timeidx=0)
        Ti           = getvar(wrf_file, "T2")
        T            = Ti-273.15
        T.attrs      = Ti.attrs
        T.attrs['description'] = "2m TEMP"
        T.attrs['units'] = "C"
        Hi           = np.array(getvar(wrf_file, "rh2")) * 1.0
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

        ##varied parameterization scheme to forecast rain..note this is a sum of rain from the starts of the model run  
        rain_ci   = getvar(wrf_file, "RAINC")
        rain_c    = np.array(rain_ci)
        rain_sh   = np.array(getvar(wrf_file, "RAINSH"))
        rain_nc   = np.array(getvar(wrf_file, "RAINNC"))
        qpf_i     = rain_c + rain_sh + rain_nc
        qpf       = np.where(qpf_i>0,qpf_i, qpf_i*0)
        r_o       = xr.DataArray(qpf, name='r_o', dims=('south_north', 'west_east'))
        r_o.attrs = rain_ci.attrs
        r_o.attrs['description'] = "ACCUMULATED TOTAL PRECIPITATION"
        var_list = [H,T,W,WD,r_o]
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

    ### Name file after initial time of wrf 
    # file_name = np.datetime_as_string(time_list[0],unit='h')
    # print("WRF initialized at :",str(file_name))

    # ## Write and save DataArray (.zarr) file
    # make_dir = Path(str(xr_dir) + str('/') + file_name + str(f"_wrf_ds.zarr"))

    ### Check if file exists....else write file
    # if make_dir.exists():
    #     the_size = make_dir.stat().st_size
    #     print(
    #         ("\n{} already exists\n" "and is {} bytes\n" "will not overwrite\n").format(
    #             file_name, the_size
    #         )
    #     )
    # else:
    #     make_dir.mkdir(parents=True, exist_ok=True)
    #     wrf_ds.compute()
    #     wrf_ds.to_zarr(make_dir, "w")
    #     print(f"wrote {make_dir}")

    # make_dir.mkdir(parents=True, exist_ok=True)
    # wrf_ds.compute()
    # wrf_ds.to_zarr(make_dir, "w")
    # print(f"wrote {make_dir}")
    
    ### return path to xr file to open
    # return str(make_dir)
    return wrf_ds, xy_np




# def dict_xarry(var1, var2, var3):
#     var_dict={}
#     var3 = np.array(var3, dtype=float)
#     dims = ('time', 'south_north', 'west_east')
#     var_dict.update({'FFMC' : (dims,np.array(var1, dtype=float))})
#     var_dict.update({'m_o' : (dims,np.array(var2, dtype=float))})
#     var_dict.update({'time' : ('time',var3)})
#     return var_dict

