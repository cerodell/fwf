#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import sys
import json
import joblib
import logging
import simplekml
import numpy as np
import pandas as pd
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon

import matplotlib.pyplot as plt
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

from datetime import datetime
from utils.ml_data import MLDATA
from utils.firep import FIREP

from context import data_dir
import warnings

warnings.simplefilter(action="ignore", category=UserWarning)


# # Function to reduce precision of coordinates
# def reduce_precision(coords, precision=2):
#     return [(round(x, precision), round(y, precision)) for x, y in coords]


data_dict = {}

# Initialize MLP model and load dataset
mlD = MLDATA(config={"method": "averaged"})
cases_df = mlD.open_ml_ds()
for year in ["2021", "2022", "2023"]:
    # for year in ["2021"]:
    firep = FIREP(config={"year": year})
    firep_df = firep.open_firep()

    for ID, group in cases_df.groupby("id"):
        print("ID:", ID)
        # ID = 24237018.0
        ID = int(ID)
        id_df = firep_df.loc[firep_df["id"] == int(ID)]

        if len(id_df) == 0:
            print("No ID")
        else:
            kml = simplekml.Kml()
            id_df = id_df.round(2)
            group = group.round(2)
            # Optionally simplify geometries
            # tolerance = 1  # Set tolerance level; adjust based on your dataset and requirements
            # id_df['geometry'] = id_df['geometry'].simplify(tolerance, preserve_topology=True)

            for index, row in id_df.iterrows():
                data_dict[str(row["id"])] = {
                    "fireID": str(int(row["id"])),
                    "initialdat": row["initialdat"],
                    "finaldate": row["finaldate"],
                    "lats": str(np.round(np.mean([id_df["min_y"], id_df["max_y"]]), 2)),
                    "lons": str(np.round(np.mean([id_df["min_x"], id_df["max_x"]]), 2)),
                    "area_ha": row["area_ha"],
                }
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
                    f'/Users/crodell/fwf/scripts/test/frp-paper/fire-cases/web/data/fires/fire_outlines-{int(row["id"])}.kml'
                )


#   # Writing the dictionary to a file as JSON
# with open(f"/Users/crodell/fwf/scripts/test/frp-paper/fire-cases/web/data/ml-fires-info.json", "w") as file:
#     json.dump(data_dict, file)


# # kml.save('/Users/crodell/fwf/scripts/test/frp-paper/fire-cases/web/data/fire_outlines.kml')


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
