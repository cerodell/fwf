#!/Users/crodell/miniconda3/envs/fwx/bin/python

import os
import context
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path


adda_dir = "/Volumes/ThunderBay/CRodell/ADDA_V2/"
doi, model, domain, trial = pd.Timestamp("2002-01-01"), "adda", "d01", "01"


def get_timestamp_vars(file_name):
    return str(file_name).split("/")[-1][9:-9]


def get_files_vars(date_of_int):
    return sorted(
        Path(str(adda_dir) + f'/{date_of_int.strftime("%Y")}/').glob(
            f"cstm_d01_{doi.strftime('%Y')}*"
        ),
        key=get_timestamp_vars,
    )


adda_files = get_files_vars(doi)

# file = adda_files[1]

# move2dir = f'mv {file}/{str(file).split("/")[-1]} {str(file).rsplit("/", 2)[0]}/test/{str(file).split("/")[-1]}'


def get_actual(file):
    move2dir = f'mv {file}/{str(file).split("/")[-1]} {str(file).rsplit("/", 2)[0]}/test/{str(file).split("/")[-1]}'
    os.system(move2dir)
    return


[get_actual(file) for file in adda_files]
