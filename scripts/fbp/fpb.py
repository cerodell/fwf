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
date = pd.Timestamp(2018, 7, 18)
domain = "d02"
wrf_model = "wrf3"

## Path to hourly/daily fwi data
forecast_date = date.strftime("%Y%m%d06")
# hourly_file_dir = (
#     str(data_dir) + f"/FWF-WAN00CP-04/fwf-hourly-{domain}-{forecast_date}.zarr"
# )
hourly_file_dir = str(fwf_zarr_dir) + str(f"/fwf-hourly-{domain}-{forecast_date}.zarr")

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
ELV, LAT, LON, FUELS, WD, dx, dy = (
    terrain_ds.HGT.values[0, :, :],
    terrain_ds.XLAT.values[0, :, :],
    terrain_ds.XLONG.values[0, :, :] * -1,
    fuels_ds.fuels.values.astype(int),
    hourly_ds.WD,
    float(hourly_ds.attrs["DX"]),
    float(hourly_ds.attrs["DY"]),
)

# unique, count = np.unique(FUELS, return_counts=True)
# count[unique == fc_dict["M3"]["Code"]]

## create zeros array for easy conditional statements
shape = LAT.shape
zero_full = np.zeros(shape, dtype=float)
zero_full3D = np.zeros(hourly_ds.F.shape, dtype=float)
zero_full3D_daily = np.zeros(daily_ds.U.shape, dtype=float)


## Convert Wind Direction from degrees to radians
WD = WD * np.pi / 180

## Reorient to Wind Azimuth (WAZ)
WAZ = WD + np.pi
WAZ = xr.where(WAZ > 2 * np.pi, WAZ - 2 * np.pi, WAZ)

## Take gradient dz/dx and dz/dy of elevation
gradient = np.gradient(ELV)
y_grad = gradient[0]
x_grad = gradient[1]

## Solve Percent Ground Slope (37)
GS = 100 * np.sqrt((x_grad / dx) ** 2 + (y_grad / dy) ** 2)

# Solve for slope Aspect
ASPECT = np.arctan2((y_grad / dy), -(x_grad / dx)) * (180 / np.pi)


# Solve for Uphill slope Azimuth Angle (SAZ)
SAZ = np.where(
    ASPECT < 0,
    90.0 - ASPECT,
    np.where(ASPECT > 90.0, 360.0 - ASPECT + 90.0, 90.0 - ASPECT),
)

# SAZ = np.where(SAZ == 360, 0, SAZ)


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
FFMC, BUI, GFL, PC, PH = hourly_ds.F, daily_ds.U, 0.3, 50, 50
index = [i for i in range(1, len(FFMC) + 1) if i % 24 == 0]
BUI_i = BUI.values
BUI_day1 = np.stack([BUI_i[0]] * index[0])
BUI_day2 = np.stack([BUI_i[1]] * (len(FFMC) - index[0]))
BUI = np.vstack([BUI_day1, BUI_day2])

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
hourly_ds["SFC"] = SFC


###################   Rate of Spread Equations  #######################
#######################################################################
def solve_isi(hourly_ds, W, fbp=False):
    W, F, m_o = W, hourly_ds.F, hourly_ds.m_o

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
ISZ = solve_isi(hourly_ds, W=0, fbp=True)
hourly_ds["ISZ"] = ISZ
## (O-1A grass) grass curing coefficient (Wotton et. al. 2009)
CF = xr.where(C < 58.8, 0.005 * (np.exp(0.061 * C) - 1), 0.176 + 0.02 * (C - 58.8))

## General Rate of Spread Equation for C-1 to C-5, and C-7 (26)
def solve_gen_ros(ROS, fueltype, ISI):
    ROS = xr.where(
        FUELS == fc_dict[fueltype]["Code"],
        fc_dict[fueltype]["a"]
        * (1 - np.exp(-fc_dict[fueltype]["b"] * ISI) ** fc_dict[fueltype]["c"]),
        ROS,
    )
    return ROS


