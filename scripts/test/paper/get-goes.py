#!/Users/crodell/miniconda3/envs/fwf/bin/python

import context
import s3fs
import os

import numpy as np
import pandas as pd

from context import data_dir, root_dir

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


goes = "17"
bucket = f"noaa-goes{goes}"
product = "ABI-L2-FDCF"
date_range = pd.date_range("2021-06-01", "2021-11-01", freq="H")

s3 = s3fs.S3FileSystem(anon=True)
# s3.ls(f"{bucket}") ## uncomment to list all goes products
for doi in date_range:
    print(doi.strftime("%Y-%m-%d-T%H"))
    files = s3.ls(
        f"{bucket}/{product}/{doi.strftime('%Y')}/{doi.strftime('%j')}/{doi.strftime('%H')}"
    )
    for file in files:
        file_name = file.split("/")[-1]
        if os.path.exists(
            f'/Volumes/WFRT-Ext22/frp/goes/g{goes}/{doi.strftime("%Y")}/{file_name}'
        ):
            print("File exists")
        else:
            print("Downloading..")
            print(file_name)
            s3.download(
                file,
                f'/Volumes/WFRT-Ext22/frp/goes/g{goes}/{doi.strftime("%Y")}/{file_name}',
            )
