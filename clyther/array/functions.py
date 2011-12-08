'''
Created on Dec 7, 2011

@author: sean
'''
import math
import clyther as cly
import clyther.runtime as clrt
import opencl as cl
from opencl.type_formats import ctype_from_format
from ctypes import c_int, c_float

@cly.global_work_size(lambda a, *_: [a.size])
@cly.kernel
def _arange(a, start, step):
    i = clrt.get_global_id(0)
    a[i] = start + i * step 
 
def arange(ctx, *args, **kwargs):
    '''
    
    '''
    
    start = 0 
    step = 1
    
    if len(args) == 1:
        stop = args[0]  
    elif len(args) == 2:
        start = args[0]
        stop = args[1]
    elif len(args) == 3:
        start = args[0]
        stop = args[1]
        step = args[2]
    else:
        raise Exception("")
    
    size = int(math.ceil((stop - start) / float(step)))
    
    empty = cl.empty(ctx, [size], kwargs.get('ctype', 'f'))
    
    queue = kwargs.get('queue', None)
    if queue is None:
        queue = cl.Queue(ctx, ctx.devices[0]) 

    
    arange_kernel = _arange.compile(ctx, a=cl.global_memory(empty.format), start=c_float, step=c_float)

    arange_kernel(queue, empty, empty.array_info, start, step)
    
    queue.barrier()
    
    return empty
    
    
@cly.global_work_size(lambda a, *_: [a.size])
@cly.kernel
def _ones(a):
    i = clrt.get_global_id(0)
    a[i] = 1 

def ones(ctx, shape, ctype='f', queue=None):
    empty = cl.empty(ctx, shape, ctype)
    _ones_kernel = _ones.compile(ctx, a=cl.global_memory(empty.format))
    
    if queue is None: queue = cl.Queue(ctx) 

    _ones_kernel(queue, empty, empty.array_info)
    
    queue.barrier()
    
    return empty

def empty_like(A):
    return cl.empty(A.context, A.shape, A.format)
    
    
    