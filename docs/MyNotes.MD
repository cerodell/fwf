# Notes for me :)  


| Hourly Dataset `hourly_ds`  | Daily Dataset `daily_ds`  | 
 --------------------------- | ------------------------- |
| Fine Fuel Moisture Code **FFMC**  | Duff Moisture Code **DMC**  |
| Initial Spread INdex **ISI**  | Drought Moisture Code **DC**  |
| Fire Weather Index **FWI** | Build Up Index **BUI** |
| *WRF*: Temp, RH, <br> Wind Speed/Direction <br> Hourly Rain Fall Totals | *WRF*: Average Temp, RH, <br> Wind Speed/Direction <br> 24 hour Rain Fall Totals <br> between (1100-1300) local time|



## FFMC
- Will be an hourly output and live in `hourly_ds`
- Seems to be working well Jun 7th 2020 

## DMC
- Will be an daily output and live in `daily_ds`
- Seems to be working well Jun 7th 2020 But needs more spin up time!!!!!!!!!


## DC
- Will be an daily output and live in `daily_ds`
- Seems to be working well Jun 7th 2020 But needs more spin up time!!!!!!!!!


## ISI
- Will be an hourly output and live in `hourly_ds`
- Seems to be working well Jun 7th 2020 

## BUI 
- Will be an daily output and live in `daily_ds`
- Seems to be working well Jun 7th 2020 But needs more spin up time!!!!!!!!!



## FWI
- Will be an hourly output and live in `hourly_ds`
- Seems to be working well but BUI/DC need more spin up time Jun 7th 2020 


--- 
# Development Needs/Wants 
- add numba to methods/functions see: https://clouds.eos.ubc.ca/~phil/courses/parallel_python/00_intro.html

- do varification of forecasts
    - start with plotting and do sanity check of values 
    - get obs from cwfis and compare values

- website add more layers to maps
    - sort how to animate
    - hybrid py & js
        - make Geojsons with python
        - using folium to create html with geojsons 
        - remove them from html and find way to read them in js (will help with animating??)
        - edit html after clean and add js scripts to read GEoJson data
        - the idea is to back a base html with folium that can genrater what i want then operationalize in js to keep things safe from breaking


