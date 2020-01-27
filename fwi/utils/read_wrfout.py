import context
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime

from wrf import (getvar, g_uvmet)



""" ####################################################################### """
""" ###################### Grab WRF Variables ####################### """

def readwrf(filein):
    """
    This Fucntion read wrfout file and grabs varibels of internts and outputs as an xarray
    
    Parameters
    ----------
    
    files: netcdf files
    Returns
    -------
    
    ds_wrf: an xarray of wind speed (km h-1), temp (degC) & rh (%) 
    """
    ds_list = []
    pathlist = sorted(Path(filein).glob('wrfout_d03_*'))
    #print(pathlist)
    for path in pathlist:
        path_in_str = str(path)
        wrf_file = Dataset(path_in_str,'r')
        
        rh        = getvar(wrf_file, "rh2")*1
        temp      = getvar(wrf_file, "T2")-273.15
        # uv         = getvar(wrf_file, "uvmet10", units='km h-1') 
        # lats      = getvar(wrf_file, "lat")
        # lons      = getvar(wrf_file, "lon")
        wsp_wdir  = g_uvmet.get_uvmet10_wspd_wdir(wrf_file,units='km h-1')
        wsp_array    = np.array(wsp_wdir[0])
        wsp = xr.DataArray(wsp_array, name='wsp', dims=('south_north', 'west_east'))

        # wps=xr.Dataset({'WSP': np.array(wsp_i),'XLONG': (['south_north', 'west_east'], wsp_i.XLONG),
        #                 'XLAT': (['south_north', 'west_east'], wsp_i.XLAT),
        #                 'time': (wsp_i.Time)})
        
        ##varied parameterization scheme to forecast rain..note this is a sum of rain from the starts of the model run  
        # rain_c    = getvar(wrf_file, "RAINC")
        # rain_sh   = getvar(wrf_file, "RAINSH")
        # rain_nc   = getvar(wrf_file, "RAINNC")
        # qpf       = rain_c + rain_sh + rain_nc

        var_list = [rh,temp,wsp]
        ds = xr.merge(var_list)
        ds_list.append(ds)

    ds_wrf = xr.combine_nested(ds_list, 'time')

    out_dir = str(context.data_dir)
    out_dir = Path(str(context.data_dir)+str('/xr/'))
    out_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now() # current date and time
    folder_date = now.strftime("%Y%m%d")
    file_date = now.strftime("%Y%m%d_%H")
    print("date and time:",file_date)

    ## Write and save DataArray (.zarr) file
    full_dir = str(out_dir) + str('/') + folder_date+str('/') + file_date+ str(f"_ds_wrf.zarr")

    ds_wrf.compute()
    ds_wrf.to_zarr(full_dir, "w")
    print(f"wrote {out_dir}")
    
    return full_dir




def dict_xarry(var1, var2, var3):
    var_dict={}
    var3 = np.array(var3, dtype=float)
    dims = ('time', 'south_north', 'west_east')
    var_dict.update({'ffmc' : (dims,np.array(var1, dtype=float))})
    var_dict.update({'m_o' : (dims,np.array(var2, dtype=float))})
    var_dict.update({'time' : ('time',var3)})
    return var_dict

