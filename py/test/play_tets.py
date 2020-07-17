import context
import math
import numpy as np
import pandas as pd
import xarray as xr

a_limit = 3

a = np.random.randint(10, size=(2, 4))
zero = np.zeros_like(a)

print(a)
a_condtion  = xr.where(a < a_limit, zero, a*-1)
print(a_condtion)