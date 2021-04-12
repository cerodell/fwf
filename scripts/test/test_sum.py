#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
from utils.test.sumdef import summe


## Test of the repo fwf
z = summe(4, 5)
print(z)

try:
    var
except NameError:
    var_exists = False
    a = 4
    print(a)
else:
    var_exists = True
    print(var_exists)
