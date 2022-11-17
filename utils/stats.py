import itertools
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from scipy.stats import pearsonr
from sklearn.metrics import mean_squared_error, mean_absolute_error
from context import data_dir

# import seaborn as sns

# sns.set(font_scale=1.4)


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
    diff = y_true - y_pred
    mbe = diff.mean()
    # print('MBE = ', mbe)
    return mbe


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


def buildsats(path):
    # print(str(path))
    gpm25 = pd.read_csv(str(data_dir) + "/obs/gpm25.csv")
    UK_ds = xr.open_dataset(str(path))
    modeled, observed = [], []
    for i in range(len(UK_ds.test)):
        UK = UK_ds.isel(test=i)
        UK_pm25 = UK.pm25.values
        UK_pm25_mean = np.mean(UK_pm25)
        # print(np.unique(np.isnan(UK_pm25)))
        random_sample = gpm25[gpm25.id.isin(UK.random_sample.values)].copy()
        if str(path.parts[-1])[:2] == "RK":
            cordx, cordy = "lon", "lat"
        else:
            cordx, cordy = "Easting", "Northing"

        y = xr.DataArray(
            np.array(random_sample[cordy]),
            dims="ids",
            coords=dict(ids=random_sample.id.values),
        )
        x = xr.DataArray(
            np.array(random_sample[cordx]),
            dims="ids",
            coords=dict(ids=random_sample.id.values),
        )
        pm25_points = UK.pm25.interp(
            x=x, y=y, method="linear", kwargs={"fill_value": UK_pm25_mean}
        )

        random_sample["modeled_PM2.5"] = pm25_points
        modeled.append(pm25_points.values)
        observed.append(random_sample["PM2.5"].values)
        # print(modeled)

    modeled, observed = np.ravel(modeled), np.ravel(observed)

    rmse = mean_squared_error(observed, modeled, squared=False)
    # print(f"root mean squared error {rmse}")
    mae = mean_absolute_error(observed, modeled)
    # print(f"mean absolute error {mean_absolute_error(observed, modeled)}")
    pr = float(pearsonr(observed, modeled)[0])
    # print(f"pearson's r {pr}")
    mbe = MBE(observed, modeled)
    # print(f"mean error (bias) {mbe}")

    config = str(path.parts[-1])[:-9]
    config = config.replace("Spherical", "")
    config = config.replace("-", " ")
    df = pd.DataFrame(
        {
            "config": [config],
            "frac": str(path.parts[-1])[-5:-3],
            "rmse": [rmse],
            "mae": [mae],
            "pr": [pr],
            "mbe": [mbe],
        }
    )
    return df


def buildsatsRK(path):
    # print(str(path))
    gpm25 = pd.read_csv(str(data_dir) + "/obs/gpm25.csv")
    UK_ds = xr.open_dataset(str(path))
    modeled, observed = [], []
    for i in range(len(UK_ds.test)):
        UK = UK_ds.isel(test=i)
        UK_pm25 = UK.pm25.values
        UK_pm25_mean = np.mean(UK_pm25)
        # print(np.unique(np.isnan(UK_pm25)))
        random_sample = gpm25[gpm25.id.isin(UK.random_sample.values)].copy()
        y = xr.DataArray(
            np.array(random_sample["lat"]),
            dims="ids",
            coords=dict(ids=random_sample.id.values),
        )
        x = xr.DataArray(
            np.array(random_sample["lon"]),
            dims="ids",
            coords=dict(ids=random_sample.id.values),
        )
        pm25_points = UK.pm25.interp(
            x=x, y=y, method="linear", kwargs={"fill_value": UK_pm25_mean}
        )

        random_sample["modeled_PM2.5"] = pm25_points
        modeled.append(pm25_points.values)
        observed.append(random_sample["PM2.5"].values)
        # print(modeled)

    modeled, observed = np.ravel(modeled), np.ravel(observed)

    rmse = mean_squared_error(observed, modeled, squared=False)
    # print(f"root mean squared error {rmse}")
    mae = mean_absolute_error(observed, modeled)
    # print(f"mean absolute error {mean_absolute_error(observed, modeled)}")
    pr = float(pearsonr(observed, modeled)[0])
    # print(f"pearson's r {pr}")
    mbe = MBE(observed, modeled)
    # print(f"mean error (bias) {mbe}")

    config = str(path.parts[-1])[:-9]
    config = config.replace("Spherical", "")
    config = config.replace("-", " ")
    df = pd.DataFrame(
        {
            "config": [config],
            "frac": str(path.parts[-1])[-5:-3],
            "rmse": [rmse],
            "mae": [mae],
            "pr": [pr],
            "mbe": [mbe],
        }
    )
    return df


