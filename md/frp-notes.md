# Notes

Feature selection for multi layer persptron model to predict FRP

## Training dataset
I am using fire cases from XXX number of fires for 2021 and 2022 to create the MLP model.
I will use 2023 with XX fire cases studies to verfiy model performace. I will aslo create spatial maps of FRP for comparison

| Header | 2021 | 2022 | 2023 |
|----------|----------|----------|----------|
| Fire Cases |  1826  |  1949  |  595*  |
| Spatially averaged | 111030   | 75275  |  ????? |

### Feature Selection


Make distribution figure

![Heat Map](../data/images/rave/mlp/features/distributions-as-is.png)


Drop outliers using 2STD for each variable

![Heat Map](../data/images/rave/mlp/features/distributions-2std.png)




Make heatmap show corelation of all features and target

![Heat Map](../data/images/rave/mlp/features/correlation_heatmap-as-is.png)


Drop outliers using 2STD for each variable

![Heat Map](../data/images/rave/mlp/features/correlation_heatmap-2std.png)



Lets test by using sklearn RobustScaler which "Scale features using statistics that are robust to outliers."


I will test by dropping 1 outside STD as it make for a nice distirbution accross all the data
I think that the FRP values are relvant and not erroneous which ill need to confrim thats the case...meaning i need to add the case number to the ml-data so i can look at these extreme cases



after testing/learning i found that dropping STD is bad as the model needs that data to learn and its not erronoise but true obs..also ths suports the use of a RobustScaler which scale feature that more robust to outliers

May 2
I am now testing by taking my ~5000 fire cases and randomly smaplying and removing 10% (500) for testing and leaving the remianing 90% (4500) for training the model.

Where i then will use my 500 testing cases to perform stats and do time seires all on the RAVE grid, which is something i think ill need to use in operations as LAI, NDVI and my satic vars have higer res than my nwp forecast

I nee to fidn away to remove bad fire cases from the 5000 i have
ideas are
- to remvoe by lenght, if less than 24 hours drop
- fires with many missing values, we want them continuous


May 10 TODO!!


Make climo of fuel load data

Make fire cases (as nc files!!) to include fuel load data
make with both WRF and ERA5-land derived FWI (might be to just open and and fuel data for the exisitign wrf fire zarr files)
make new ml data with this improved fuel load data
traing new ml with fuel load data
also set up a script to tune MLP


combing traing of mlp and rf and lst inot functions so its portable to scripts


May 17
We have made a new training datset grabing fires that had moderate and higher corelations with the ISI form the FWI systme. This was to ensure that our training datset was learing from feaures we know that are impornts

Leanring more about FRP and its area depenedinces and that i have trained a model on a 3x3km grid ill also need to alway run the moel on that grid res. (the rave paper says something to the extentent)

goal is to make a 3x3 km domain over the entire 12x12km WRF d02 domain. to do this ill reproject the 4x4km and 12x12 to 3x3km and nest the old 4x4 into the 12x12

i also need tot test the model in an operation way, to do that i will use all active fire grid from the past 24hours as the grid ill sum or average for comaprison to RAVE. this seems most fair as currently i cant model the fire growth



TODO

add lat dependency also and time of year dependency



## Hudson Bay fire ID 24450415
## Oak Fire ID 25485086
## Caldor Fire ID 24564294
## marshal Fire ID NOT IN GLOB FIRE DATABASE
