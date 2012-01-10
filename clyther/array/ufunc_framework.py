'''
Created on Dec 7, 2011

@author: sean
'''
import clyther as cly
import clyther.runtime as clrt
import opencl as cl
from ctypes import c_uint

from clyther.array.utils import broadcast_shape
from clyther.array.clarray import CLArray

@cly.global_work_size(lambda group_size: [group_size])
@cly.local_work_size(lambda group_size: [group_size])
@cly.kernel
def reduce_kernel(function, output, array, shared, group_size):
    
    lid = clrt.get_local_id(0)
    gid = clrt.get_group_id(0)

    stride = group_size
    
    i = c_uint(gid * group_size + lid)
    
    igs = i + group_size
    
    tmp = array[i]
    
    if igs < array.size:
        tmp = function(tmp, array[igs])
        
    i += stride*2
        
    while i < array.size:
        tmp = function(tmp, array[i])
        i += stride
        
    shared[lid] = tmp
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
        
@cly.global_work_size(lambda a: a.shape)
@cly.kernel
def ufunc_kernel(function, a, b, out):
    
    index = cl.cl_uint4(clrt.get_global_id(0), clrt.get_global_id(1), clrt.get_global_id(2), 0)
    
    
    a_strides = index * a.strides
    aidx = a.offset + a_strides.x + a_strides.y + a_strides.z
    
    b_strides = index * b.strides
    bidx = b.offset + b_strides.x + b_strides.y + b_strides.z

    out_strides = index * out.strides
    oidx = out.offset + out_strides.x + out_strides.y + out_strides.z
        
    a0 = a[aidx]
    b0 = b[bidx]
    
    out[oidx] = function(a0, b0) 
        


class BinaryUfunc(object):
    def __init__(self, device_func):
        self.device_func = device_func
        
    def __call__(self, context, x, y, out=None, queue=None):
        
        if queue is None:
            if hasattr(x,'queue'):
                queue = x.queue
            elif hasattr(y,'queue'):
                queue = y.queue
            else:
                queue = context.queue
            
            
        if not isinstance(x, cl.DeviceMemoryView):
            x = context.asarray(x)
        if not isinstance(y, cl.DeviceMemoryView):
            y = context.asarray(y)
        
        if y.queue != queue:
            queue.enqueue_wait_for_events(y.queue.marker())
        if x.queue != queue:
            queue.enqueue_wait_for_events(x.queue.marker())
        
        new_shape = broadcast_shape(x.shape, y.shape)
        
        a = cl.broadcast(x, new_shape)
        b = cl.broadcast(y, new_shape)
        
        if out is None:
            out = context.empty(shape=new_shape, ctype=x.format, queue=queue)
        
#        kernel_source = ufunc_kernel._compile(queue.context, function=self.device_func,
#                                      a=cl.global_memory(a.format, flat=True),
#                                      b=cl.global_memory(b.format, flat=True),
#                                      out=cl.global_memory(out.format, flat=True), source_only=True)

        kernel = ufunc_kernel.compile(context, function=self.device_func,
                                      a=cl.global_memory(a.format, flat=True),
                                      b=cl.global_memory(b.format, flat=True),
                                      out=cl.global_memory(out.format, flat=True), 
                                      cly_meta=self.device_func.func_name)
        

        kernel(queue, a, a.array_info, b, b.array_info, out, out.array_info)
        
        array = CLArray._view_as_this(out)
        array.__array_init__(context, queue)
        return array
    
    def reduce(self, context, x, out=None, initial=0.0, queue=None):
        
        if queue is None:
            queue = x.queue
        
        if not isinstance(x, cl.DeviceMemoryView):
            x = cl.from_host(queue.context, x)
            
        #output, input, shared, group_size, initial=0.0
        size = x.size
        shared = cl.local_memory(x.ctype, ndim=1, shape=[size])
        
        group_size = size // 2
        for item in [2, 4, 8, 16, 32, 64, 128, 256, 512]:
            if group_size < item:
                group_size = item // 2
                break
        else:
            group_size = 512
        
        if out is None:
            out = cl.empty(queue.context, [1], x.format)
        
        kernel = reduce_kernel.compile(queue.context,
                                       function=self.device_func,
                                       output=cl.global_memory(out.ctype, flat=True),
                                       array=cl.global_memory(x.ctype, flat=True),
                                       shared=shared,
                                       group_size=cl.cl_uint,
                                       cly_meta=self.device_func.func_name)
        
        max_wgsize = kernel.work_group_size(queue.device)
        
        group_size = min(max_wgsize, group_size)
        
        kernel(queue, out, out.array_info, x, x.array_info, shared, shared.local_info, group_size)
#        reduce_kernel(queue, self.device_func, out, x, shared, group_size)
#        reduce_kernel(queue, self.device_func, out, x, shared, group_size)
        
        array = CLArray._view_as_this(out)
        array.__array_init__(context, queue)
        return array


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

