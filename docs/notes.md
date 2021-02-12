# FWF
---
## Fire Weather Forecast Model

The Fire Weather Index (FWI) System, developed by Van Wagner (1977) and Van Wanger and Pickett (1985), estimates how past/current/future weather conditions affect the moisture content within the varied forest fuel layers across the lands scape. The FWI is used daily in wildfire operations to assess the likelihood of wildfire activity and the severity of fire behavior if fires were to occur. It comprises six different indices/codes that are empirically derived from meteorological variables. Provincial wildfire agencies use forecast predictions of the FWI to allocate finite resources (i.e., fire crews, aircraft etc.) for fire suppression response.

A new model called the Fire Weather Forecast (FWF), utilizes gridded output from Weather Research and Forecasting (WRF) numerical weather prediction (NWP) model to resolve the FWI System. The model domain covers the majority of North America with a 4-km or 12-km spatial and 1-h temporal resolution. The FWF system solves the FWI empirical formulae for fuel moisture codes and indices at every grid point within the NWP model. The fast-responding codes/indices (fine fuel moisture code, initial spread index, fire weather index, and daily severity rating) are resolved hourly, while the slow-responding codes/indices (duff moisture code, drought code, and buildup index) are resolved once daily at noon local time.

---
## Data Structure



| Hourly Dataset `hourly_ds`  | Daily Dataset `daily_ds`  |
 --------------------------- | ------------------------- |
| Fine Fuel Moisture Code **FFMC**  | Duff Moisture Code **DMC**  |
| Initial Spread INdex **ISI**  | Drought Moisture Code **DC**  |
| Fire Weather Index **FWI** | Build Up Index **BUI** |
| *WRF*: Temp, RH, <br> Wind Speed/Direction <br> Hourly Rain Fall Totals | *WRF*: Average Temp, RH, <br> Wind Speed/Direction <br> 24 hour Rain Fall Totals <br> between (1100-1300) local time|

---
## Model Domain
