#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 09:31:34 2019

@author: rodell
"""

import os
import errno
import urllib
from datetime import datetime

""" ###################### Set Paths ####################### """

user      = 'rodell'
url_am    = 'https://wildfire.alberta.ca/files/amwx.csv'
url_pm    = 'https://wildfire.alberta.ca/files/pmwx.csv'

save   = '/Users/'+user+'/Google Drive File Stream/Shared drives/Research/CRodell/Model/Data/awf/'

""" ###################### Grab Time ####################### """


now = datetime.now() # current date and time
date_time = now.strftime("%Y%m%d")
print("date and time:",date_time)


""" ###################### Grab and svae am ####################### """

response = urllib.request.urlopen(url_am)
html = response.read()

with open(save + 'am/'+ date_time +'.csv', 'wb') as f:
        f.write(html)


""" ###################### Grab and save pm ####################### """

response = urllib.request.urlopen(url_pm)
html = response.read()


with open(save + 'pm/' + date_time + '.csv', 'wb') as f:
        f.write(html)



