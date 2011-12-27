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
    
def main_reduce():
    ctx = cl.Context(device_type=cl.Device.GPU)
    
    sum = add.reduce
    
#    for size in range(250, 258):
    size = 1027
        
    a = ca.arange(ctx, size, ctype=cl.cl_int)
    
    result = sum(a)
    
    with a.map() as view:
        print size, view.sum(), result.item()
    
    
def main_ufunc():
    
    ctx = cl.Context(device_type=cl.Device.GPU)
    
    size = 10
    a = ca.arange(ctx, size, ctype=c_float)
    b = ca.arange(ctx, size, ctype=c_float).reshape([size, 1])

    o1 = add(a, b)
    
    with o1.map() as view:
        print view

    with a.map() as view:
        print np.sum(view)

    result = add.reduce(a)
    
    result.queue.finish()
    
    with a.map() as view:
        print view
        print view.sum()
        
    print result.item()
    
if __name__ == '__main__':
    main_reduce()
