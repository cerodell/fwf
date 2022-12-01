import context
import math
import json
import numpy as np
import pandas as pd
import xarray as xr


from pathlib import Path

from datetime import datetime
from context import data_dir

import warnings

warnings.filterwarnings("ignore")

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


"""########################################################################"""
""" ##################### Fine Fuel Moisture Code #########################"""
"""########################################################################"""


def solve_ffmc(ds, F):
    W, T, H, r_o = (ds.W, ds.T, ds.H, ds.r_o)

    # #Eq. 1
    m_o = 147.2 * (101 - F) / (59.5 + F)

    ########################################################################
    ### Solve for the effective raut
    r_f = xr.where(r_o > 0.5, (r_o - 0.5), xr.where(r_o < 1e-7, 1e-5, r_o))
    ########################################################################
    ### (1) Solve the Rautfagner 1985 (m_r)
    m_o = xr.where(
        m_o <= 150,
        m_o + (42.5 * r_f * np.exp((-100 / (251 - m_o))) * (1 - np.exp((-6.93 / r_f)))),
        m_o
        + (42.5 * r_f * np.exp((-100 / (251 - m_o))) * (1 - np.exp((-6.93 / r_f))))
        + (0.0015 * np.power((m_o - 150), 2) * np.power(r_f, 0.5)),
    )

    m_o = np.where(m_o > 250, 250, np.where(m_o < 0, 0.0, m_o))

    ########################################################################
    ### (2a) Solve Equilibrium Moisture content for dry

    E_d = (
        0.942 * np.power(H, 0.679)
        + 11 * np.exp((H - 100) / 10)
        + 0.18 * (21.1 - T) * (1 - np.exp((-0.115 * H)))
    )

    ########################################################################
    ### (2b) Solve Equilibrium Moisture content for wett

    E_w = (
        0.618 * (np.power(H, 0.753))
        + 10 * np.exp((H - 100) / 10)
        + 0.18 * (21.1 - T) * (1 - np.exp((-0.115 * H)))
    )
    ########################################################################
    ### (3a) ate step to k_d (k_a)
    k_a = 0.424 * (1 - np.power(H / 100, 1.7)) + 0.0694 * (np.power(W, 0.5)) * (
        1 - np.power(H / 100, 8)
    )

    ########################################################################
    ### (3b) Log dryfor hourly computation, log to base 10 (k_d)
    k_d = k_a * 0.581 * np.exp(0.0365 * T)

    ########################################################################
    ### (4a) ate steps to k_w (k_b)
    k_b = 0.424 * (1 - np.power(((100 - H) / 100), 1.7)) + 0.0694 * np.power(W, 0.5) * (
        1 - np.power(((100 - H) / 100), 8)
    )

    ########################################################################
    ### (4b)  Log wet for hourly computation, log to base 10 (k_w)
    k_w = k_b * 0.581 * np.exp(0.0365 * T)

    ########################################################################
    ### (5a) ate dry moisture code (m_d)
    m_d = E_d + (m_o - E_d) * 10 ** (-k_d)

    ########################################################################
    ### (5b) ate wet moisture code (m_w)
    m_w = E_w - (E_w - m_o) * 10 ** (-k_w)

    ########################################################################
    ### (5c) combwet, neutral moisture codes
    m = xr.where(m_o > E_d, m_d, m_w)
    m = xr.where((E_d >= m_o) & (m_o >= E_w), m_o, m)
    # m_o = xr.DataArray(m, name="m_o", dims=("temp", "wind", "rh", "precip"))

    # ds["m_o"] = m_o

    ########################################################################
    ### (6) Solve for FFMC
    F = (59.5 * (250 - m)) / (147.2 + m)  ## Van 1985
    # F = xr.DataArray(F, name="F", dims=("temp", "wind", "rh", "precip"))
    ds["F"] = F

    return ds


"""########################################################################"""
""" ########################## Duff Moisture Code #########################"""
"""########################################################################"""


def solve_dmc(ds, P, L_e):

    W, T, H, r_o, P_o, L_e = (
        ds.W,
        ds.T,
        ds.H,
        ds.r_o,
        P,
        L_e,
    )

    zero_full = np.zeros_like(ds.T)

    ########################################################################
    ### (11) Solve for the effective rain (r_e)
    r_e = (0.92 * r_o) - 1.27

    ########################################################################
    ### (12) NOTE Alteratered for more accurate calculation (Lawson 2008)
    M_o = 20 + 280 / np.exp(0.023 * P_o)

    ########################################################################
    ### (13a) Solve for coefficients b where P_o <= 33 (b_low)
    b_low = xr.where(P_o <= 33, 100 / (0.5 + 0.3 * P_o), zero_full)

    ########################################################################
    ### (13b) Solve for coefficients b where 33 < P_o <= 65 (b_mid)

    b_mid = xr.where((P_o > 33) & (P_o <= 65), 14 - 1.3 * np.log(P_o), zero_full)

    ########################################################################
    ### (13c) Solve for coefficients b where  P_o > 65 (b_high)

    b_high = xr.where(P_o > 65, 6.2 * np.log(P_o) - 17.2, zero_full)
    ########################################################################
    ### Combine (13a 13b 13c) for coefficients b
    b = b_low + b_mid + b_high

    ########################################################################
    ### (14) Solve for moisture content
    M_r = M_o + 1000 * r_e / (48.77 + b * r_e)

    ########################################################################
    ### (15) Duff moisture code (P_r) Alteration more accurate calculation (Lawson 2008)
    P_r = 43.43 * (5.6348 - np.log(M_r - 20))
    ## Apply rain condition if precip is less than 2.8 then use yesterday's DC
    P_r = xr.where(r_o <= 1.5, P_o, P_r)
    P_r = xr.where(P_r < 0, 0, P_r)

    ########################################################################
    ### (16) Log drying rate (K)
    K = (
        1.894 * (T + 1.1) * (100 - H) * (L_e * 1e-4)
    )  ## NOTE they use 1e-04 in the R but in the paper is 1e-06 code not sure what to use.

    ########################################################################
    ### (17) Duff moisture
    P = P_r + K

    # P = xr.DataArray(P, name="P", dims=("temp", "wind", "rh", "precip"))
    ds["P"] = P

    return ds


