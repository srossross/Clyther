'''
Created on Dec 7, 2011

@author: sean
'''
import clyther as cly
import clyther.runtime as clrt
import opencl as cl
from ctypes import c_uint

from clyther.array.functions import empty, arange
from clyther.array.utils import broadcast_shape
from clyther.array.clarray import CLArray

@cly.global_work_size(lambda group_size: [group_size])
@cly.local_work_size(lambda group_size: [group_size])
@cly.kernel
def reduce_kernel(function, output, input, shared, group_size, initial=0.0):
    
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
        
@cly.global_work_size(lambda a: [a.size])
@cly.kernel
def ufunc_kernel(function, a, b, out):
    gid = clrt.get_global_id(0)
    
    a0 = a[gid]
    b0 = b[gid]
    
    out[gid] = function(a0, b0)
    
class BinaryUfunc(object):
    def __init__(self, device_func):
        self.device_func = device_func
        
    def __call__(self, x, y, out=None, queue=None):
        
        if queue is None:
            queue = x.queue
            
        if not isinstance(x, cl.DeviceMemoryView):
            x = cl.from_host(queue.context, x)
        if not isinstance(y, cl.DeviceMemoryView):
            y = cl.from_host(queue.context, y)
        
        new_shape = broadcast_shape(x.shape, x.shape)
        
        a = cl.broadcast(x, new_shape)
        b = cl.broadcast(y, new_shape)
        
        if out is None:
            out = cl.empty(queue.context, new_shape, x.format)
        
        ufunc_kernel(queue, self.device_func, a, b, out)
        
        
        array = CLArray._view_as_this(out)
        array.__array_init__(queue)
        return array
    
    def reduce(self, x, out=None, initial=0.0, queue=None):
        
        if queue is None:
            queue = x.queue
            
        if not isinstance(x, cl.DeviceMemoryView):
            x = cl.from_host(queue.context, x)
            
            #output, input, shared, group_size, initial=0.0
        size = x.size
        shared = cl.local_memory(x.format, [size])
        
        group_size = size // 2

        if out is None:
            out = empty(queue.context, [1], x.format)

        reduce_kernel(queue, self.device_func, out, x, shared, group_size, initial)
        
        return out


@cly.global_work_size(lambda a: [a.size])
@cly.kernel
def unary_ufunc_kernel(function, a, out):
    gid = clrt.get_global_id(0)
    
    a0 = a[gid]
    out[gid] = function(a0)
    
class UnaryUfunc(object):
    def __init__(self, device_func):
        self.device_func = device_func
        
    def __call__(self, x, out=None, queue=None):
        
        if queue is None:
            queue = x.queue

        if not isinstance(x, cl.DeviceMemoryView):
            x = cl.from_host(queue.context, x)
        
        if out is None:
            out = cl.empty(queue.context, x.shape, x.format)
        
        unary_ufunc_kernel(queue, self.device_func, x, out)
        
        array = CLArray._view_as_this(out)
        array.__array_init__(queue)
        return array
    
def binary_ufunc(device_func):
    return BinaryUfunc(device_func)

def unary_ufunc(device_func):
    return UnaryUfunc(device_func)

