import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from utils.make_intercomp import daily_merge_ds

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.ndimage as ndimage
from scipy.ndimage.filters import gaussian_filter


from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

## Define model/domain and datetime of interest
# date = pd.Timestamp("today")
date = pd.Timestamp(2018, 7, 20)
domain = "d02"
wrf_model = "wrf3"

## Path to hourly/daily fwi data
forecast_date = date.strftime("%Y%m%d06")
hourly_file_dir = (
    str(data_dir) + f"/FWF-WAN00CP-04/fwf-hourly-{domain}-{forecast_date}.zarr"
)

## Path to fuel converter spreadsheet
fuel_converter = str(data_dir) + "/fbp/fuel_converter.csv"
## Path to fuels data
fuelsin = str(data_dir) + f"/fbp/fuels-{wrf_model}-{domain}.zarr"
## Path to terrain data
terrain = str(data_dir) + f"/terrain/hgt-{wrf_model}-{domain}.nc"

## Open hourly/daily fwi data
hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = daily_merge_ds(forecast_date, domain, wrf_model)

## Open fuels converter
fc_df = pd.read_csv(fuel_converter)
fc_df = fc_df.drop_duplicates(subset=["CFFDRS"])
fc_df["Code"] = fc_df["National_FBP_Fueltypes_2014"]
## set index
fc_df = fc_df.set_index("CFFDRS")
fc_dict = fc_df.transpose().to_dict()
## Open gridded fuels
fuels_ds = xr.open_zarr(fuelsin)
## Open gridded terrain
terrain_ds = xr.open_dataset(terrain)


## Define Static Variables
ELV, LAT, LON, FUELS = (
    terrain_ds.HGT.values[0, :, :],
    terrain_ds.XLAT.values[0, :, :],
    terrain_ds.XLONG.values[0, :, :] * -1,
    fuels_ds.fuels.values.astype(int),
)
unique, count = np.unique(FUELS, return_counts=True)
count[unique == fc_dict["M3"]["Code"]]
## create zeros array for conditional statements
shape = LAT.shape
zero_full = np.zeros(shape, dtype=float)
zero_full3D = np.zeros(hourly_ds.F.shape, dtype=float)


FMC = zero_full
LATN = zero_full
###################    Foliar Moisture Content:  #######################
########################################################################
FMC = zero_full
## Solve Normalized latitude (degrees) with no terrain data (1)
# LATN = 46 + 23.4 * np.exp(-0.0360 * (150 - terrain_ds.XLONG))

## Solve Julian date of minimum FMC with no terrain data (2)
# D_o = 151 * (terrain_ds.XLAT/LATN)

## Solve Normalized latitude (degrees) with terrain data (3)
LATN = 43 + 33.7 * np.exp(-0.0351 * (150 - LON))

## Solve Julian date of minimum FMC with no terrain data (4)
D_o = 142.1 * (LAT / LATN) + 0.0172 * ELV

## Get day of year or Julian date
D_j = int(date.strftime("%j"))

## Solve Number of days between the current date and D_o (5)
ND = abs(D_j - D_o)

## Solve Foliar moisture content(%) where ND < 30 (6)
FMC = xr.where(ND < 30.0, 85 + 0.0189 * ND ** 2, FMC)
## Solve Foliar moisture content(%) where 30 <= ND < 50 (7)
FMC = xr.where((ND >= 30) & (ND < 50), 32.9 + 3.17 * ND - 0.0288 * ND ** 2, FMC)
## Solve Foliar moisture content(%) where ND >= 50 (8)
FMC = xr.where(ND >= 50, 120, FMC)
FMC = xr.DataArray(FMC, name="FMC", dims=("south_north", "west_east"))
hourly_ds["FMC"] = FMC


###################    Surface Fuel Consumption  #######################
########################################################################
## Define frequently used variables
FFMC, BUI, GFL, PC, PH = daily_ds.F, daily_ds.U, 0.3, 50, 50
SFC = zero_full


def sanitycheck(array, fueltype):
    indx = np.argwhere(FUELS == fc_dict[fueltype]["Code"])
    if len(indx) >= 1:
        point = 0
        test = array.values
        print(test[0, indx[point, 0], indx[point, 1]])
        print(FUELS[indx[point, 0], indx[point, 1]])
        print(FUELS[indx[point, 0], indx[point, 1]] == fc_dict[fueltype]["Code"])
    else:
        print("None Fuel Type Not In Domain")


## Solve Surface Fuel Consumption for C1 Fuels  (9)
SFC = xr.where(
    FUELS == fc_dict["C1"]["Code"],
    xr.where(
        FFMC > 84,
        0.75 + 0.75 * (1 - np.exp(-0.23 * (FFMC - 84))) ** 0.5,
        0.75 - 0.75 * (1 - np.exp(-0.23 * (84 - FFMC))) ** 0.5,
    ),
    SFC,
)

