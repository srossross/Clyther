'''
Created on Dec 12, 2011

@author: sean
'''
import clyther as cly
import  clyther.array as ca 
import opencl as cl
from ctypes import c_float
import numpy as np

@ca.binary_ufunc
def add(a, b): 
    return a + b


def main():
    ctx = cl.Context(device_type=cl.Device.GPU)
    queue = cl.Queue(ctx)
    
    npa = np.arange(1.0 * 12.0, dtype=c_float)
    a = ca.arange(ctx, 12, ctype=c_float)
    
    out = ca.empty_like(a[:])
    output = cl.broadcast(out, a[:].shape)
    
    ca.blitz(queue, lambda: a[:] + a[:] + 1, out=output)
    
    print npa[1:] + npa[:-1]
    
    with out.map() as view:
        print view
    
def main_ufunc():
    
    ctx = cl.Context(device_type=cl.Device.GPU)
    queue = cl.Queue(ctx)
    
    a = ca.arange(ctx, 12, ctype=c_float)
#    npa = np.arange(1.0 * 12.0, dtype=c_float)
#    
#    a = cl.from_host(ctx, npa)
    
    #Broadcasting rules
    o1 = add(a[::2], 3)
    
    with o1.map() as view:
        print view

    result = add.reduce(a)
    
    queue.finish()
    
    print float(result)
    
if __name__ == '__main__':
    main()
