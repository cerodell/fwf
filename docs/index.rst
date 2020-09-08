Welcome to Fire Weather Forecast Model
======================================

Overview:
#########

   The Fire Weather Forecast (FWF) model is built off a preexisting fire-weather model,
   the Fire Weather Index System (FWI). The FWI system developed by Van Wanger and Pickett
   estimates how past/current/future weather conditions affect the moisture content within
   varied forest fuel layers across Canada. Knowing the fuel moisture content at all locations
   enables fire management agencies to understand where fires may occur and how fast they may grow/spread.

   The new FWF model differs from current FWI models by fully utilizing a numerical weather
   prediction (NWP) model. Fuel moisture codes/indices are calculated at every grid point 
   within the NWP model at a 4 km spatial resolution. The Fine Fuel Moisture Code, Initial 
   Spread Index, and Fire Weather Index are resolved at a one-hour temporal resolution while 
   the Duff Moisture Code, Drought Code and Build up Index are solved once daily at noon local.
   This differs from the current FWI model that interpolate noon local weather forecast data from
   900-point location across Canada. The interpolated weather data uses a fixed dry adiabatic 
   lapse and terrain data at 1 x 1 km resolution. The interpolated weather data is then used to
   solve all moisture codes/indices once daily at noon local.

| For the current FWF forecast check out:
| https://firesmoke.ca/forecasts/fireweather/current/
|


.. image:: _static/images/fwf_example.png    
   :scale: 30%
   :align: center

Documentation
==================
.. toctree::
   :maxdepth: 2
   :caption: Model:

   ms

   api
   
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
