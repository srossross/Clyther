'''
Created on Dec 12, 2011

@author: sean
'''
import clyther as cly
from clyther.array.ufuncs import binary_ufunc, ufunc_kernel 
from clyther.array.blitz import blitz 
import opencl as cl
from ctypes import c_float
import numpy as np

@binary_ufunc
def add(a, b): 
    return a + b


def main():
    ctx = cl.Context(device_type=cl.Device.GPU)
    queue = cl.Queue(ctx)
    
    npa = np.arange(1.0 * 12.0, dtype=c_float)
    
    a = cl.from_host(ctx, npa)
    
    l = lambda: a[1:] + a[:-1] + 1
    
    out = cly.empty_like(a[:-1])
    blitz(queue, lambda: a[1:] + a[:-1] + 1, out=out)
    
    print npa[1:] + npa[:-1]
    
    with out.map(queue) as view:
        print np.asarray(view)
    #Broadcasting rules
    
    
    
def main_ufunc():
    
    ctx = cl.Context(device_type=cl.Device.GPU)
    queue = cl.Queue(ctx)
    
    npa = np.arange(1.0 * 12.0, dtype=c_float)
    
    a = cl.from_host(ctx, npa)
    
    #Broadcasting rules
    o1 = add(queue, a[::2], 3)
    
    with o1.map(queue) as view:
        print np.asarray(view)

    result = add.reduce(queue, a)
    queue.finish()
    
    print float(result)
    
if __name__ == '__main__':
    main_ufunc()
