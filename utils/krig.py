import itertools
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from shapely.geometry import Polygon


def pixel2poly(x, y, z, resolution):
    """
    x: x coords of cell
    y: y coords of cell
    z: matrix of values for each (x,y)
    resolution: spatial resolution of each cell
    """
    polygons = []
    values = []
    half_res = resolution / 2
    for i, j in itertools.product(range(len(x)), range(len(y))):
        minx, maxx = x[i] - half_res, x[i] + half_res
        miny, maxy = y[j] - half_res, y[j] + half_res
        polygons.append(
            Polygon([(minx, miny), (minx, maxy), (maxx, maxy), (maxx, miny)])
        )
        if isinstance(z, (int, float)):
            values.append(z)
        else:
            values.append(z[j, i])
    return polygons, values


def plotvariogram(krig):
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(111)
    ax.plot(krig.lags / 1000, krig.semivariance, "go")
    ax.plot(
        krig.lags / 1000,
        krig.variogram_function(krig.variogram_model_parameters, krig.lags),
        "k-",
    )
    ax.grid(True, linestyle="--", zorder=1, lw=0.5)
    # ax.grid(True)

    try:
        fig_title = f"Coordinates type: {(krig.coordinates_type).title()}" + "\n"
    except:
        fig_title = ""
    if krig.variogram_model == "linear":
        fig_title += "Using '%s' Variogram Model" % "linear" + "\n"
        fig_title += f"Slope: {krig.variogram_model_parameters[0]}" + "\n"
        fig_title += f"Nugget: {krig.variogram_model_parameters[1]}"
    elif krig.variogram_model == "power":
        fig_title += "Using '%s' Variogram Model" % "power" + "\n"
        fig_title += f"Scale:  {krig.variogram_model_parameters[0]}" + "\n"
        fig_title += f"Exponent: + {krig.variogram_model_parameters[1]}" + "\n"
        fig_title += f"Nugget: {krig.variogram_model_parameters[2]}"
    elif krig.variogram_model == "custom":
        print("Using Custom Variogram Model")
    else:
        fig_title += f"Using {(krig.variogram_model).title()} Variogram Model" + "\n"
        fig_title2 = (
            f"Partial Sill: {np.round(krig.variogram_model_parameters[0])}" + "\n"
        )
        fig_title2 += (
            f"Full Sill: {np.round(krig.variogram_model_parameters[0] + krig.variogram_model_parameters[2])}"
            + "\n"
        )
        fig_title2 += (
            f"Range (km): {np.round(krig.variogram_model_parameters[1])/1000}" + "\n"
        )
        fig_title2 += f"Nugget: {np.round(krig.variogram_model_parameters[2],2)}"
    ax.set_title(fig_title, loc="left", fontsize=14)
    # fig_title2 = (
    #     f"Q1 = {np.round(krig.Q1,4)}"
    #     + "\n"
    #     + f"Q2 = {np.round(krig.Q2,4)}"
    #     + "\n"
    #     + f"cR = {np.round(krig.cR,4)}"
    # )
    ax.set_title(fig_title2, loc="right", fontsize=14)

    ax.set_xlabel("Lag (Distance km)", fontsize=12)
    ax.set_ylabel("Semivariance", fontsize=12)
    ax.tick_params(axis="both", which="major", labelsize=12)
    return
