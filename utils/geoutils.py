#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import salem
import numpy as np
import xarray as xr
import geojsoncontour
import pandas as pd
import geopandas as gpd
import branca.colormap as cm
import scipy.ndimage as ndimage
from sklearn.neighbors import KDTree

import matplotlib.pyplot as plt
import matplotlib.colors


from wrf import getvar
from context import data_dir


def mycontourf_to_geojson(cmaps, var, da, folderdate, domain, timestamp):
    """
    This makes a geojson file from a matplot lib countourf

    Parameters
    ----------
    cmaps: dictionary
        contains variable attributes from ``colormaps.json``
            - variable name
            - variable title
            - contour levels/range
            - color palette

    var: str
        - variable name

    ds: DataSet
        - either daily_ds or houlry_ds

    index: int
        - time index

    folderdate: str
        - file directory to geojson files
        - ``../fwf/data/geojson/YYYYMMDDHH``

    colornumber: str
        - colors30 or colors15
        - will provide either 30 or 15 contour levels

    Returns
    -------
    file: geojson
        - ``../fwf/data/geojson/YYYYMMDDHH``

    """

    vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
    name, colors, sigma = (
        str(cmaps[var]["name"]),
        cmaps[var]["colors"],
        cmaps[var]["sigma"],
    )

    geojson_filename = str(name + "-" + timestamp + "-" + domain)
    levels = cmaps[var]["levels"]
    Cnorm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)
    contourf = plt.contourf(
        da.XLONG.values,
        da.XLAT.values,
        ndimage.gaussian_filter(da.values, sigma=sigma),
        levels=levels,
        linestyles="None",
        norm=Cnorm,
        colors=colors,
        extend="both",
    )
    plt.close()

    geojsoncontour.contourf_to_geojson(
        contourf=contourf,
        min_angle_deg=None,
        ndigits=2,
        stroke_width=None,
        fill_opacity=None,
        geojson_properties=None,
        unit="",
        geojson_filepath=str(data_dir) + f"/geojson/{geojson_filename}.geojson",
    )

    # print(
    #     f"wrote geojson to: /bluesky/fireweather/fwf/data/geojson/{folderdate}/{geojson_filepath}.geojson"
    # )

    return


def mask(ds_unmasked, wrf_file_dir):
    """
    This masks out all lakes, oceans, and snow cover from model domain.

    Parameters
    ----------
    ds_unmasked: DataSet
        - either daily_ds or houlry_ds

    wrf_file_dir: str
        - file directory to wrf NetCDF files
        - ``/nfs/kitsault/archives/forecasts/WAN00CP-04/YYMMDD00/``

    Returns
    -------
    ds: DataSet
        -  masked daily_ds or houlry_ds

    """
    LANDMASK, LAKEMASK, SNOWC = wrfmasks(wrf_file_dir)
    SNOWC[:, :600] = 0
    ds = xr.where(LANDMASK == 1, ds_unmasked, np.nan)
    ds = ds.transpose("time", "south_north", "west_east")
    # ds = xr.where(LAKEMASK == 0, ds, np.nan)
    # ds = ds.transpose("time", "south_north", "west_east")
    ds = xr.where(SNOWC == 0, ds, np.nan)
    ds = ds.transpose("time", "south_north", "west_east")
    ds["Time"] = ds_unmasked["Time"]
    return ds


def wrfmasks(wrf_file_dir):
    wrf_file = Dataset(wrf_file_dir[-1], "r")
    ### Get Land Mask and Lake Mask data
    LANDMASK = getvar(wrf_file, "LANDMASK")
    LAKEMASK = getvar(wrf_file, "LAKEMASK")
    SNOWC = getvar(wrf_file, "SNOWC")

    return LANDMASK, LAKEMASK, SNOWC


def jsonmask(ds_unmasked, wrf_file_dir):
    LANDMASK, LAKEMASK, SNOWC = wrfmasks(wrf_file_dir)
    ds = xr.where(LANDMASK == 1, ds_unmasked, "")
    if len(ds_unmasked.Time) == 61:
        ds["T"] = ds_unmasked["T"]
        ds["H"] = ds_unmasked["H"]
        ds["W"] = ds_unmasked["W"]
        ds["WD"] = ds_unmasked["WD"]
        ds["r_o"] = ds_unmasked["r_o"]
    else:
        pass
    ds = ds.transpose("time", "south_north", "west_east")
    # ds = xr.where(LAKEMASK == 0, ds, np.nan)
    # ds = ds.transpose("time", "south_north", "west_east")
    # ds = xr.where(SNOWC == 0, ds, '')
    # ds = ds.transpose("time", "south_north", "west_east")
    ds["Time"] = ds_unmasked["Time"]
    return ds


def latlngmask(array, wrf_file_dir):
    LANDMASK, LAKEMASK, SNOWC = wrfmasks(wrf_file_dir)
    SNOWC[:, :600] = 0
    arraymasked = np.where(LANDMASK == 1, array, "")
    arraymasked = np.where(SNOWC == 0, arraymasked, "")
    return arraymasked


def delete3D(array3D):
    x = array3D.shape
    array2D = np.reshape(array3D, (x[0], (x[1] * x[2])))
    y_list = []
    for i in range(x[0]):
        index = np.argwhere(array2D[i, :] == "")
        y = np.delete(array2D[i, :], index)
        y_list.append(y)
    final = np.stack(y_list)
    # final = np.float32(final)
    return final


