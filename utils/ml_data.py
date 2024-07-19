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
from sklearn.model_selection import train_test_split

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
        self.burn_time = config.get("burn_time", 0)
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
        og_len = len(df)
        df = df.loc[df["area_ha"] > self.min_fire_size]
        df = df.loc[df["burn_time"] > self.burn_time]
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
        df["hour_sin"] = (
            0.1 + (np.sin((2 * np.pi * df["solar_hour"] / 24) + phi_sin) + 1) * 0.45
        )
        df["hour_cos"] = (
            0.1 + (np.cos((2 * np.pi * df["solar_hour"] / 24) + phi_sin) + 1) * 0.45
        )

        # df["hour_sin"] =  df["hour_sin"]**2
        # df["hour_cos"] =   df["hour_cos"]**2

        df.loc[df["LAI"] > 7, "LAI"] = 7
        df.loc[df["LAI"] < 0, "LAI"] = 0.01
        # df["R"] = df['R'] / 50
        # df["Total_Fuel_Load"] = (
        #     df["Dead_Wood"] + df["Live_Wood"] + df["Live_Leaf"] + df["Dead_Foliage"]
        # )
        # og_len = len(df)
        if self.transform == True:
            df["FRP"] = np.log1p(df["FRP"])
            df["FRE"] = np.log1p(df["FRE"])
            # df['R'] = df['R']**2
            # df['S'] = np.log1p(df['S'])
            # df['U'] = np.log1p(df['U'])
            # df['LAI'] = np.log1p(df['LAI'])
            # df['Live_Wood'] = np.log1p(df['Live_Wood'])
            # df['Dead_Wood'] = np.log1p(df['Dead_Wood'])
            # df['Live_Leaf'] = np.log1p(df['Live_Leaf'])
            # df['Dead_Foliage'] = np.log1p(df['Dead_Foliage'])

            # df['Total_Fuel_Load'] = np.log1p(df['Total_Fuel_Load'])
            # df['CLIMO_FRP'] = df['CLIMO_FRP'] / df['CLIMO_FRP'].max()
        if self.filter_std:
            ################ FRP ###################
            frp_max_threshold = 1000
            frp_min_threshold = 1
            print(
                f'Number pf FRP obs above {frp_max_threshold} MW {len(df[np.expm1(df["FRP"]) > frp_max_threshold])}'
            )
            print(
                f'Number pf FRP obs below {frp_min_threshold} MW {len(df[np.expm1(df["FRP"]) < frp_min_threshold])}'
            )
            print("-------------------------------------")

            for var in ["FRP"]:
                print("==================================")
                print(f"MAX {var}: ", np.expm1(df[var]).max())
                print(f"MIN {var}: ", np.expm1(df[var]).min())
                mean_frp = df[var].mean()
                std_frp = df[var].std()
                threshold = 3
                # Define the lower and upper bounds
                lower_bound = mean_frp - threshold * std_frp
                upper_bound = mean_frp + threshold * std_frp
                # Filter the DataFrame
                df = df[(df[var] >= lower_bound) & (df[var] <= upper_bound)]
                print(f"NEW MAX {var}: ", np.expm1(df[var]).max())
                print(f"NEW MIN {var}: ", np.expm1(df[var]).min())
            print("-------------------------------------")
            print(
                f'Number pf FRP obs above {frp_max_threshold} MW {len(df[np.expm1(df["FRP"]) > frp_max_threshold])}'
            )
            print(
                f'Number pf FRP obs below {frp_min_threshold} MW {len(df[np.expm1(df["FRP"]) < frp_min_threshold])}'
            )
            print(
                f"Percentage of data dropped:  {np.round(100-((len(df)/og_len)*100),3)}%"
            )

        if self.feature_engineer == True:
            df = self.add_engineered_features(df, self.feature_vars, wrf=False)

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
            curves_ds = salem.open_xr_dataset(
                str(data_dir) + "/static/curves-wrf-d02.nc"
            )
            fire_time = ds.time.values
            hour_one = pd.Timestamp(fire_time[0]).hour
            curves_ds = curves_ds.roll(time=-hour_one, roll_coords=True)
            for var in list(curves_ds):
                CURVES_VAR = curves_ds[var].values
                N = len(fire_time)
                ds[var] = (("time", y, x), np.tile(CURVES_VAR, (N + 1, 1, 1))[:N, :, :])
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
        fuels_roi["Total_Fuel_Load"] = (
            fuels_roi["Live_Leaf"]
            + fuels_roi["Live_Wood"]
            + fuels_roi["Dead_Foliage"]
            + fuels_roi["Dead_Wood"]
        )

        for var in list(fuels_roi):
            ds[var] = fuels_roi[var]

        if self.transform == True:
            print("Transforming Features")
            ds["R"] = np.log1p(ds["R"])
            ds["S"] = np.log1p(ds["S"])
            ds["U"] = np.log1p(ds["U"])
            ds["Total_Fuel_Load"] = np.log1p(ds["Total_Fuel_Load"])
            # ds['CLIMO_FRP'] = ds['CLIMO_FRP'] / ds['CLIMO_FRP'].max()

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
        # ds["hour_sin"] = (
        #     0.2 + (np.sin((2 * np.pi * ds["solar_hour"] / 24) + phi_sin) + 1) * 0.35
        # ) * 100
        # ds["hour_cos"] = (
        #     0.2 + (np.cos((2 * np.pi * ds["solar_hour"] / 24) + phi_sin) + 1) * 0.35
        # ) * 100
        ds["hour_sin"] = (
            0.1 + (np.sin((2 * np.pi * ds["solar_hour"] / 24) + phi_sin) + 1) * 0.45
        )
        ds["hour_cos"] = (
            0.1 + (np.cos((2 * np.pi * ds["solar_hour"] / 24) + phi_sin) + 1) * 0.45
        )
        # ds["hour_sin"] = ds["hour_sin"]**2
        # ds["hour_cos"] = ds["hour_cos"]**2
        # ds["hour_sin"] =  np.sin((2 * np.pi * ds["solar_hour"] / 24) + phi_sin)
        # ds["hour_cos"] =  np.cos((2 * np.pi * ds["solar_hour"] / 24) + phi_sin)
        ds = self.add_engineered_features(ds, self.feature_vars, wrf)

        return ds

    def get_training(self):

        df = self.open_ml_ds()
        # Group by the unique ID
        # grouped = df.groupby('id')
        # # Filter out groups with fewer than 72 rows
        # filtered_groups = [group for name, group in grouped if len(group) >= 144]
        # # Concatenate the filtered groups back into a single DataFrame
        # df = pd.concat(filtered_groups)
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
        user_config = self.user_config
        print("Number of fires: ", len(np.unique(df["id"].values)))
        user_config["num_fire"] = str(len(np.unique(df["id"].values)))
        ## Sampling dataset for test and training
        IDS = np.unique(df["id"].values)
        # sample_size = int(0.12 * len(IDS))
        # sample_size = int(0.12 * len(IDS))

        # Split into 70% train and 30% remaining
        # train_ids, remaining_ids = train_test_split(IDS, test_size=0.30, random_state=np.random.randint(low=75, high=150))
        train_ids, remaining_ids = train_test_split(
            IDS, test_size=0.30, random_state=100
        )

        # Split the remaining 30% into 15% validation and 15% test
        # val_ids, test_ids = train_test_split(remaining_ids, test_size=0.50, random_state=np.random.randint(low=75, high=150))
        val_ids, test_ids = train_test_split(
            remaining_ids, test_size=0.50, random_state=100
        )

        # Verify the splits
        print(f"Training IDs: {len(train_ids)}")
        print(f"Validation IDs: {len(val_ids)}")
        print(f"Testing IDs: {len(test_ids)}")

        # ids = np.random.choice(IDS, size=sample_size, replace=False)

        df_train = df[df["id"].isin(train_ids)]
        unique_train_df = df_train.drop_duplicates(subset="id", keep="first")
        train_fires_array = np.stack(
            [
                unique_train_df["id"].values,
                unique_train_df["local_time"].dt.year.values,
            ]
        )

        df_val = df[df["id"].isin(val_ids)]
        unique_val_df = df_val.drop_duplicates(subset="id", keep="first")
        val_fires_array = np.stack(
            [
                unique_val_df["id"].values,
                unique_val_df["local_time"].dt.year.values,
            ]
        )

        df_test = df[df["id"].isin(test_ids)]
        unique_test_df = df_test.drop_duplicates(subset="id", keep="first")
        test_fires_array = np.stack(
            [
                unique_test_df["id"].values,
                unique_test_df["local_time"].dt.year.values,
            ]
        )

        print(f"Training percentage: {np.round(100*len(df_train)/len(df),1)}")
        print(f"Validation percentage: {np.round(100*len(df_val)/len(df),1)}")
        print(f"Testing percentage: {np.round(100*len(df_test)/len(df),1)}")
        user_config["num_fire_train"] = str(len(unique_train_df.values))
        user_config["num_fire_val"] = str(len(unique_val_df.values))
        user_config["num_fire_test"] = str(len(unique_test_df.values))
        user_config["pre_fire_train"] = np.round(100 * len(df_train) / len(df), 1)
        user_config["pre_fire_val"] = np.round(100 * len(df_val) / len(df), 1)
        user_config["pre_fire_test"] = np.round(100 * len(df_test) / len(df), 1)

        # Function to add perturbations
        def add_perturbations(df, scale):
            df = df_train.loc[df_train["FRP"] > np.log1p(500)]
            df = df[self.feature_vars + self.target_vars]
            perturbations = np.random.normal(loc=0, scale=scale, size=df.shape).astype(
                "float32"
            )
            perturbed_df = df.copy()
            perturbed_df = pd.DataFrame(
                df.values + perturbations, columns=self.feature_vars + self.target_vars
            )
            return perturbed_df

        if self.transform == True:
            # cold_fires = df_train.loc[df_train["FRP"] < np.log1p(1)]
            # cool_fires = df_train.loc[df_train["FRP"] < np.log1p(10)]
            warm_fires = add_perturbations(
                df_train.loc[df_train["FRP"] > np.log1p(500)], 0.01
            )
            hot_fires = add_perturbations(
                df_train.loc[df_train["FRP"] > np.log1p(1000)], 0.01
            )
            hotter_fires = add_perturbations(
                df_train.loc[df_train["FRP"] > np.log1p(1500)], 0.01
            )
            hotter_still_fire = add_perturbations(
                df_train.loc[df_train["FRP"] > np.log1p(2000)], 0.01
            )
            hottest_fires = add_perturbations(
                df_train.loc[df_train["FRP"] > np.log1p(3000)], 0.01
            )
        else:
            # cold_fires = df_train.loc[df_train["FRP"] < 1]
            # cool_fires = df_train.loc[df_train["FRP"] < 10]
            warm_fires = add_perturbations(df_train.loc[df_train["FRP"] > 500], 0.01)
            hot_fires = add_perturbations(df_train.loc[df_train["FRP"] > 1000], 0.01)
            hotter_fires = add_perturbations(df_train.loc[df_train["FRP"] > 1500], 0.01)
            hotter_still_fire = add_perturbations(
                df_train.loc[df_train["FRP"] > 2000], 0.01
            )
            hottest_fires = add_perturbations(
                df_train.loc[df_train["FRP"] > 3000], 0.01
            )
        df_train = pd.concat(
            [
                df_train,
                # cold_fires,
                # cool_fires,
                warm_fires,
                hot_fires,
                hotter_fires,
                hotter_still_fire,
                hottest_fires,
            ]
        )
        df_train.reset_index(drop=True, inplace=True)

        X_train = df_train[self.feature_vars].copy()

        X_val = df_val[self.feature_vars].copy()
        X_test = df_test[self.feature_vars].copy()

        y_train = df_train[self.target_vars]
        y_val = df_val[self.target_vars]
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
            # target_scaler = MinMaxScaler().fit(y_train)
            # target_scaler = RobustScaler().fit(y_train)
            # y_train = target_scaler.transform(y_train)
            for var in self.target_vars:
                user_config[f"{var}_MAX"] = float(y_train[var].max())
            y_train = y_train / y_train.max()
            self.target_scaler = "MAX_MIN"
        else:
            self.target_scaler = None

        X_train = feature_scaler.transform(X_train)
        X_val = feature_scaler.transform(X_val)
        X_test = feature_scaler.transform(X_test)

        self.feature_scaler = feature_scaler

        self.train_fires_array = train_fires_array
        self.val_fires_array = val_fires_array
        self.test_fires_array = test_fires_array
        self.length_of_training = len(y_train)
        self.X_val = X_val
        self.y_val = y_val
        self.df_val = df_val

        self.user_config = user_config
        return y_train, X_train, X_val, y_val

    def save_model(self, model, y_out_this_nhn, save_dir, logger):
        if self.target_scaler_type == True:
            # print("self.target_scaler_type is: ", self.target_scaler_type)
            # y_out_this_nhn = self.target_scaler.inverse_transform(y_out_this_nhn)
            y_out_this_nhn = y_out_this_nhn * self.user_config["FRP_MAX"]

        if self.transform == True:
            y_out_this_nhn = np.expm1(y_out_this_nhn)
            y_val = np.expm1(self.y_val)
        else:
            y_val = self.y_val

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
            save_dir / "train_cases.txt",
            self.train_fires_array,
            fmt="%d",
            delimiter=",",
        )
        np.savetxt(
            save_dir / "val_cases.txt", self.val_fires_array, fmt="%d", delimiter=","
        )
        np.savetxt(
            save_dir / "test_cases.txt", self.test_fires_array, fmt="%d", delimiter=","
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

        def solve_stats(y_val, y_out_this_nhn, target, stats_dict=None):
            if stats_dict is None:
                stats_dict = {}

            if target.lower() == "fre":
                try:
                    y_nhn = y_out_this_nhn[:, 1].ravel()
                except:
                    y_nhn = y_out_this_nhn.ravel()
                y_t = y_val["FRE"].values
                units = "(MJ)"
            elif target.lower() == "frp":
                try:
                    y_nhn = y_out_this_nhn[:, 0].ravel()
                except:
                    y_nhn = y_out_this_nhn.ravel()
                y_t = y_val["FRP"].values
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
            self.df_val["model"] = y_nhn
            print(f"Min prediction of {target}: {float(np.min(y_nhn))}")
            self.df_val["obs"] = y_t
            self.df_val = self.df_val.round(1)
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            ax.scatter(y_nhn, y_t, color="tab:red", s=15)
            ax.set_xlabel(f"Modeled {target.upper()} {units}")
            ax.set_ylabel(f"Observed {target.upper()} {units}")
            ax.set_title(f"MBE: {mbe}   RMSE: {rmse}   r2: {r2}   r: {r}")
            ax.axline((0, 0), slope=1, color="k", linestyle="--", lw=0.5)
            if target == "FRP":
                min_lim = -100
                max_lim = np.max(np.stack([y_nhn, y_t])) - min_lim
            else:
                min_lim = -1e5
                max_lim = np.max(np.stack([y_nhn, y_t])) - min_lim
            ax.set_xlim(min_lim, max_lim)
            ax.set_ylim(min_lim, max_lim)
            # ticks = [10, 20, 50, 100, 200, 300, 500, 800, 1000, 1500,2000, 3000]
            # ax.set_xticks(ticks)
            # ax.set_yticks(ticks)
            fig.savefig(str(save_dir) + f"/{target}-scatter.png")
            return stats_dict

        targets = self.user_config["target_vars"]
        stats_dict = None
        for target in targets:
            stats_dict = solve_stats(y_val, y_out_this_nhn, target, stats_dict)

        for key, value in stats_dict.items():
            print(f"{key}: {value}")

        # Save statistics
        stats_path = save_dir / "stats.json"
        with open(stats_path, "w") as json_file:
            json.dump(stats_dict, json_file, indent=4)

        logger.info("Model name: %s", str(feature_scaler_path).split("/")[-2])
        print("Model name: ", str(feature_scaler_path).split("/")[-2])

        return

    # def save_model_tunning(self, model, y_out_this_nhn, save_dir, logger, history):
    #     if self.target_scaler_type == True:
    #         # print("self.target_scaler_type is: ", self.target_scaler_type)
    #         # y_out_this_nhn = self.target_scaler.inverse_transform(y_out_this_nhn)
    #         y_out_this_nhn[:, 0] = y_out_this_nhn[:, 0] * np.log1p(self.MAXFRP)
    #         y_out_this_nhn[:, 1] = y_out_this_nhn[:, 1] * np.log1p(self.MAXFRE)

    #     if self.transform == True:
    #         y_out_this_nhn = np.expm1(y_out_this_nhn)
    #         y_val = np.expm1(self.y_val)
    #     else:
    #         y_val = self.y_val

    #       # Save model and scaler
    #     if self.package == "tf":
    #         model_path = save_dir / "model.keras"
    #         model.save(model_path)
    #         model_config_info = model.get_config()
    #     else:
    #         model_path = save_dir / "model.joblib"
    #         joblib.dump(model, model_path)
    #         model_config_info = model.get_params()

    #     model_path = save_dir / "model.joblib"
    #     joblib.dump(model, model_path)
    #     feature_scaler_path = save_dir / "feature-scaler.joblib"
    #     joblib.dump(self.feature_scaler, feature_scaler_path)
    #     np.savetxt(
    #         save_dir / "train_cases.txt", self.train_fires_array, fmt="%d", delimiter=","
    #     )
    #     np.savetxt(
    #         save_dir / "val_cases.txt", self.val_fires_array, fmt="%d", delimiter=","
    #     )
    #     np.savetxt(
    #         save_dir / "test_cases.txt", self.test_fires_array, fmt="%d", delimiter=","
    #     )

    #     # Save model configuration and statistics
    #     model_config = {
    #         "user_config": self.user_config,
    #         "model_config": model_config_info,
    #         "feature_scaler_info": str(feature_scaler_path),
    #         "model_info": str(model_path),
    #     }
    #     config_path = save_dir / "config.json"
    #     with open(config_path, "w") as json_file:
    #         json.dump(model_config, json_file, indent=4)

    #     def solve_stats(y_val, y_out_this_nhn, target, stats_dict=None):
    #         if stats_dict is None:
    #             stats_dict = {}

    #         if target.lower() == "fre":
    #             try:
    #                 y_nhn = y_out_this_nhn[:, 1].ravel()
    #             except:
    #                 y_nhn = y_out_this_nhn.ravel()
    #             y_t = y_val["FRE"].values
    #             units = "(MJ)"
    #         elif target.lower() == "frp":
    #             try:
    #                 y_nhn = y_out_this_nhn[:, 0].ravel()
    #             except:
    #                 y_nhn = y_out_this_nhn.ravel()
    #             y_t = y_val["FRP"].values
    #             units = "(MW)"

    #         mbe = str(np.round(MBE(y_t, y_nhn), 2))
    #         rmse = np.round(RMSE(y_t, y_nhn), 2)
    #         r2 = np.round(r2_score(y_t, y_nhn), 2)
    #         r = np.round(stats.pearsonr(y_t, y_nhn)[0], 2)

    #         stats_dict[target] = {
    #             "rmse": str(rmse),
    #             "mbe": str(mbe),
    #             "r2_score": str(r2),
    #             "pearson_r": str(r),
    #             "length_of_training": str(self.length_of_training),
    #         }
    #         self.df_val["model"] = y_nhn
    #         self.df_val["obs"] = y_t
    #         self.df_val = self.df_val.round(1)

    #         fig = plt.figure()
    #         ax = fig.add_subplot(1, 1, 1)
    #         ax.scatter(y_nhn, y_t, color="tab:red", s=15)
    #         ax.set_xlabel(f"Modeled {target.upper()} {units}")
    #         ax.set_ylabel(f"Observed {target.upper()} {units}")
    #         ax.set_title(f"MBE: {mbe}   RMSE: {rmse}   r2: {r2}   r: {r}")
    #         ax.axline((0, 0), slope=1, color="k", linestyle="--", lw=0.5)
    #         # min_lim = min(min(y_nhn), min(y_t))
    #         # max_lim = max(max(y_nhn), max(y_t))
    #         # ax.set_xlim(min_lim, max_lim)
    #         # ax.set_ylim(min_lim, max_lim)
    #         # ax.set_xscale('log')
    #         # ax.set_yscale('log')
    #         fig.savefig(str(save_dir) + f"/{target}-scatter.png")
    #         return stats_dict

    #     targets = self.user_config["target_vars"]
    #     stats_dict = None
    #     for target in targets:
    #         stats_dict = solve_stats(y_val, y_out_this_nhn, target, stats_dict)

    #     for key, value in stats_dict.items():
    #         print(f"{key}: {value}")

    #     # Save statistics
    #     stats_path = save_dir / "stats.json"
    #     with open(stats_path, "w") as json_file:
    #         json.dump(stats_dict, json_file, indent=4)

    #     logger.info("Model name: %s", str(feature_scaler_path).split("/")[-2])
    #     print("Model name: ", str(feature_scaler_path).split("/")[-2])

    #     return