"""########################################################################"""
""" ############################ Drought Code #############################"""
"""########################################################################"""


def solve_dc(ds, D, L_f):

    ### Call on initial conditions
    W, T, H, r_o, D_o, L_f = (
        ds.W,
        ds.T,
        ds.H,
        ds.r_o,
        D,
        L_f,
    )

    T = np.where(T < (-2.8), -2.8, T)

    ########################################################################
    ### (18) Solve for the effective rain (r_d)
    r_d = 0.83 * r_o - 1.27

    ########################################################################
    ### (19) Solve for initial moisture equivalent (Q_o)
    Q_o = 800 * np.exp(-1 * D_o / 400)

    ########################################################################
    ### (20) Solve for moisture equivalent (Q_r)
    Q_r = Q_o + 3.937 * r_d

    ########################################################################
    ### (21) Solve for DC after rain (D_r)
    ## Alteration to Eq. 21 (Lawson 2008)
    D_r = D_o - 400 * np.log(1 + 3.937 * r_d / Q_o)
    # D_r = 400 * np.log(800 / Q_r)
    D_r = xr.where(D_r < 0, 0.0, D_r)
    D_r = xr.where(r_o <= 2.8, D_o, D_r)

    ########################################################################
    ### (22) Solve for potential evapotranspiration (V)
    # V = (0.36 * (T + 2.8)) + L_f
    V = (0.36 * (T + 2.8)) + L_f
    V = xr.where(V < 0, 0.0, V)

    ########################################################################
    ## Alteration to Eq. 23 (Lawson 2008)
    D = D_r + V * 0.5
    # D = xr.DataArray(D, name="D", dims=("temp", "wind", "rh", "precip"))
    ds["D"] = D

    return ds


"""########################################################################"""
""" #################### Initial Spread Index #############################"""
"""########################################################################"""


def solve_isi(ds, fbp=False):
    ### Call on initial conditions
    W, F = ds.W, ds.F

    m_o = 147.2 * (101 - F) / (59.5 + F)

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
    # R = xr.DataArray(R, name="R", dims=("temp", "wind", "rh", "precip"))
    ds["R"] = R

    return ds


"""########################################################################"""
""" ########################## Build up Index #############################"""
"""########################################################################"""


def solve_bui(ds):

    ### Call on initial conditions
    P, D = ds.P, ds.D
    zero_full = np.zeros_like(ds.T)

    ########################################################################
    ### (27a and 27b) Solve for build up index where P =< 0.4D (U_a)
    U_low = xr.where(P <= 0.4 * D, 0.8 * P * D / (P + (0.4 * D)), zero_full)

    U_high = xr.where(
        P > 0.4 * D,
        P - (1 - 0.8 * D / (P + (0.4 * D))) * (0.92 + np.power((0.0114 * P), 1.7)),
        zero_full,
    )

    U = U_low + U_high
    # U = xr.DataArray(U, name="U", dims=("temp", "wind", "rh", "precip"))
    ds["U"] = U

    return ds


"""########################################################################"""
""" ###################### Fire Weather Index #############################"""
"""########################################################################"""


def solve_fwi(ds):

    ### Call on initial conditions

    U, R = ds.U, ds.R

    ########################################################################
    ### (28) Solve for duff moisture function where U =< 80(f_D_a)
    f_D = xr.where(
        U > 80,
        1000 / (25 + 108.64 * np.exp(-0.023 * U)),
        (0.626 * np.power(U, 0.809)) + 2,
    )

    ########################################################################
    # (29) Solve for intermitate FWI
    B = 0.1 * R * f_D

    ########################################################################
    ### (30) Solve FWI
    S = xr.where(B <= 1, B, np.exp(2.72 * np.power((0.434 * np.log(B)), 0.647)))
    # S = xr.DataArray(S, name="S", dims=("temp", "wind", "rh", "precip"))
    ds["S"] = S

    ########################################################################
    ### (31) Solve for daily severity rating (DSR)
    DSR = 0.0272 * np.power(S, 1.77)
    # DSR = xr.DataArray(DSR, name="DSR", dims=("temp", "wind", "rh", "precip"))
    ds["DSR"] = DSR

    return ds


def compressor(ds):
    """
    this function comresses datasets
    """
    comp = dict(zlib=True, complevel=9)
    encoding = {var: comp for var in ds.data_vars}
    return ds, encoding
