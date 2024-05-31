## Introduction

- **Define Fire Radiative Power (FRP)**:
  - Explain its importance for wildfire smoke modeling, focusing on plume rise and emission production, often referred to as the "top-down approach to smoke forecasting".
  - Discuss current methods that use fixed diurnal curves and/or persistence, which can lead to overprediction of emissions and injection height (Di Giuseppe, 2017).

- **Paper Breakdown**:
  - Methods
  - Datasets
  - Target Variable
  - Feature Selection
  - MLP Model

## Methods
### **Datasets**

#### FWF/WRF Model
  - Description of the model used.

#### Global Fuel Characteristic Model and Dataset
  - Used for wildfire prediction.
  - While available only up to 2021, live fuels were found to be most important according to a random forest feature selection process. The model could yield improvement once the fuels model is operational.

#### RAVE Dataset
  - A hybrid geostationary/polar orbiting FRP dataset over North America.
  - Grid resolution: 3x3 km.

#### GlobFire Fire Perimeters
  - A global dataset of individual fire perimeters for 2021-2023.
  - Available in ESRI shapefile format, derived from the MCD64A1 burned area product.
  - Each fire shapefile has a unique fire identification code, initial and final dates, geometry, and final area in hectares.
  - Enables quick extraction of fires over North America.
  - Provides variables of interest for all fire cases to test feature selection and the MLP model.

### Target Variable

#### Mean FRP
  - The mean values of FRP from each individual fire were used.
  - Mean FRP was chosen as it smooths the time series and prevents outliers.
  - A direct input-to-target model could not generate meaningful results due to the stochastic nature of wildfires.

### Feature Selection

- Utilized a random forest generator from `scikit-learn` to determine the most important features for input to an MLP model.
- Physical understanding of the problem was also used:
  - The use of ISI and BUI made sense as they constitute the hourly FWI, which showed a strong correlation with wildfires.
  - Using these sub-indexes is logical based on what they represent:
    - ISI: Potential surface spread of a fire (based heavily on surface fuel moisture and wind speed).
    - BUI: Potential energy stored in the vegetation (based on climatological conditions affecting the vegetation over the past weeks, months, and even years).
  - Fuel loading of live and dead wood and foliage is logical in the context of more sophisticated coupled fire-atmosphere models, which require these inputs to model fire behavior/growth/spread.
    - Fuel loading is also helpful to enhance the Fire Weather Index system developed for a standard jack pine stand. Using some type of fuel loading (LAI or VOD) as done in Di Giuseppe (2023) helps improve results.

### MLP Model

- Used an MLP model with two layers and 32 neurons in each layer.
  - This was tested using a training dataset with a specified number of fires.
  - The data was split, keeping 12% of the fires for testing/verification, leading to an approximate 15% split in the total dataset.
- Used TensorFlow with early stopping.

## Results and Discussion
