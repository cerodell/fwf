# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Getting Started with the AρρEEARS API: Submitting and Downloading an Area Request
# ### This tutorial demonstrates how to use Python to connect to the AρρEEARS API
# The Application for Extracting and Exploring Analysis Ready Samples ([AρρEEARS](https://appeears.earthdatacloud.nasa.gov/)) offers a simple and efficient way to access and transform geospatial data from a variety of federal data archives in an easy-to-use web application interface. AρρEEARS enables users to subset [geospatial data](https://appeears.earthdatacloud.nasa.gov/products) spatially, temporally, and by band/layer for point and area samples. AρρEEARS returns not only the requested data, but also the associated quality values, and offers interactive visualizations with summary statistics in the web interface.  The [AρρEEARS API](https://appeears.earthdatacloud.nasa.gov/api/) offers users **programmatic access** to all features available in AρρEEARS, with the exception of visualizations. The API features are demonstrated in this notebook.
# ***
# ### Example: Submit an area request using a U.S. National Park boundary as the region of interest for extracting elevation, vegetation and land surface temperature data
# Connect to the AρρEEARS API, query the list of available products, submit an area sample request, download the request, become familiar with the AρρEEARS Quality API, and import the results into Python for visualization. AρρEEARS area sample requests allow users to subset their desired data by spatial area via vector polygons (shapefiles or GeoJSONs). Users can also reproject and reformat the output data. AρρEEARS returns the valid data from the parameters defined within the sample request.
# #### Data Used in the Example:
# - Data layers:
#     - NASA MEaSUREs Shuttle Radar Topography Mission (SRTM) Version 3 Digital Elevation Model
#         - [SRTMGL1_NC.003](https://doi.org/10.5067/MEaSUREs/SRTM/SRTMGL1.003), 30m, static: 'SRTM_DEM'
#     - Combined MODIS Leaf Area Index (LAI)
#         - [MCD15A3H.006](https://doi.org/10.5067/MODIS/MCD15A3H.006), 500m, 4 day: 'Lai_500m'
#     - Terra MODIS Land Surface Temperature
#         - [MOD11A2.061](https://doi.org/10.5067/MODIS/MOD11A2.061), 1000m, 8 day: 'LST_Day_1km', 'LST_Night_1km'
# ***
# # Topics Covered:
# 1. **Getting Started**
#     1a. Set Up the Working Environment
#     1b. Login [Login]
# 2. **Query Available Products [Product API]**
#     2a. Search and Explore Available Products [List Products]
#     2b. Search and Explore Available Layers [List Layers]
# 3. **Submit an Area Request [Tasks]**
#     3a. Import a Shapefile
#     3b. Search and Explore Available Projections [Spatial API]
#     3c. Compile a JSON [Task Object]
#     3d. Submit a Task Request [Submit Task]
#     3e. Retrieve Task Status [Retrieve Task]
# 4. **Download a Request [Bundle API]**
#     4a. Explore Files in Request Output [List Files]
#     4b. Download Files in a Request (Automation) [Download File]
# 5. **Explore AρρEEARS Quality Service [Quality API]**
#     5a. List Quality Layers [List Quality Layers]
#     5b. Show Quality Values [List Quality Values]
#     5c. Decode Quality Values [Decode Quality Values]
# 6. **BONUS: Import Request Output and Visualize**
#     6a. Import a GeoTIFF
#     6b. Plot a GeoTIFF
# ***
# ### Dependencies:
# - This tutorial was tested using Python 3.6.1.
# - A [NASA Earthdata Login](https://urs.earthdata.nasa.gov/) account is required to complete this tutorial. You can create an account at the link provided.
# - To execute section 6, the [Geospatial Data Abstraction Library](http://www.gdal.org/) (GDAL) is required.
# ***
# ### AρρEEARS Information:
# To access AρρEEARS, visit: https://appeears.earthdatacloud.nasa.gov/
# > For comprehensive documentation of the full functionality of the AρρEEARS API, please see the AρρEEARS [API Documentation](https://appeears.earthdatacloud.nasa.gov/api/)
#
# Throughout the tutorial, specific sections of the API documentation can be accessed by clicking on the bracketed [] links in the section headings.
# ***
# ### Files Used in this Tutorial:
# - [Administrative Boundaries of National Park System Units 12/31/2017 - National Geospatial Data Asset (NGDA) NPS National Parks Dataset](https://irma.nps.gov/DataStore/DownloadFile/594958)
#
# ### Source Code used to Generate this Tutorial:
# - [Jupyter Notebook](https://git.earthdata.nasa.gov/projects/LPDUR/repos/appeears-api-getting-started/browse/AppEEARS_API_Area.ipynb)

