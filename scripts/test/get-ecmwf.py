from herbie import Herbie


import matplotlib.pyplot as plt
import cartopy.crs as ccrs


############### gfs #################

H = Herbie("2021-07-11", model="gfs", product="pgrb2.0p25")
# Show all available sources
H.SOURCES
# Show all available products
H.PRODUCTS
ds = H.xarray(":500 mb:")


######################################


############### ecmwf #################
# H = Herbie("2019-05-26", model="ecmwf", product="oper", fxx=12)
# H.download()


# # Show the searchString_help
# print(H.searchString_help)


# ds = H.xarray(":2t:")
# ds["t2m"].plot()
######################################
