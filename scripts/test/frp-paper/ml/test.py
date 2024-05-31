total_fuel = (
    fwf_ds["Live_Wood"]
    + fwf_ds["Dead_Wood"]
    + fwf_ds["Live_Leaf"]
    + fwf_ds["Dead_Foliage"]
)
fwf_ds["U_lat_sin_total_fuel"] = fwf_ds["U"] * fwf_ds["lat_sin"] * total_fuel
fwf_ds["U_lat_cos_total_fuel"] = fwf_ds["U"] * fwf_ds["lat_cos"] * total_fuel

fwf_ds["U_lon_sin_total_fuel"] = fwf_ds["U"] * fwf_ds["lon_sin"] * total_fuel
fwf_ds["U_lon_cos_total_fuel"] = fwf_ds["U"] * fwf_ds["lon_cos"] * total_fuel
