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

#Create an array
a = ca.arange(ctx, 12)

# Multiply is not defined
try:
    c = a * 2
except TypeError as err:
    print 'Expected:', err
    
    
@ca.binary_ufunc
def multuply(x, y):
    return x * y

c = multuply(a, 2)

with c.map() as arr:
    print arr
