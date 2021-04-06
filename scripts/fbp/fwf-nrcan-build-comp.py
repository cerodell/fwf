import context
import gdal
import salem
import pickle
import pyproj
import numpy as np
import pandas as pd
import xarray as xr
from sklearn.neighbors import KDTree

from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from scipy import stats

from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from utils.make_intercomp import make_daily_noon

from context import data_dir, vol_dir, gog_dir
from datetime import datetime, date, timedelta

wrf_model = "wrf3"
domain = "d02"
fuel_type = "C2"

date_range = pd.date_range("2019-04-01", "2019-09-30")


## Open intercomp of met/fwi to observed dataset
obs_ds = xr.open_zarr(str(data_dir) + "/intercomp/" + f"intercomp-d02-20191001.zarr")


## Get All Stations CSV
df = pd.read_csv(str(data_dir) + "/nrcan-wxstations.csv", sep=",")


## Path to fuel converter spreadsheet
fuel_converter = str(data_dir) + "/fbp/fuel_converter.csv"

## Open fuels converter
fc_df = pd.read_csv(fuel_converter)
fc_df = fc_df.drop_duplicates(subset=["CFFDRS"])
fc_df["Code"] = fc_df["National_FBP_Fueltypes_2014"]
## set index
fc_df = fc_df.set_index("CFFDRS")
fc_dict = fc_df.transpose().to_dict()


## path to fwf zarr file
fbp_filein = str(vol_dir) + f"/fwf-daily-{domain}-2019040100-2019100100.zarr"

## Path to fuels data terrain data
static_filein = str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}.zarr"

## path to nrcan and fwf kdtree
nrc_file, fwf_file = (
    str(data_dir) + "/kdtree/nrc_tree.p",
    str(data_dir) + "/kdtree/fwf_tree.p",
)
fuels_file = str(data_dir) + "/kdtree/fuels_tree.p"
## path to nrcan fuels tiff
nrcan_fuels = str(vol_dir) + "/fuels/resampled/test/nrcan.tif"

## Open datsets: gridded static and FWF
static_ds = xr.open_zarr(static_filein)

ds = xr.open_zarr(fbp_filein)
try:
    ds["time"] = ds.Time
except:
    pass
XLAT, XLONG = ds.XLAT.values, ds.XLONG.values
FUELS = static_ds.FUELS.values
flat_FWF_FUELS = FUELS.ravel()
# lats, lons = XLAT[FUELS == fc_dict[fuel_type]["Code"]], XLONG[FUELS == fc_dict[fuel_type]["Code"]]

# lats, lons = df.lat.values, df.lon.values
# locs = list(zip(lats.tolist(), lons.tolist()))

lats, lons, wmos = obs_ds.lats.values, obs_ds.lons.values, obs_ds.wmo.values
locs = list(zip(lats.tolist(), lons.tolist()))


## open nrcan fueks tiff data
nrc_fuels = gdal.Open(nrcan_fuels)
## get raster array
fuels_raster = nrc_fuels.GetRasterBand(1).ReadAsArray()
## flatten var for indexing with kdtree
flat_fuels_raster = fuels_raster.ravel()
try:
    fuels_tree, fuels_locs, trim_fuels_raster = pickle.load(open(fuels_file, "rb"))
    print("Found NRCAN Fuels Tree")
except:
    print("Could not find NRCAN Fuels Tree building....")
    # create lat/lon grids
    gt = nrc_fuels.GetGeoTransform()  # get coordinates
    nPx, nPy = np.shape(fuels_raster)  # get size of data
    lat_grid, lon_grid = np.zeros((nPx, nPy)), np.zeros(
        (nPx, nPy)
    )  # create storage arrays

    # fill grids
    for nY in range(nPy):
        for nX in range(nPx):
            lat_grid[nX, nY] = gt[3] + nY * gt[4] + nX * gt[5]
            lon_grid[nX, nY] = gt[0] + nY * gt[1] + nX * gt[2]

    # reproject to lat/lon
    wgs84 = pyproj.Proj("+init=EPSG:4326")
    epsg = pyproj.Proj("+init=EPSG:3978")
    nrc_lon, nrc_lat = pyproj.transform(epsg, wgs84, lon_grid.ravel(), lat_grid.ravel())
    NLONG, NLAT = np.reshape(nrc_lon, np.shape(lon_grid)), np.reshape(
        nrc_lat, np.shape(lat_grid)
    )

    # mask where there's no data to make the kd-tree smaller
    fuels_lon = nrc_lon[np.isfinite(flat_fuels_raster)]
    fuels_lat = nrc_lat[np.isfinite(flat_fuels_raster)]
    trim_fuels_raster = flat_fuels_raster[np.isfinite(flat_fuels_raster)]

    ## build a kd-tree for nrcan tiff
    fuels_locs = pd.DataFrame({"lat": fuels_lat, "lon": fuels_lon})
    fuels_tree = KDTree(fuels_locs)
    pickle.dump([fuels_tree, fuels_locs, trim_fuels_raster], open(fuels_file, "wb"))
    print("NRCAN Fuels Tree built")


