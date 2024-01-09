import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset

from context import data_dir, xr_dir, wrf_dir, tzone_dir
from datetime import datetime, date, timedelta


domain = "d02"
wrf_model = "wrf3"

### Open Fuel converter spreadsheet
fuel_converter = str(data_dir) + "/fbp/fuel_converter_dev.csv"
fc_df = pd.read_csv(fuel_converter)
fc_df = fc_df.drop_duplicates(subset=["FWF_Code"])

### Open any wrf dataset
### Get a wrf file
if wrf_model == "wrf3":
    wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CP-04/18072000/wrfout_{domain}_2018-07-20_11:00:00"
else:
    wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CG-01/21022000/wrfout_{domain}_2021-02-20_11:00:00"
wrf_ds = xr.open_dataset(wrf_filein)
dx, dy = float(wrf_ds.attrs["DX"]), float(wrf_ds.attrs["DY"])

wrf_ds = wrf_ds.HGT.to_dataset()
wrf_ds = wrf_ds.isel(Time=0)
try:
    wrf_ds = wrf_ds.drop_vars("XTIME")
except:
    pass


### Open tzone ST dataset
tzone_st_filein = str(tzone_dir) + f"/tzone_{wrf_model}_{domain}-ST.zarr"
tzone_st_ds = xr.open_zarr(tzone_st_filein)
tzone_st_ds["ZoneST"] = tzone_st_ds["Zone"]
tzone_st_ds = tzone_st_ds.drop_vars("Zone")

### Open tzone DT dataset
tzone_dt_filein = str(tzone_dir) + f"/tzone_{wrf_model}_{domain}-DT.zarr"
tzone_dt_ds = xr.open_zarr(tzone_dt_filein)
tzone_dt_ds["ZoneDT"] = tzone_dt_ds["Zone"]
tzone_dt_ds = tzone_dt_ds.drop_vars("Zone")

### Open fuels  dataset
fuels_fielin = str(data_dir) + f"/fbp/fuels-{wrf_model}-{domain}-2019.zarr"
fuels_ds = xr.open_zarr(fuels_fielin)

## get array of values to make percent conifer (PC) mask
fuels = fuels_ds["fuels"].values
shape = fuels.shape

## make an zero full array of domain shape
pc_mask = np.zeros(shape, dtype="float32")
id_mask = np.zeros(shape, dtype="<U10")

## get all M type fuels..M fuels type us PC in FBP calculations
ms_df = fc_df[fc_df["CFFDRS"].str.contains("M1")]

## no populate zero full with PC values defined in CFFDRS columns
index = ms_df.index.values
for i in index:
    ## build mask for PC
    pc_mask[fuels == ms_df["FWF_Code"][i]] = ms_df["CFFDRS"][i][-3:-1]
    ## replace all fuels values of M type to be the same code. This will greatly increat comps speed in FBP code
    fuels[fuels == ms_df["FWF_Code"][i]] = ms_df["FWF_Code"][index[0]]

## can print for sanity check
unique, count = np.unique(fuels, return_counts=True)

## make PC Dataarray and add to fuels dataset
PC = xr.DataArray(pc_mask, name="PC", dims=("south_north", "west_east"))
fuels_ds["PC"] = PC

## make new fuels Dataarray and add to fuels dataset
FUELS = xr.DataArray(fuels, name="FUELS", dims=("south_north", "west_east"))
fuels_ds["FUELS"] = FUELS
## lets also keep the origanil fuels array for ploting purposes
fuels_ds["FUELS_D"] = fuels_ds["fuels"]
fuels_ds = fuels_ds.drop_vars("fuels")

## no populate zero full with PC values defined in CFFDRS columns
index = fc_df.index.values
fuels_d = fuels_ds["FUELS_D"].values
for i in index:
    if str(fc_df["CFFDRS"][i]) == "Urban or built-up area":
        id_mask[fuels_d == fc_df["FWF_Code"][i]] = "Urban"
    else:
        id_mask[fuels_d == fc_df["FWF_Code"][i]] = str(fc_df["CFFDRS"][i])
FUELS_ID = xr.DataArray(id_mask, name="FUELS_ID", dims=("south_north", "west_east"))
fuels_ds["FUELS_ID"] = FUELS_ID

