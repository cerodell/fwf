import context
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from context import data_dir, xr_dir, wrf_dir

# from wrf import (getvar, g_uvmet)

from wrf import (to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ALL_TIMES)


filein = str(wrf_dir)



ds_list = []
pathlist = sorted(Path(filein).glob('wrfout_d03_*'))
#print(pathlist)
for path in pathlist:
    path_in_str = str(path)
    wrf_file = Dataset(path_in_str,'r')
    
    rh        = getvar(wrf_file, "rh2")
    temp      = getvar(wrf_file, "T2")-273.15
    # uv         = getvar(wrf_file, "uvmet10", units='km h-1') 
    # lats      = getvar(wrf_file, "lat")
    # lons      = getvar(wrf_file, "lon")
    wsp_wdir  = g_uvmet.get_uvmet10_wspd_wdir(wrf_file,units='km h-1')
    wsp_array    = np.array(wsp_wdir[0])
    wsp = xr.DataArray(wsp_array, name='wsp', dims=('south_north', 'west_east'))

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

# ds_wrf.compute()
# ds_wrf.to_zarr(full_dir, "w")
# print(f"wrote {out_dir}")


