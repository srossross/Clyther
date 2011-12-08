'''
Created on Dec 2, 2011

@author: sean
'''
import ctypes

import opencl as cl
import numpy as np
import clyther.runtime as clrt
import clyther as cly
from ctypes import c_float
    
def f2test(f2):
    
    f2.x = f2.y

@cly.global_work_size(lambda a, scale: [a.size])
@cly.kernel
def generate_sin(a, scale=c_float(1)):
    
    gid = clrt.get_global_id(0)
    n = clrt.get_global_size(0)
    r = gid / ctypes.c_float(n)
    
    a[gid].x = gid
    a[gid].y = clrt.native_sin(r) * scale;
    
def funcB(x, y):
    
    return x * y

def funcA(a, b, c=funcB):
    y = int()
    z = c(a, y=y) + b
    return

def main():
    ctx = cl.Context(device_type=cl.Device.CPU)
    
    a = cl.empty(ctx, [10], '(2)f')
    
    queue = cl.Queue(ctx, ctx.devices[0])
    
    generate_sin(queue, a=a)
    
    with a.map(queue) as b:
        print np.asarray(b)

if __name__ == '__main__':
    main()

