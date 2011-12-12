'''
Created on Dec 11, 2011

@author: sean
'''
import clyther as cly
import clyther.runtime as clrt
import opencl as cl
from ctypes import c_float, c_int
import numpy as np
import ctypes

@cly.global_work_size(lambda : [1])
#@cly.global_work_size([1])
#@cly.local_work_size(lambda group_size: [group_size])
@cly.kernel
def reduce(shared, initial=c_float(0.0)):
    lid = clrt.get_local_id(0)
    shared[lid] = initial

def main():
    
    ctx = cl.Context()
    
    queue = cl.Queue(ctx)
#    print reduce.compile(ctx, shared=cl.local_memory('f'), initial=c_float, source_only=True)

    local_mem = cl.local_memory('f', [10])
    print reduce(queue, local_mem, initial=c_int(1))


if __name__ == '__main__':
    main()
