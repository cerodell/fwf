#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import sys
import os
import json
import joblib
import logging
import simplekml
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon

import matplotlib.pyplot as plt
import plotly.express as px

# import dash
# from dash import dcc, html
# from dash.dependencies import Input, Output

from datetime import datetime
from utils.ml_data import MLDATA
from utils.firep import FIREP

from context import data_dir
import warnings

warnings.simplefilter(action="ignore", category=UserWarning)
warnings.simplefilter(action="ignore", category=FutureWarning)


# # Function to reduce precision of coordinates
# def reduce_precision(coords, precision=2):
#     return [(round(x, precision), round(y, precision)) for x, y in coords]

ml_ver = "v8"
all_dict = {}
save_dir = "/Users/crodell/fwf/scripts/test/frp-paper/fire-cases/web/data"
# Initialize MLP model and load dataset
mlD = MLDATA(config={"method": f"averaged-{ml_ver}"})
cases_df = mlD.open_ml_ds()
for year in ["2021", "2022", "2023"]:
    firep = FIREP(config={"year": year})
    firep_df = firep.open_firep()

    for ID, group in cases_df.groupby("id"):
        mean_fire_dict = {}
        sum_fire_dict = {}
        ID = int(ID)
        id_df = firep_df.loc[firep_df["id"] == int(ID)]
        if len(id_df) == 0:
            print("No ID")
        else:
            if os.path.exists(
                f"/Volumes/ThunderBay/CRodell/fires/{ml_ver}/{year}-{ID}.nc"
            ):
                ds = xr.open_dataset(
                    f"/Volumes/ThunderBay/CRodell/fires/{ml_ver}/{year}-{ID}.nc"
                )
                ds_nan = xr.open_zarr(
                    f"/Volumes/WFRT-Ext23/fire/full/{year}-{ID}.zarr"
                )["FRP"].to_dataset()
                ds = xr.where(np.isnan(ds_nan["FRP"].values) == True, np.nan, ds)
                ds = ds.salem.roi(shape=id_df, all_touched=True)
                ds_space_avg = ds.mean(dim=("x", "y"))
                ds_space_sum = ds.sum(dim=("x", "y"))
                ds_space_sum = xr.where(
                    np.isnan(ds_space_avg["FRP"].values) == True, "", ds_space_sum
                )
                FRPSUM = list(ds_space_sum["FRP"].values.astype(str))
                MODELED_FRP_SUM = list(ds_space_sum["MODELED_FRP"].values.astype(str))

                sum_fire_dict = {
                    # "fireID": str(int(row["id"])),
                    # "initialdat": row["initialdat"],
                    # "finaldate": row["finaldate"],
                    "lats": str(np.round(np.mean([id_df["min_y"], id_df["max_y"]]), 2)),
                    "lons": str(np.round(np.mean([id_df["min_x"], id_df["max_x"]]), 2)),
                    # "area_ha": row["area_ha"],
                    # "local_datetime": local_time,
                    "FRP": list(ds_space_sum["FRP"].values.astype(str)),
                    "MODELED_FRP": list(ds_space_sum["MODELED_FRP"].values.astype(str)),
                    "FWI": list(ds_space_sum["S"].values.astype(str)),
                    "HFI": list(ds_space_sum["HFI"].values.astype(str)),
                    "FFMC": list(ds_space_sum["F"].values.astype(str)),
                    "ISI": list(ds_space_sum["ISI"].values.astype(str)),
                    "ROS": list(ds_space_sum["ROS"].values.astype(str)),
                    "SFC": list(ds_space_sum["SFC"].values.astype(str)),
                    "TFC": list(ds_space_sum["TFC"].values.astype(str)),
                    "BUI": list(ds_space_sum["U"].values.astype(str)),
                    "PM25": list(ds_space_sum["PM25"].values.astype(str)),
                    "NDVI": list(ds_space_sum["NDVI"].values.astype(str)),
                    "LAI": list(ds_space_sum["LAI"].values.astype(str)),
                    "WS": list(ds_space_sum["W"].values.astype(str)),
                    "WD": list(ds_space_sum["WD"].values.astype(str)),
                    "RH": list(ds_space_sum["H"].values.astype(str)),
                    "TEMP": list(ds_space_sum["T"].values.astype(str)),
                    "PRECIP": list(ds_space_sum["r_o_hourly"].values.astype(str)),
                    "HGT": [str(ds_space_sum["HGT"].values[0])],
                    "GS": [str(ds_space_sum["GS"].values[0])],
                    "Live_Leaf": list(ds_space_sum["Live_Leaf"].values.astype(str)),
                    "Dead_Foliage": list(
                        ds_space_sum["Dead_Foliage"].values.astype(str)
                    ),
                    "Live_Wood": list(ds_space_sum["Live_Wood"].values.astype(str)),
                    "Dead_Wood": list(ds_space_sum["Dead_Wood"].values.astype(str)),
                }

                ds_space_avg = xr.where(
                    np.isnan(ds_space_avg["FRP"].values) == True, "", ds_space_avg
                )
                FRP = list(ds_space_avg["FRP"].values.astype(str))
                MODELED_FRP = list(ds_space_avg["MODELED_FRP"].values.astype(str))

            else:
                FRP = None
                MODELED_FRP = None

            kml = simplekml.Kml()
            id_df = id_df.round(2)
            group = group.round(2)
            local_time = list(
                pd.to_datetime(group["local_time"])
                .dt.strftime("%Y-%m-%dT%H")
                .values.astype(str)
            )

            # Identify rows where 'FRP' is NaN
            nan_frp_mask = group["FRP"].isna()

            # Replace all columns in those rows with ''
            group.loc[nan_frp_mask, :] = group.loc[nan_frp_mask, :].map(lambda x: "")

            # Optionally simplify geometries
            # tolerance = 1  # Set tolerance level; adjust based on your dataset and requirements
            # id_df['geometry'] = id_df['geometry'].simplify(tolerance, preserve_topology=True)
            for index, row in id_df.iterrows():
                mean_fire_dict = {
                    "fireID": str(int(row["id"])),
                    "initialdat": row["initialdat"],
                    "finaldate": row["finaldate"],
                    "lats": str(np.round(np.mean([id_df["min_y"], id_df["max_y"]]), 2)),
                    "lons": str(np.round(np.mean([id_df["min_x"], id_df["max_x"]]), 2)),
                    "area_ha": row["area_ha"],
                    "local_datetime": local_time,
                    "FRP": list(group["FRP"].values.astype(str)),
                    "FWI": list(group["S"].values.astype(str)),
                    "HFI": list(group["HFI"].values.astype(str)),
                    "FFMC": list(group["F"].values.astype(str)),
                    "ISI": list(group["ISI"].values.astype(str)),
                    "ROS": list(group["ROS"].values.astype(str)),
                    "SFC": list(group["SFC"].values.astype(str)),
                    "TFC": list(group["TFC"].values.astype(str)),
                    "BUI": list(group["U"].values.astype(str)),
                    "PM25": list(group["PM25"].values.astype(str)),
                    "NDVI": list(group["NDVI"].values.astype(str)),
                    "LAI": list(group["LAI"].values.astype(str)),
                    "WS": list(group["W"].values.astype(str)),
                    "WD": list(group["WD"].values.astype(str)),
                    "RH": list(group["H"].values.astype(str)),
                    "TEMP": list(group["T"].values.astype(str)),
                    "PRECIP": list(group["r_o_hourly"].values.astype(str)),
                    "HGT": [str(group["HGT"].values[0])],
                    "GS": [str(group["GS"].values[0])],
                    "Live_Leaf": list(group["Live_Leaf"].values.astype(str)),
                    "Dead_Foliage": list(group["Dead_Foliage"].values.astype(str)),
                    "Live_Wood": list(group["Live_Wood"].values.astype(str)),
                    "Dead_Wood": list(group["Dead_Wood"].values.astype(str)),
                    "OFFSET_NORM": list(group["OFFSET_NORM"].values.astype(str)),
                }

                all_dict[str(row["id"])] = {
                    "fireID": str(int(row["id"])),
                    "initialdat": row["initialdat"],
                    "finaldate": row["finaldate"],
                    "lats": str(np.round(np.mean([id_df["min_y"], id_df["max_y"]]), 2)),
                    "lons": str(np.round(np.mean([id_df["min_x"], id_df["max_x"]]), 2)),
                    "area_ha": row["area_ha"],
                }
                if FRP != None:
                    print("++TEST ID:", ID)
                    mean_fire_dict["OBS_FRP"] = FRP
                    mean_fire_dict["MODELED_FRP"] = MODELED_FRP
                    all_dict[str(row["id"])]["TYPE"] = "test"
                    # Writing the dictionary to a file as JSON
                    with open(
                        f"{save_dir}/fires-v2/ml-test-mean-fires-info-{int(ID)}.json",
                        "w",
                    ) as file:
                        json.dump(mean_fire_dict, file)

                    sum_fire_dict["fireID"] = str(int(row["id"]))
                    sum_fire_dict["initialdat"] = row["initialdat"]
                    sum_fire_dict["finaldate"] = row["finaldate"]
                    sum_fire_dict["area_ha"] = row["area_ha"]
                    sum_fire_dict["local_datetime"] = local_time
                    with open(
                        f"{save_dir}/fires-{ml_ver}/ml-test-sum-fires-info-{int(ID)}.json",
                        "w",
                    ) as file:
                        json.dump(sum_fire_dict, file)

                else:
                    print("--TRAIN ID:", ID)
                    all_dict[str(row["id"])]["TYPE"] = "train"
                    # Writing the dictionary to a file as JSON
                    with open(
                        f"{save_dir}/fires-{ml_ver}/ml-train-mean-fires-info-{int(ID)}.json",
                        "w",
                    ) as file:
                        json.dump(mean_fire_dict, file)

                geom = row.geometry
                # Handle Polygon geometries
                if isinstance(geom, Polygon):
                    pol = kml.newpolygon(name=row.get("NAME", str(int(row["id"]))))
                    outer_ring = [(x, y) for x, y in zip(*geom.exterior.coords.xy)]
                    pol.outerboundaryis.coords = outer_ring
                    # Add inner boundaries (holes)
                    for interior in geom.interiors:
                        inner_ring = [(x, y) for x, y in zip(*interior.coords.xy)]
                        pol.innerboundaryis.append(inner_ring)

                # Handle MultiPolygon geometries
                elif isinstance(geom, MultiPolygon):
                    for (
                        polygon
                    ) in geom.geoms:  # Iterate over polygons in a MultiPolygon
                        pol = kml.newpolygon(name=row.get("NAME", str(int(row["id"]))))
                        outer_ring = [
                            (x, y) for x, y in zip(*polygon.exterior.coords.xy)
                        ]
                        pol.outerboundaryis.coords = outer_ring
                        # Add inner boundaries (holes)
                        for interior in polygon.interiors:
                            inner_ring = [(x, y) for x, y in zip(*interior.coords.xy)]
                            pol.innerboundaryis.append(inner_ring)

                else:
                    continue  # Skip non-polygon geometries
                kml.save(
                    f'{save_dir}/fires-{ml_ver}/fire_outlines-{int(row["id"])}.kml'
                )


