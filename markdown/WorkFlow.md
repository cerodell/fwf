## Main Brach

The repository currently has three main branches:

- `master`
- `wfr3`
- `dev-wfr4`

### master
  - is the current operational brnach and should not be touched unless merging from a development branch
  - NOTE: master is currently working with wrf3 (ie WFRT's WAN00CP-04) forecast.

### wfrt3
  - this brnach is to run cases studies of the wrf3 (ie WFRT's WAN00CP-04)
  - it runs fwf in both the 4 km and 12 km met domains 
  - currently working with 2018 datasets 
  - used for developing a Fire Behavior Predcitons system for use in the smoke plume rise paramiterzation study. 

### dev-wfr4
  - this is a development branch to operationalze the new wrf4 domain (ie WFRT's WAN00CG-01)
  - it runs fwf in both the 4 km and 12 km met domains 



#### Quick Commands 
`$ git checkout                                     // change to the stable branch`

`$ git merge master                                  // forces creation of commit object during merge`
