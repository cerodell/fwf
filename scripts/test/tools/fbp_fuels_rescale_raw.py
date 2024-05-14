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

from context import data_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))


## choose model domain
domain = "rave"


file_paths = []
save_path = []
vol_dir = "/Volumes/Scratch/fwf-data"

# ## Path toe Peter E's converted fuels grid
# CBH_filein = (
#     str(vol_dir) + "/fuels/can_fuels2019b/CBH_m_p.tif"
# )

# file_paths.append(CBH_filein)
# save_path.append("CBH.tif")

# CFL_filein = (
#     str(vol_dir) + "/fuels/can_fuels2019b/CFL_b_kgm2_p.tif"
# )

# file_paths.append(CFL_filein)
# save_path.append("CFL.tif")

# us_CBH_filein = (
#     str(vol_dir) + "/fuels/LF2020_CBH_200_CONUS/Tif/LC20_CBH_200.tif"
# )
# # us_CBH_filein = str(vol_dir) + f"/fuels/resampled/{domain}/us_CBH.tif"

# file_paths.append(us_CBH_filein)
# save_path.append("us_CBH.tif")

## loop all tiffs of AK to gridded adn mask fuels type tag to be the same as CFFDRS
folders = ["%.2d" % i for i in range(1, 21)]
print(folders)
for folder in folders:
    ak_filein = str(vol_dir) + f"/fuels/{folder}_AK_140CBH/AK_140CBH\AK_140CBH.tif"
    file_paths.append(ak_filein)
    save_path.append(f"ak_{folder}_CBH.tif")


def resmaple(filein, fileout, domain):
    with rasterio.open(filein) as dataset:
        res = int(np.array(dataset.transform)[0])
        print(res)
        upscale_factor = 2
        if domain == "rave":
            upscale_factor = 3000 // res
            print(
                f"Using an upscale factor of {upscale_factor} will result in {upscale_factor * res} res tiff"
            )
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
            upscale_factor = 1000 // res
            # warnings.warn(
            #     "You are using an upscale factor that donest match either of the wrf domains"
            # )

        # resample data to target shape
        data = dataset.read(
            out_shape=(
                dataset.count,
                int(dataset.height / upscale_factor),
                int(dataset.width / upscale_factor),
            ),
            resampling=Resampling.average,
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
