'''
Created on Dec 7, 2011

@author: sean
'''

import clyther as cly
import clyther.runtime as clrt
import opencl as cl
from ctypes import c_float, c_int
import numpy as np
import ctypes

@cly.global_work_size(lambda a: [a.size])
@cly.kernel
def setslice(a, value):
    
    i = clrt.get_global_id(0)
    a[i] = value
    
    clrt.barrier(clrt.CLK_GLOBAL_MEM_FENCE)

@cly.global_work_size(lambda a: [a.size])
@cly.kernel
def conv(a, b, ret):
    
    i = clrt.get_global_id(0)
    ret[i] = b.size
    
def main():
    
    ctx = cl.Context(device_type=cl.Device.GPU)

    ret = cl.empty(ctx, [16], 'l')

    queue = cl.Queue(ctx)
        
        
    print setslice.compile(ctx, a=cl.global_memory('l'), value=c_int, source_only=True)
    
#    print setslice(queue, ret[::2], c_int(6))
#    print setslice(queue, ret[1::2], c_int(5))
    
    with ret.map(queue) as foo:
        print np.asarray(foo)


#    kernel = conv._cache.values()[0].values()[0]
    
#    print kernel.program.source
    
    
if __name__ == '__main__':
    main()
