import context
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors
import cartopy.crs as crs
from pathlib import Path
import cartopy.feature as cfeature
from datetime import datetime



filein = "/Users/rodell/Google Drive File Stream/Shared drives/Research/CRodell/Pelican_Mnt_Fire/Data/AQ"

aq_list = {}
pathlist = sorted(Path(filein).glob('*'))
#print(pathlist)
for path in pathlist:
    path_in_str = str(path)
    aq_file = pd.read_csv(path_in_str, skiprows = 3)
    aq_file = aq_file[1:]
    aq_list.update({str(path_in_str[-11:-4]): aq_file})


# plt.plot(np.array(aq_list['u5_air1']['CO2'], dtype = float))

##Time of Interst...Start and Stop in PDT!!!!!!!!!!!!
start     = datetime(2001,7,19,17,30,00)   ##Pre: (2019,5,6,15,30)  ##Post: (2019,5,16,00,00)
start_str = start.strftime('%m/%d/%y %H:%M:%S')

stop     = datetime(2001,7,19,18,20,00)    ##Pre: (2019,5,7,15,30)  ##Post: (2019,5,21,00,00)
stop_str = stop.strftime('%m/%d/%y %H:%M:%S')


    ##Loop and convert list to datetime type list
    Date =[]
    for i in range(len(Date_Str)):
        Date_i = datetime.strptime(Date_Str[i], '%m/%d/%y %H:%M:%S')
        Date.append(Date_i)
        
    time_start     = Date_Str.index(start_str)
    time_stop      = Date_Str.index(stop_str) + 1
    time_h         = Date_Str[time_start:time_stop] 
    time_h         = [datetime.strptime(time_h[i], '%m/%d/%y %H:%M:%S') for i in range(len(time_h))]

# "############################# Make Plots #############################"

%matplotlib
fig, ax = plt.subplots(1, figsize=(14,10))
fig.suptitle('Pelican Mountain \n Air Quality', fontsize=16)
fig.subplots_adjust(hspace=0.18)
for key in aq_list.keys():
#     theTime = ('20'+aq_list[key]['year'][800:] + '-' + aq_list[key]['month'][800:] + '-0' + \
#         aq_list[key]['day'][800:] + 'T' + aq_list[key]['hour'][800:] + ':' + aq_list[key]['minute'][800:] + ':' + \
#             aq_list[key]['second'][800:])
#     print(theTime)       
#     theTime = np.datetime64(theTime)
    plt.plot(theTime,np.array(aq_list[key]['PM2.5_sensor A'][800:], dtype = float), label = key)
#ax[0].set_xlabel("Datetime (PDT)", fontsize = ylabel)
ax.set_ylabel("PM2.5 (PPB)", fontsize = 12)
ax.xaxis.grid(color='gray', linestyle='dashed')
ax.yaxis.grid(color='gray', linestyle='dashed')
ax.legend()




fig, ax = plt.subplots(1, figsize=(14,10))
fig.suptitle('Pelican Mountain \n Air Quality', fontsize=16)
fig.subplots_adjust(hspace=0.18)
for key in aq_list.keys():
    plt.plot(np.array(aq_list[key]['CO2'][800:], dtype = float), label = key)
#ax[0].set_xlabel("Datetime (PDT)", fontsize = ylabel)
ax.set_ylabel("CO2 (PPM)", fontsize = 12)
ax.xaxis.grid(color='gray', linestyle='dashed')
ax.yaxis.grid(color='gray', linestyle='dashed')
ax.legend()

 
    