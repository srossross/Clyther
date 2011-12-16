
import opencl as cl
import clyther as cly
import clyther.array as ca
from ctypes import c_float
import numpy as np
#Always have to create a context.
ctx = cl.Context()

#can 
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

#can do sin
d = ca.sin(c)


import clyther.runtime as clrt
#===============================================================================
# Controll the kernel
#===============================================================================


@cly.global_work_size(lambda a: [a.size])
@cly.kernel
def generate_sin(a):
    
    gid = clrt.get_global_id(0)
    n = clrt.get_global_size(0)
    
    r = c_float(gid) / c_float(n)
    
    # sin wave with 16 occilations
    x = r * c_float(16.0 * 3.1415)
    
    # x is a range from -1 to 1
    a[gid].x = r * 2.0 - 1.0
    
    # y is sin wave
    a[gid].y = clrt.native_sin(x)

queue = cl.Queue(ctx)

a = cl.empty(ctx, [200], cly.float2)

event = generate_sin(queue, a)

event.wait()

print a
with a.map(queue) as view:
    print np.asarray(view)

#===============================================================================
# From here I can keep boiling down until I get the the bare openCL C framework 
#===============================================================================

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

#===============================================================================
# Compile to openCL code 
#===============================================================================

print generate_sin.compile(ctx, a=cl.global_memory('f'), source_only=True) 

