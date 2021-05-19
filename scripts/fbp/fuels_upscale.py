import context
import salem
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr

# from affine import Affine
from pathlib import Path


import rasterio
from rasterio import Affine, MemoryFile
from rasterio.enums import Resampling

from context import data_dir, wrf_dir, vol_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))


## choose model domain
domain = "d03"


file_paths = []
save_path = []

# ## Path to 2014 nrcan fuels data tif
# fbp2014_filein = (
#     str(vol_dir) + "/fuels/National_FBP_Fueltypes_version2014b/nat_fbpfuels_2014b.tif"
# )
# file_paths.append(fbp2014_filein)
# save_path.append("nrcan.tif")

## Path toe Peter E's converted fuels grid
# fbp2019_filein = (
#     str(vol_dir) + "/fuels/can_fuels2019b.tif"
# )

# file_paths.append(fbp2019_filein)
# save_path.append("nrcan_2019.tif")

## Path to 2016 land fire US fuels data tif
# us_filein = str(vol_dir) + "/fuels/LF2020_FBFM13_200_CONUS/Tif/LC20_F13_200.tif"
# file_paths.append(us_filein)
# save_path.append('landfire.tif')

# ## loop all tiffs of AK to gridded adn mask fuels type tag to be the same as CFFDRS
# folders = ["%.2d" % i for i in range(1, 21)]
# print(folders)
# for folder in folders:
#     ak_filein = (
#         str(vol_dir) + f"/fuels/{folder}_AK_140CFFDRS/AK_140CFFDRS\AK_140CFFDRS.tif"
#     )
#     file_paths.append(ak_filein)
#     save_path.append(f'ak_{folder}.tif')


def resmaple(filein, fileout, domain):
    with rasterio.open(filein) as dataset:
        res = np.array(dataset.transform)[0]
        if domain == "d03":
            upscale_factor = 4000 // res
            print(
                f"Using an upscale factor of {upscale_factor} will result in {upscale_factor * res} res tiff"
            )
        elif domain == "d02":
            upscale_factor = 12000 // res
            print(
                f"Using an upscale factor of {upscale_factor} will result in {upscale_factor * res} res tiff"
            )
        else:
            # upscale_factor = 1000 // res
            warnings.warn(
                "You are using an upscale factor that donest match either of the wrf domains"
            )

        # resample data to target shape
        data = dataset.read(
            out_shape=(
                dataset.count,
                int(dataset.height / upscale_factor),
                int(dataset.width / upscale_factor),
            ),
            resampling=Resampling.mode,
        )

        # scale image transform
        transform = dataset.transform * dataset.transform.scale(
            (dataset.width / data.shape[-1]), (dataset.height / data.shape[-2])
        )
        with rasterio.open(
            str(vol_dir) + f"/fuels/resampled/{domain}/{fileout}",
            "w",
            driver="GTiff",
            height=data.shape[1],
            width=data.shape[2],
            count=1,
            dtype=data.dtype,
            crs=dataset.crs,
            transform=transform,
        ) as dst:
            dst.write(data)

    return


for i in range(len(file_paths)):
    resmaple(file_paths[i], save_path[i], domain)