## Solve a few static variable in the FBP system and add to terrain dataframe
## Take gradient dz/dx and dz/dy of elevation
gradient = np.gradient(wrf_ds.HGT)
y_grad = gradient[0]
x_grad = gradient[1]

## Solve Percent Ground Slope (37)
GS = 100 * np.sqrt((x_grad / dx) ** 2 + (y_grad / dy) ** 2)
GS = xr.DataArray(GS, name="GS", dims=("south_north", "west_east"))
wrf_ds["GS"] = GS
wrf_ds["GS"].attrs = {
    "FieldType": 104,
    "MemoryOrder": "XY ",
    "description": "Percent Ground Slope",
    "projection": "PolarStereographic(stand_lon=-110.0, moad_cen_lat=53.99999237060547, truelat1=57.0, truelat2=90.0, pole_lat=90.0, pole_lon=0.0)",
    "units": "%",
}
# Solve for slope Aspect
ASPECT = np.arctan2((y_grad / dy), -(x_grad / dx)) * (180 / np.pi) + 180
ASPECT = xr.DataArray(ASPECT, name="ASPECT", dims=("south_north", "west_east"))
wrf_ds["ASPECT"] = ASPECT
wrf_ds["ASPECT"].attrs = {
    "FieldType": 104,
    "MemoryOrder": "XY ",
    "description": "Terrain Slope Aspect",
    "projection": "PolarStereographic(stand_lon=-110.0, moad_cen_lat=53.99999237060547, truelat1=57.0, truelat2=90.0, pole_lat=90.0, pole_lon=0.0)",
    "units": "degrees",
}

# Solve for Uphill slope Azimuth Angle (SAZ)
SAZ = np.where(
    ASPECT < 0,
    90.0 - ASPECT,
    np.where(ASPECT > 90.0, 360.0 - ASPECT + 90.0, 90.0 - ASPECT),
)
SAZ = xr.DataArray(SAZ, name="SAZ", dims=("south_north", "west_east"))
wrf_ds["SAZ"] = SAZ
wrf_ds["SAZ"].attrs = {
    "FieldType": 104,
    "MemoryOrder": "XY ",
    "description": "Terrain Slope Azimuth Angle",
    "projection": "PolarStereographic(stand_lon=-110.0, moad_cen_lat=53.99999237060547, truelat1=57.0, truelat2=90.0, pole_lat=90.0, pole_lon=0.0)",
    "units": "degrees",
}

## Merge all static zarr files
static_ds = xr.merge([tzone_st_ds, tzone_dt_ds, fuels_ds, wrf_ds])
static_ds = static_ds.drop_vars("south_north")
static_ds = static_ds.drop_vars("west_east")
try:
    static_ds = static_ds.drop_vars("XTIME")
except:
    pass

## set attributes for each static file
static_ds.ZoneDT.attrs = {
    "FieldType": 104,
    "MemoryOrder": "XY ",
    "description": "Day Light Savings Time Zone Offsets From UTC",
    "pyproj_srs": "+proj=stere +lat_0=90 +lat_ts=57 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs",
    "units": "hours_",
}

static_ds.ZoneST.attrs = {
    "FieldType": 104,
    "MemoryOrder": "XY ",
    "description": "Standard Time Time Zone Offsets From UTC",
    "pyproj_srs": "+proj=stere +lat_0=90 +lat_ts=57 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs",
    "units": "hours_",
}

static_ds.HGT.attrs = {
    "FieldType": 104,
    "MemoryOrder": "XY ",
    "description": "Terrain Height",
    "pyproj_srs": "+proj=stere +lat_0=90 +lat_ts=57 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs",
    "units": "meters",
}

static_ds.FUELS.attrs = {
    "FieldType": 104,
    "MemoryOrder": "XY ",
    "description": "CFFDRS Fuels Type",
    "pyproj_srs": "+proj=stere +lat_0=90 +lat_ts=57 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs",
    "units": "fuel type code",
}

## Write to static dataset to zarr file and load all arrays to memory
static_ds = static_ds.compute()

static_ds.to_netcdf(
    str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}.nc", mode="w"
)
print(f"Wrote: {str(data_dir)}/static/static-vars-{wrf_model}-{domain}.nc")
