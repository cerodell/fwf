Structure
============

Flow Chart
------------
.. image:: _static/images/fwf-model-flowchart.png    
   :scale: 40%
   :align: center


File Directories
------------------
master
******

``/bluesky/fireweather/fwf/master`` is the operational directory, its where the code to run the model resides.
    - all_fwf_run.sh 
    - run.py 
    - geojson_maker.py 
    - ds2json.py 
    - geo2topo_mv.sh
    - index_generator.py

utils
******
``/bluesky/fireweather/fwf/utils``  is the model code  directory, all the scripts in ``master`` call on class methods and other functions in this directory.
    - fwf.py
    - read_wrfout.py
    - geoutils.py

data
******
``/bluesky/fireweather/fwf/data``   is the current forecast data directory, the directory has subfolders for each data type. 
    - the key subfolder is ``/xr``  the current fwf forecast zarr files live there.
    - the current fwf zarr forecast data is broken up into two groups ``hourly`` and ``daily`` the table below shows whats in each group.


+---------------------------------------------------+-------------------------------------------------+
| **Hourly Dataset** ``fwf-hourly-YYYYMMDDHH.zarr`` | **Daily Dataset** ``fwf-hourly-YYYYMMDDHH.zarr``| 
+===================================================+=================================================+
| Fine Fuel Moisture Code **FFMC**                  | Duff Moisture Code **DMC**                      |
+---------------------------------------------------+-------------------------------------------------+
| Initial Spread INdex **ISI**                      | Drought Moisture Code **DC**                    |
+---------------------------------------------------+-------------------------------------------------+
| Fire Weather Index **FWI**                        | Build Up Index **BUI**                          |
+---------------------------------------------------+-------------------------------------------------+
| - *WRF*: Temp, RH,                                | - *WRF*: Average Temp, RH,                      |
| - Wind Speed/Direction                            | - Wind Speed/Direction                          |
| - Hourly Rain Fall Totals                         | - 24 hour Rain Fall between (1100-1300) local   |
+---------------------------------------------------+-------------------------------------------------+


archive
********
``/bluesky/archive/fireweather/data/`` is the archive directory, it where copies of completed forecasts are stored as `.tgz`
    - ``fwf-hourly-YYYYMMDDHH.tgz`` for the hourly forecasts
    - ``fwf-daily-YYYYMMDDHH.tgz`` for the daily forecasts

wrf
********
the model currently uses 4-km WRF 00Z but is adaptable to other domains. 
    - ``/nfs/kitsault/archives/forecasts/WAN00CP-04/YYMMDD00/`` is the WRF directory where the model pulls in `.nc` files
    - If you change to a new model domain you'll first need to run `timezone.py` to generate a tzone_ds.zarr file (Note it takes awhile to generate ~3 hours but you only need to run it once!)


Required packages
------------------
.. code-block:: python

    conda install -c conda-forge netcdf4
    conda install -c conda-forge dask
    conda install -c conda-forge zarr
    conda install -c conda-forge wrf-python
    conda install -c conda-forge timezonefinder
    conda install -c conda-forge cartopy
    conda install -c conda-forge xarray
    conda install -c conda-forge pandas

Website 
--------

To visualize the data on leaflet several steps are made to simplify and reduce the file as much as possible. 

Visualization Steps
*******************
#. zarr file data is first masked to remove all lakes, oceans, and snow cover.
    * see ``/bluesky/fireweather/fwf/utils/geoutils.py``
#. after mask is applied fire weather indices/codes are made into contourf
    * customize by changing ``/bluesky/fireweather/fwf/json/colormaps.json``
#. from contourf they are converted to geojson files using geojsoncontour
    * geojsoncontour reference: https://pypi.org/project/geojsoncontour/
    * note all indices and moisture codes are rounded to the third decimal 
    * steps 1-3 are done in python all in ``/bluesky/fireweather/fwf/firewx_website/python/geojson_maker.py``

#. next geojsons are converted to topojsons using ``geo2topo``
    * ``geo2topo -q 1e4 path_to_infile/file_YYYYMMDDHH.geojson > path_to_outfile/file_YYYYMMDDHH.json``
    * reference: https://github.com/topojson/topojson-server
    * a ``q`` (ie quantization count) of `1e4` reduces the geojson file by about half and doest take away for the quality of the visualization on leaflet
    * there are many ways to simplify topojson and reduce the file size further
    * reference: https://github.com/topojson/topojson-simplify 

#. topojsons are stored as json files: ``/bluesky/archive/fireweather/forecast/YYYYMMDDHH`` 
    * stored as .json extension so server can gzip and send file to client

