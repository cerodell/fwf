import context
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from context import data_dir, xr_dir, wrf_dir

from wrf import (getvar, g_uvmet)



""" ####################################################################### """
""" ###################### Grab WRF Variables ####################### """

def readwrf(filein):
    """
    This Fucntion reads wrfout files and grabs varibels of internts and writes/outputs as an xarray
    
    Parameters
    ----------
    
    files: netcdf files
    Returns
    -------
    
    ds_wrf: an xarray of wind speed (km h-1), temp (degC), rh (%) & qpf (mm)
    """
    ds_list, time_list = [], []
    pathlist = sorted(Path(filein).glob('wrfout_d03_*'))
    # print(pathlist)
    for path in pathlist:
        path_in_str = str(path)
        wrf_file = Dataset(path_in_str,'r')
        
        time         = getvar(wrf_file, "times", timeidx=0)
        H            = getvar(wrf_file, "rh2")*1
        T            = getvar(wrf_file, "T2")-273.15
        # uv          = getvar(wrf_file, "uvmet10", units='km h-1') 
        # lats        = getvar(wrf_file, "lat")
        # lons        = getvar(wrf_file, "lon")
        wsp_wdir     = g_uvmet.get_uvmet10_wspd_wdir(wrf_file,units='km h-1')
        wsp_array    = np.array(wsp_wdir[0])
        W            = xr.DataArray(wsp_array, name='W', dims=('south_north', 'west_east'))
        
        ##varied parameterization scheme to forecast rain..note this is a sum of rain from the starts of the model run  
        # rain_c    = getvar(wrf_file, "RAINC")
        # rain_sh   = getvar(wrf_file, "RAINSH")
        # rain_nc   = getvar(wrf_file, "RAINNC")
        # qpf       = rain_c + rain_sh + rain_nc

        var_list = [H,T,W]
        ds = xr.merge(var_list)
        ds_list.append(ds)
        time_list.append(time)

    ### Combine xarrays and rename to match van wangers defs 
    ds_wrf = xr.combine_nested(ds_list, 'time')
    ds_wrf = ds_wrf.rename_vars({"T2":"T", "rh2":"H"})

    ### Name file after initial time of wrf 
    file_name = np.datetime_as_string(time_list[0],unit='h')
    print("WRF initialized at :",str(file_name))

    # ## Write and save DataArray (.zarr) file
    make_dir = Path(str(xr_dir) + str('/') + file_name+str('/') + str(f"_ds_wrf.zarr"))
    make_dir.mkdir(parents=True, exist_ok=True)

    ### Check if file exists....if not write file
    if make_dir.exists():
        the_size = make_dir.stat().st_size
        print(
            ("\n{} already exists\n" "and is {} bytes\n" "will not overwrite\n").format(
                file_name, the_size
            )
        )
    else:
        ds_wrf.compute()
        ds_wrf.to_zarr(make_dir, "w")
        print(f"wrote {make_dir}")
    
    ### return path to xr file to open
    return str(make_dir)




# def dict_xarry(var1, var2, var3):
#     var_dict={}
#     var3 = np.array(var3, dtype=float)
#     dims = ('time', 'south_north', 'west_east')
#     var_dict.update({'FFMC' : (dims,np.array(var1, dtype=float))})
#     var_dict.update({'m_o' : (dims,np.array(var2, dtype=float))})
#     var_dict.update({'time' : ('time',var3)})
#     return var_dict