# Writing the dictionary to a file as JSON
with open(
    f"{save_dir}/ml-fires-info-{ml_ver}.json",
    "w",
) as file:
    json.dump(all_dict, file)


# # Initialize MLP model and load dataset
# mlp = MLP(config={"method": "averaged"})
# cases_df = mlp.open_ml_ds()
# for year in ["2021", "2022", "2023"]:
#   firep = FIREP(config={"year": year})
#   firep_df = firep.open_firep()

#   for ID, group in cases_df.groupby("id"):
#       # data_dict = {}
#       print("ID:", ID)
#       id_df = firep_df.loc[firep_df["id"]==int(ID)]
#       if len(id_df) == 0:
#           print("No ID")
#       else:
#         group = group.round(2)
#         for index, row in id_df.iterrows():
#           data_dict = {
#               "fireID": str(int(row["id"])),
#               "initialdat": row["initialdat"],
#               "finaldate": row["finaldate"],
#               "lats": str(np.round(np.mean([id_df["min_y"],id_df["max_y"]]),2)),
#               "lons": str(np.round(np.mean([id_df["min_x"],id_df["max_x"]]),2)),
#               "area_ha": row["area_ha"],
#               "local_datetime": list(pd.to_datetime(group["local_time"]).dt.strftime("%Y-%m-%dT%H").values.astype(str)),
#               "FRP": list(group["FRP"].values.astype(str)),
#               "FWI": list(group["S"].values.astype(str)),
#               "HFI": list(group["HFI"].values.astype(str)),
#               "FFMC": list(group["F"].values.astype(str)),
#               "ISI": list(group["ISI"].values.astype(str)),
#               "ROS": list(group["ROS"].values.astype(str)),
#               "SFC": list(group["SFC"].values.astype(str)),
#               "TFC": list(group["TFC"].values.astype(str)),
#               "BUI": list(group["U"].values.astype(str)),
#               "PM25": list(group["PM25"].values.astype(str)),
#               "NDVI": list(group["NDVI"].values.astype(str)),
#               "LAI": list(group["LAI"].values.astype(str)),
#               "WS": list(group["W"].values.astype(str)),
#               "WD": list(group["WD"].values.astype(str)),
#               "RH": list(group["H"].values.astype(str)),
#               "TEMP": list(group["T"].values.astype(str)),
#               "PRECIP": list(group["r_o_hourly"].values.astype(str)),
#               "HGT": list(group["HGT"].values[0].astype(str)),
#               "GS": list(group["GS"].values[0].astype(str)),
#               "RH": list(group["H"].values.astype(str)),
#               "Live_Leaf": list(group["Live_Leaf"].values.astype(str)),
#               "Dead_Foliage": list(group["Dead_Foliage"].values.astype(str)),
#               "Live_Wood": list(group["Live_Wood"].values.astype(str)),
#               "Dead_Wood": list(group["Dead_Wood"].values.astype(str))
#           }
#           # Writing the dictionary to a file as JSON
#         with open(f"/Users/crodell/fwf/scripts/test/frp-paper/fire-cases/web/data/fires/ml-fires-info-{int(ID)}.json", "w") as file:
#             json.dump(data_dict, file)