final_list, yays, nays = [], [], []
for var in ["CFB", "FMC", "HFI", "ROS", "SFC", "TFC"]:
    # for var in ['HFI']:
    print(var)
    nrc_time_list, fwf_time_list = [], []
    for date in date_range:
        print(date)
        compare_date = date.strftime("%Y%m%d")
        ## path to nrcan tiff file
        nrc_filein = str(gog_dir) + f"/NRC_FBP/{var}/{var.lower()}{compare_date}.tif"
        # get time of interest
        try:
            fbp_ds = ds.sel(time=compare_date)
        except:
            fbp_ds = ds
        # flatten var for indexing with kdtree
        fwf_var_flat = fbp_ds[var].values.ravel()

        ## open nrcan var tiff data
        nrc_ds = salem.open_xr_dataset(nrc_filein)
        raster = nrc_ds.data.values
        raster[raster < 0] = np.nan
        flat_raster = raster.ravel()

        if raster.shape != (2281, 2709):
            exit
        else:
            print("Shape passed test")
        try:
            nrc_tree, nrc_locs = pickle.load(open(nrc_file, "rb"))
            # print('Found NRCAN Tree')
        except:
            print("Could not find NRCAN Tree building....")

            nrc_var = gdal.Open(nrc_filein)
            ## get raster array
            raster = nrc_var.GetRasterBand(1).ReadAsArray()
            ## mask nan
            raster[raster < 0] = np.nan
            ## flatten var for indexing with kdtree
            flat_raster = raster.ravel()
            # create lat/lon grids
            gt = nrc_var.GetGeoTransform()  # get coordinates
            nPx, nPy = np.shape(raster)  # get size of data
            lat_grid, lon_grid = np.zeros((nPx, nPy)), np.zeros(
                (nPx, nPy)
            )  # create storage arrays

            # fill grids
            for nY in range(nPy):
                for nX in range(nPx):
                    lat_grid[nX, nY] = gt[3] + nY * gt[4] + nX * gt[5]
                    lon_grid[nX, nY] = gt[0] + nY * gt[1] + nX * gt[2]

            # reproject to lat/lon
            wgs84 = pyproj.Proj("+init=EPSG:4326")
            epsg = pyproj.Proj("+init=EPSG:3978")
            nrc_lon, nrc_lat = pyproj.transform(
                epsg, wgs84, lon_grid.ravel(), lat_grid.ravel()
            )
            NLONG, NLAT = np.reshape(nrc_lon, np.shape(lon_grid)), np.reshape(
                nrc_lat, np.shape(lat_grid)
            )

            # mask where there's no data to make the kd-tree smaller
            # trimlon = nrc_lon[np.isfinite(flat_raster)]
            # trimlat = nrc_lat[np.isfinite(flat_raster)]
            # trimraster = flat_raster[np.isfinite(flat_raster)]

            ## build a kd-tree for nrcan tiff
            nrc_locs = pd.DataFrame({"lat": nrc_lat, "lon": nrc_lon})
            nrc_tree = KDTree(nrc_locs)
            pickle.dump([nrc_tree, nrc_locs], open(nrc_file, "wb"))
            print("NRCAN Tree built")

        try:
            fwf_tree, fwf_locs = pickle.load(open(fwf_file, "rb"))
            # print('Found FWF Tree')
        except:
            ## build a kd-tree for fwf
            print("Could not find FWF Tree building....")
            fwf_locs = pd.DataFrame({"XLAT": XLAT.ravel(), "XLONG": XLONG.ravel()})
            fwf_tree = KDTree(fwf_locs)
            pickle.dump([fwf_tree, fwf_locs], open(fwf_file, "wb"))
            print("NRCAN FWF built")

        save_fuels, save_index = [], []
        nrc_value_list, fwf_value_list, nrc_dist_list, fwf_dist_list = [], [], [], []
        for i in range(len(lats)):
            single_fuel_loc = np.array([lats[i], lons[i]]).reshape(1, -1)
            fuels_dist, fuels_ind = fuels_tree.query(single_fuel_loc, k=1)
            fwf_dist, fwf_ind = fwf_tree.query(single_fuel_loc, k=1)
            if (fwf_dist > 0.1) | (fuels_dist > 0.1):
                pass
            else:
                if (
                    flat_FWF_FUELS[int(fwf_ind)] == trim_fuels_raster[int(fuels_ind)]
                ) & (flat_FWF_FUELS[int(fwf_ind)] < 118):
                    nrc_dist, nrc_ind = nrc_tree.query(single_fuel_loc, k=1)
                    if nrc_dist > 0.1:
                        pass
                    else:
                        nrc_value_list.append(flat_raster[int(nrc_ind)])
                        fwf_value_list.append(fwf_var_flat[int(fwf_ind)])
                        nrc_dist_list.append(float(nrc_dist))
                        fwf_dist_list.append(float(fwf_dist))
                        yays.append(trim_fuels_raster[int(fuels_ind)])
                        save_fuels.append(flat_FWF_FUELS[int(fwf_ind)])
                        save_index.append(i)
                else:
                    nays.append(trim_fuels_raster[int(fuels_ind)])

        nrc_time_list.append(nrc_value_list)
        fwf_time_list.append(fwf_value_list)

    nrc_var = xr.DataArray(
        nrc_time_list,
        name=f"{var}",
        coords={
            "time": date_range,
            "wmo": wmos[save_index],
            "fueltype": ("wmo", save_fuels),
        },
        dims=("time", "wmo"),
    )

    fwf_var = xr.DataArray(
        fwf_time_list,
        name=f"{var}_day1",
        coords={
            "time": date_range,
            "wmo": wmos[save_index],
            "fueltype": ("wmo", save_fuels),
        },
        dims=("time", "wmo"),
    )

    var_ds = xr.merge([nrc_var, fwf_var])
    print(list(var_ds))
    final_list.append(var_ds)