# %% [markdown]
# ***

# %% [markdown]
# # 1. Getting Started

# %% [markdown]
# ***
# ## 1a. Set Up the Working Environment
# #### Import the required packages, set the input/working directory, and create an output directory for the results.

# %%
# Import packages

import context
import requests as r
import getpass, pprint, time, os, cgi, json
import geopandas as gpd

from context import data_dir

# %% [markdown]
# #### If you are missing any of the packages above, download them in order to use the full functionality of this tutorial.

# %%
# Set input directory, change working directory
inDir = str(data_dir)  # IMPORTANT: Update to reflect directory on your OS
os.chdir(inDir)  # Change to working directory
api = "https://appeears.earthdatacloud.nasa.gov/api/"  # Set the AρρEEARS API to a variable

# %% [markdown]
# <div class="alert alert-block alert-warning" >
# <b>If you plan to execute this tutorial on your own OS, `inDir` above needs to be changed.</b>
# </div>

# %% [markdown]
# ***
# ## 1b. Login[[Login](https://appeears.earthdatacloud.nasa.gov/api/#login)]
# #### To submit a request, you must first login to the AρρEEARS API. The AρρEEARS API requires the same [NASA Earthdata Login](https://urs.earthdata.nasa.gov/) as the AρρEEARS user interface. Use the `getpass` package to enter your NASA Earthdata login **Username** and **Password**. When prompted after executing the code block below, enter your username followed by your password.

# %%
# user = getpass.getpass(prompt = 'Enter NASA Earthdata Login Username: ')      # Input NASA Earthdata Login Username
# password = getpass.getpass(prompt = 'Enter NASA Earthdata Login Password: ')  # Input NASA Earthdata Login Password

# %% [markdown]
# #### Use the `requests` package to post your username and password. A successful login will provide you with a token to be used later in this tutorial to submit a request. For more information or if you are experiencing difficulties, please see the [API Documentation](https://lpdaacsvc.cr.usgs.gov/appeears/api/?language=Python%203#login).

# %%
user, password = "cerodell", "$/BA_*8)kZY7aiP"
token_response = r.post(
    "{}login".format(api), auth=(user, password)
).json()  # Insert API URL, call login service, provide credentials & return json
del user, password  # Remove user and password information
token_response  # Print response

# %% [markdown]
# #### Above, you should see a Bearer token. Notice that this token will expire approximately 48 hours after being acquired.
# ***
# # 2. Query Available Products [[Product API](https://appeears.earthdatacloud.nasa.gov/api/#product)]
# ## 2a. Search and Explore Available Products [[List Products](https://appeears.earthdatacloud.nasa.gov/api/#list-products)]
# #### The product API provides details about all of the products and layers available in AρρEEARS. Below, call the product API to list all of the products available in AρρEEARS.

# %%
product_response = r.get(
    "{}product".format(api)
).json()  # request all products in the product service
print(
    "AρρEEARS currently supports {} products.".format(len(product_response))
)  # Print no. products available in AppEEARS

# %% [markdown]
# #### Next, create a dictionary indexed by product name, making it easier to query a specific product.

# %%
products = {
    p["ProductAndVersion"]: p for p in product_response
}  # Create a dictionary indexed by product name & version
products["VNP13A2.001"]  # Print information for MCD15A3H.006 NDVI Product
products["VNP15A2H.001"]  # Print information for VNP15A2H.001 LAI/FPAR Product

# %% [markdown]
# #### The product service provides many useful details, including if a product is currently available in AρρEEARS, a description, and information on the spatial and temporal resolution.

# %% [markdown]
# #### Below, make a list of all product+version names, and search for products containing *Leaf Area Index* in their description.

# %%
prodNames = {
    p["ProductAndVersion"] for p in product_response
}  # Make list of all products (including version)
for (
    p
) in prodNames:  # Make for loop to search list of products 'Description' for a keyword
    if "Leaf Area Index" in products[p]["Description"]:
        pprint.pprint(
            products[p]
        )  # Print info for each product containing LAI in its description

# %% [markdown]
# #### Using the info above, start a list of desired products by using the highest temporal resolution LAI product, `MCD15A3H.006`.