def delete2D(array2D):
    x = array2D.shape
    array1D = np.reshape(array2D, (x[0] * x[1]))
    index = np.argwhere(array1D == "")
    final = np.delete(array1D, index)
    # final = np.float32(final)
    return final


def colormaps(cmaps, var):
    vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
    name, colors = cmaps[var]["name"], cmaps[var]["colors30"]
    levels = len(colors)
    cmap = cm.LinearColormap(colors, vmin=vmin, vmax=vmax, caption=name).to_step(levels)
    cmap.caption = cmaps[var]["title"]
    return cmap


def get_pyproj_loc(pyproj_srs, df, lat=None, lon=None):
    if lat == None:
        pass
    else:
        if (type(lat) == float) or (type(lat) == int):
            lat, lon = [lat], [lon]
            df = pd.DataFrame({"lats": lat, "lons": lon})
        else:
            df = pd.DataFrame({"lats": lat, "lons": lon})
    # get_locs_time = datetime.now()
    try:
        loc_values = df.wmo.values
        loc = "wmo"
    except:
        loc_values = df.index.values
        loc = "loc"
    gpm25 = gpd.GeoDataFrame(
        df,
        crs="EPSG:4326",
        #  crs="+init=epsg:4326",
        geometry=gpd.points_from_xy(df["lons"], df["lats"]),
    ).to_crs(pyproj_srs)

    x = xr.DataArray(
        np.array(gpm25.geometry.x),
        dims=loc,
        coords={loc: loc_values},
    )
    y = xr.DataArray(
        np.array(gpm25.geometry.y),
        dims=loc,
        coords={loc: loc_values},
    )
    # print("Locs Time: ", datetime.now() - get_locs_time)

    return x, y


# def contourf_to_geojson(contourf, geojson_filepath=None, min_angle_deg=None,
#                         ndigits=5, unit='', stroke_width=1, fill_opacity=.9, fill_opacity_range=None,
#                         geojson_properties=None, strdump=False, serialize=True):
#     """Transform matplotlib.contourf to geojson with MultiPolygons."""
#     if fill_opacity_range:
#         variable_opacity = True
#         min_opacity, max_opacity = fill_opacity_range
#         opacity_increment = (max_opacity - min_opacity) / len(contourf.levels)
#         fill_opacity = min_opacity
#     else:
#         variable_opacity = False
#     polygon_features = []
#     contourf_levels = get_contourf_levels(contourf.levels, contourf.extend)
#     for coll, level in zip(contourf.collections, contourf_levels):
#         color = coll.get_facecolor()
#         muli = MP(coll, min_angle_deg, ndigits)
#         polygon = muli.mpoly()
#         fcolor = rgb2hex(color[0])
#         if polygon.coordinates:
#             properties = set_contourf_properties(stroke_width, fcolor, fill_opacity, level, unit)
#             if geojson_properties:
#                 properties.update(geojson_properties)
#             feature = Feature(geometry=polygon, properties=properties)
#             polygon_features.append(feature)
#             # print(len(polygon.coordinates))
#             if variable_opacity:
#                 fill_opacity += opacity_increment
#     feature_collection = FeatureCollection(polygon_features)
#     return _render_feature_collection(feature_collection, geojson_filepath, strdump, serialize)


def make_KDtree(model, domain, lats, lons):

    static_ds = salem.open_xr_dataset(
        str(data_dir) + f"/static/static-vars-{model}-{domain}.nc"
    )
    shape = static_ds.XLAT.shape
    locs = pd.DataFrame(
        {"lats": static_ds.XLAT.values.ravel(), "lons": static_ds.XLONG.values.ravel()}
    )
    ## build kdtree
    fwf_tree = KDTree(locs)
    print("Fire KDTree built")
    yy, xx = [], []
    # df = pd.DataFrame(
    #     {'lat': [case_info['min_lat'],case_info['max_lat'], case_info['max_lat'], case_info['min_lat']],
    #     'lon': [case_info['min_lon'],case_info['min_lon'], case_info['max_lon'], case_info['max_lon']]
    #     }
    # )
    try:
        df = pd.DataFrame({"lat": lats, "lon": lons})
    except:
        df = pd.DataFrame({"lat": [lats], "lon": [lons]})
    for index, row in df.iterrows():
        ## arange wx station lat and long in a formate to query the kdtree
        single_loc = np.array([row.lat, row.lon]).reshape(1, -1)
        ## query the kdtree retuning the distacne of nearest neighbor and index
        dist, ind = fwf_tree.query(single_loc, k=1)
        ## set condition to pass on fire farther than 0.1 degrees
        if dist > 0.1:
            pass
        else:
            ## if condition passed reformate 1D index to 2D indexes
            ind_2d = np.unravel_index(int(ind), shape)
            ## append the indexes to lists
            yy.append(ind_2d[0])
            xx.append(ind_2d[1])
    yy, xx = np.array(yy), np.array(xx)
    # yy, yy_counts = np.unique(yy, return_counts=True)
    # xx, xx_counts = np.unique(xx, return_counts=True)

    return yy, xx