def plotsns(metric, cmap, df_final):
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(
        1,
        1,
        1,
    )
    df = df_final[["config", "frac", metric]]
    df = df.pivot("config", "frac", metric)
    if metric == "rmse":
        title = "Root Mean Square Error"
    elif metric == "mae":
        title = "Mean Absolute Error"
    elif metric == "pr":
        title = "Pearson correlation coefficient (r)"
    elif metric == "mbe":
        title = "Mean Error (Bias) "
    else:
        raise ValueError("Not a valid metric option")
    sns.heatmap(df, annot=True, fmt=".4g", ax=ax, cmap=cmap, cbar_kws={"label": title})
    return


def cfcompliant(filein):
    """
    Converts Hysplit dataset to be cf compliant.
    Also, reformats julian datatime to standard datetime and creates LAT LONG arrays of the model domain.
    """
    ## open dataset
    ds = xr.open_dataset(filein)

    ## get PM25 as numpy array
    PM25 = ds.PM25.values
    ## get time flags as numpy array
    tflag = ds.TFLAG.values

    ## get first time index...this will need to be rethought but works for 00Z initialization times
    hysplit_start = str(tflag[0, 0, 0]) + "0" + str(tflag[0, 0, 1])

    ## convert from julian datetime to standard datetime
    start = datetime.strptime(hysplit_start, "%Y%j%H%M%S").strftime("%Y%m%d%H%M%S")
    print(f"start: {start}")

    ## get last time index...this will need to be rethought but works (most of the time) with the if else statement below
    hysplit_stop = str(tflag[-1, 0, 0]) + str(tflag[-1, 0, 1])

    ## convert from julian datetime to standard datetime
    if len(hysplit_stop) < 9:
        stop = datetime.strptime(hysplit_stop, "%Y%j%H").strftime("%Y%m%d%H%M%S")
    else:
        stop = datetime.strptime(hysplit_stop, "%Y%j%H%M%S").strftime("%Y%m%d%H%M%S")
    print(f"stop: {stop}")

    ## create a new datetime numpy array with one hour frequency
    date_range = pd.date_range(start, stop, freq="1H")

    ## get x coordinate dimensions and create an array
    xnum = ds.dims["COL"]
    dx = ds.attrs["XCELL"]
    xorig = ds.attrs["XORIG"]
    x = np.arange(0, xnum)

    ## get y coordinate dimensions and create an array
    ynum = ds.dims["ROW"]
    dy = ds.attrs["YCELL"]
    yorig = ds.attrs["YORIG"]
    y = np.arange(0, ynum)

    ## create LAT and LONG 2D arrays based on the x and y coordinates
    X = np.arange(0, xnum) * dx + xorig
    Y = np.arange(0, ynum) * dy + yorig
    XX, YY = np.meshgrid(X, Y)

    ## get z coordinate dimensions and create an array
    Z = np.array(ds.attrs["VGLVLS"][:-1])
    z = np.arange(0, len(Z))

    ## create new dataset a set up to be CF Compliant
    ds_cf = xr.Dataset(
        data_vars=dict(
            pm25=(["time", "z", "y", "x"], PM25.astype("float32")),
            x=(["x"], x.astype("int32")),
            y=(["y"], y.astype("int32")),
            z=(["z"], z.astype("int32")),
            Times=(["time"], date_range.astype("S19")),
        ),
        coords=dict(
            LONG=(["y", "x"], XX.astype("float32")),
            LAT=(["y", "x"], YY.astype("float32")),
            HEIGHT=(["z"], Z.astype("float32")),
            time=date_range,
        ),
        attrs=dict(description="BlueSky Canada PM25 Forecast"),
    )

    ## add axis attributes from cf compliance
    ds_cf["time"].attrs["axis"] = "Time"
    ds_cf["x"].attrs["axis"] = "X"
    ds_cf["y"].attrs["axis"] = "Y"
    ds_cf["z"].attrs["axis"] = "Z"

    ## add units attributes from cf compliance
    ds_cf["pm25"].attrs["units"] = "um m^-3"
    ds_cf["LONG"].attrs["units"] = "degree_east"
    ds_cf["LAT"].attrs["units"] = "degree_north"

    return ds_cf
