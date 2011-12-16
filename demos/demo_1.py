'''
Created on Dec 15, 2011

@author: sean
'''

import opencl as cl
import clyther as cly
import clyther.array as ca
from ctypes import c_float
import numpy as np
#Always have to create a context.
ctx = cl.Context()

#can print the current devices
print ctx.devices

#Create an array
a = ca.arange(ctx, 12)

print a

#map is the same as a memory map
with a.map() as arr:
    print arr

#can clice
b = a[1::2]

with b.map() as arr:
    print arr

#ufuncs
c = a + 1

with c.map() as arr:
    print arr
