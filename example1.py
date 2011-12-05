'''
Created on Dec 2, 2011

@author: sean
'''
import ctypes

from opencl.copencl import global_memory
import opencl.copencl as cl
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
def generate_sin(a, scale):
    
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
    sin = generate_sin.compile(ctx, a=global_memory(clrt.float2), scale=ctypes.c_float)
    
    a = cl.empty(ctx, [10], 'ff')
    
    queue = cl.Queue(ctx, ctx.devices[0])
    sin(queue, a , 1)
    
    with a.map(queue) as b:
        print np.asarray(b)

def main2():
#    argtypes = {'a':ctypes.c_int, 'b':ctypes.c_int, 'c':funcB}
#    create_kernel_source(funcA, argtypes)

    argtypes = {'a':global_memory(clrt.float2, [10]), 'scale':ctypes.c_float}
    args, source = create_kernel_source(generate_sin, argtypes)
    
    print source
    
    ctx = cl.Context(device_type=cl.Device.CPU)
    program = cl.Program(ctx, source=source)
    
    try:
        program.build()
    except cl.OpenCLException:
        for log in program.logs:
            print log
            print
        raise
    
    print ctx
    
    generate_sin_kernel = program.kernel('generate_sin')
    generate_sin_kernel.argtypes = (global_memory(float2, [10]), ctypes.c_float)
    
    a = cl.empty(ctx, [10], 'ff')
    print a
    
    queue = cl.Queue(ctx, ctx.devices[0])
    generate_sin_kernel(queue, a, 1, global_work_size=[10])

    with a.map(queue) as b:
        print np.asarray(b)
    
#    argtypes = {'f2':float2}
#    create_kernel_source(f2test, argtypes)
    

if __name__ == '__main__':
    main()

