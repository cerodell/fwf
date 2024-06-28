#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import json
import salem
import joblib
import numpy as np
import pandas as pd
import xarray as xr
import plotly.express as px

from pathlib import Path
from context import data_dir
from sklearn.preprocessing import (
    StandardScaler,
    RobustScaler,
    MinMaxScaler,
    PowerTransformer,
)

# from utils.tf import activate_logging, create_model_directory
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
        def str_to_bool(s):
            if isinstance(s, str):
                return s.lower() == "true"
            return s

        self.user_config = config
        self.filein = "/Users/crodell/fwf/data/ml-data/training-data/"
        self.feature_vars = config.get("feature_vars", None)
        self.target_vars = config.get("target_vars", None)
        self.years = config.get("years", ["2021", "2022", "2023"])
        self.filter_std = str_to_bool(config.get("filter_std", False))
        self.method = config.get("method", "averaged")
        self.min_fire_size = config.get("min_fire_size", 0)
        self.transform = str_to_bool(config.get("transform", False))
        self.feature_scaler_type = config.get("feature_scaler_type", "standard")
        self.target_scaler_type = config.get("target_scaler_type", False)
        self.main_cases = str_to_bool(config.get("main_cases", False))
        self.shuffle_data = str_to_bool(config.get("shuffle_data", False))
        self.model_type = config.get("model_type")
        self.package = config.get("package")
        self.feature_engineer = str_to_bool(config.get("feature_engineer", False))
        self.smoothing = str_to_bool(config.get("smoothing", False))

        return

    def get_ds(self, year):
        """
        Open a dataset for a given year and convert it to a pandas DataFrame.
        """
        path = f"{self.filein}{year}-fires-{self.method}.nc"
        return xr.open_dataset(path).to_dataframe().reset_index()

    def add_engineered_features(self, dfs, feature_names, wrf):
        for feature in feature_names:
            # Split the feature name to identify the components
            components = feature.split("-")
            components_array = []
            for comp in components:
                components_array.append(dfs[comp].values)

            # Assign the new feature to the dataset
            try:
                dfs[feature] = np.prod(components_array, axis=0)
            except:
                if wrf == False:
                    dfs[feature] = (
                        ("time", "y", "x"),
                        np.prod(components_array, axis=0),
                    )
                elif wrf == True:
                    dfs[feature] = (
                        ("time", "south_north", "west_east"),
                        np.prod(components_array, axis=0),
                    )

        return dfs

    def mod_ds(self, df):
        """
        Modify the dataset by cleaning and adding new columns.
        """
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
        # df["hour_sin"] = np.sin(2 * np.pi * df["solar_hour"] / 24)
        # df["hour_cos"] = np.cos(2 * np.pi * df["solar_hour"] / 24)
        phi_sin = -np.pi
        # Compute hour_sin and hour_cos with the phase shift
        # df["hour_sin"] = 0.1 + (np.sin((2 * np.pi * df["solar_hour"] / 24) + phi_sin) + 1) * 0.45
        # df["hour_cos"] = 0.1 + (np.cos((2 * np.pi * df["solar_hour"] / 24) + phi_sin) + 1) * 0.45
        df["hour_sin"] = np.sin(np.pi * df["solar_hour"] / 24) + phi_sin
        df["hour_cos"] = np.cos(np.pi * df["solar_hour"] / 24) + phi_sin
        df.loc[df["LAI"] > 7, "LAI"] = 7
        df.loc[df["LAI"] < 0, "LAI"] = 0.01
        # df["R"] = df['R'] / 50
        df["Total_Fuel_Load"] = (
            df["Dead_Wood"] + df["Live_Wood"] + df["Live_Leaf"] + df["Dead_Foliage"]
        )

        if self.transform == True:
            # df["Total_Fuel_Load"] = df["Total_Fuel_Load"]/34
            # df["R"] = df["R"]/50
            # df["F"] = df["F"]/101
            # pt = PowerTransformer(
            #     method="yeo-johnson", standardize=False
            # )  # Yeo-Johnson allows for zero values
            # df["Total_Fuel_Load"] = np.log1p(df["Total_Fuel_Load"])
            # df["Live_Wood"] = pt.fit_transform(df[["Live_Wood"]] + 1)
            # df["Live_Leaf"] = pt.fit_transform(df[["Live_Leaf"]] + 1)
            # df["Dead_Foliage"] = pt.fit_transform(df[["Dead_Foliage"]] + 1)
            df["FRP"] = np.log1p(df["FRP"])
            df["FRE"] = np.log1p(df["FRE"])
            df["FRP_MAX"] = np.log1p(df["FRP_MAX"])
            df["FRE_MAX"] = np.log1p(df["FRE_MAX"])
            # df["U"] = np.log1p(df["U"])
            # df["R"] = np.log1p(df["R"])
            # df["F"] = np.log1p(df["F"])
            # df["LAI"] = np.log1p(df["LAI"])
        if self.feature_engineer == True:
            df = self.add_engineered_features(df, self.feature_vars, wrf=False)
        if self.filter_std:
            ################ FRE ###################
            # df["FRE_raw"] = np.expm1(df["FRE"])
            # print(len(df[df['FRE_raw'] > 20000000]))

            # print('MAX FRE: ', df['FRE_raw'].max())
            # mean_frp = df['FRE'].mean()
            # std_frp = df['FRE'].std()
            # threshold = 3

            # # Define the lower and upper bounds
            # lower_bound = mean_frp - threshold * std_frp
            # upper_bound = mean_frp + threshold * std_frp

            # # Filter the DataFrame
            # df = df[(df['FRE'] >= lower_bound) & (df['FRE'] <= upper_bound)]
            # print('NEW MAX FRE: ', df['FRE_raw'].max())
            # print(len(df[df['FRE_raw'] > 20000000]))

            ################ FRP ###################
            df["FRP_raw"] = np.expm1(df["FRP"])
            print(len(df[df["FRP_raw"] > 4000]))
            print("MAX FRP: ", df["FRP_raw"].max())
            mean_frp = df["FRP"].mean()
            std_frp = df["FRP"].std()
            threshold = 3

            # Define the lower and upper bounds
            lower_bound = mean_frp - threshold * std_frp
            upper_bound = mean_frp + threshold * std_frp

            # Filter the DataFrame
            df = df[(df["FRP"] >= lower_bound) & (df["FRP"] <= upper_bound)]
            print("NEW MAX FRP: ", df["FRP_raw"].max())
            print(len(df[df["FRP_raw"] > 4000]))
            # print('NEW MAX FRE: ', df['FRE_raw'].max())
            # print(len(df[df['FRE_raw'] > 20000000]))

            ################ ISI ###################
            # df["R_raw"] = np.expm1(df["R"])
            # print(len(df[df['R_raw'] > 100]))

            # print('MAX ISI: ', df['R_raw'].max())
            mean_frp = df["R"].mean()
            std_frp = df["R"].std()
            threshold = 3

            # Define the lower and upper bounds
            lower_bound = mean_frp - threshold * std_frp
            upper_bound = mean_frp + threshold * std_frp

            # Filter the DataFrame
            df = df[(df["R"] >= lower_bound) & (df["R"] <= upper_bound)]
            # print('NEW MAX ISI: ', df['R_raw'].max())
            # print(len(df[df['R_raw'] > 100]))

            ####### R-hour_sin-Total_Fuel_Load#######
            try:
                # print('MAX ISI: ', df['R_raw'].max())
                mean_frp = df["R-hour_sin-Total_Fuel_Load"].mean()
                std_frp = df["R-hour_sin-Total_Fuel_Load"].std()
                threshold = 3

                # Define the lower and upper bounds
                lower_bound = mean_frp - threshold * std_frp
                upper_bound = mean_frp + threshold * std_frp

                # Filter the DataFrame
                df = df[
                    (df["R-hour_sin-Total_Fuel_Load"] >= lower_bound)
                    & (df["R-hour_sin-Total_Fuel_Load"] <= upper_bound)
                ]
                # print('NEW MAX ISI: ', df['R_raw'].max())
            except:
                pass

        print("Length of dataframe: ", len(df))
        return df

    def open_ml_ds(self):
        """
        Open and modify datasets for all specified years.
        """
        return self.mod_ds(
            pd.concat([self.get_ds(year) for year in self.years], ignore_index=True)
        )

    def get_static(self, ds, static=None):
        if static != None:
            # print('Static_ds has been given')
            static_ds = static
            y, x = "south_north", "west_east"
            lons, lats = static_ds["XLONG"].values, static_ds["XLAT"].values
        else:
            static_ds = salem.open_xr_dataset(
                str(data_dir) + "/static/static-rave-3km.nc"
            ).drop_vars(["time", "xtime"])
            y, x = "y", "x"
            lons, lats = static_ds.salem.grid.ll_coordinates
        lon_sin = np.sin(np.radians(lons))
        lon_cos = np.cos(np.radians(lons))
        lat_sin = np.sin(np.radians(lats))
        lat_cos = np.cos(np.radians(lats))

        static_ds["lat_sin"] = ((y, x), lat_sin)
        static_ds["lat_cos"] = ((y, x), lat_cos)
        static_ds["lon_sin"] = ((y, x), lon_sin)
        static_ds["lon_cos"] = ((y, x), lon_cos)

        static_ds["lats"] = ((y, x), lats)
        static_ds["lons"] = ((y, x), lons)

        ASPECT_sin = np.sin(np.radians(static_ds["ASPECT"].values))
        ASPECT_cos = np.cos(np.radians(static_ds["ASPECT"].values))
        static_ds["ASPECT_sin"] = ((y, x), ASPECT_sin)
        static_ds["ASPECT_cos"] = ((y, x), ASPECT_cos)

        SAZ_sin = np.sin(np.radians(static_ds["SAZ"].values))
        SAZ_cos = np.cos(np.radians(static_ds["SAZ"].values))
        static_ds["SAZ_sin"] = ((y, x), SAZ_sin)
        static_ds["SAZ_cos"] = ((y, x), SAZ_cos)

        if static != None:
            # print('Static_ds has been given')
            static_roi = static_ds.expand_dims("time")
            static_roi.coords["time"] = pd.Series(ds.time.values[0])
            static_roi = static_roi.reindex(time=ds.time, method="ffill")
            fuel_date_range = pd.DatetimeIndex(ds["Time"].values)
            fuel_date_range = pd.date_range(
                ds["Time"].values[0], ds["Time"].values[-1], freq="MS"
            )
            if len(fuel_date_range) == 0:
                fuel_date_range = [pd.Timestamp(ds["Time"].values[0])]

        else:
            static_roi = self.add_static(ds, static_ds)
            fuel_date_range = pd.date_range(
                ds.attrs["initialdat"][:-3] + "-01", ds.attrs["finaldate"], freq="MS"
            )

        for var in list(static_roi):
            ds[var] = static_roi[var]

        fuels_ds = xr.combine_nested(
            [self.open_fuels(moi) for moi in fuel_date_range], concat_dim="time"
        )
        fuels_roi = ds.salem.transform(fuels_ds, interp="linear")
        fuels_roi = fuels_roi.reindex(time=ds.time, method="ffill")
        fuels_roi = xr.where(fuels_roi < 0, 0, fuels_roi)

        for var in list(fuels_roi):
            ds[var] = fuels_roi[var]
        ds["Total_Fuel_Load"] = (
            ds["Dead_Wood"] + ds["Live_Wood"] + ds["Live_Leaf"] + ds["Dead_Foliage"]
        )

        # if self.transform == True:
        #     ds["Total_Fuel_Load"] = ds["Total_Fuel_Load"]/34
        #     ds["R"] = ds["R"]/50
        #     ds["F"] = ds["F"]/101
        #     TFL = np.log1p(ds["Total_Fuel_Load"].values)
        #     ds["R"] = np.log1p(ds["R"])
        #     ds["F"] = np.log1p(ds["F"])
        #     ds["Total_Fuel_Load"] = (("time", y, x), TFL)

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
        fuel_dir = f"/Volumes/ThunderBay/CRodell/ecmwf/fuel-load/"
        fuels_ds = salem.open_xr_dataset(
            fuel_dir + f'{2021}/CFUEL_timemean_2021{moi.strftime("_%m")}.nc'
        ).sel(lat=slice(75, 20), lon=slice(-170, -50))
        fuels_ds.coords["time"] = moi
        return fuels_ds

    def get_eng_features(self, ds, wrf=False):
        ds = get_solar_hours(ds)
        phi_sin = -np.pi
        # Compute hour_sin and hour_cos with the phase shift
        # ds["hour_sin"] = 0.1 + (np.sin((2 * np.pi * ds["solar_hour"] / 24) + phi_sin) + 1) * 0.45
        # ds["hour_cos"] = 0.1 + (np.cos((2 * np.pi * ds["solar_hour"] / 24) + phi_sin) + 1) * 0.45
        ds["hour_sin"] = np.sin(np.pi * ds["solar_hour"] / 24) + phi_sin
        ds["hour_cos"] = np.cos(np.pi * ds["solar_hour"] / 24) + phi_sin
        ds = self.add_engineered_features(ds, self.feature_vars, wrf)

        return ds

    def get_training(self):

        df = self.open_ml_ds()

        #### REMOVE AFTER TESTING!!!!!!!!!!
        ######==================================+####################
        # df = df.iloc[:1000].reset_index(drop=True)
        ######==================================+####################
        ######==================================+####################
        ######==================================+####################
        ######==================================+####################
        ######==================================+####################
        ######==================================+####################
        ######==================================+####################

        print("Number of fires: ", len(np.unique(df["id"].values)))
        self.user_config["num_fire"] = str(len(np.unique(df["id"].values)))
        if self.main_cases == False:
            ## Sampling dataset for test and training
            IDS = np.unique(df["id"].values)
            sample_size = int(0.12 * len(IDS))
            ids = np.random.choice(IDS, size=sample_size, replace=False)
            # ids = np.append(ids, [25485086, 25407482, 24360611, 24448308, 24450415, 26695902, 25282348])
            ids = np.append(
                ids,
                [
                    25485086,
                    25282348,
                    25584809,
                    24359928,
                    24565483,
                    24296232,
                    24450415,
                    24296232,
                    24359300,
                    24359787,
                    24360611,
                    24448285,
                    24448308,
                    24449463,
                    24452554,
                    24453236,
                    24564607,
                    25407482,
                    25408581,
                    25490483,
                    25490527,
                    25585271,
                    25589765,
                    26352132,
                    26414901,
                    26415153,
                    26415924,
                    26418444,
                    26479269,
                    26480614,
                    26480912,
                    26481445,
                    26563583,
                    26564768,
                    26565481,
                    26565517,
                    26567513,
                    26568336,
                    26568545,
                    26574540,
                    26574808,
                    26691139,
                    26692849,
                    26695902,
                    26703460,
                    26815399,
                    26418468,
                    26418461,
                ],
            )

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
        print("Number of training fires: ", len(np.unique(df_train["id"].values)))
        self.user_config["num_fire_train"] = str(len(np.unique(df_train["id"].values)))
        print("Number of testing fires: ", len(np.unique(df_test["id"].values)))
        self.user_config["num_fire_test"] = str(len(np.unique(df_train["id"].values)))
        # large_fires = df_train.loc[df_train["area_ha"] > 50000]
        # larger_fires = df_train.loc[df_train["area_ha"] > 100000]
        if self.transform == True:
            cold_fires = df_train.loc[df_train["FRP"] < np.log1p(1)]
            cool_fires = df_train.loc[df_train["FRP"] < np.log1p(10)]
            warm_fires = df_train.loc[df_train["FRP"] > np.log1p(1000)]
            hot_fires = df_train.loc[df_train["FRP"] > np.log1p(1500)]
            hotter_fires = df_train.loc[df_train["FRP"] > np.log1p(2000)]
            hotter_still_fire = df_train.loc[df_train["FRP"] > np.log1p(3000)]
            hottest_fires = df_train.loc[df_train["FRP"] > np.log1p(4000)]
        else:
            cold_fires = df_train.loc[df_train["FRP"] < 1]
            cool_fires = df_train.loc[df_train["FRP"] < 10]
            warm_fires = df_train.loc[df_train["FRP"] > 1000]
            hot_fires = df_train.loc[df_train["FRP"] > 1500]
            hotter_fires = df_train.loc[df_train["FRP"] > 2000]
            hotter_still_fire = df_train.loc[df_train["FRP"] > 3000]
            hottest_fires = df_train.loc[df_train["FRP"] > 4000]
        df_train = pd.concat(
            [
                df_train,
                # large_fires,
                # larger_fires,
                cold_fires,
                cool_fires,
                warm_fires,
                hot_fires,
                hotter_fires,
                hotter_still_fire,
                hottest_fires,
            ]
        )
        df_train.reset_index(drop=True, inplace=True)

        if self.feature_vars:
            X_train = df_train[self.feature_vars].copy()
            X_test = df_test[self.feature_vars].copy()
        else:
            X_train = df_train[1:].copy()
            X_test = df_test[1:].copy()

        if self.smoothing == True:
            print("Will use smoother max frp/fre for training")
            y_train = df_train[["FRP_MAX", "FRE_MAX"]]
            y_test = df_test[["FRP", "FRE"]]
        else:
            y_train = df_train[self.target_vars]
            y_test = df_test[self.target_vars]

        if self.shuffle_data:
            X_train, y_train = shuffle(X_train, y_train, random_state=42)

        # Scale features
        if self.feature_scaler_type == "standard":
            feature_scaler = StandardScaler().fit(X_train)
        elif self.feature_scaler_type == "robust":
            feature_scaler = RobustScaler().fit(X_train)
        elif self.feature_scaler_type == "minmax":
            feature_scaler = MinMaxScaler().fit(X_train)

        if self.target_scaler_type == True:
            self.MAXFRP = 6000
            self.MAXFRE = 2e7
            y_train["FRP"] = (y_train["FRP"] - np.log1p(0)) / (
                np.log1p(self.MAXFRP) - np.log1p(0)
            )
            y_train["FRE"] = (y_train["FRE"] - np.log1p(0)) / (
                np.log1p(self.MAXFRE) - np.log1p(0)
            )
        # Scale targets
        # print(self.target_scaler_type)
        # if self.target_scaler_type == "standard":
        #     print('Using standard scaler for features')
        #     target_scaler = StandardScaler().fit(y_train)
        # elif self.feature_scaler_type == "robust":
        #     print('Using robust scaler for features')
        #     target_scaler = RobustScaler().fit(y_train)
        # elif self.feature_scaler_type == "minmax":

        # print('Using min max scaler for features')
        # target_scaler = MinMaxScaler().fit(y_train)
        # print(target_scaler)
        # y_train = target_scaler.transform(y_train)
        # else:
        target_scaler = "None"

        X_train = feature_scaler.transform(X_train)
        X_test = feature_scaler.transform(X_test)

        self.feature_scaler = feature_scaler
        self.target_scaler = target_scaler

        self.fires_array = fires_array
        self.length_of_training = len(y_train)
        self.X_test = X_test
        self.y_test = y_test
        self.df_test = df_test

        print("Percent of data used for testing: ", (len(y_test) / len(df)) * 100)
        self.user_config["percent_data_fore_test"] = str((len(y_test) / len(df)) * 100)
        return y_train, X_train, y_test, X_test

    def save_model(self, model, y_out_this_nhn, save_dir, logger):
        if self.target_scaler_type == True:
            # print("self.target_scaler_type is: ", self.target_scaler_type)
            y_out_this_nhn[:, 0] = y_out_this_nhn[:, 0] * np.log1p(self.MAXFRP)
            y_out_this_nhn[:, 1] = y_out_this_nhn[:, 1] * np.log1p(self.MAXFRE)

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
        feature_scaler_path = save_dir / "feature-scaler.joblib"
        joblib.dump(self.feature_scaler, feature_scaler_path)
        np.savetxt(
            save_dir / "test_cases.txt", self.fires_array, fmt="%d", delimiter=","
        )

        # Save model configuration and statistics
        model_config = {
            "user_config": self.user_config,
            "model_config": model_config_info,
            "feature_scaler_info": str(feature_scaler_path),
            "model_info": str(model_path),
        }
        config_path = save_dir / "config.json"
        with open(config_path, "w") as json_file:
            json.dump(model_config, json_file, indent=4)

        def solve_stats(y_test, y_out_this_nhn, target, stats_dict=None):
            if stats_dict is None:
                stats_dict = {}

            if target.lower() == "fre":
                try:
                    y_nhn = y_out_this_nhn[:, 1].ravel()
                except:
                    y_nhn = y_out_this_nhn.ravel()
                y_t = y_test["FRE"].values
                units = "(MJ)"
            elif target.lower() == "frp":
                try:
                    y_nhn = y_out_this_nhn[:, 0].ravel()
                except:
                    y_nhn = y_out_this_nhn.ravel()
                y_t = y_test["FRP"].values
                units = "(MW)"

            mbe = str(np.round(MBE(y_t, y_nhn), 2))
            rmse = np.round(RMSE(y_t, y_nhn), 2)
            r2 = np.round(r2_score(y_t, y_nhn), 2)
            r = np.round(stats.pearsonr(y_t, y_nhn)[0], 2)

            stats_dict[target] = {
                "rmse": str(rmse),
                "mbe": str(mbe),
                "r2_score": str(r2),
                "pearson_r": str(r),
                "length_of_training": str(self.length_of_training),
            }
            self.df_test["model"] = y_nhn
            self.df_test["obs"] = y_t
            self.df_test = self.df_test.round(1)

            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            ax.scatter(y_nhn, y_t, color="tab:red", s=15)
            ax.set_xlabel(f"Modeled {target.upper()} {units}")
            ax.set_ylabel(f"Observed {target.upper()} {units}")
            ax.set_title(f"MBE: {mbe}   RMSE: {rmse}   r2: {r2}   r: {r}")
            ax.axline((0, 0), slope=1, color="k", linestyle="--", lw=0.5)
            fig.savefig(str(save_dir) + f"/{target}-scatter.png")
            return stats_dict

        targets = self.user_config["target_vars"]
        stats_dict = None
        for target in targets:
            stats_dict = solve_stats(y_test, y_out_this_nhn, target, stats_dict)

        for key, value in stats_dict.items():
            print(f"{key}: {value}")

        # Save statistics
        stats_path = save_dir / "stats.json"
        with open(stats_path, "w") as json_file:
            json.dump(stats_dict, json_file, indent=4)

        logger.info("Model name: %s", str(feature_scaler_path).split("/")[-2])
        print("Model name: ", str(feature_scaler_path).split("/")[-2])

        if self.model_type == "rf":
            result = permutation_importance(
                model, X_test, y_test, n_repeats=10, random_state=42, n_jobs=-1
            )

            # Display importance
            feature = self.feature_vars
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

    def save_model_tunning(self, model, y_out_this_nhn, save_dir, logger, history):
        if self.target_scaler_type == True:
            # print("self.target_scaler_type is: ", self.target_scaler_type)
            y_out_this_nhn[:, 0] = y_out_this_nhn[:, 0] * np.log1p(self.MAXFRP)
            y_out_this_nhn[:, 1] = y_out_this_nhn[:, 1] * np.log1p(self.MAXFRE)
            # y_out_this_nhn = self.target_scaler.inverse_transform(y_out_this_nhn)

        if self.transform == True:
            # print("self.transform is: ", self.transform)
            y_out_this_nhn = np.expm1(y_out_this_nhn)
            y_test = np.expm1(self.y_test)
        else:
            y_test = self.y_test
            X_test = self.X_test

        # if self.target_scaler_type == True:
        #     y_out_this_nhn[:,0] = y_out_this_nhn[:,0] * np.log1p(4000)
        #     y_out_this_nhn[:,1] = y_out_this_nhn[:,1] * np.log1p(1.131e7)
        # Save model and scaler
        if self.package == "tf":
            model_path = save_dir / "model.keras"
            model.save(model_path)
            model_config_info = model.get_config()
            model_weights_info = model.get_weights()
            weights_path = save_dir / "model_weights.h5"
            model.save_weights(weights_path)
        else:
            model_path = save_dir / "model.joblib"
            joblib.dump(model, model_path)
            model_config_info = model.get_params()

        feature_scaler_path = save_dir / "feature-scaler.joblib"
        joblib.dump(self.feature_scaler, feature_scaler_path)
        np.savetxt(
            save_dir / "test_cases.txt", self.fires_array, fmt="%d", delimiter=","
        )

        optimizer_config_str = {
            key: str(value) for key, value in model.optimizer.get_config().items()
        }
        history_str = {key: str(value) for key, value in history.history.items()}
        # Save model configuration and statistics
        model_config = {
            "model_config": model_config_info,
            "feature_vars": self.feature_vars,
            "feature_scaler_type": self.feature_scaler_type,
            "target_scaler_type": self.target_scaler_type,
            "transform": str(self.transform),
            "feature_scaler_info": str(feature_scaler_path),
            "model_info": str(model_path),
            "model_weights": str(weights_path) if self.package == "tf" else "",
            "feature_engineer": str(self.feature_engineer),
            "main_cases": str(self.main_cases),
            "shuffle_data": str(self.shuffle_data),
            "epochs": len(history.epoch),
            "history": history_str,
            "optimizer": optimizer_config_str,
            "loss": model.loss,
            "metrics": model.metrics_names,
        }

        config_path = save_dir / "config.json"
        with open(config_path, "w") as json_file:
            json.dump(model_config, json_file, indent=4)

        def solve_stats(y_test, y_out_this_nhn, target, stats_dict=None):
            if stats_dict is None:
                stats_dict = {}

            if target == "fre":
                y_nhn = y_out_this_nhn[:, 1].ravel()
                y_t = y_test["FRE"].values
                units = "(MJ)"
            elif target == "frp":
                y_nhn = y_out_this_nhn[:, 0].ravel()
                y_t = y_test["FRP"].values
                units = "(MW)"

            mbe = str(np.round(MBE(y_t, y_nhn), 2))
            rmse = np.round(RMSE(y_t, y_nhn), 2)
            r2 = np.round(r2_score(y_t, y_nhn), 2)
            r = np.round(stats.pearsonr(y_t, y_nhn)[0], 2)

            stats_dict[target] = {
                "rmse": str(rmse),
                "mbe": str(mbe),
                "r2_score": str(r2),
                "pearson_r": str(r),
                "length_of_training": str(self.length_of_training),
            }
            self.df_test["model"] = y_nhn
            self.df_test["obs"] = y_t
            test = self.df_test.loc[self.df_test["id"] == 26564768]
            self.df_test = self.df_test.round(1)
            # # Create the scatter plot
            # fig = px.scatter(
            #     self.df_test,
            #     x='model',
            #     y='obs',
            #     color='id',  # Color points by category
            #     # size='z',  # Size points by z
            #     hover_data=['model', 'obs', 'id','R', 'U', ] + self.feature_vars # Information to display on hover
            # )

            # # Update layout for better visibility
            # fig.update_layout(
            #     title='Scatter Plot with Hover Information',
            #     xaxis_title='X Axis',
            #     yaxis_title='Y Axis',
            #     template='plotly_white'
            # )

            # # Show the plot
            # fig.show()

            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            ax.scatter(y_nhn, y_t, color="tab:red", s=15)
            ax.set_xlabel(f"Modeled {target.upper()} {units}")
            ax.set_ylabel(f"Observed {target.upper()} {units}")
            ax.set_title(f"MBE: {mbe}   RMSE: {rmse}   r2: {r2}   r: {r}")
            ax.axline((0, 0), slope=1, color="k", linestyle="--", lw=0.5)
            fig.savefig(str(save_dir) + f"/{target}-scatter.png")
            plt.close()
            return stats_dict

        stats_dict = solve_stats(y_test, y_out_this_nhn, "frp")
        stats_dict = solve_stats(y_test, y_out_this_nhn, "fre", stats_dict)

        for key, value in stats_dict.items():
            print(f"{key}: {value}")

        # Save statistics
        stats_path = save_dir / "stats.json"
        with open(stats_path, "w") as json_file:
            json.dump(stats_dict, json_file, indent=4)

        logger.info("Model name: %s", str(feature_scaler_path).split("/")[-2])
        print("Model name: ", str(feature_scaler_path).split("/")[-2])

        if self.model_type == "rf":
            result = permutation_importance(
                model, X_test, y_test, n_repeats=10, random_state=42, n_jobs=-1
            )

            # Display importance
            feature = self.feature_vars
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
