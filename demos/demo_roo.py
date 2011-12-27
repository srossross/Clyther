'''
Created on Dec 15, 2011

@author: sean
'''


import opencl as cl
import clyther as cly
import clyther.array as ca
from ctypes import c_float
import numpy as np

import clyther.runtime as clrt
#===============================================================================
# Controll the kernel
#===============================================================================

#Always have to create a context.
ctx = cl.Context()

@cly.global_work_size(lambda a: [a.size])
@cly.kernel
def generate_sin(a):
    
    gid = clrt.get_global_id(0)
    n = clrt.get_global_size(0)
    
    r = c_float(gid) / c_float(n)
    
    # sin wave with 8 peaks
    y = r * c_float(16.0 * 3.1415)
    
    # x is a range from -1 to 1
    a[gid].x = r * 2.0 - 1.0
    
    # y is sin wave
    a[gid].y = clrt.native_sin(y)

queue = cl.Queue(ctx)

a = cl.empty(ctx, [200], cly.float2)

event = generate_sin(queue, a)

event.wait()

print a
with a.map(queue) as view:
    print np.asarray(view)

#===============================================================================
# Plotting
#===============================================================================
from maka import roo

ctx = roo.start()
queue = cl.Queue(ctx)

a = cl.gl.empty_gl(ctx, [200], cly.float2)

event = generate_sin(queue, a)
event.wait()

roo.plot(a)

roo.show()
