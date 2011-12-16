'''
Created on Dec 11, 2011

@author: sean
'''
import clyther as cly
import clyther.array as ca
import clyther.runtime as clrt
import opencl as cl
from ctypes import c_float, c_int, c_uint
import numpy as np
import ctypes
from meta.decompiler import decompile_func
from meta.asttools.visitors.pysourcegen import python_source


def main():
    
    ctx = cl.Context(device_type=cl.Device.GPU)
    queue = cl.Queue(ctx)
    
    host_init = np.arange(8, dtype=c_float) + 1
    device_input = cl.from_host(ctx, host_init)
    
    output = ca.reduce(queue, lambda a, b: a + b, device_input)
    
    print "-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- "
    print "data:", host_init
    print "-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- "
    print "host   sum:", host_init.sum()
    
    with output.map(queue) as view:
        print "device sum:", np.asarray(view).item()

    output = ca.reduce(queue, lambda a, b: a * b, device_input, initial=1.0)
    
    print "host   product:", host_init.prod()
    
    with output.map(queue) as view:
        print "device product:", np.asarray(view).item()


if __name__ == '__main__':
    main()