## Solve Fuel Consumption for C2, M3, and M4 Fuels  (10)
SFC = xr.where(
    (FUELS == fc_dict["C2"]["Code"])
    | (FUELS == fc_dict["M3"]["Code"])
    | (FUELS == fc_dict["M4"]["Code"]),
    5.0 * (1 - np.exp(-0.0115 * BUI)),
    SFC,
)

## Solve Fuel Consumption for C3, C4 Fuels  (11)
SFC = xr.where(
    (FUELS == fc_dict["C3"]["Code"]) | (FUELS == fc_dict["C4"]["Code"]),
    5.0 * (1 - np.exp(-0.0164 * BUI)) ** 2.24,
    SFC,
)

## Solve Fuel Consumption for C5, C6 Fuels  (12)
SFC = xr.where(
    (FUELS == fc_dict["C5"]["Code"]) | (FUELS == fc_dict["C6"]["Code"]),
    5.0 * (1 - np.exp(-0.0149 * BUI)) ** 2.48,
    SFC,
)

## Solve Fuel Consumption for C7 Fuels  (13, 14, 15)
SFC = xr.where(
    (FUELS == fc_dict["C7"]["Code"]),
    xr.where(FFMC > 70, 2 * (1 - np.exp(-0.104 * (FFMC - 70))), 0)
    + 1.5 * (1 - np.exp(-0.0201 * BUI)),
    SFC,
)

## Solve Fuel Consumption for D1 Fuels  (16)
SFC = xr.where((FUELS == fc_dict["D1"]["Code"]), 1.5 * (1 - np.exp(-0.0183 * BUI)), SFC)


## Solve Fuel Consumption for M1, M2 Fuels  (17)
SFC = xr.where(
    (FUELS == fc_dict["M1"]["Code"]) | (FUELS == fc_dict["M2"]["Code"]),
    PC / 100 * (5.0 * (1 - np.exp(-0.0115 * BUI)))
    + ((100 - PC) / 100 * (1.5 * (1 - np.exp(-0.0183 * BUI)))),
    SFC,
)


## Solve Fuel Consumption for O1a, O1b Fuels  (18)
SFC = xr.where(
    (FUELS == fc_dict["O1a"]["Code"]) | (FUELS == fc_dict["O1b"]["Code"]), GFL, SFC
)


## Solve Fuel Consumption for S1 Fuels  (19, 20, 25)
SFC = xr.where(
    (FUELS == fc_dict["S1"]["Code"]),
    4.0 * (1 - np.exp(-0.025 * BUI)) + 4.0 * (1 - np.exp(-0.034 * BUI)),
    SFC,
)


## Solve Fuel Consumption for S2 Fuels  (21, 22, 25)
SFC = xr.where(
    (FUELS == fc_dict["S2"]["Code"]),
    10.0 * (1 - np.exp(-0.013 * BUI)) + 6.0 * (1 - np.exp(-0.060 * BUI)),
    SFC,
)


## Solve Fuel Consumption for S3 Fuels  (23, 24, 25)
SFC = xr.where(
    (FUELS == fc_dict["S3"]["Code"]),
    12.0 * (1 - np.exp(-0.0166 * BUI)) + 20.0 * (1 - np.exp(-0.0210 * BUI)),
    SFC,
)

# Remove negative SFC value
SFC = xr.where(SFC <= 0, 1e-6, SFC)
SFC = xr.DataArray(SFC, name="SFC", dims=("time", "south_north", "west_east"))
daily_ds["SFC"] = SFC


###################   Rate of Spread Equations  #######################
#######################################################################
def solve_isi(hourly_ds, fbp=False, zero_ws=False):
    ### Call on initial conditions
    if zero_ws == True:
        W, F, m_o = 0.0, hourly_ds.F, hourly_ds.m_o
    elif zero_ws == False:
        W, F, m_o = hourly_ds.W, hourly_ds.F, hourly_ds.m_o
    else:
        raise ValueError("ERROR: Can Not Solve ISI")
    ### (24) Solve for wind function (f_W) with condition for fbp
    f_W = xr.where(
        (W >= 40) & (fbp == True),
        12 * (1 - np.exp(-0.0818 * (W - 28))),
        np.exp(0.05039 * W),
    )

    ### (25) Solve for fine fuel moisture function (f_F)
    f_F = 91.9 * np.exp(-0.1386 * m_o) * (1 + np.power(m_o, 5.31) / 4.93e7)

    ### (26) Solve for initial spread index (R)
    R = 0.208 * f_W * f_F
    R = xr.DataArray(R, name="R", dims=("time", "south_north", "west_east"))

    return R


## Define frequently used variables
PDF = 35  # percent dead balsam fir default
C = 80  # degree of curing(%)
ISI = hourly_ds.R
ISZ = solve_isi(hourly_ds, fbp=True, zero_ws=True)
hourly_ds["ISZ"] = ISZ