def solve_ros(ISI, FMC, PDF, fc_dict, *args):
    ROS = zero_full3D
    for i in [1, 2, 3, 4, 5, 7]:
        ROS = solve_gen_ros(ROS, f"C{i}", ISI)

    ## Fuel Type Specific Rate of Spread Equations
    ##  (M-1 leaftess) (27)
    ROS_M1 = (PC / 100 * solve_gen_ros(zero_full3D, "C2", ISI)) + (
        PC / 100 * solve_gen_ros(zero_full3D, "D1", ISI)
    )

    ##  (M-2 green)   (28)
    ROS_M2 = (PC / 100 * solve_gen_ros(zero_full3D, "C2", ISI)) + (
        0.2 * (PC / 100 * solve_gen_ros(zero_full3D, "D1", ISI))
    )

    ##  (M-3)
    fc_dict["M3"]["a"] = 170 * np.exp(-35.0 / PDF)  # (29)
    fc_dict["M3"]["b"] = 0.082 * np.exp(-36 / PDF)  # (30)
    fc_dict["M3"]["c"] = 1.698 - 0.00303 * PDF  # (31)

    ROS_M3 = solve_gen_ros(zero_full3D, "M3", ISI)

    ##  (M-4)
    fc_dict["M4"]["a"] = 140 * np.exp(-35.5 / PDF)  # (22)
    fc_dict["M4"]["b"] = 0.0404  # (33)
    fc_dict["M4"]["c"] = 3.02 * np.exp(-0.00714 * PDF)  # (34)

    ROS_M4 = solve_gen_ros(zero_full3D, "M4", ISI)

    ROS_O1a = xr.where(
        (FUELS == fc_dict["O1a"]["Code"]),
        fc_dict["O1a"]["a"]
        * ((1 - np.exp(-fc_dict["O1a"]["b"] * ISI)) ** fc_dict["O1a"]["c"])
        * CF,
        zero_full3D,
    )

    ## (O-1B grass) grass curing coefficient (Wotton et. al. 2009)
    ROS_O1b = xr.where(
        (FUELS == fc_dict["O1b"]["Code"]),
        fc_dict["O1b"]["a"]
        * ((1 - np.exp(-fc_dict["O1b"]["b"] * ISI)) ** fc_dict["O1b"]["c"])
        * CF,
        zero_full3D,
    )

    if args:
        ## Surface spread rate
        ROS = ROS + ROS_M1 + ROS_M2 + ROS_M3 + ROS_M4 + ROS_O1a + ROS_O1b
        ROS = ROS * BE
    else:
        ROS = ROS + ROS_M1 + ROS_M2 + ROS_M3 + ROS_M4 + ROS_O1a + ROS_O1b

    return ROS


def solve_c6(ISI, FMC, fc_dict, *args):
    ##  (C-6) Conifer plantation spread rate
    T = 1500 - 2.75 * FMC  # (59)
    h = 460 + 25.9 * FMC  # (60)
    FME = (((1.5 - 0.00275 * FMC) ** 4.0) / (460 + (25.9 * FMC))) * 1000  # (61)

    ROS_C6 = xr.where(
        (FUELS == fc_dict["C6"]["Code"]),
        30 * (1 - np.exp(-0.08 * ISI)) ** 3.0,
        zero_full3D,
    )

    if args:
        ## (63)
        RSS = ROS_C6 * BE
        ## (64)
        RSC = xr.where(
            (FUELS == fc_dict["C6"]["Code"]),
            60 * (1 - np.exp(-0.0497 * ISI)) ** 1.0 * (FME / 0.778),
            zero_full3D,
        )
        ## (56)
        CSI = 0.001 * (fc_dict["C6"]["Code"] ** 1.5) * (460 + 25.9 * FMC) ** 1.5
        ## (57)
        RSO = CSI / (300 * SFC)
        ## (58)
        CFB = 1 - np.exp(-0.23 * (ROS_C6 - RSO))
        ## (65)
        ROS = xr.where(
            (FUELS == fc_dict["C6"]["Code"]), RSS + CFB * (RSC - RSS), zero_full3D
        )
    else:
        ROS = ROS_C6

    return ROS


## Surface spread rate with zero wind on level terrain
RSZ = solve_ros(ISZ, FMC, PDF, fc_dict)
RSZ_C6 = solve_c6(ISZ, FMC, fc_dict)
RSZ = RSZ + RSZ_C6


###################   Effect of Slope on Rate of Spread  #######################
################################################################################
WS = hourly_ds.W