# %%
prods = [
    "MCD15A3H.006"
]  # Start a list for products to be requested, beginning with MCD15A3H.006
prods.append(
    "MOD11A2.061"
)  # Append the MOD11A2.061 8 day LST product to the list of products desired
prods.append(
    "SRTMGL1_NC.003"
)  # Append the SRTMGL1_NC.003 product to the list of products desired
prods  # Print list

# %% [markdown]
# ***
# # 2b. Search and Explore Available Layers [[List Layers](https://appeears.earthdatacloud.nasa.gov/api/#list-layers)]
# #### The product API allows you to call all of the layers available for a given product. Each product is referenced by its `ProductAndVersion` property. For a list of the layer names only, print the keys from the dictionary below.

# %%
lst_response = r.get(
    "{}product/{}".format(api, prods[1])
).json()  # Request layers for the 2nd product (index 1) in the list: MOD11A2.061
list(lst_response.keys())

# %% [markdown]
# #### Use the dictionary key `'LST_Day_1km'` to see the information for that layer in the response.

# %%
lst_response["LST_Day_1km"]  # Print layer response

# %% [markdown]
# #### AρρEEARS also allows subsetting data spectrally (by band). Create a tupled list with product name and specific layers desired.

# %%
layers = [
    (prods[1], "LST_Day_1km"),
    (prods[1], "LST_Night_1km"),
]  # Create tupled list linking desired product with desired layers

# %% [markdown]
# #### Next, request the layers for the `MCD15A3H.006` product.

# %%
lai_response = r.get(
    "{}product/{}".format(api, prods[0])
).json()  # Request layers for the 1st product (index 0) in the list: MCD15A3H.006
list(lai_response.keys())  # Print the LAI layer names

# %%
lai_response["Lai_500m"]["Description"]  # Make sure the correct layer is requested

# %% [markdown]
# #### Above, `Lai_500m` is the desired layer within the `MCD15A3h.006` product.
# #### Next, append `Lai_500m` to the tupled list of desired product/layers.

# %%
layers.append(
    (prods[0], "Lai_500m")
)  # Append to tupled list linking desired product with desired layers

# %% [markdown]
# #### Thirdly, request the layers for the `SRTMGL1_NC.003` product.

# %%
dem_response = r.get(
    "{}product/{}".format(api, prods[2])
).json()  # Request layers for the 3rd product (index 2) in the list: SRTMGL1_NC.003
list(dem_response.keys())  # Print the SRTM DEM layer names

# %% [markdown]
# #### Finally, append `SRTMGL1_DEM` to the tupled list of desired products/layers.

# %%
layers.append(
    (prods[2], "SRTMGL1_DEM")
)  # Append to tupled list linking desired product with desired layers

# %% [markdown]
# #### Below, take the tupled list (layers) and create a list of dictionaries to store each layer+product combination. This will make it easier to insert into the json file used to submit a request in Section 3.

# %%
prodLayer = []
for l in layers:
    prodLayer.append({"layer": l[1], "product": l[0]})
prodLayer

# %% [markdown]
# ***
# # 3. Submit an Area Request [[Tasks](https://appeears.earthdatacloud.nasa.gov/api/#tasks)]
# #### The **Submit task** API call provides a way to submit a new request to be processed. It can accept data via JSON, query string, or a combination of both. In the example below, compile a json and submit a request. Tasks in AρρEEARS correspond to each request associated with your user account. Therefore, each of the calls to this service requires an authentication token (see Section 1c.), which is stored in a header below.

# %%
token = token_response["token"]  # Save login token to a variable
head = {
    "Authorization": "Bearer {}".format(token)
}  # Create a header to store token information, needed to submit a request

# %% [markdown]
# ---
# ## 3a. Import a Shapefile
# #### In this section, begin by importing a shapefile using the `geopandas` package. The shapefile is publically available for download from the [NPS website](https://irma.nps.gov/DataStore/Reference/Profile/2224545?lnv=True).

# %%
nps = gpd.read_file(
    "{}nps_boundary.shp".format(inDir + os.sep + "Data" + os.sep)
)  # Read in shapefile as dataframe using geopandas
print(nps.head())  # Print first few lines of dataframe

# %% [markdown]
# #### Below, query the `geopandas` dataframe for the national park that you are interested in using for your region of interest, here *Grand Canyon National Park*.

# %%
nps_gc = nps[
    nps["UNIT_NAME"] == "Grand Canyon National Park"
].to_json()  # Extract Grand Canyon NP and set to variable
nps_gc = json.loads(nps_gc)  # Convert to json format

