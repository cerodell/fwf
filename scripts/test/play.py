import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.ndimage as ndimage
from scipy.ndimage.filters import gaussian_filter

from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta

from PIL import Image

Image.MAX_IMAGE_PIXELS = None


filein = (
    str(data_dir)
    + "/fbp/Canadian_Forest_FBP_Fuel_Types_v20191114/fuel_layer/FBP_FuelLayer.tif"
)

filein = (
    str(data_dir) + "/fbp/National_FBP_Fueltypes_version2014b/nat_fbpfuels_2014b.tif"
)
im = Image.open(filein)
# im.show()

imarray = np.array(im)


unique = np.unique(imarray)


from osgeo import osr, gdal

# get the existing coordinate system
ds = gdal.Open(filein)
old_cs = osr.SpatialReference()
old_cs.ImportFromWkt(ds.GetProjectionRef())

# create the new coordinate system
wgs84_wkt = """
GEOGCS["WGS 84",
    DATUM["WGS_1984",
        SPHEROID["WGS 84",6378137,298.257223563,
            AUTHORITY["EPSG","7030"]],
        AUTHORITY["EPSG","6326"]],
    PRIMEM["Greenwich",0,
        AUTHORITY["EPSG","8901"]],
    UNIT["degree",0.01745329251994328,
        AUTHORITY["EPSG","9122"]],
    AUTHORITY["EPSG","4326"]]"""
new_cs = osr.SpatialReference()
new_cs.ImportFromWkt(wgs84_wkt)

# create a transform object to convert between coordinate systems
transform = osr.CoordinateTransformation(old_cs, new_cs)

# get the point to transform, pixel (0,0) in this case
width = ds.RasterXSize
height = ds.RasterYSize
gt = ds.GetGeoTransform()
minx = gt[0]
miny = gt[3] + width * gt[4] + height * gt[5]

# get the coordinates in lat long
latlong = transform.TransformPoint(minx, miny)


# import rasterio
# import numpy as np
# from affine import Affine
# from pyproj import Proj, transform


# # Read raster
# with rasterio.open(filein) as r:
#     T0 = r.transform  # upper-left pixel corner affine transform
#     p1 = Proj(r.crs)
#     A = r.read()  # pixel values

# # All rows and columns
# cols, rows = np.meshgrid(np.arange(A.shape[2]), np.arange(A.shape[1]))

# # Get affine transform for pixel centres
# T1 = T0 * Affine.translation(0.5, 0.5)
# # Function to convert pixel row/column index (from 0) to easting/northing at centre
# rc2en = lambda r, c: (c, r) * T1

# # All eastings and northings (there is probably a faster way to do this)
# eastings, northings = np.vectorize(rc2en, otypes=[np.float, np.float])(rows, cols)

# # Project all longitudes, latitudes
# p2 = Proj(proj='latlong',datum='WGS84')
# longs, lats = transform(p1, p2, eastings, northings)
