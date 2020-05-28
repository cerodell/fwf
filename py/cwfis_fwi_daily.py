"""
Created on Tue Sep 17 16:26:15 2019

@author: crodell
"""

import os
import errno
import urllib.request
from datetime import datetime

user      = 'rodell'


# Function for creating filepath if the path does not already exist
def make_sure_path_exists(path):
    if os.path.isdir(path):
        return
    else:
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise


now = datetime.now() # current date and time
date_time = now.strftime("%Y%m%d")
print("date and time:",date_time)

save   = '/Users/'+user+'/Google Drive File Stream/Shared drives/Research/CRodell/Model/Data/cwfis/2020/'
make_sure_path_exists(save)


url    = 'https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/current/cwfis_fwi_'

response = urllib.request.urlopen(url + date_time + '.csv')
html = response.read()

with open(save + 'cwfis_fwi_' + date_time + '.csv', 'wb') as f:
        f.write(html)