## General Rate of Spread Equation for C-1 to C-5, and C-7 (26)
def solve_rsi(RSI, fueltype, ISI):
    RSI = xr.where(
        FUELS == fc_dict[fueltype]["Code"],
        fc_dict[fueltype]["a"]
        * (1 - np.exp(-fc_dict[fueltype]["b"] * ISI) ** fc_dict[fueltype]["c"]),
        RSI,
    )
    return RSI


RSI = zero_full3D
for i in [1, 2, 3, 4, 5, 7]:
    RSI = solve_rsi(RSI, f"C{i}", ISZ)


## Fuel Type Specific Rate of Spread Equations
##  (M-1 leaftess) (27)
RSI_M1 = (PC / 100 * solve_rsi(zero_full3D, "C2", ISZ)) + (
    PC / 100 * solve_rsi(zero_full3D, "D1", ISZ)
)

##  (M-2 green)   (28)
RSI_M2 = (PC / 100 * solve_rsi(zero_full3D, "C2", ISZ)) + (
    0.2 * (PC / 100 * solve_rsi(zero_full3D, "D1", ISZ))
)

##  (M-3)
fc_dict["M3"]["a"] = 170 * np.exp(-35.0 / PDF)  # (29)
fc_dict["M3"]["b"] = 0.082 * np.exp(-36 / PDF)  # (30)
fc_dict["M3"]["c"] = 1.698 - 0.00303 * PDF  # (31)

RSI_M3 = solve_rsi(zero_full3D, "M3", ISZ)

##  (M-4)
fc_dict["M4"]["a"] = 140 * np.exp(-35.5 / PDF)  # (22)
fc_dict["M4"]["b"] = 0.0404  # (33)
fc_dict["M4"]["c"] = 3.02 * np.exp(-0.00714 * PDF)  # (34)

RSI_M4 = solve_rsi(zero_full3D, "M4", ISZ)


## (O-1A grass) grass curing coefficient (Wotton et. al. 2009)
CF = xr.where(C < 58.8, 0.005 * (np.exp(0.061 * C) - 1), 0.176 + 0.02 * (C - 58.8))

RSI_O1a = xr.where(
    (FUELS == fc_dict["O1a"]["Code"]),
    fc_dict["O1a"]["a"]
    * ((1 - np.exp(-fc_dict["O1a"]["b"] * ISZ)) ** fc_dict["O1a"]["c"])
    * CF,
    zero_full3D,
)

## (O-1B grass) grass curing coefficient (Wotton et. al. 2009)
RSI_O1b = xr.where(
    (FUELS == fc_dict["O1b"]["Code"]),
    fc_dict["O1b"]["a"]
    * ((1 - np.exp(-fc_dict["O1b"]["b"] * ISZ)) ** fc_dict["O1b"]["c"])
    * CF,
    zero_full3D,
)

##  (C-6) Conifer plantation spread rate
T = 1500 - 2.75 * FMC  # (59)
h = 460 + 25.9 * FMC  # (60)
FME = (((1.5 - 0.00275 * FMC) ** 4.0) / (460 + (25.9 * FMC))) * 1000  # (61)
RSI_C6 = 30 * (1 - np.exp(-0.08 * ISZ)) ** 3.0  # (62)


## Surface spread rate with zero wind on level terrain
RSZ = RSI + RSI_M1 + RSI_M2 + RSI_M3 + RSI_M4 + RSI_O1a + RSI_O1b + RSI_C6


###################   Effect of Slope on Rate of Spread  #######################
################################################################################
## Define frequently used variables
dx, dy = float(hourly_ds.attrs["DX"]), float(hourly_ds.attrs["DY"])


## Solve Percent Ground Slope (37)
## Take gradient of x and y
gradient = np.gradient(ELV)
y_grad = gradient[0]
x_grad = gradient[1]
## Now solve GS
GS = 100 * np.sqrt((x_grad / dx) ** 2 + (y_grad / dy) ** 2)


## Solve Factor, Upslope (39)
## NOTE they use have another condition in the R code: if GS >= 70 SF = 10
## Also they don't have the GS<60 condition in the code..not sure why
SF = xr.where(GS < 60, 3.533 * ((GS / 100) ** 1.2), zero_full)

## Surface spread rate with zero wind, upslope (40)
RSF = RSZ * SF


## Solve ISF (ie ISI, with zero wind upslope) (41)
def solve_isf(ISF, fueltype, RSF):
    ISF = xr.where(
        FUELS == fc_dict[fueltype]["Code"],
        np.log(1 - (RSF / fc_dict[fueltype]["a"]) ** (1 / fc_dict[fueltype]["c"]))
        / -fc_dict[fueltype]["b"],
        ISF,
    )
    return ISF


ISF = zero_full3D
for fueltype in ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "D1", "S1", "S2", "S3"]:
    ISF = solve_isf(ISF, fueltype, RSF)


SAZ = np.arctan(np.sqrt((x_grad / dx) / (y_grad / dy)))
ind = np.where(np.isnan(SAZ))


# test_elv = np.array([[2, 0, 0, 0], [1, 2, 3, 4]])
# test_gradient = np.gradient(test_elv)
