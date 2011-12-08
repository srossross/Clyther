'''
Created on Dec 7, 2011

@author: sean
'''

import clyther as cly
import clyther.runtime as clrt
import opencl as cl
from ctypes import c_float
import numpy as np


@cly.global_work_size(lambda a: [a.size // 8])
@cly.local_work_size([8])
@cly.kernel
def conv(a, b, ret):
    
    i = clrt.get_global_id(0)
    
    w = (b.size-1)/2
    
    start = 0 if (i < w) else i-w
    stop = a.size if (i+w >= a.size) else i+w+1 
    
    sum = c_float(0.)
    
    for k in range(start,stop):
        sum += a[k] * b[k+w-i]
        
    ret[i] = sum
        
def main():
    
    ctx = cl.Context(device_type=cl.Device.CPU)

    a = cly.arange(ctx, 16)
    b = cly.ones(ctx, [3])
    ret = cly.empty_like(a)

    queue = cl.Queue(ctx)
#    
#    with a.map(queue) as foo:
#        print np.asarray(foo)
#
#    with a.map(queue) as foo:
#        print np.asarray(foo)
        
    print conv(queue, a, b, ret)
    
    with ret.map(queue) as foo:
        print np.asarray(foo)
        
#    source = conv.compile(ctx, a=cl.global_memory(c_float), 
#                          b=cl.global_memory(c_float), 
#                          ret=cl.global_memory(c_float),
#                          source_only=source_only)
#    
#    
#    print source
#    print source.argnames
#    print source.argtypes
    
    
if __name__ == '__main__':
    main()
