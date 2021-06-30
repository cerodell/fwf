#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python


import context
import math
import json
import numpy as np
import pandas as pd
import xarray as xr
from numba import vectorize


from pathlib import Path

# from netCDF4 import Dataset
from datetime import datetime
from utils.read_wrfout import readwrf
from context import data_dir, fwf_dir

import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

wrf_model = "wrf4"
domain = "d02"
forecast_date = "2021062306"
hourly_ds = xr.open_dataset(str(fwf_dir) + f"/fwf-hourly-{domain}-{forecast_date}.nc")
og_ds = hourly_ds

hourly_ds = hourly_ds.drop_vars(["HFI", "TFC", "ROS", "SFC", "ISI", "CFB", "FMC"])
daily_ds = xr.open_dataset(str(fwf_dir) + f"/fwf-daily-{domain}-{forecast_date}.nc")


def rechunk(ds):
    ds = ds.load()
    ds = ds.chunk(chunks="auto")
    ds = ds.unify_chunks()
    return ds


def solve_isi(hourly_ds, W, fbp=False):
    """
    Calculates the hourly initial spread index

    Parameters
    ----------
    hourly_ds: DataSet
        - Dataset of hourly forecast variables
            - W: DataArray
                - Wind speed, km/hr
            - F: DataArray
                - Fine fuel moisture code
            - R: DataArray
                - Initial spread index

    Returns
    -------
    R: DataArray
        - Datarray of ISI
    """
    ### Call on initial conditions
    W, F, m_o = hourly_ds.W, hourly_ds.F, hourly_ds.m_o

    ########################################################################
    ### (24) Solve for wind function (f_W) with condition for fbp
    f_W = xr.where(
        (W >= 40) & (fbp == True),
        12 * (1 - np.exp(-0.0818 * (W - 28))),
        np.exp(0.05039 * W),
    )

    ########################################################################
    ### (25) Solve for fine fuel moisture function (f_F)
    f_F = 91.9 * np.exp(-0.1386 * m_o) * (1 + np.power(m_o, 5.31) / 4.93e7)

    ########################################################################
    ### (26) Solve for initial spread index (R)
    R = 0.208 * f_W * f_F
    R = xr.DataArray(R, name="R", dims=("time", "south_north", "west_east"))

    return R


## Open gridded static
static_ds = xr.open_dataset(
    str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}.nc"
)

(ELV, LAT, LON, FUELS, GS, SAZ, PC) = (
    static_ds.HGT.values,
    static_ds.XLAT.values,
    static_ds.XLONG.values * -1,
    static_ds.FUELS.values.astype(int),
    static_ds.GS.values,
    static_ds.SAZ.values,
    static_ds.PC.values,
)

unique = np.unique(FUELS)


FBPloopTime = datetime.now()
print("Start of FBP")
## Open fuels converter
PRPloopTime = datetime.now()
# hourly_ds = rechunk(hourly_ds)
fc_df = pd.read_csv(str(data_dir) + "/fbp/fuel_converter.csv")
fc_df = fc_df.drop_duplicates(subset=["CFFDRS"])
fc_df["Code"] = fc_df["FWF_Code"]
# drop fuels not in our domain
drop_fuels = list(set(fc_df["Code"].values) - set(unique))
for code in drop_fuels:
    fc_df = fc_df[fc_df["Code"] != code]

## strip unneeded charaters
fc_df.loc[fc_df["CFFDRS"] == "M1 C25%", "CFFDRS"] = "M1"
fc_df = fc_df[~fc_df["CFFDRS"].str.contains("M1/")]
fc_df = fc_df.set_index("CFFDRS")
## convert to dictionary
fc_dict = fc_df.transpose().to_dict()

# daily_ds = rechunk(daily_ds)
print(f"PRP run time {datetime.now() - PRPloopTime}")

INTloopTime = datetime.now()


C1 = FUELS == fc_dict["C1"]["Code"]
# # test = np.ix_(C1[0],C1[1])
# # C1 = tuple(list(zip(*C1)))


## Define Static Variables
WD, dx, dy = (
    hourly_ds.WD,
    float(hourly_ds.DX),
    float(hourly_ds.DY),
)

zero_full = np.zeros(LAT.shape, dtype=float)
zero_full3D = np.zeros(hourly_ds.F.shape, dtype=float)
date = str(np.datetime_as_string(hourly_ds.Time.values[0], unit="D"))
## Convert Wind Direction from degrees to radians
WD = WD * np.pi / 180

