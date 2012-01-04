'''
Created on Dec 15, 2011

@author: sean
'''

import opencl as cl
import clyther as cly
from ctypes import c_float
import numpy as np
from math import sin
import clyther.runtime as clrt
#===============================================================================
# Controll the kernel
#===============================================================================

#Always have to create a context.
ctx = cl.Context()

@cly.global_work_size(lambda a: a.shape)
@cly.kernel
def generate_sin(a):
    
    gid = clrt.get_global_id(0)
    n = clrt.get_global_size(0)
    
    r = c_float(gid) / c_float(n)
    
    # sin wave with 8 oscillations
    y = r * c_float(16.0 * 3.1415)
    
    # x is a range from -1 to 1
    a[gid].x = r * 2.0 - 1.0
    
    # y is sin wave
    a[gid].y = sin(y)

queue = cl.Queue(ctx)

a = cl.empty(ctx, [200], cl.cl_float2)
event = generate_sin(queue, a)

event.wait()

print a
with a.map(queue) as view:
    print np.asarray(view)
