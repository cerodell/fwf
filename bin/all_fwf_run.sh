
echo "$(date) ---> start fwf model"
### Run fwf model
/bluesky/fireweather/fwf/scripts/run.py
echo "$(date) ---> fwf model done"

echo "$(date) ---> start geojson maker for leaflet map"
### Create geojson files for display on leaflet
/bluesky/fireweather/fwf/scripts/geojson_maker.py
echo "$(date) ---> geojson maker done"


echo "$(date) ---> start ds2json for plotly line plts"
### Create json file for plotly line plots
/bluesky/fireweather/fwf/scripts/ds2json.py
echo "$(date) ---> ds2json done"


echo "$(date) ---> convert geojson to topojson then mv all data to forecast folder"
### Convert gejsons to topojsons and move to current forecast folder
/bluesky/fireweather/fwf/bin/geo2topo_mv.sh
echo "$(date) ---> convert/mv  done"

echo "$(date) ---> build new intercomparsion dataset"
### Create new index.html file for current forecast
/bluesky/fireweather/fwf/scripts/build_intercomp.py
echo "$(date) ---> new intercomparsion dataset made"

echo "$(date) ---> add intercomparsion dataset to webpage"
### Create new index.html file for current forecast
/bluesky/fireweather/fwf/scripts/wx_by_tzone.py
echo "$(date) ---> new intercomparsion dataset added to webpage"

echo "$(date) ---> add weather station key webpage"
### Create new index.html file for current forecast
/bluesky/fireweather/fwf/scripts/wx_keys.py
echo "$(date) ---> new weather station keys added to webpage"

# echo "$(date) ---> make new index.html"
# ### Create new index.html file for current forecast
# /bluesky/fireweather/fwf/scripts/index_generator.py
# echo "$(date) ---> new index.html done"


# echo "$(date) ---> make new symlink"
# ### Creat new symlink to todays forecast
# cd /bluesky/archive/fireweather/forecasts/
# ln -fnsv $(date '+%Y%m%d00') current
# echo "$(date) ---> new symlink created"


# echo "$(date) ---> start intercomp_json for plotly line plts"
# ### Create json file for plotly line plots
# /bluesky/fireweather/fwf/scripts/intercomp_json.py
# echo "$(date) ---> intercomp_json done"