# %% [markdown]
# ---
# ## 3b. Search and Explore Available Projections [[Spatial API](https://appeears.earthdatacloud.nasa.gov/api/#spatial)]
# #### The spatial API provides some helper services used to support submitting area task requests. The call below will retrieve the list of supported projections in AρρEEARS.

# %%
projections = r.get(
    "{}spatial/proj".format(api)
).json()  # Call to spatial API, return projs as json
projections  # Print projections and information

# %% [markdown]
# #### Create a dictionary of projections with projection `Name` as the keys.

# %%
projs = {}  # Create an empty dictionary
for p in projections:
    projs[p["Name"]] = p  # Fill dictionary with `Name` as keys
list(projs.keys())  # Print dictionary keys

# %% [markdown]
# #### Print the information for the projection used in this tutorial.

# %%
projs["geographic"]

# %% [markdown]
# ---
# ## 3c. Compile a JSON  [[Task Object](https://appeears.earthdatacloud.nasa.gov/api/#task-object)]
# #### In this section, begin by setting up the information needed to compile an acceptable json for submitting an AρρEEARS area request. For detailed information on required json parameters, see the [API Documentation](https://appeears.earthdatacloud.nasa.gov/api/).

# %%
task_name = input(
    "Enter a Task Name: "
)  # User-defined name of the task: 'NPS Vegetation Area' used in example

# %%
task_type = ["point", "area"]  # Type of task, area or point
proj = projs["geographic"]["Name"]  # Set output projection
outFormat = ["geotiff", "netcdf4"]  # Set output file format type
startDate = (
    "07-01-2017"  # Start of the date range for which to extract data: MM-DD-YYYY
)
endDate = "07-31-2017"  # End of the date range for which to extract data: MM-DD-YYYY
recurring = False  # Specify True for a recurring date range
# yearRange = [2000,2016]            # if recurring = True, set yearRange, change start/end date to MM-DD

# %% [markdown]
# #### Below, compile the JSON to be submitted as an area request. Notice that `nps_gc` is inserted from the shapefile transformed to a json via the `geopandas` and `json` packages above in section 3a.

# %%
task = {
    "task_type": task_type[1],
    "task_name": task_name,
    "params": {
        "dates": [{"startDate": startDate, "endDate": endDate}],
        "layers": prodLayer,
        "output": {"format": {"type": outFormat[0]}, "projection": proj},
        "geo": nps_gc,
    },
}

# %% [markdown]
# ***
# ## 3d. Submit a Task Request [[Submit Task](https://appeears.earthdatacloud.nasa.gov/api/#submit-task)]
# #### Below, post a call to the API task service, using the `task` json created above.

# %%
task_response = r.post(
    "{}task".format(api), json=task, headers=head
).json()  # Post json to the API task service, return response as json
task_response  # Print task response

# %% [markdown]
# ***
# ## 3e. Retrieve Task Status [[Retrieve Task](https://appeears.earthdatacloud.nasa.gov/api/#retrieve-task)]
# #### This API call will list all of the requests associated with your user account, automatically sorted by date descending with the most recent requests listed first.

# %% [markdown]
# #### The AρρEEARS API contains some helpful formatting resources. Below, limit the API response to 2 entries and set `pretty` to True to format the response as an organized json, making it easier to read. Additional information on AρρEEARS API [pagination](https://appeears.earthdatacloud.nasa.gov/api/#pagination) and [formatting](https://appeears.earthdatacloud.nasa.gov/api/#formatting) can be found in the API documentation.

# %%
params = {
    "limit": 2,
    "pretty": True,
}  # Limit API response to 2 most recent entries, return as pretty json

# %%
tasks_response = r.get(
    "{}task".format(api), params=params, headers=head
).json()  # Query task service, setting params and header
tasks_response  # Print tasks response

# %% [markdown]
# #### Next, take the task id returned from the `task_response` that was generated when submitting your request, and use the AρρEEARS API status service to check the status of your request.

# %%
task_id = task_response["task_id"]  # Set task id from request submission
status_response = r.get(
    "{}status/{}".format(api, task_id), headers=head
).json()  # Call status service with specific task ID & user credentials
status_response

# %% [markdown]
# #### Above, if your request is still processing, you can find information on the status of how close it is to completing.
# #### Below, call the task service for your request every 20 seconds to check the status of your request.

