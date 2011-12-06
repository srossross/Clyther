'''
Created on Dec 2, 2011

@author: sean
'''
import ctypes

import opencl as cl
import numpy as np
import clyther.runtime as clrt
from clyther.runtime import float2
from clyther.cly_kernel import kernel, global_work_size

source = """

__kernel void generate_sin(__global float2* a, float scale)
{
    int id = get_global_id(0);
    int n = get_global_size(0);
    float r = (float)id / (float)n;
    
    a[id].x = id;
    a[id].y = native_sin(r) * scale;
}
"""
    
def f2test(f2):
    
    f2.x = f2.y

@global_work_size(lambda a, scale: [a.size])
@kernel
def generate_sin(a, scale=1):
    
    id = clrt.get_global_id(0)
    n = clrt.get_global_size(0)
    r = id / ctypes.c_float(n)
    
    a[id].x = id
    a[id].y = clrt.native_sin(r) * scale;
    
def funcB(x, y):
    
    return x * y

def funcA(a, b, c=funcB):
    y = int()
    z = c(a, y=y) + b
    return

def main():
    ctx = cl.Context(device_type=cl.Device.CPU)
    
    sin = generate_sin.compile(ctx, a=cl.global_memory(clrt.float2), scale=ctypes.c_float)
    
    a = cl.empty(ctx, [10], 'ff')
    
    queue = cl.Queue(ctx, ctx.devices[0])
    
    sin(queue, a=a)
    
    with a.map(queue) as b:
        print np.asarray(b)

if __name__ == '__main__':
    main()