## Solve Factor, Upslope (39)
## NOTE they use have another condition in the R code: if GS >= 70 SF = 10
## Also they don't have the GS<60 condition in the code..not sure why
SF = xr.where(GS < 60, 3.533 * ((GS / 100) ** 1.2), zero_full)

## Surface spread rate with zero wind, upslope (40)
RSF = RSZ * SF

## Solve ISF (ie ISI, with zero wind upslope) for the majority of fuels (41)
## NOTE adjusted base don 41a, 41b (Wotton 2009)
def solve_isf(ISF, fueltype, RSF):
    ISF = xr.where(
        FUELS == fc_dict[fueltype]["Code"],
        xr.where(
            (1 - (RSF / fc_dict[fueltype]["a"]) ** (1 / fc_dict[fueltype]["c"]))
            >= 0.01,
            np.log(1 - (RSF / fc_dict[fueltype]["a"]) ** (1 / fc_dict[fueltype]["c"]))
            / -fc_dict[fueltype]["b"],
            np.log(0.01) / -fc_dict[fueltype]["b"],
        ),
        ISF,
    )
    return ISF


ISF = zero_full3D
for fueltype in ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "D1", "S1", "S2", "S3"]:
    ISF = solve_isf(ISF, fueltype, RSF)


unique, count = np.unique(np.isnan(RSF), return_counts=True)

## Solve ISF (ie ISI, with zero wind upslope) for M1 and M2 (42)
ISF_M1M2 = xr.where(
    (FUELS == fc_dict["M1"]["Code"]) | (FUELS == fc_dict["M2"]["Code"]),
    np.log(1 - ((100 - RSF) / (PC * fc_dict["C2"]["a"])) ** (1 / fc_dict["C2"]["c"]))
    / -fc_dict["C2"]["b"],
    zero_full3D,
)

## Solve ISF (ie ISI, with zero wind upslope) for O1a and O1b (grass)(43)
ISF_O1a = xr.where(
    (FUELS == fc_dict["O1a"]["Code"]),
    np.log(1 - (RSF / (CF * fc_dict["O1a"]["a"])) ** (1 / fc_dict["O1a"]["c"]))
    / -fc_dict["O1a"]["b"],
    zero_full3D,
)

ISF_O1b = xr.where(
    (FUELS == fc_dict["O1b"]["Code"]),
    np.log(1 - (RSF / (CF * fc_dict["O1b"]["a"])) ** (1 / fc_dict["O1b"]["c"]))
    / -fc_dict["O1b"]["b"],
    zero_full3D,
)

## Combine all ISFs (ie ISI, with zero wind upslope)
ISF = ISF + ISF_M1M2 + ISF_O1a + ISF_O1b

### (25) Solve for fine fuel moisture function (f_F)
m_o = hourly_ds.m_o
f_F = 91.9 * np.exp(-0.1386 * m_o) * (1 + ((m_o ** 5.31) / 4.93e7))
# f_F = xr.where(f_F < 0.001, 0.1, f_F)
## Compute the slope equivalent wind speed (WSE) (44)
WSE = xr.where(ISF > 0.1, np.log(ISF / (0.208 * f_F)) / 0.05039, zero_full3D)

## Net vectored wind speed in the x-direction (47)
WSX = (WS * np.sin(WAZ)) + (WSE * np.sin(SAZ * (np.pi / 180)))

## Net vectored wind speed in they-direction (48)
WSY = (WS * np.cos(WAZ)) + (WSE * np.cos(SAZ * (np.pi / 180)))

## Net vectored wind speed (49_
WSV = np.sqrt(WSX ** 2 + WSY ** 2)
GS_stacked = np.stack([GS, GS])
WSV = np.where((GS > 0) & (FFMC > 0), WSV, WS)

## Spread direction azimuth and convert from radians to degrees (50)
RAZ = np.arccos(WSY / WSV) * 180 / np.pi
## Convert RAZ values at locations of negative WSX to account for the full compas direction of movement. (51)
RAZ = xr.where(WSX < 0, 360 - RAZ, RAZ)

## Solve ISI equation (from the FWI System) (52, 53, 53a)
ISI = solve_isi(hourly_ds, WSV, fbp=True)
hourly_ds["ISI"] = ISI