# %%
# Ping API until request is complete, then continue to Section 4
starttime = time.time()
while r.get("{}task/{}".format(api, task_id), headers=head).json()["status"] != "done":
    print(r.get("{}task/{}".format(api, task_id), headers=head).json()["status"])
    time.sleep(20.0 - ((time.time() - starttime) % 20.0))
print(r.get("{}task/{}".format(api, task_id), headers=head).json()["status"])

# %% [markdown]
# ***
# # 4. Download a Request [[Bundle API](https://appeears.earthdatacloud.nasa.gov/api/#bundle)]
# #### Before downloading the request output, set up an output directory to store the output files, and examine the files contained in the request output.

# %%
destDir = os.path.join(
    inDir, task_name
)  # Set up output directory using input directory and task name
if not os.path.exists(destDir):
    os.makedirs(destDir)  # Create the output directory

# %% [markdown]
# ---
# ## 4a. Explore Files in Request Output [[List Files](https://appeears.earthdatacloud.nasa.gov/api/#list-files)]
# #### The bundle API provides information about completed tasks. For any completed task, a bundle can be queried to return the files contained as a part of the task request. Below, call the bundle API and return all of the output files.

# %%
bundle = r.get(
    "{}bundle/{}".format(api, task_id), headers=head
).json()  # Call API and return bundle contents for the task_id as json
bundle  # Print bundle contents

# %% [markdown]
# ***
# ## 4b. Download Files in a Request (Automation) [[Download File](https://appeears.earthdatacloud.nasa.gov/api/#download-file)]
# #### Now, use the contents of the bundle to select the file name and id and store as a dictionary.

# %%
files = {}  # Create empty dictionary
for f in bundle["files"]:
    files[f["file_id"]] = f[
        "file_name"
    ]  # Fill dictionary with file_id as keys and file_name as values
files

# %% [markdown]
# #### Use the `files` dictionary and a `for` loop to automate downloading all of the output files into the output directory.

# %%
for f in files:
    dl = r.get(
        "{}bundle/{}/{}".format(api, task_id, f),
        headers=head,
        stream=True,
        allow_redirects="True",
    )  # Get a stream to the bundle file
    if files[f].endswith(".tif"):
        filename = files[f].split("/")[1]
    else:
        filename = files[f]
    filepath = os.path.join(destDir, filename)  # Create output file path
    with open(filepath, "wb") as f:  # Write file to dest dir
        for data in dl.iter_content(chunk_size=8192):
            f.write(data)
print("Downloaded files can be found at: {}".format(destDir))

# %% [markdown]
# ***
# # 5. Explore AρρEEARS Quality Service [[Quality API](https://appeears.earthdatacloud.nasa.gov/api/#quality)]
# #### The quality API provides quality details about all of the data products available in AρρEEARS. Below are examples of how to query the quality API for listing quality products, layers, and values. The final example (Section 5c.) demonstrates how AρρEEARS quality services can be leveraged to decode pertinent quality values for your data.
# #### First, reset pagination to include `offset` which allows you to set the number of results to skip before starting to return entries. Next, make a call to list all of the data product layers and the associated quality product and layer information.

# %%
params = {
    "limit": 6,
    "pretty": True,
    "offset": 20,
}  # Limit response to 6 entries, start w/ 20th entry, return pretty json
quality_response = r.get(
    "{}quality".format(api), params=params
).json()  # Call quality API using pagination and return json
quality_response  # Print response

# %% [markdown]
# ---
# ## 5a. List Quality Layers [[List Quality Layers](https://appeears.earthdatacloud.nasa.gov/api/#list-quality-layers)]
# #### This API call will list all of the quality layer information for a product.

# %%
product = "MCD15A3H.006"  # Product used in the example
ql_response = r.get(
    "{}quality/{}".format(api, product)
).json()  # Call API to retrieve quality layers for selected product
ql_response  # Print response

# %% [markdown]
# ---
# ## 5b. Show Quality Values [[List Quality Values](https://appeears.earthdatacloud.nasa.gov/api/#list-quality-values)]
# #### This API call will list all of the values for a given quality layer.

# %%
qlayer = ql_response[1]["QualityLayers"][
    0
]  # Set quality layer from ql_response for 'Lai_500m'
qv_response = r.get(
    "{}quality/{}/{}".format(api, product, qlayer)
).json()  # Call API for list of bit-word quality values
qv_response  # Print response

# %% [markdown]
# ---
# ## 5c. Decode Quality Values [[Decode Quality Values](https://appeears.earthdatacloud.nasa.gov/api/#decode-quality-values)]
# #### This API call will decode the bits for a given quality value.

