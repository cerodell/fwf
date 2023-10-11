#!/Users/crodell/miniconda3/envs/fwf/bin/python

import context
import s3fs

import numpy as np
import pandas as pd

from context import data_dir, root_dir

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


# bucket = f'noaa-hrrr-bdp-pds'
# date_range = pd.date_range("2023-08-22", "2023-08-22", freq ='H')

# s3 = s3fs.S3FileSystem(anon=True)
# # s3.ls(f"{bucket}") ## uncomment to list all goes products
# for doi in date_range:
#   print(doi.strftime('%Y-%m-%d-T%H'))
#   # files = s3.ls(f"{bucket}/")
#   files = s3.ls(f"{bucket}/hrrr.{doi.strftime('%Y%m%d')}/conus/")
#   for file in files:
#       file_name = file.split("/")[-1]
#       print(file_name)
#       # s3.download(file,str(data_dir)+f'/hrrr/{doi.strftime("%Y")}/{file_name}')
import s3fs
import xarray

s3 = s3fs.S3FileSystem(anon=True)


def lookup(path):
    return s3fs.S3Map(path, s3=s3)


path = "hrrrzarr/sfc/20210101/20210101_00z_anl.zarr/surface/TMP"
ds = xarray.open_mfdataset([lookup(path), lookup(f"{path}/surface")], engine="zarr")

ds.TMP.plot()