###########   BUI Effect on Surface Fire Rate of Spread  #############
#######################################################################
## Buildup effect on spread rate (54)
def solve_be(BE, fueltype, BUI):
    BE = xr.where(
        FUELS == fc_dict[fueltype]["Code"],
        xr.where(
            (BUI > 0) & (fc_dict[fueltype]["BUI_o"] > 0),
            np.exp(
                50
                * np.log(fc_dict[fueltype]["q"])
                * (1 / BUI - 1 / fc_dict[fueltype]["BUI_o"])
            ),
            1,
        ),
        BE,
    )
    return BE


BE = zero_full3D
for fueltype in fc_df.index.values[:-8]:
    BE = solve_be(BE, fueltype, BUI)

ROS = solve_ros(ISI, FMC, PDF, fc_dict, BE)
ROS_C6 = solve_c6(ISI, FMC, fc_dict, BE)
ROS = ROS + ROS_C6
ROS = xr.where(ROS < 0, 0.0, ROS)
hourly_ds["ROS"] = ROS
hourly_ds["ROS"].attrs = {
    "FieldType": 104,
    "MemoryOrder": "XY ",
    "description": "Rate of Spread",
    "projection": "PolarStereographic(stand_lon=-110.0, moad_cen_lat=53.99999237060547, truelat1=57.0, truelat2=90.0, pole_lat=90.0, pole_lon=0.0)",
    "stagger": "",
    "units": "m min^-1",
}
################   Critical Surface Fire Intensity  ###################
#######################################################################


def solve_cfb(CFB, ROS, fueltype, FMC):
    ## Solve Critical surface intensity for crowning (56)
    CSI = 0.001 * (fc_dict[fueltype]["Code"] ** 1.5) * (460 + 25.9 * FMC) ** 1.5
    ## Solve Critical spread rate for crowning (57)
    RSO = CSI / (300 * SFC)
    ## Solve Crown fraction burned (58)
    CFB_i = xr.where(ROS > RSO, 1 - np.exp(-0.23 * (ROS - RSO)), CFB)
    CFB = xr.where(FUELS == fc_dict[fueltype]["Code"], CFB_i, CFB)
    return CFB


CFB = 0
for fueltype in fc_df.index.values[:-8]:
    CFB = solve_cfb(CFB, ROS, fueltype, FMC)
hourly_ds["CFB"] = CFB
hourly_ds["CFB"].attrs = {
    "FieldType": 104,
    "MemoryOrder": "XY ",
    "description": "Crown Fraction Burned",
    "projection": "PolarStereographic(stand_lon=-110.0, moad_cen_lat=53.99999237060547, truelat1=57.0, truelat2=90.0, pole_lat=90.0, pole_lon=0.0)",
    "stagger": "",
    "units": "%",
}
#####################   Total Fuel Consumption  #######################
#######################################################################


def solve_tfc(TFC, fueltype, CFB):
    CFC = fc_dict[fueltype]["CFL"] * CFB
    TFC = xr.where(FUELS == fc_dict[fueltype]["Code"], SFC + CFC, TFC)
    return TFC


TFC = 0
for fueltype in fc_df.index.values[:-8]:
    TFC = solve_tfc(TFC, fueltype, CFB)
hourly_ds["TFC"] = TFC
hourly_ds["TFC"].attrs = {
    "FieldType": 104,
    "MemoryOrder": "XY ",
    "description": "Total Fuel Consumption",
    "projection": "PolarStereographic(stand_lon=-110.0, moad_cen_lat=53.99999237060547, truelat1=57.0, truelat2=90.0, pole_lat=90.0, pole_lon=0.0)",
    "stagger": "",
    "units": "kg m^-2",
}

#########################   Fire Intensity  ###########################
#######################################################################

HFI = 300 * TFC * ROS
hourly_ds["HFI"] = HFI
hourly_ds["HFI"].attrs = {
    "FieldType": 104,
    "MemoryOrder": "XY ",
    "description": "Head Fire Intensity",
    "projection": "PolarStereographic(stand_lon=-110.0, moad_cen_lat=53.99999237060547, truelat1=57.0, truelat2=90.0, pole_lat=90.0, pole_lon=0.0)",
    "stagger": "",
    "units": "kW m^-1",
}


save_test = str(data_dir) + f"/test/fpb-{domain}-{forecast_date}.zarr"
hourly_ds.to_zarr(save_test, mode="w")

print("Total Run Time: ", datetime.now() - startTime)
