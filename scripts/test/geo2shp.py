import context
import json
import numpy as np
import pandas as pd
import geopandas as gpd
from context import gog_dir

fielin = (
    str(gog_dir) + "/Research/FireSmoke/FeildWork/PelicanMountain/PelicanMountain.json"
)
df = gpd.read_file(fielin)

save_unit4 = (
    str(gog_dir) + "/Research/FireSmoke/FeildWork/PelicanMountain/unit_4/unit_4.shp"
)
unit4 = df[df["title"] == "Unit_4"]
unit4.to_file(save_unit4)


save_unit1 = (
    str(gog_dir) + "/Research/FireSmoke/FeildWork/PelicanMountain/unit_1/unit_1.shp"
)
unit1 = df[df["title"] == "Unit_1"]
unit1.to_file(save_unit1)

save_unit5 = (
    str(gog_dir) + "/Research/FireSmoke/FeildWork/PelicanMountain/unit_5/unit_5.shp"
)
unit5 = df[df["title"] == "Unit_5_C"]
unit5.to_file(save_unit5)
