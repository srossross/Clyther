import clyther as cly

import opencl as cl

import clyther.runtime as clrt

@cly.global_work_size(lambda a: a.shape)
@cly.kernel
def foo(a):
    x = clrt.get_global_id(0)
    y = clrt.get_global_id(1)
   
    a[x, y] = x + y * 100
     
ctx = cl.Context(device_type=cl.Device.CPU)

queue = cl.Queue(ctx)

a = cl.empty(ctx, [4, 4], 'f')

foo(queue, a)

print foo._compile(ctx, a=cl.global_memory('f'), source_only=True)

import numpy as np
with a.map(queue) as view:
    print np.asarray(view)
