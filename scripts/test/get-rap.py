from herbie import Herbie

# Herbie object for the HRRR model 6-hr surface forecast product
H = Herbie(
    "2022-10-25 12:00",
    model="rap",
    #   product='nat',
    fxx=1,
    #   priority = 'nomads'
)

# Download the full GRIB2 file
H.download()

# # Download a subset, like all fields at 500 mb
# mb = H.xarray(":500 mb")

# # Read subset with xarray, like 2-m temperature.
t2m = H.xarray("TMP:2 m")

t2m["t2m"].plot()
