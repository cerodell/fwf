Welcome to Fire Weather Forecast Model
======================================

Overview:
#########

    The FWF model is built off a preexisting fire-weather model,
    the Fire Weather Index System (FWI). The FWI system developed 
    by Van Wanger and Pickett estimates how past/current/future weather
    conditions affect the moisture content within varied forest fuel layers
    across Canada. Knowing the fuel moisture content at all locations enables
    the fires management agencies to understand where fires may occur and
    how fast they may grow/spread. 

    The FWF model differs from the current FWI systems by calculating the moisture
    codes/indices at every grid point within the model domain at a one-hour temporal 
    and 4 km spatial resolution. The current FWI system calculates the moisture 
    codes/indices once daily at noon local at 900 point locations across Canada. 
    The current model then interpolates the weather between those stations to create
    a spatial forecast. 

| For the current FWF forecast check out:
| https://firesmoke.ca/forecasts/fireweather/current/
|


.. image:: _static/images/fwf_example.png    
   :scale: 50%
   :align: center

Documentation
==================
.. toctree::
   :maxdepth: 2
   :caption: Model:

   api
   
   ms

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
