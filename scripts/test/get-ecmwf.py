from herbie import Herbie

# Herbie object for the HRRR model 6-hr surface forecast product
H = Herbie("2022-01-26", model="ecmwf", product="oper", fxx=12)
H.download()


# Show the searchString_help
print(H.searchString_help)


ds = H.xarray(":2t:")
ds["t2m"].plot()
