#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python
import context
import os
import json
import numpy as np
import pandas as pd
import xarray as xr

from datetime import datetime


def MBE(y_true, y_pred):
    """
    Parameters:
        y_true (array): Array of observed values
        y_pred (array): Array of prediction values

    Returns:
        mbe (float): Biais score
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    y_true = y_true.reshape(len(y_true), 1)
    y_pred = y_pred.reshape(len(y_pred), 1)
    diff = y_pred - y_true
    mbe = diff.mean()
    # print('MBE = ', mbe)
    return mbe


def MAE(y_true, y_pred):
    """
    Parameters:
        y_true (array): Array of observed values
        y_pred (array): Array of prediction values

    Returns:
        mae (float): Mean Absolute Error
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    y_true = y_true.reshape(len(y_true), 1)
    y_pred = y_pred.reshape(len(y_pred), 1)
    diff = np.abs(y_pred - y_true)
    mae = diff.mean()
    # print('MAE = ', mae)
    return mae


# def RMSE(target, prediction):
#     return np.sqrt(
#         ((np.array(target) - np.array(prediction)) ** 2).mean() / len(np.array(target))
#     )


def RMSE(predictions, targets):

    differences = predictions - targets  # the DIFFERENCEs.

    differences_squared = differences ** 2  # the SQUAREs of ^

    mean_of_differences_squared = differences_squared.mean()  # the MEAN of ^

    rmse_val = np.sqrt(mean_of_differences_squared)  # ROOT of ^

    return rmse_val  # get the ^
