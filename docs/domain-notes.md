Hello! 

Looking over the hysplit scripts for both the BSF and BSP I think i have a handle on the conversation of our met netcdf file to hysplit arl files.

For BSF i look at this script:
/bluesky/bsf-ops/modules/HYSPLIT/v7/hysplit.py

For BSP i look at this script:
https://github.com/WFRTgroup/bluesky/blob/master/bluesky/dispersers/hysplit/hysplit_utils.py


In both BSF and BSP we provided a `user_defined_grid=true` (in BSP this is defined in the config file). 


How we define our input grid for the conversion from netcdf to arl is:


"height_latitude": 30.0,
"center_longitude": -98.5,
"dispersion_offset": 0,
"center_latitude": 55.0,
"spacing_longitude": 0.1,
"width_longitude": 92.0,
"spacing_latitude": 0.1,

I'll focus more on BSP as it will be replacing the BSF soon.

For BSP when you define `user_defined_grid=true`  will make a grid-based on in info defined in the config file by taking take the center lat and lng and space out to bounds of the height_latitude and width_longitude by the given spacing.

See here:
https://github.com/WFRTgroup/bluesky/blob/d9d067d607faea908584a2dcaf2a23e73ba0a1ee/bluesky/dispersers/hysplit/hysplit_utils.py#L305-L315

What do you guys think? Is this the correct way to represent out meteorology grid as input in hysplit? I don't think it is as our meteorology grid is polar stereographic and each grid spacing is not 0.1 deg or 12km. The spacing changes at different positions within the model grid. 

Now comes the question can we set `user_defined_grid=false` ? 

I had asked Tobias to try this over the summer but he was unable to get the BSP run.

Maybe it is worth looking into this again? 

Also ill look into how people not using BlueSky convert meteorology netcdf file to arl files while accounting for model projections. 

Another thing we need to think about is how to visualize the hysplit dispersion output if we keep are meteorology in the polar stereographic projection.
Leaflet is in a google Mercator projection. ANd overlaying images (likely we do now) will not work. Or at least i couldn't get it to overlay correctly maybe others can? I think using vector tiles might be a better way to go as the lat/lng information is embedded within though files. 




Lastly, regrading Stull's thought about bringing the wester boundary in or east. I think we have too, a very small portion stretches the international dateline. The conversion from met files to arl files isnt supported over the international dateline: 

https://github.com/WFRTgroup/bluesky/blob/d9d067d607faea908584a2dcaf2a23e73ba0a1ee/bluesky/dispersers/hysplit/hysplit_utils.py#L258-L259



I went back to the WRFtoARL in /bluesky/bsf-ops/modules/HYSPLIT/v7/hysplit.py

What WRFtoARL does is:

    """ Convert WRF-format met data to ARL format.
    
    This method uses the executable configured with WRFTOARL_BINARY
    to convert WRF NetCDF files to ARL formatted files one at a time
    and then concatenates them to create a single "hysplit.arl" file
    containing all met data.
    """

I think how it works is first grabs met info that is extracted/define in WRFLocalMet located in /bluesky/bsf-ops/modules/WRFdata/v1/wrfdata.py

In WRFLocalMet there is a fillMetDomainInfo module which reads one of our met netcdf files and defines a domain by 