obs_ds_int = obs_ds.sel(time=slice(date_range[0], date_range[-1]))
obs_ds_int = obs_ds_int.isel(wmo=save_index)
final_list.append(obs_ds_int)

final_ds = xr.merge(final_list)


def rechunk(ds):
    try:
        ds = ds.chunk(chunks="auto")
        ds = ds.unify_chunks()
        for var in list(ds):
            ds[var].encoding = {}
    except:
        ds = ds.compute()
    return ds


final_ds = rechunk(final_ds)

## path to save compare dataset
save_out = (
    str(vol_dir)
    + f'/fwf-v-nrcan-{domain}-{date_range[0].strftime("%Y%m%d")}-{date_range[-1].strftime("%Y%m%d")}.zarr'
)
final_ds.to_zarr(save_out, mode="w")
var_list = ["CFB", "FMC", "HFI", "ROS", "SFC", "TFC"]
fig = plt.figure(figsize=[10, 10])
if len(date_range) > 1:
    fig.suptitle(
        f'Comp of FWF vs NRCAN  \n {date_range[0].strftime("%Y%m%d")} - {date_range[-1].strftime("%Y%m%d")}',
        fontsize=14,
    )
else:
    fig.suptitle(
        f'Comp of FWF vs NRCAN  \n {str(date_range[0].strftime("%Y%m%d"))}', fontsize=14
    )
for i in range(len(var_list)):
    ax = fig.add_subplot(3, 3, i + 1)
    fwf_array_ = final_ds[f"{var_list[i]}_day1"].values.ravel()
    ncr_array_ = final_ds[f"{var_list[i]}"].values.ravel()
    fwf_array = fwf_array_[~np.isnan(ncr_array_)]
    ncr_array = ncr_array_[~np.isnan(ncr_array_)]
    if var_list[i] != "CFB":
        ncr_array_f = ncr_array[(fwf_array > 0.9) & (ncr_array > 0.9)]
        fwf_array_f = fwf_array[(fwf_array > 0.9) & (ncr_array > 0.9)]
    else:
        ncr_array_f = ncr_array[(fwf_array > 0.09) & (ncr_array > 0.09)]
        fwf_array_f = fwf_array[(fwf_array > 0.09) & (ncr_array > 0.09)]

    r = round(stats.pearsonr(ncr_array_f, fwf_array_f)[0], 2)
    rmse = str(
        round(
            mean_squared_error(ncr_array_f, fwf_array_f, squared=False),
            2,
        )
    )
    print(np.unique(np.isnan(ncr_array)))
    ax.scatter(fwf_array_f, ncr_array_f, s=5)
    ax.set_title(var_list[i] + f" p_r: {r}  rmse: {rmse}", fontsize=12)
    ax.set_xlabel("FWF", fontsize=8)
    ax.set_ylabel("NRCAN", fontsize=8)
fig.tight_layout()
plt.show()
print(f"yays {len(yays)/len(var_list)}")
print(f"nays {len(nays)/len(var_list)}")
print(np.unique(save_fuels, return_counts=True))