# %%
val = 1  # Set a specific value
q_response = r.get(
    "{}quality/{}/{}/{}".format(api, product, qlayer, val)
).json()  # Call quality API for specific value
q_response  # Print response

# %% [markdown]
# ***
# # 6. BONUS: Import Request Output and Visualize
# #### Here, import one of the output GeoTIFFs and show some basic visualizations using the `matplotlib` package.

# %%
# Import packages
import matplotlib.pyplot as plt
import numpy as np
from osgeo import gdal

list(files.values())  # List files downloaded

# %% [markdown]
# ---
# ## 6a. Import a GeoTIFF
# #### To perform the next step below, you will need to have [GDAL](http://www.gdal.org/) installed on your OS. Open the GeoTIFF file for the SRTM DEM, and read in as an array.
#

# %%
dem = gdal.Open(
    destDir + "/SRTMGL1_NC.003_SRTMGL1_DEM_doy2000042_aid0001.tif"
)  # Read file in
demBand = dem.GetRasterBand(1)  # Read the band (layer)
demData = demBand.ReadAsArray().astype(
    "float"
)  # Import band as an array with type float

# %% [markdown]
# #### Next, query the metadata for the fill value, and set fill value equal to `nan`.

# %%
demFill = demBand.GetNoDataValue()  # Returns fill value
demData[demData == demFill] = np.nan  # Set fill value to nan

# %% [markdown]
# ---
# ## 6b. Plot a GeoTIFF
# #### In this section, begin by highlighting the functionality of the `matplotlib` plotting package.

# %%
# Set matplotlib plots inline
# %matplotlib inline

# %% [markdown]
# #### First, make a basic plot of the DEM data.

# %%
plt.imshow(demData)
# Visualize a basic plot of the DEM data

# %% [markdown]
# #### Next, add some additional parameters to the plot.

# %%
import warnings

warnings.filterwarnings("ignore")

fig = plt.figure(figsize=(10, 7.5))  # Set the figure size (x,y)
plt.axis("off")  # Remove the axes' values
ax = fig.add_subplot(111)

# Plot the array, using a colormap and setting a custom linear stretch based on the min/max Elevation values
plt.imshow(demData, vmin=np.nanmin(demData), vmax=np.nanmax(demData), cmap="terrain")

# %% [markdown]
# #### Finally, add important map items including a legend and title.

# %%
plt.style.use("dark_background")  # Default to a black background
fig2 = plt.figure(figsize=(10, 7.5))  # Set the figure size
plt.axis("off")  # Remove the axes' values
ax1 = fig2.add_subplot(111)  # Make a subplot
fig2.subplots_adjust(top=3.8)  # Adjust spacing
ax1.set_title(
    "SRTM DEM: Grand Canyon NP", fontsize=15, fontweight="bold", color="white"
)  # Add title

# Plot the masked data, using a colormap and setting a custom linear stretch based on the min/max DEM values
im = plt.imshow(
    demData, vmin=np.nanmin(demData), vmax=np.nanmax(demData), cmap="terrain"
)

cb = plt.colorbar(
    im, orientation="horizontal", fraction=0.047, pad=0.004, shrink=0.6
)  # Add a colormap legend
cb.set_label(label="Elevation (m)", color="white")  # Set Label and color
cb.outline.set_edgecolor("white")  # Set edge color

# %% [markdown]
# ### This example can provide a template to use for your own research workflows. Leveraging the AρρEEARS API for searching, extracting, and formatting analysis ready data, and importing it directly into Python means that you can keep your entire research workflow in a single software program, from start to finish.

# %% [markdown]
# ***
# <div class="alert alert-block alert-info">
# <h1> Contact Information </h1>
#
# <h3> Material written by LP DAAC$^{1}$ </h3>
#
# <b>Contact:</b> LPDAAC@usgs.gov
#
# <b>Voice:</b> +1-605-594-6116
#
# <b>Organization:</b> Land Processes Distributed Active Archive Center (LP DAAC)
#
# <b>Website:</b> https://lpdaac.usgs.gov/
#
# <b>Date last modified:</b> 05-06-2022
#
# $^{1}$Innovate! Inc., contractor to the U.S. Geological Survey, Earth Resources Observation and Science (EROS) Center, Sioux Falls, South Dakota, 57198-001, USA. Work performed under USGS contract G15PD00467 for LP DAAC$^{2}$.
#
# $^{2}$LP DAAC Work performed under NASA contract NNG14HH33I.
