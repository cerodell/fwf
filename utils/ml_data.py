#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import json
import salem
import joblib
import numpy as np
import pandas as pd
import xarray as xr

from pathlib import Path
from context import data_dir
from sklearn.preprocessing import (
    StandardScaler,
    RobustScaler,
    MinMaxScaler,
    PowerTransformer,
)
from utils.tf import activate_logging, create_model_directory
from sklearn.inspection import permutation_importance

from scipy import stats
from utils.stats import MBE, RMSE
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from utils.solar_hour import get_solar_hours

from sklearn.utils import shuffle


class MLDATA:
    """
    A class to manipulate and process multi-year fire data.
    """

    def __init__(self, config):
        self.filein = "/Users/crodell/fwf/data/ml-data/training-data/"
        self.keep_vars = config.get("keep_vars")
        self.years = config.get("years", ["2021", "2022", "2023"])
        self.filter_std = config.get("filter_std")
        self.method = config.get("method", "averaged")
        self.min_fire_size = config.get("min_fire_size", 0)
        self.transform = config.get("transform")
        self.scaler_type = config.get("scaler_type", "standard")
        self.main_cases = config.get("main_cases", False)
        self.shuffle_data = config.get("shuffle_data", False)
        self.model_type = config.get("model_type")
        self.package = config.get("package")
        self.feature_engineer = config.get("feature_engineer", False)

    def get_ds(self, year):
        """
        Open a dataset for a given year and convert it to a pandas DataFrame.
        """
        path = f"{self.filein}{year}-fires-{self.method}.nc"
        return xr.open_dataset(path).to_dataframe().reset_index()

    def mod_ds(self, df):
        """
        Modify the dataset by cleaning and adding new columns.
        """
        print(len(df))
        df = df.loc[df["area_ha"] > self.min_fire_size]
        df = df.loc[df["burn_time"] > 24]
        df.loc[df["HGT"] < 0, "HGT"] = 0
        df["local_time"] = pd.to_datetime(df["time"]) - pd.to_timedelta(
            df["ZoneST"].astype(int), unit="h"
        )
        df["hour"] = df["local_time"].dt.hour
        df["month"] = df["local_time"].dt.month
        df["dayofyear"] = df["local_time"].dt.dayofyear
        df["dayofyear_sin"] = np.sin(2 * np.pi * df["dayofyear"] / 365)
        df["dayofyear_cos"] = np.cos(2 * np.pi * df["dayofyear"] / 365)
        df["hour_sin"] = np.sin(2 * np.pi * df["solar_hour"] / 24)
        df["hour_cos"] = np.cos(2 * np.pi * df["solar_hour"] / 24)
        df.loc[df["LAI"] > 7, "LAI"] = 7
        df.loc[df["LAI"] < 0, "LAI"] = 0.01

        if self.transform == True:
            # pt = PowerTransformer(
            #     method="yeo-johnson", standardize=False
            # )  # Yeo-Johnson allows for zero values
            # df["Dead_Wood"] = pt.fit_transform(df[["Dead_Wood"]] + 1)
            # df["Live_Wood"] = pt.fit_transform(df[["Live_Wood"]] + 1)
            # df["Live_Leaf"] = pt.fit_transform(df[["Live_Leaf"]] + 1)
            # df["Dead_Foliage"] = pt.fit_transform(df[["Dead_Foliage"]] + 1)
            df["FRP"] = np.log1p(df["FRP"])
            df["U"] = np.log1p(df["U"])
            df["R"] = np.log1p(df["R"])
            df["LAI"] = np.log1p(df["LAI"])

        if self.feature_engineer == True:
            print(list(df))
            total_fuel = (
                df["Live_Wood"] + df["Dead_Wood"] + df["Live_Leaf"] + df["Dead_Foliage"]
            )
            df["S_hour_sin"] = df["hour_sin"] * df["S"]
            df["S_hour_cos"] = df["hour_cos"] * df["S"]

            df["R_hour_sin"] = df["hour_sin"] * df["R"]
            df["R_hour_cos"] = df["hour_cos"] * df["R"]

            df["U_hour_sin"] = df["hour_sin"] * df["U"]
            df["U_hour_cos"] = df["hour_cos"] * df["U"]

            df["U_Dead_Wood"] = df["Dead_Wood"] * df["U"]
            df["U_Live_Wood"] = df["Live_Wood"] * df["U"]
            df["U_Live_Leaf"] = df["Live_Leaf"] * df["U"]
            df["U_Dead_Foliage"] = df["Dead_Foliage"] * df["U"]

            df["F_Dead_Wood"] = df["Dead_Wood"] * df["F"]
            df["F_Live_Wood"] = df["Live_Wood"] * df["F"]
            df["F_Live_Leaf"] = df["Live_Leaf"] * df["F"]
            df["F_Dead_Foliage"] = df["Dead_Foliage"] * df["F"]

            df["S_lat_sin"] = df["lat_sin"] * df["S"]
            df["S_lat_cos"] = df["lat_cos"] * df["S"]

            df["S_lon_sin"] = df["lon_sin"] * df["S"]
            df["S_lon_cos"] = df["lon_cos"] * df["S"]

            df["R_lat_sin"] = df["lat_sin"] * df["R"]
            df["R_lat_cos"] = df["lat_cos"] * df["R"]

            df["R_lon_sin"] = df["lon_sin"] * df["R"]
            df["R_lon_cos"] = df["lon_cos"] * df["R"]

            df["U_lat_sin"] = df["lat_sin"] * df["U"]
            df["U_lat_cos"] = df["lat_cos"] * df["U"]

            df["U_lon_sin"] = df["lon_sin"] * df["U"]
            df["U_lon_cos"] = df["lon_cos"] * df["U"]

            df["U_lat_sin_total_fuel"] = df["U"] * df["lat_sin"] * total_fuel
            df["U_lat_cos_total_fuel"] = df["U"] * df["lat_cos"] * total_fuel

            df["U_lon_sin_total_fuel"] = df["U"] * df["lon_sin"] * total_fuel
            df["U_lon_cos_total_fuel"] = df["U"] * df["lon_cos"] * total_fuel

            df["R_hour_sin_Live_Wood"] = df["R"] * df["hour_sin"] * df["Live_Wood"]
            df["R_hour_cos_Live_Wood"] = df["R"] * df["hour_cos"] * df["Live_Wood"]

            df["R_hour_sin_Dead_Wood"] = df["R"] * df["hour_sin"] * df["Dead_Wood"]
            df["R_hour_cos_Dead_Wood"] = df["R"] * df["hour_cos"] * df["Dead_Wood"]

            df["R_hour_sin_Live_Leaf"] = df["R"] * df["hour_sin"] * df["Live_Leaf"]
            df["R_hour_cos_Live_Leaf"] = df["R"] * df["hour_cos"] * df["Live_Leaf"]

            df["R_hour_sin_Dead_Foliage"] = (
                df["R"] * df["hour_sin"] * df["Dead_Foliage"]
            )
            df["R_hour_cos_Dead_Foliage"] = (
                df["R"] * df["hour_cos"] * df["Dead_Foliage"]
            )

            df["U_lat_sin_Live_Wood"] = df["U"] * df["lat_sin"] * df["Live_Wood"]
            df["U_lat_cos_Live_Wood"] = df["U"] * df["lat_cos"] * df["Live_Wood"]
            df["U_lat_sin_Dead_Wood"] = df["U"] * df["lat_sin"] * df["Dead_Wood"]
            df["U_lat_cos_Dead_Wood"] = df["U"] * df["lat_cos"] * df["Dead_Wood"]
            df["U_lat_sin_Live_Leaf"] = df["U"] * df["lat_sin"] * df["Live_Leaf"]
            df["U_lat_cos_Live_Leaf"] = df["U"] * df["lat_cos"] * df["Live_Leaf"]
            df["U_lat_sin_Dead_Foliage"] = df["U"] * df["lat_sin"] * df["Dead_Foliage"]
            df["U_lat_cos_Dead_Foliage"] = df["U"] * df["lat_cos"] * df["Dead_Foliage"]
            df["F_lat_sin_Dead_Foliage"] = df["F"] * df["lat_sin"] * df["Dead_Foliage"]
            df["F_lat_cos_Dead_Foliage"] = df["F"] * df["lat_cos"] * df["Dead_Foliage"]

            df["U_lon_sin_Live_Wood"] = df["U"] * df["lon_sin"] * df["Live_Wood"]
            df["U_lon_cos_Live_Wood"] = df["U"] * df["lon_cos"] * df["Live_Wood"]
            df["U_lon_sin_Dead_Wood"] = df["U"] * df["lon_sin"] * df["Dead_Wood"]
            df["U_lon_cos_Dead_Wood"] = df["U"] * df["lon_cos"] * df["Dead_Wood"]
            df["U_lon_sin_Live_Leaf"] = df["U"] * df["lon_sin"] * df["Live_Leaf"]
            df["U_lon_cos_Live_Leaf"] = df["U"] * df["lon_cos"] * df["Live_Leaf"]
            df["U_lon_sin_Dead_Foliage"] = df["U"] * df["lon_sin"] * df["Dead_Foliage"]
            df["U_lon_cos_Dead_Foliage"] = df["U"] * df["lon_cos"] * df["Dead_Foliage"]
            df["F_lon_sin_Dead_Foliage"] = df["F"] * df["lon_sin"] * df["Dead_Foliage"]
            df["F_lon_cos_Dead_Foliage"] = df["F"] * df["lon_cos"] * df["Dead_Foliage"]
            # if self.keep_vars:
        #     df = df[["FRP"] + self.keep_vars]

        if self.filter_std:
            means = df.mean()
            stds = df.std()
            df = df[
                (df < (means + self.filter_std * stds))
                & (df > (means - self.filter_std * stds))
            ].dropna()

        return df

    def open_ml_ds(self):
        """
        Open and modify datasets for all specified years.
        """
        return self.mod_ds(
            pd.concat((self.get_ds(year) for year in self.years), ignore_index=True)
        )

    def get_static(self, ds):
        static_ds = salem.open_xr_dataset(
            str(data_dir) + "/static/static-rave-3km.nc"
        ).drop_vars(["time", "xtime"])
        lons, lats = static_ds.salem.grid.ll_coordinates
        lon_sin = np.sin(np.radians(lons))
        lon_cos = np.cos(np.radians(lons))
        lat_sin = np.sin(np.radians(lats))
        lat_cos = np.cos(np.radians(lats))

        static_ds["lat_sin"] = (("y", "x"), lat_sin)
        static_ds["lat_cos"] = (("y", "x"), lat_cos)
        static_ds["lon_sin"] = (("y", "x"), lon_sin)
        static_ds["lon_cos"] = (("y", "x"), lon_cos)

        static_ds["lats"] = (("y", "x"), lats)
        static_ds["lons"] = (("y", "x"), lons)

        ASPECT_sin = np.sin(np.radians(static_ds["ASPECT"].values))
        ASPECT_cos = np.cos(np.radians(static_ds["ASPECT"].values))
        static_ds["ASPECT_sin"] = (("y", "x"), ASPECT_sin)
        static_ds["ASPECT_cos"] = (("y", "x"), ASPECT_cos)

        SAZ_sin = np.sin(np.radians(static_ds["SAZ"].values))
        SAZ_cos = np.cos(np.radians(static_ds["SAZ"].values))
        static_ds["SAZ_sin"] = (("y", "x"), SAZ_sin)
        static_ds["SAZ_cos"] = (("y", "x"), SAZ_cos)

        static_roi = self.add_static(ds, static_ds)
        for var in list(static_roi):
            ds[var] = static_roi[var]

        fuel_date_range = pd.date_range(
            ds.attrs["initialdat"][:-3] + "-01", ds.attrs["finaldate"], freq="MS"
        )
        fuels_ds = xr.combine_nested(
            [self.open_fuels(moi) for moi in fuel_date_range], concat_dim="time"
        )
        fuels_roi = ds.salem.transform(fuels_ds, interp="linear")
        fuels_roi = fuels_roi.reindex(time=ds.time, method="ffill")
        fuels_roi = xr.where(fuels_roi < 0, 0, fuels_roi)
        for var in list(fuels_roi):
            ds[var] = fuels_roi[var]

        return ds

    def add_index(self, static_roi, fire_ds):
        static_roi = static_roi.expand_dims("time")
        static_roi.coords["time"] = pd.Series(fire_ds.time.values[0])
        return static_roi.reindex(time=fire_ds.time, method="ffill")

    def add_static(self, fire_ds, static_ds):
        return self.add_index(
            fire_ds.salem.transform(static_ds, interp="nearest"), fire_ds
        )

    def open_fuels(self, moi):
        moi = pd.Timestamp(moi)
        fuel_dir = f"/Volumes/WFRT-Ext23/fuel-characteristics/fuel-load/"
        fuels_ds = salem.open_xr_dataset(
            fuel_dir + f'{2021}/CFUEL_timemean_2021{moi.strftime("_%m")}.nc'
        ).sel(lat=slice(75, 20), lon=slice(-170, -50))
        fuels_ds.coords["time"] = moi
        return fuels_ds

    def get_eng_features(self, ds):
        ds = get_solar_hours(ds)
        hour_sin = np.sin(2 * np.pi * ds["solar_hour"] / 24)
        hour_cos = np.cos(2 * np.pi * ds["solar_hour"] / 24)
        total_fuel = (
            ds["Live_Wood"] + ds["Dead_Wood"] + ds["Live_Leaf"] + ds["Dead_Foliage"]
        )
        ds["R_hour_sin"] = hour_sin * ds["R"]
        ds["R_hour_cos"] = hour_cos * ds["R"]
        ds["S_hour_sin"] = hour_sin * ds["S"]
        ds["S_hour_cos"] = hour_cos * ds["S"]
        ds["U_hour_sin"] = hour_sin * ds["U"]
        ds["U_hour_cos"] = hour_cos * ds["U"]

        ds["U_Dead_Wood"] = ds["Dead_Wood"] * ds["U"]
        ds["U_Live_Wood"] = ds["Live_Wood"] * ds["U"]
        ds["U_Live_Leaf"] = ds["Live_Leaf"] * ds["U"]
        ds["U_Dead_Foliage"] = ds["Dead_Foliage"] * ds["U"]

        ds["F_Dead_Wood"] = ds["Dead_Wood"] * ds["F"]
        ds["F_Live_Wood"] = ds["Live_Wood"] * ds["F"]
        ds["F_Live_Leaf"] = ds["Live_Leaf"] * ds["F"]
        ds["F_Dead_Foliage"] = ds["Dead_Foliage"] * ds["F"]

        ds["S_lat_sin"] = ds["lat_sin"] * ds["S"]
        ds["S_lat_cos"] = ds["lat_cos"] * ds["S"]

        ds["S_lon_sin"] = ds["lon_sin"] * ds["S"]
        ds["S_lon_cos"] = ds["lon_cos"] * ds["S"]

        ds["R_lat_sin"] = ds["lat_sin"] * ds["R"]
        ds["R_lat_cos"] = ds["lat_cos"] * ds["R"]

        ds["R_lon_sin"] = ds["lon_sin"] * ds["R"]
        ds["R_lon_cos"] = ds["lon_cos"] * ds["R"]

        ds["U_lat_sin"] = ds["lat_sin"] * ds["U"]
        ds["U_lat_cos"] = ds["lat_cos"] * ds["U"]

        ds["U_lon_sin"] = ds["lon_sin"] * ds["U"]
        ds["U_lon_cos"] = ds["lon_cos"] * ds["U"]

        ds["U_lat_sin_total_fuel"] = ds["U"] * ds["lat_sin"] * total_fuel
        ds["U_lat_cos_total_fuel"] = ds["U"] * ds["lat_cos"] * total_fuel

        ds["U_lon_sin_total_fuel"] = ds["U"] * ds["lon_sin"] * total_fuel
        ds["U_lon_cos_total_fuel"] = ds["U"] * ds["lon_cos"] * total_fuel

        ds["R_hour_sin_Live_Wood"] = ds["R"] * hour_sin * ds["Live_Wood"]
        ds["R_hour_cos_Live_Wood"] = ds["R"] * hour_cos * ds["Live_Wood"]

        ds["R_hour_sin_Dead_Wood"] = ds["R"] * hour_sin * ds["Dead_Wood"]
        ds["R_hour_cos_Dead_Wood"] = ds["R"] * hour_cos * ds["Dead_Wood"]

        ds["R_hour_sin_Live_Leaf"] = ds["R"] * hour_sin * ds["Live_Leaf"]
        ds["R_hour_cos_Live_Leaf"] = ds["R"] * hour_cos * ds["Live_Leaf"]

        ds["R_hour_sin_Dead_Foliage"] = ds["R"] * hour_sin * ds["Dead_Foliage"]
        ds["R_hour_cos_Dead_Foliage"] = ds["R"] * hour_cos * ds["Dead_Foliage"]

        ds["U_lat_sin_Live_Wood"] = ds["U"] * ds["lat_sin"] * ds["Live_Wood"]
        ds["U_lat_cos_Live_Wood"] = ds["U"] * ds["lat_cos"] * ds["Live_Wood"]
        ds["U_lat_sin_Dead_Wood"] = ds["U"] * ds["lat_sin"] * ds["Dead_Wood"]
        ds["U_lat_cos_Dead_Wood"] = ds["U"] * ds["lat_cos"] * ds["Dead_Wood"]
        ds["U_lat_sin_Live_Leaf"] = ds["U"] * ds["lat_sin"] * ds["Live_Leaf"]
        ds["U_lat_cos_Live_Leaf"] = ds["U"] * ds["lat_cos"] * ds["Live_Leaf"]
        ds["U_lat_sin_Dead_Foliage"] = ds["U"] * ds["lat_sin"] * ds["Dead_Foliage"]
        ds["U_lat_cos_Dead_Foliage"] = ds["U"] * ds["lat_cos"] * ds["Dead_Foliage"]
        ds["F_lat_sin_Dead_Foliage"] = ds["F"] * ds["lat_sin"] * ds["Dead_Foliage"]
        ds["F_lat_cos_Dead_Foliage"] = ds["F"] * ds["lat_cos"] * ds["Dead_Foliage"]

        ds["U_lon_sin_Live_Wood"] = ds["U"] * ds["lon_sin"] * ds["Live_Wood"]
        ds["U_lon_cos_Live_Wood"] = ds["U"] * ds["lon_cos"] * ds["Live_Wood"]
        ds["U_lon_sin_Dead_Wood"] = ds["U"] * ds["lon_sin"] * ds["Dead_Wood"]
        ds["U_lon_cos_Dead_Wood"] = ds["U"] * ds["lon_cos"] * ds["Dead_Wood"]
        ds["U_lon_sin_Live_Leaf"] = ds["U"] * ds["lon_sin"] * ds["Live_Leaf"]
        ds["U_lon_cos_Live_Leaf"] = ds["U"] * ds["lon_cos"] * ds["Live_Leaf"]
        ds["U_lon_sin_Dead_Foliage"] = ds["U"] * ds["lon_sin"] * ds["Dead_Foliage"]
        ds["U_lon_cos_Dead_Foliage"] = ds["U"] * ds["lon_cos"] * ds["Dead_Foliage"]
        ds["F_lon_sin_Dead_Foliage"] = ds["F"] * ds["lon_sin"] * ds["Dead_Foliage"]
        ds["F_lon_cos_Dead_Foliage"] = ds["F"] * ds["lon_cos"] * ds["Dead_Foliage"]
        return ds

    def get_training(self):

        df = self.open_ml_ds()
        print("Number of fires: ", len(np.unique(df["id"].values)))
        if self.main_cases == False:
            ## Sampling dataset for test and training
            IDS = np.unique(df["id"].values)
            sample_size = int(0.1 * len(IDS))
            ids = np.random.choice(IDS, size=sample_size, replace=False)
            ids = np.append(ids, [25485086, 25407482, 24360611, 24448308, 24450415])
            df_test = df[df["id"].isin(ids)]
            unique_test_df = df_test.drop_duplicates(subset="id", keep="first")
            fires_array = np.stack(
                [
                    unique_test_df["id"].values,
                    unique_test_df["local_time"].dt.year.values,
                ]
            )

        else:
            fires_array = np.loadtxt(
                f"/Users/crodell/fwf/data/ml-data/training-data/test_cases.txt",
                delimiter=",",
            )
            ids = np.array(fires_array[0].astype(int))
            years = fires_array[1].astype(int)
            df_test = df[df["id"].isin(ids)]

        df_train = df[~df["id"].isin(ids)]
        large_fires = df_train.loc[df_train["area_ha"] > 50000]
        larger_fires = df_train.loc[df_train["area_ha"] > 100000]
        if self.transform == True:
            hot_fires = df_train.loc[df_train["FRP"] > np.expm1(1000)]
            hotter_fires = df_train.loc[df_train["FRP"] > np.expm1(2000)]
            hottest_fires = df_train.loc[df_train["FRP"] > np.expm1(2500)]
        else:
            warm_fires = df_train.loc[df_train["FRP"] > 1000]
            hot_fires = df_train.loc[df_train["FRP"] > 1500]
            hotter_fires = df_train.loc[df_train["FRP"] > 2000]
            hotter_still_fire = df_train.loc[df_train["FRP"] > 3000]
            hottest_fires = df_train.loc[df_train["FRP"] > 4000]
        df_train = pd.concat(
            [
                df_train,
                warm_fires,
                hot_fires,
                hotter_fires,
                hotter_still_fire,
                hottest_fires,
            ]
        )
        df_train.reset_index(drop=True, inplace=True)

        if self.keep_vars:
            X_train = df_train[self.keep_vars]
            X_test = df_test[self.keep_vars]
        else:
            X_train = df_train[1:]
            X_test = df_test[1:]

        y_train = df_train["FRP"]
        y_test = df_test["FRP"]

        if self.shuffle_data:
            X_train, y_train = shuffle(X_train, y_train, random_state=42)

        # Scale features
        if self.scaler_type == "standard":
            scaler = StandardScaler().fit(X_train)
        elif self.scaler_type == "robust":
            scaler = RobustScaler().fit(X_train)
        elif self.scaler_type == "minmax":
            scaler = MinMaxScaler().fit(X_train)

        X_train = scaler.transform(X_train)
        X_test = scaler.transform(X_test)

        self.scaler = scaler
        self.fires_array = fires_array
        self.length_of_training = len(y_train)
        self.X_test = X_test
        self.y_test = y_test

        print("Percent of data used for training: ", (len(y_test) / len(y_train)) * 100)
        return y_train, X_train, y_test, X_test

    def save_model(self, model, y_out_this_nhn, save_dir, logger):

        if self.transform == True:
            y_out_this_nhn = np.expm1(y_out_this_nhn)
            y_test = np.expm1(self.y_test)
        else:
            y_test = self.y_test

        X_test = self.X_test

        # Save model and scaler
        if self.package == "tf":
            model_path = save_dir / "model.keras"
            model.save(model_path)
            model_config_info = model.get_config()
        else:
            model_path = save_dir / "model.joblib"
            joblib.dump(model, model_path)
            model_config_info = model.get_params()

        model_path = save_dir / "model.joblib"
        joblib.dump(model, model_path)
        scaler_path = save_dir / "scaler.joblib"
        joblib.dump(self.scaler, scaler_path)
        np.savetxt(
            save_dir / "test_cases.txt", self.fires_array, fmt="%d", delimiter=","
        )

        # Save model configuration and statistics
        model_config = {
            "model_config": model_config_info,
            "features_used": self.keep_vars,
            "scaler_type": self.scaler_type,
            "transform": str(self.transform),
            "scaler_info": str(scaler_path),
            "model_info": str(model_path),
            "feature_engineer": str(self.feature_engineer),
            "scaler_type": str(self.scaler_type),
            "main_cases": str(self.main_cases),
            "shuffle_data": str(self.shuffle_data),
        }
        config_path = save_dir / "config.json"
        with open(config_path, "w") as json_file:
            json.dump(model_config, json_file, indent=4)

        stats_dict = {
            "rmse": str(RMSE(y_test, y_out_this_nhn)),
            "mbe": str(MBE(y_test, y_out_this_nhn)),
            "r2_score": str(r2_score(y_test, y_out_this_nhn)),
            "pearson_r": str(np.round(stats.pearsonr(y_test, y_out_this_nhn)[0], 2)),
            "length_of_training": str(self.length_of_training),
        }
        for key, value in stats_dict.items():
            print(f"{key}: {value}")

        # Save statistics
        stats_path = save_dir / "stats.json"
        with open(stats_path, "w") as json_file:
            json.dump(stats_dict, json_file, indent=4)

        logger.info("Model name: %s", str(scaler_path).split("/")[-2])
        print("Model name: ", str(scaler_path).split("/")[-2])

        if self.model_type == "rf":
            result = permutation_importance(
                model, X_test, y_test, n_repeats=10, random_state=42, n_jobs=-1
            )

            # Display importance
            feature = self.keep_vars
            for i in range(len(feature)):
                print(
                    f"Feature {feature[i]}: Importance {result.importances_mean[i]:.4f} ± {result.importances_std[i]:.4f}"
                )
                stats_dict[feature[i]] = (
                    f"importances_mean {result.importances_mean[i]}",
                    f"importances_std: {result.importances_std[i]}",
                )

            # Save statistics
            stats_path = save_dir / "stats.json"
            with open(stats_path, "w") as json_file:
                json.dump(stats_dict, json_file, indent=4)

            # Get feature importances
            importances = model.feature_importances_

            # Convert the importances into a more readable format
            feature_importances = pd.DataFrame(
                importances, index=feature, columns=["importance"]
            ).sort_values("importance", ascending=False)

            # Display the feature importances
            print(feature_importances)

            # Plotting the feature importances
            plt.figure(figsize=(12, 8))
            feature_importances.plot(kind="bar")
            plt.title("Feature Importance")
            plt.savefig(save_dir / "feature_importance.png")
            plt.close()

        return
