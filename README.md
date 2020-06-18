# FWF
---
## Fire Weather Forecast Model 


This project aims to create a  Fire Weather Forecast (FWF) Model. FWF will be
constructed off preexisting fire weather models such as the Fire Weather Index
System (FWI) and the Fire behavior Prediction Model (FBP). The indices that
make each of the models will be calculated using a numerical weather prediction
model WRF-ARW. 


The new FWI System hereafter referred to as FWI-UBC, will make use of 
equations developed by Van Wagner (1977) and Van Wanger and Pickett (1985). 
The moisture codes that are the foundation of the FWI system the; Fine Fuel 
Moisture Code (FFMC), Duff Moisture Code (DMC) and Drought Code (DC), will be
validated against FWI in-situ measurements at weather stations across Canada,
to ensure accuracy of our product. The mentioned moisture codes along with
the; Initial Spread Index (ISI), Buildup Index (BUI) and the Fire Weather 
Index (FWI) will be graphically displayed via FWF online maps encompassing
regions of interest to the user.  Also, for large fires, point-location 
forecast(s) will be disseminated online in Meteogram format. Product variables 
will include maps of high-resolution FWI-system indices and surface weather 
variables such as wind speed/ direction, temperature, and relative humidity 

---
## Model structure

- `/bluesky/fireweather/fwf/` is the operational directory, its where the model code resides and current forecast data 
resides.

- the current forecast data is broken up into two groups `hourly` and `daily` the table below shows whats in each group.


| Hourly Dataset `hourly_ds`  | Daily Dataset `daily_ds`  | 
 --------------------------- | ------------------------- |
| Fine Fuel Moisture Code **FFMC**  | Duff Moisture Code **DMC**  |
| Initial Spread INdex **ISI**  | Drought Moisture Code **DC**  |
| Fire Weather Index **FWI** | Build Up Index **BUI** |
| *WRF*: Temp, RH, <br> Wind Speed/Direction <br> Hourly Rain Fall Totals | *WRF*: Average Temp, RH, <br> Wind Speed/Direction <br> 24 hour Rain Fall Totals <br> between (1100-1300) local time|


- `/bluesky/archive/fireweather/` is the archive directory, it where copies of completed forecasts are stored as `tar.gz`
    - `../hourly/` for the hourly forecasts
    - `../daily/` for the daily forecasts

- `/nfs/kitsault/archives/forecasts/WAN00CP-04/YYMMDD00/` is the WRF directory where the model pulls in `.nc` files
- the model currently uses 4-km WRF 00Z but is adaptable to other domains. 
    - Youll first need to run `timezone.py` to generate a tzone_ds.zarr file (Note it takes awhile to generate ~3 hours)
    - after it should run as per normal

    
- `fwf/fwi/utils/ubc_fwi/fwf.py` contains the FWF class that does all the calculations.
	- note FWF calls on function `read_wrf` in `fwf/fwi/utils/wrf/read_wrfout.py` this script compiles the `.nc` wrfout files into a compact `.zarr` file 

- `fwf/py/ubc_fwi/run.py` is the script that runs the model



---
#### Required packages

`conda install -c conda-forge netcdf4`

`conda install -c conda-forge dask`

`conda install -c conda-forge zarr`

`conda install -c conda-forge wrf-python`

`conda install -c conda-forge timezonefinder`

`conda install -c conda-forge cartopy`

`conda install -c conda-forge xarray`

`conda install -c conda-forge pandas`

---
## Website 

To visualize the data on leaflet many several steps are made to simplify and reduce the file as much as possible. 

#### Data
- 1\) zarr file data is first masked to remove all lakes, oceans, and snow cover.
- 2\) after mask is applied fire weather indices/codes are made into contourf plots 
- 3\) from contourf they are converted to geojson files
    - note all indices and moisture codes are rounded to the third decimal 
    - steps 1-3 are done in python all in `/bluesky/fireweather/fwf/firewx_website/python/geojson_maker.py`

- 4\) next geojsons are converted to topojsons using `geo2topo`
    - `geo2topo -q 1e4 file_YYYYMMDDHH.geojson > file_YYYYMMDDHH.geojson`
    - *YES TOPOJSON HAS THE SAME FILE EXTENTION*
    - reference: https://github.com/topojson/topojson-server
    - a `q` (ie quantization count) of `1e4` reduce the geojson file by about half and doest take away for the quality of the visualization on leaflet
        - there are many ways to simplify topojson and reduce the file size further
            - reference: https://github.com/topojson/topojson-simplify 

- 5\) topojsons are stored: `/bluesky/fireweather/fwf/data/topojson/` 