## Reorient to Wind Azimuth (WAZ)
WAZ = WD + np.pi
WAZ = xr.where(WAZ > 2 * np.pi, WAZ - 2 * np.pi, WAZ)
print(f"INT run time {datetime.now() - INTloopTime}")

###################    Foliar Moisture Content:  #######################
########################################################################
FMCloopTime = datetime.now()
## Solve Normalized latitude (degrees) with terrain data (3)
LATN = 43 + 33.7 * np.exp(-0.0351 * (150 - LON))

## Solve Julian date of minimum FMC with terrain data (4)
D_o = 142.1 * (LAT / LATN) + 0.0172 * ELV

## Get day of year or Julian date
date = pd.Timestamp(date)

D_j = int(date.strftime("%j"))

## Solve Number of days between the current date and D_o (5)
ND = abs(D_j - D_o)

## Solve Foliar moisture content(%) where ND < 30 (6)
FMC = zero_full
FMC = xr.where(ND < 30.0, 85 + 0.0189 * ND ** 2, FMC)
## Solve Foliar moisture content(%) where 30 <= ND < 50 (7)
FMC = xr.where((ND >= 30) & (ND < 50), 32.9 + 3.17 * ND - 0.0288 * ND ** 2, FMC)
## Solve Foliar moisture content(%) where ND >= 50 (8)
FMC = xr.where(ND >= 50, 120, FMC)
FMC = xr.DataArray(FMC, name="FMC", dims=("south_north", "west_east"))
hourly_ds["FMC"] = FMC.astype(dtype="float32")
print(f"FMC run time {datetime.now() - FMCloopTime}")


###################    Surface Fuel Consumption  #######################
########################################################################
SFCloopTime = datetime.now()

## Define frequently used variables
FFMC, BUI, GFL, PH = hourly_ds.F, daily_ds.U, 0.3, 50
index = [i for i in range(1, len(FFMC) + 1) if i % 24 == 0]
## Build a BUI datarray fo equal length to hourly forecast bisecting is by day
BUI_i = BUI.values
try:
    BUI_day1 = np.stack([BUI_i[0]] * index[0])
    BUI_day2 = np.stack([BUI_i[1]] * (len(FFMC) - index[0]))
    BUI = np.vstack([BUI_day1, BUI_day2])
except:
    BUI = np.stack([BUI_i[0]] * len(FFMC))
    print(len(BUI))

BUI = xr.DataArray(BUI, name="BUI", dims=("time", "south_north", "west_east"))
# hourly_ds["BUI"] = BUI

## Solve Surface Fuel Consumption for C1 Fuels adjusted from (Wotton et. al. 2009) (9)
SFC = zero_full3D
# SFC = xr.DataArray(zero_full3D, name="SFC", dims=("time", "south_north", "west_east"))


SFC = xr.where(
    FUELS == fc_dict["C1"]["Code"],
    xr.where(
        FFMC > 84,
        0.75 + 0.75 * (1 - np.exp(-0.23 * (FFMC - 84))) ** 0.5,
        0.75 - 0.75 * (1 - np.exp(-0.23 * (84 - FFMC))) ** 0.5,
    ),
    SFC,
)

# SFC[:,C1[:,0],C1[0,:]] = xr.where(
#         FFMC > 84,
#         0.75 + 0.75 * (1 - np.exp(-0.23 * (FFMC - 84))) ** 0.5,
#         0.75 - 0.75 * (1 - np.exp(-0.23 * (84 - FFMC))) ** 0.5,
#     )

## Solve Fuel Consumption for C2, M3, and M4 Fuels  (10)
SFC = xr.where(
    (FUELS == fc_dict["C2"]["Code"]),
    # | (FUELS == fc_dict["M3"]["Code"])
    # | (FUELS == fc_dict["M4"]["Code"]),
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
    (FUELS == fc_dict["M1"]["Code"]),  # | (FUELS == fc_dict["M2"]["Code"]),
    PC / 100 * (5.0 * (1 - np.exp(-0.0115 * BUI)))
    + ((100 - PC) / 100 * (1.5 * (1 - np.exp(-0.0183 * BUI)))),
    SFC,
)

## Solve Fuel Consumption for O1a, O1b Fuels  (18)
SFC = xr.where(
    (FUELS == fc_dict["O1a"]["Code"]) | (FUELS == fc_dict["O1b"]["Code"]),
    GFL,
    SFC,
)

# ## Solve Fuel Consumption for S1 Fuels  (19, 20, 25)
# SFC = xr.where(
#     (FUELS == fc_dict["S1"]["Code"]),
#     4.0 * (1 - np.exp(-0.025 * BUI)) + 4.0 * (1 - np.exp(-0.034 * BUI)),
#     SFC,
# )

