import context
import salem
import numpy as np
import xarray as xr
import pandas as pd
import geopandas as gpd
from pathlib import Path
from netCDF4 import Dataset
import cartopy.crs as crs

from datetime import datetime
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from datetime import datetime, date, timedelta

from wrf import to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ll_to_xy, xy_to_ll


from context import data_dir, root_dir

startTime = datetime.now()

model = "wrf"
trail_name = "02"

### Open Station Data
# wx_ds = xr.open_dataset(str(data_dir) + f'/obs/observations-d03-20191231-20221231.nc')
wx_ds = xr.open_dataset(
    str(data_dir) + f"/intercomp/{trail_name}/{model}/d02d03-20210401-20221101-null.nc"
)
bad_wx = [3153, 3167, 3266, 3289]
for wx in bad_wx:
    wx_ds = wx_ds.drop_sel(wmo=wx)


### Open WRF d02 domain
filein = str(data_dir) + f"/wrf/wrfout_d02_2021-01-14_00:00:00"
wrf_d02 = xr.open_dataset(filein)

### Open WRF d03 domain
filein = str(data_dir) + f"/wrf/wrfout_d03_2021-01-14_00:00:00"
wrf_d03 = xr.open_dataset(filein)


## set plot title and save dir/name
Plot_Title = "Model Domains in Mercator Projection"
save_file = "/images/paper/study-map.png"
save_dir = str(data_dir) + save_file


# Get the cartopy mapping object
ncfile = Dataset(str(data_dir) + f"/wrf/wrfout_d02_2021-01-14_00:00:00")
slp = getvar(ncfile, "slp")
cart_proj = get_cartopy(slp)


## bring in state/prov boundaries
states_provinces = cfeature.NaturalEarthFeature(
    category="cultural",
    name="admin_1_states_provinces_lines",
    scale="50m",
    facecolor="none",
)

# get the data at the latest time step
ds = salem.open_wrf_dataset(
    str(data_dir) + f"/wrf/wrfout_d01_2023-04-20_00:00:00"
).isel(time=-1)


## convert lat lon coordinate in master obs to meter base x y as define by wrf polar stere projection


def transform_locs(lons, lats):
    df = pd.DataFrame(
        data={
            "lons": lons,
            "lats": lats,
        }
    )
    pyproj_srs = ds.attrs["pyproj_srs"]
    print(pyproj_srs)
    locs = gpd.GeoDataFrame(
        df,
        crs="EPSG:4326",
        geometry=gpd.points_from_xy(df["lons"], df["lats"]),
    ).to_crs(pyproj_srs)
    xx, yy = smap.grid.transform(
        locs.geometry.x, locs.geometry.y, crs=ds.salem.grid.proj
    )
    return xx, yy


# get the axes ready
fig, ax = plt.subplots(figsize=[14, 10])

# plot the salem map background, make countries in grey
smap = ds.salem.get_map(countries=False)
smap.set_shapefile(countries=True, lw=0.4)
smap.set_shapefile(
    oceans=True,
)
smap.set_shapefile(
    lakes=True,
)
smap.set_shapefile(states=True, lw=0.4)
smap.set_shapefile(prov=True, lw=0.4)

smap.plot(ax=ax)

xx, yy = transform_locs(wx_ds.lons, wx_ds.lats)
## plot wx stations locations
ax.scatter(
    xx,
    yy,
    color="tab:grey",
    zorder=10,
    alpha=1,
    s=4,
    label="WxStations",
)

## get d03 lats and lon
linewidth = 2.6
lons, lats = np.array(wrf_d03.XLONG)[0], np.array(wrf_d03.XLAT)[0]
xx, yy = transform_locs(lons[0], lats[0])
ax.plot(xx, yy, color="tab:green", linewidth=linewidth, zorder=8, alpha=1)
xx, yy = transform_locs(lons[-1].T, lats[-1].T)
ax.plot(xx, yy, color="tab:green", linewidth=linewidth, zorder=8, alpha=1)
xx, yy = transform_locs(lons[:, 0], lats[:, 0])
ax.plot(xx, yy, color="tab:green", linewidth=linewidth, zorder=8, alpha=1)
xx, yy = transform_locs(
    lons[:, -1].T,
    lats[:, -1].T,
)
ax.plot(
    xx,
    yy,
    color="tab:green",
    linewidth=linewidth,
    zorder=8,
    alpha=1,
    label="4 km Domain",
)


## get d02 lats and lon
linewidth = 2.6
lons, lats = np.array(wrf_d02.XLONG)[0], np.array(wrf_d02.XLAT)[0]
xx, yy = transform_locs(lons[0], lats[0])
ax.plot(xx, yy, color="tab:red", linewidth=linewidth, zorder=8, alpha=1)
xx, yy = transform_locs(lons[-1].T, lats[-1].T)
ax.plot(xx, yy, color="tab:red", linewidth=linewidth, zorder=8, alpha=1)
xx, yy = transform_locs(lons[:, 0], lats[:, 0])
ax.plot(xx, yy, color="tab:red", linewidth=linewidth, zorder=8, alpha=1)
xx, yy = transform_locs(
    lons[:, -1].T,
    lats[:, -1].T,
)
ax.plot(
    xx,
    yy,
    color="tab:red",
    linewidth=linewidth,
    zorder=8,
    alpha=1,
    label="12 km Domain",
)

## add legend
ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, 1.0),
    ncol=5,
    fancybox=True,
    shadow=True,
)

## tighten up fig
plt.tight_layout()

# save as png
fig.savefig(save_dir, bbox_inches="tight", dpi=240)


# ## plot d02
# ax.plot(lons[-1].T, lats[-1].T, color="red", linewidth=linewidth, zorder=8, alpha=1, )
# ax.plot(lons[:, 0], lats[:, 0], color="red", linewidth=linewidth, zorder=8, alpha=1,)
# ax.plot(
#     lons[:, -1].T,
#     lats[:, -1].T,
#     color="red",
#     linewidth=linewidth,
#     zorder=8,
#     alpha=1,
#     label="12 km WRF Domain",
# )

## get d03 lats and lon
# lats, lons = np.array(wrf_d03.XLAT), np.array(wrf_d03.XLONG)
# lats, lons = lats[0], lons[0]

# ## plot d03
# ax.plot(lons[0], lats[0], color="blue", linewidth=linewidth, zorder=8, alpha=1, transform=crs.PlateCarree(),)
# ax.plot(lons[-1].T, lats[-1].T, color="blue", linewidth=linewidth, zorder=8, alpha=1, transform=crs.PlateCarree(),)
# ax.plot(lons[:, 0], lats[:, 0], color="blue", linewidth=linewidth, zorder=8, alpha=1, transform=crs.PlateCarree(),)
# ax.plot(
#     lons[:, -1].T,
#     lats[:, -1].T,
#     color="blue",
#     linewidth=linewidth,
#     zorder=8,
#     alpha=1,
#     label="4 km WRF Domain",
#     transform=crs.PlateCarree(),
# )


# # ## set map bounds
# # ax.set_xlim([-190, -39])
# # ax.set_ylim([22, 82])

# ## add legend
# ax.legend(
#     loc="upper center",
#     bbox_to_anchor=(0.5, 1.0),
#     ncol=5,
#     fancybox=True,
#     shadow=True,
# )

# ## tighten up fig
# plt.tight_layout()

# ## save as png
# # fig.savefig(save_dir, dpi=240)