```
lat_dataset = gdal.Open("NETCDF:"+gdalFilename+":XLAT")
lat = lat_dataset.ReadAsArray()

lon_dataset = gdal.Open("NETCDF:"+gdalFilename+":XLONG")
lon = lon_dataset.ReadAsArray()

(nyCRS, nxCRS) = np.shape(lat)

met_info.met_domain_info["nxCRS"] = nxCRS
met_info.met_domain_info["nyCRS"] = nyCRS
met_info.met_domain_info["lat_min"] = np.min(lat)
met_info.met_domain_info["lat_max"] = np.max(lat)
met_info.met_domain_info["lon_min"] = np.min(lon)
met_info.met_domain_info["lon_max"] = np.max(lon)

This doesn't show that the projection information is being extracted form the met data only some bounds.

So once this is fead in to WRFtoARL is will default to a domain set up defined by gridded bounds wont account for the projection. I looks like WRFtoARL has procedures to convert netcdf to arl  accounting for projection. However I dont think we are telling it to do that. 

So what i think we need to do is first look at config set up and see if we define `USER_DEFINED_GRID=True`

Another place we may want to look is the fillMetDomainInfo module. The module doesn't appear to grab enough information for WRFtoARL to account for for our metrologies projection when its making the conversion from netcdf to arl. 


My reasoning comes from all this comes from the BSF log file.
Allowed me to see what module are being used where based on the sequence they are logged. 

BlueSky: BlueSky Framework version 3.5.1 (rev 39130)
BlueSky: Using OUTPUT_DIR: /bluesky/bsf-3.5.1-43555/output/bsc-wrf2arl/east18
BlueSky: Using WORK_DIR: /bluesky/bsf-3.5.1-43555/working/bsc-wrf2arl/east18
BlueSky: Emissions period: 20200915 18Z to 20200919 06Z
BlueSky: Dispersion period: 20200916 18Z to 20200919 06Z
WRF: Got 60 nested WRF files
WRF: Got 60 WRF files
WRF: Available meteorology: 20200916 18Z to 20200919 06Z
WRF: Dispersion will run for 60 hours
WRFLocalMet: Extract fire-local meteorological data v1
WRFLocalMet: Obtaining met_domain_info from /bluesky/bsf-3.5.1-43555/input/bsc-wrf2arl/east18/wrfout_d02_2020-09-16_18:00:00
WRFLocalMet: Unable to extract local met from WRF data; elevation is undefined
WRFToARL: Convert WRF-format met data to ARL format. v7
WRFToARL: Converting WRF data into ARL format for the HYSPLIT model
Context: Keeping a copy of hysplit.arl in cache
WRFToARL: Converting Nested WRF data into ARL format for the HYSPLIT model
Context: Keeping a copy of hysplit_nest.arl in cache
Archive: Creating archive: /bluesky/bsf-3.5.1-43555/output/bsc-wrf2arl/east18/archive-2020091618.tar.gz
BlueSky: Completed in 13 minutes 26.32 seconds












I went back to WRFtoARL in /bluesky/bsf-ops/modules/HYSPLIT/v7/hysplit.py

What WRFtoARL does is:
    """ Convert WRF-format met data to ARL format.

    This method uses the executable configured with WRFTOARL_BINARY
    to convert WRF NetCDF files to ARL formatted files one at a time
    and then concatenates them to create a single "hysplit.arl" file
    containing all met data.
    """


From my understanding WRFtoARL uses met_info that is first extracted/define in WRFLocalMet

WRFLocalMet is located in /bluesky/bsf-ops/modules/WRFdata/v1/wrfdata.py

In WRFLocalMet there is a fillMetDomainInfo module

fillMetDomainInfo reads one of our WRF met netcdf files and defines the met_info used in WRFtoARL by:

lat_dataset = gdal.Open("NETCDF:"+gdalFilename+":XLAT")
lat = lat_dataset.ReadAsArray()

lon_dataset = gdal.Open("NETCDF:"+gdalFilename+":XLONG")
lon = lon_dataset.ReadAsArray()

(nyCRS, nxCRS) = np.shape(lat)

met_info.met_domain_info["nxCRS"] = nxCRS
met_info.met_domain_info["nyCRS"] = nyCRS
met_info.met_domain_info["lat_min"] = np.min(lat)
met_info.met_domain_info["lat_max"] = np.max(lat)
met_info.met_domain_info["lon_min"] = np.min(lon)
met_info.met_domain_info["lon_max"] = np.max(lon)

There is no projection information being extracted or stored in met_info.

As said before, met_info is then used in  WRFtoARL to convert our met netcdf files to arl. 

WRFtoARL has procedures to convert netcdf to arl  accounting for projections but we arent using them.

What we are using are domain bonds. The bonds are either set by:
USER_DEFINED_GRID=True

or by the bounds defined in met_info


What we need to do is first look at our config and see if we define `USER_DEFINED_GRID=True`
if set to true WRFtoARL will by pass the netcdf attributes (projection etc) when converting netcdf to arl

If we aren't defining `USER_DEFINED_GRID=True` than we need to look at the fillMetDomainInfo module and add a few lines of code to extract the projection information for the netcdf files. 

Adding projection to met_info will allow WRFtoARL follow different procedures and create arl files with the met projection in mind. 


My reasoning for all this comes from the BSF log file. I was looking at the print statements and where they are in each script. 
Allowed me to see what module is being used where based on the sequence they are logged.
BlueSky: BlueSky Framework version 3.5.1 (rev 39130)
BlueSky: Using OUTPUT_DIR: /bluesky/bsf-3.5.1-43555/output/bsc-wrf2arl/east18
BlueSky: Using WORK_DIR: /bluesky/bsf-3.5.1-43555/working/bsc-wrf2arl/east18
BlueSky: Emissions period: 20200915 18Z to 20200919 06Z
BlueSky: Dispersion period: 20200916 18Z to 20200919 06Z
WRF: Got 60 nested WRF files
WRF: Got 60 WRF files
WRF: Available meteorology: 20200916 18Z to 20200919 06Z
WRF: Dispersion will run for 60 hours
WRFLocalMet: Extract fire-local meteorological data v1
WRFLocalMet: Obtaining met_domain_info from /bluesky/bsf-3.5.1-43555/input/bsc-wrf2arl/east18/wrfout_d02_2020-09-16_18:00:00
WRFLocalMet: Unable to extract local met from WRF data; elevation is undefined
WRFToARL: Convert WRF-format met data to ARL format. v7
WRFToARL: Converting WRF data into ARL format for the HYSPLIT model
Context: Keeping a copy of hysplit.arl in cache
WRFToARL: Converting Nested WRF data into ARL format for the HYSPLIT model
Context: Keeping a copy of hysplit_nest.arl in cache
Archive: Creating archive: /bluesky/bsf-3.5.1-43555/output/bsc-wrf2arl/east18/archive-2020091618.tar.gz
BlueSky: Completed in 13 minutes 26.32 seconds