# ## Solve Fuel Consumption for S2 Fuels  (21, 22, 25)
# SFC = xr.where(
#     (FUELS == fc_dict["S2"]["Code"]),
#     10.0 * (1 - np.exp(-0.013 * BUI)) + 6.0 * (1 - np.exp(-0.060 * BUI)),
#     SFC,
# )

# ## Solve Fuel Consumption for S3 Fuels  (23, 24, 25)
# SFC = xr.where(
#     (FUELS == fc_dict["S3"]["Code"]),
#     12.0 * (1 - np.exp(-0.0166 * BUI)) + 20.0 * (1 - np.exp(-0.0210 * BUI)),
#     SFC,
# )

# Remove negative SFC value
SFC = xr.where(SFC <= 0, 0.01, SFC)
# SFC = xr.DataArray(SFC, name="SFC", dims=("time", "south_north", "west_east"))
hourly_ds["SFC"] = SFC.astype(dtype="float32")
print(f"SFC run time {datetime.now() - SFCloopTime}")


## Define frequently used variables
PDF = 35  # percent dead balsam fir default
C = 80  # degree of curing(%)
# ISI = hourly_ds.R
ISZ = solve_isi(hourly_ds, W=0, fbp=True)
# hourly_ds["ISZ"] = ISZ.astype(dtype="float32")

## (O-1A grass) grass curing coefficient (Wotton et. al. 2009)
CF = xr.where(C < 58.8, 0.005 * (np.exp(0.061 * C) - 1), 0.176 + 0.02 * (C - 58.8))

## General Rate of Spread Equation for C-1 to C-5, and C-7 (26)
def solve_gen_ros(ROS, fueltype, ISI):
    func = lambda ROS, fueltype, ISI: xr.where(
        FUELS == fc_dict[fueltype]["Code"],
        fc_dict[fueltype]["a"]
        * ((1 - np.exp(-fc_dict[fueltype]["b"] * ISI)) ** fc_dict[fueltype]["c"]),
        ROS,
    )
    return xr.apply_ufunc(func, ROS, fueltype, ISI)


# def solve_gen_ros(ROS, fueltype, ISI):
#     ROS = xr.where(
#         FUELS == fc_dict[fueltype]["Code"],
#         fc_dict[fueltype]["a"]
#         * (
#             (1 - np.exp(-fc_dict[fueltype]["b"] * ISI))
#             ** fc_dict[fueltype]["c"]
#         ),
#         ROS,
#     )
#     return ROS


def solve_M_ros(fueltype, ISI):
    ROS = fc_dict[fueltype]["a"] * (
        (1 - np.exp(-fc_dict[fueltype]["b"] * ISI)) ** fc_dict[fueltype]["c"]
    )
    return ROS


def solve_ros(ISI, FMC, PDF, fc_dict, *args):
    ##  (M-3)
    # fc_dict["M3"]["a"] = 170 * np.exp(-35.0 / PDF)  # (29)
    # fc_dict["M3"]["b"] = 0.082 * np.exp(-36 / PDF)  # (30)
    # fc_dict["M3"]["c"] = 1.698 - 0.00303 * PDF  # (31)

    # ##  (M-4)
    # fc_dict["M4"]["a"] = 140 * np.exp(-35.5 / PDF)  # (22)
    # fc_dict["M4"]["b"] = 0.0404  # (33)
    # fc_dict["M4"]["c"] = 3.02 * np.exp(-0.00714 * PDF)  # (34)

    ROS = zero_full3D
    for fueltype in [
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "C7",
        "D1",
        # "S1",
        # "S2",
        # "S3",
        # "M3",
        # "M4",
    ]:
        ROS = solve_gen_ros(ROS, fueltype, ISI)

    ## Fuel Type Specific Rate of Spread Equations
    ##  (M-1 leaftess) (27)
    ROS_M1 = xr.where(
        FUELS == fc_dict["M1"]["Code"],
        ((PC / 100) * solve_M_ros("C2", ISI)) + ((PC / 100) * solve_M_ros("D1", ISI)),
        zero_full3D,
    )

    # ##  (M-2 green)   (28)
    # ROS_M2 = xr.where(
    #     FUELS == fc_dict["M2"]["Code"],
    #     ((PC / 100) * solve_M_ros("C2", ISI))
    #     + (0.2 * ((PC / 100) * solve_M_ros("D1", ISI))),
    #     zero_full3D,
    # )

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
        ROS = ROS + ROS_M1 + ROS_O1a + ROS_O1b
        # ROS = ROS + ROS_M1 + ROS_M2 + ROS_O1a + ROS_O1b
        ROS = ROS * BE
    else:
        ROS = ROS + ROS_M1 + ROS_O1a + ROS_O1b
        # ROS = ROS + ROS_M1 + ROS_M2 + ROS_O1a + ROS_O1b

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
        CSI = 0.001 * (fc_dict["C6"]["CBH"] ** 1.5) * (460 + 25.9 * FMC) ** 1.5
        ## (57)
        RSO = CSI / (300 * SFC)
        ## (58)
        CFB = xr.where(RSS > RSO, 1 - np.exp(-0.23 * (RSS - RSO)), 0)
        CFB = xr.where(CFB < 0, 0.0, CFB)
        # CFB = 1 - np.exp(-0.23 * (ROS_C6 - RSO))
        ## (65)
        ROS = np.where(
            FUELS == fc_dict["C6"]["Code"], RSS + CFB * (RSC - RSS), zero_full3D
        )
    else:
        ROS = ROS_C6

    return ROS


