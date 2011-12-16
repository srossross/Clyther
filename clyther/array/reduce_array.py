'''
Created on Dec 15, 2011

@author: sean
'''
import clyther as cly
import clyther.runtime as clrt
import opencl as cl
from ctypes import c_float, c_int, c_uint
import numpy as np
import ctypes
from meta.decompiler import decompile_func
from meta.asttools.visitors.pysourcegen import python_source

@cly.global_work_size(lambda group_size: [group_size])
@cly.local_work_size(lambda group_size: [group_size])
@cly.kernel
def cl_reduce(function, output, input, shared, group_size, initial=0.0):
    
    i = c_uint(0)
    
    lid = clrt.get_local_id(0)

    gid = clrt.get_group_id(0)
    gsize = clrt.get_num_groups(0)

    gs2 = group_size * 2

    stride = gs2 * gsize

    i = gid * gs2 + lid

    shared[lid] = initial

    while i < input.size:
        shared[lid] = function(shared[lid], input[i])
        shared[lid] = function(shared[lid], input[i + group_size])
         
        i += stride
        
        clrt.barrier(clrt.CLK_LOCAL_MEM_FENCE)
        
    #The clyther compiler identifies this loop as a constant a
    # unrolls this loop 
    for cgs in [512 , 256, 128, 64, 32, 16, 8, 4, 2]:
        
        #acts as a preprocessor define #if (group_size >= 512) etc. 
        if group_size >= cgs:
            
            if lid < cgs / 2:
                shared[lid] = function(shared[lid] , shared[lid + cgs / 2])
                 
            clrt.barrier(clrt.CLK_LOCAL_MEM_FENCE)
            
    if lid == 0:
        output[gid] = shared[0]

def reduce(queue, function, input, initial=0.0):
    '''
    reduce(queue, function, sequence[, initial]) -> value
    
    Apply a function of two arguments cumulatively to the items of a sequence,
    from left to right, so as to reduce the sequence to a single value.
    For example, reduce(lambda x, y: x+y, [1, 2, 3, 4, 5]) calculates
    ((((1+2)+3)+4)+5).  If initial is present, it is placed before the items
    of the sequence in the calculation, and serves as a default when the
    sequence is empty.

    '''

    size = input.size
    shared = cl.local_memory(input.format, [size])
    output = cl.empty(queue.context, [1], input.format)
    
    group_size = size // 2
    
    cl_reduce(queue, function, output, input , shared, group_size, initial)
    
    return output
