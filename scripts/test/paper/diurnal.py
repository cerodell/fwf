import context
import json
import numpy as np
import xarray as xr
import pandas as pd
import geopandas as gpd
from pathlib import Path

# import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import matplotlib.pyplot as plt

from context import data_dir, root_dir

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

#################### INPUTS ####################
model = "wrf"
domain = "d03"
trail_name = "02"
date_range = pd.date_range("2023-05-01", "2023-05-15")
fwf_dir = f"/Volumes/WFRT-Ext24/fwf-data/"

wrf_ds = xr.open_dataset(str(data_dir) + f"/wrf/wrfout_d02_2023-04-20_00:00:00")
QICE = wrf_ds["QICE"]


try:
    ds_locs = xr.open_dataset(str(data_dir) + f"/wrf/202305-FWI.nc")
except:
    ## open master obs file and slice along date range of interest
    ds_obs = xr.open_dataset(
        str(data_dir) + f"/obs/observations-all-20191231-20221231.nc"
    )
    ds_obs = ds_obs.isel(wmo=np.where(ds_obs.prov.values == "AB")[0])
    ## convert lat lon coordinate in master obs to meter base x y as define by wrf polar stere projection
    df = pd.DataFrame(
        data={
            "lons": ds_obs.lons.values,
            "lats": ds_obs.lats.values,
            "wmo": ds_obs.wmo.values,
        }
    )

    def get_locs(pyproj_srs):
        # get_locs_time = datetime.now()
        gpm25 = gpd.GeoDataFrame(
            df,
            crs="EPSG:4326",
            #  crs="+init=epsg:4326",
            geometry=gpd.points_from_xy(df["lons"], df["lats"]),
        ).to_crs(pyproj_srs)

        x = xr.DataArray(
            np.array(gpm25.geometry.x),
            dims="wmo",
            coords=dict(wmo=gpm25.wmo.values),
        )
        y = xr.DataArray(
            np.array(gpm25.geometry.y),
            dims="wmo",
            coords=dict(wmo=gpm25.wmo.values),
        )
        # print("Locs Time: ", datetime.now() - get_locs_time)

        return x, y

    static_ds = xr.open_dataset(str(data_dir) + f"/static/static-vars-wrf-d03.nc")
    x, y = get_locs(static_ds.attrs["pyproj_srs"])

    def open_data(doi):
        ds = xr.open_dataset(
            str(fwf_dir)
            + f"/{model}/{domain}/{trail_name}/fwf-hourly-{domain}-{doi.strftime('%Y%m%d')}06.nc"
        ).isel(time=slice(0, 24))
        ds["south_north"] = static_ds["south_north"]
        ds["west_east"] = static_ds["west_east"]
        ds = ds[["F", "R", "S", "T", "W", "H", "r_o"]]
        return ds.chunk("auto")

    ds = xr.combine_nested([open_data(doi) for doi in date_range], concat_dim="time")
    ds_locs = ds.interp(south_north=y, west_east=x)
    ds_locs = ds_locs.assign_coords(
        {
            "lats": (("wmo"), ds_obs["lats"].values),
            "lons": (("wmo"), ds_obs["lons"].values),
            "elev": (("wmo"), ds_obs["elev"].values),
            "name": (("wmo"), ds_obs["name"].values),
            "prov": (("wmo"), ds_obs["prov"].values),
            "id": (("wmo"), ds_obs["id"].values),
            "tz_correct": (("wmo"), ds_obs["tz_correct"].values),
        }
    )
    ### Prepare to write
    for var in ["elev", "name", "prov", "id"]:
        ds_locs[var] = ds_locs[var].astype(str)
    for var in list(ds_locs):
        ds_locs[var] = ds_locs[var].astype("float32")
    ds_locs.to_netcdf(str(data_dir) + f"/wrf/202305-FWI.nc", mode="w")

ds_locs["time"] = ds_locs["Time"]

# ds_locs['S'].isel(wmo = 0).plot()

utc_offset = np.timedelta64(-7, "h")

d = {
    "Time": ds_locs["Time"].values - utc_offset,
    "FWI": ds_locs["S"].isel(wmo=0).values,
    "ISI": ds_locs["R"].isel(wmo=0).values,
    "FFMC": ds_locs["F"].isel(wmo=0).values,
    "TEMP": ds_locs["T"].isel(wmo=0).values,
    "RH": ds_locs["H"].isel(wmo=0).values,
    "WS": ds_locs["W"].isel(wmo=0).values,
    "PRCIP": ds_locs["r_o"].isel(wmo=0).values,
}
df = pd.DataFrame(d)


fig = go.Figure()

fig.add_trace(go.Scatter(x=df["Time"], y=df["FWI"], name="FWI"))


fig.add_trace(go.Scatter(x=df["Time"], y=df["ISI"], name="ISI", yaxis="y2"))

fig.add_trace(go.Scatter(x=df["Time"], y=df["FFMC"], name="FFMC", yaxis="y3"))

fig.add_trace(go.Scatter(x=df["Time"], y=df["TEMP"], name="TEMP", yaxis="y4"))


# Create axis objects
fig.update_layout(
    xaxis=dict(domain=[0.2, 0.2]),  # Expanded domain
    yaxis=dict(
        title="yaxis title",
        titlefont=dict(color="#1f77b4"),
        tickfont=dict(color="#1f77b4"),
    ),
    yaxis2=dict(
        title="yaxis2 title",
        titlefont=dict(color="#ff7f0e"),
        tickfont=dict(color="#ff7f0e"),
        anchor="free",
        overlaying="y",
        side="left",
        position=0.05,  # Adjusted position
    ),
    yaxis3=dict(
        title="yaxis3 title",
        titlefont=dict(color="#d62728"),
        tickfont=dict(color="#d62728"),
        anchor="x",
        overlaying="y",
        side="right",
    ),
    yaxis4=dict(
        title="yaxis4 title",
        titlefont=dict(color="#9467bd"),
        tickfont=dict(color="#9467bd"),
        anchor="free",
        overlaying="y",
        side="right",
        position=0.95,  # Adjusted position
    ),
)

# Update layout properties
fig.update_layout(
    title_text="multiple y-axes example",
    width=1000,  # Expanded width
)

fig.show()

# %%
# Create figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig.add_trace(
    go.Scatter(x=df["Time"], y=df["FWI"], name="FWI"),
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(x=df["Time"], y=df["RH"], name="RH"),
    secondary_y=True,
)

# Add figure title
fig.update_layout(title_text="Double Y Axis Example")

# Set x-axis title
fig.update_xaxes(title_text="xaxis title")

# Set y-axes titles
fig.update_yaxes(title_text="<b>FWI</b>", secondary_y=False)
fig.update_yaxes(title_text="<b>ISI</b>", secondary_y=True)

fig.show()

# %%