RSZloopTime = datetime.now()
## Surface spread rate with zero wind on level terrain
RSZ = solve_ros(ISZ, FMC, PDF, fc_dict)
RSZ_C6 = solve_c6(ISZ, FMC, fc_dict)
RSZ = RSZ + RSZ_C6
# hourly_ds["RSZ"] = RSZ

###################   Effect of Slope on Rate of Spread  #######################
################################################################################
RSFloopTime = datetime.now()

WS = hourly_ds.W

## Solve Factor, Upslope (39)
## NOTE they use have another condition in the R code: if GS >= 70 SF = 10
## Also they don't have the GS<60 condition in the code..not sure why
SF = xr.where(GS < 60, np.exp(3.533 * ((GS / 100) ** 1.2)), zero_full)

## Surface spread rate with zero wind, upslope (40)
RSF = RSZ * SF
# hourly_ds["RSF"] = RSF.astype(dtype="float32")
print(f"RSF run time {datetime.now() - RSFloopTime}")
ISIloopTime = datetime.now()

## Solve ISF (ie ISI, with zero wind upslope) for the majority of fuels (41)
## NOTE adjusted base don 41a, 41b (Wotton 2009)


def solve_isf(ISF, fueltype, RSF):
    func = lambda ISF, fueltype, RSF: xr.where(
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
    return xr.apply_ufunc(func, ISF, fueltype, RSF)


ISF = zero_full3D
for fueltype in [
    "C1",
    "C2",
    "C3",
    "C4",
    "C5",
    "C6",
    "C7",
    "D1",
    # "S1",
    # "S2",
    # "S3",
]:
    ISF = solve_isf(ISF, fueltype, RSF)

## Solve ISF (ie ISI, with zero wind upslope) for M1 and M2 (42)
ISF_M1M2 = xr.where(
    (FUELS == fc_dict["M1"]["Code"]),  # | (FUELS == fc_dict["M2"]["Code"]),
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
# hourly_ds["ISF"] = ISF.astype(dtype="float32")

### (25) Solve for fine fuel moisture function (f_F)
m_o = hourly_ds.m_o
f_F = 91.9 * np.exp(-0.1386 * m_o) * (1 + ((m_o ** 5.31) / 4.93e7))
f_F = xr.where(f_F < 0.0, 0.1, f_F)

## Compute the slope equivalent wind speed (WSE) (44)
WSE = xr.where(ISF > 0.1, np.log(ISF / (0.208 * f_F)) / 0.05039, zero_full3D)
# print('WSE ',np.mean(WSE.values))

# NOTE Adjusted Slope equivalent wind speed (44b 44e) (Wotton 2009)
WSE = xr.where(
    (WSE > 40) & (ISF < (0.999 * 2.496 * f_F)),
    28 - (1 / 0.0818 * np.log(1 - ISF / (2.496 * f_F))),
    WSE,
)

# NOTE Adjusted Slope equivalent wind speed (44c) (Wotton 2009)
WSE = xr.where((WSE > 40) & (ISF >= (0.999 * 2.496 * f_F)), 112.45, WSE)
# print('WSE ',np.mean(WSE.values))

## Net vectored wind speed in the x-direction (47)
WSX = (WS * np.sin(WAZ)) + (WSE * np.sin(SAZ * (np.pi / 180)))

## Net vectored wind speed in they-direction (48)
WSY = (WS * np.cos(WAZ)) + (WSE * np.cos(SAZ * (np.pi / 180)))

## Net vectored wind speed (49)
WSV = np.sqrt(WSX ** 2 + WSY ** 2)
WSV = np.where((GS > 0) & (FFMC > 0), WSV, WS)

## Spread direction azimuth and convert from radians to degrees (50)
RAZ = np.arccos(WSY / WSV) * 180 / np.pi
## Convert RAZ values at locations of negative WSX to account for the full compass circle. (51)
RAZ = xr.where(WSX < 0, 360 - RAZ, RAZ)

## Solve ISI equation (from the FWI System) (52, 53, 53a)
ISI = solve_isi(hourly_ds, WSV, fbp=True)

hourly_ds["ISI"] = ISI.astype(dtype="float32")
print(f"ISI run time {datetime.now() - ISIloopTime}")

###########   BUI Effect on Surface Fire Rate of Spread  #############
#######################################################################
## Buildup effect on spread rate (54)
BEloopTime = datetime.now()


def solve_be(BE, fueltype, BUI):
    func = lambda BE, fueltype, BUI: xr.where(
        FUELS == fc_dict[fueltype]["Code"],
        xr.where(
            (BUI > 0) & (fc_dict[fueltype]["BUI_o"] > 0),
            np.exp(
                50
                * np.log(fc_dict[fueltype]["q"])
                * ((1 / BUI) - (1 / fc_dict[fueltype]["BUI_o"]))
            ),
            1,
        ),
        BE,
    )
    return xr.apply_ufunc(func, BE, fueltype, BUI)


BE = zero_full3D
for fueltype in fc_df.index.values[:-8]:
    BE = solve_be(BE, fueltype, BUI)
print(f"BE run time {datetime.now() - BEloopTime}")

ROSloopTime = datetime.now()
ROS = solve_ros(ISI, FMC, PDF, fc_dict, BE)
ROS_C6 = solve_c6(ISI, FMC, fc_dict, BE)
ROS = ROS + ROS_C6
ROS = xr.where(ROS < 0, 0.0, ROS)
hourly_ds["ROS"] = ROS.astype(dtype="float32")
print(f"ROS run time {datetime.now() - ROSloopTime}")

################   Critical Surface Fire Intensity  ###################
#######################################################################
CFBloopTime = datetime.now()


def solve_cfb(CFB, ROS, fueltype, FMC):
    if fc_dict[fueltype]["CBH"] == -99:
        CFB = CFB
    else:
        ## Solve Critical surface intensity for crowning (56)
        CSI = 0.001 * (fc_dict[fueltype]["CBH"] ** 1.5) * (460 + 25.9 * FMC) ** 1.5
        ## Solve Critical spread rate for crowning (57)
        RSO = CSI / (300 * SFC)
        # Solve Crown fraction burned (58)
        CFB_i = xr.where(ROS > RSO, 1 - np.exp(-0.23 * (ROS - RSO)), CFB)
        # CFB_i = 1 - np.exp(-0.23 * (ROS - RSO))
        CFB_i = xr.where(CFB_i < 0, 0.0, CFB_i)
        CFB = xr.where(FUELS == fc_dict[fueltype]["Code"], CFB_i, CFB)
    return CFB


CFB = zero_full3D
for fueltype in fc_df.index.values[:-8]:
    CFB = solve_cfb(CFB, ROS, fueltype, FMC)

hourly_ds["CFB"] = CFB.astype(dtype="float32")
print(f"CFB run time {datetime.now() - CFBloopTime}")

#####################   Total Fuel Consumption  #######################
#######################################################################
TFCloopTime = datetime.now()


def solve_tfc(TFC, fueltype, CFB):
    if fc_dict[fueltype]["CFL"] == -99:
        TFC = xr.where(FUELS == fc_dict[fueltype]["Code"], SFC, TFC)
    else:
        CFC = fc_dict[fueltype]["CFL"] * CFB
        TFC = xr.where(FUELS == fc_dict[fueltype]["Code"], SFC + CFC, TFC)
    return TFC


TFC = zero_full3D
for fueltype in fc_df.index.values[:-8]:
    TFC = solve_tfc(TFC, fueltype, CFB)

hourly_ds["TFC"] = TFC.astype(dtype="float32")
print(f"TFC run time {datetime.now() - TFCloopTime}")

#########################   Fire Intensity  ###########################
#######################################################################
HFIloopTime = datetime.now()

HFI = 300 * TFC * ROS
# print('HFI', np.max(HFI.values))
hourly_ds["HFI"] = HFI.astype(dtype="float32")
print(f"HFI run time {datetime.now() - HFIloopTime}")

print(f"End of FBP with run time of {datetime.now() - FBPloopTime}")

# return hourly_ds
