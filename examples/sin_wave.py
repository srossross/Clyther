'''
Created on Dec 12, 2011

@author: sean
'''
from ctypes import *
import clyther as cly
import opencl as cl
import clyther.runtime as clrt
import numpy as np

@cly.global_work_size(lambda a: [a.size])
@cly.kernel
def generate_sin(a):
    gid = clrt.get_global_id(0)
    n = clrt.get_global_size(0)
    r = c_float(gid) / c_float(n)
    
    x = r * c_float(16.0) * c_float(3.1415)
    
    a[gid].x = c_float(r * 2.0) - c_float(1.0)
    a[gid].y = clrt.native_sin(x)
    
    
def main():
    ctx = cl.Context()
    a = cl.empty(ctx, [256], cly.float2)
    
    queue = cl.Queue(ctx)
    
    generate_sin(queue, a)
    
    with a.map(queue) as view:
        array = np.asarray(view)
        print array
        
if __name__ == '__main__':
    main()


[('x','float'),('y','float')]