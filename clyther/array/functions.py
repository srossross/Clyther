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

from clyther.array import CLArray

def asarray(other, ctx, queue=None, copy=True):
    
    if not isinstance(other, cl.DeviceMemoryView):
        other = cl.from_host(ctx, other, copy=copy)
        
    array = CLArray._view_as_this(other)
    array.__array_init__(queue)
    
    return array

def empty(context, shape, ctype):
    out = cl.empty(context, shape, 'f')
    array = CLArray._view_as_this(out)
    array.__array_init__()
    return array

@cly.global_work_size(lambda a, *_: [a.size])
@cly.kernel
def _arange(a, start, step):
    i = clrt.get_global_id(0)
    a[i] = start + step * i 
 
def arange(ctx, *args, **kwargs):
    '''
    
    '''
    start = 0.0
    step = 1.0
    
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
        raise Exception("wrong number of arguments expected between 2-4 (got %i)" % (len(args) + 1))
    
    size = int(math.ceil((stop - start) / float(step)))
    
    ctype = kwargs.get('ctype', 'f')
    empty = cl.empty(ctx, [size], ctype=ctype)
    print empty.ctype
    
    queue = kwargs.get('queue', None)
    if queue is None:
        queue = cl.Queue(ctx) 

    print "start, step", start, step
    _arange(queue, empty, start, step)
    
    print _arange._cache.values()[0].values()[0].program.source
    
    queue.finish()
    
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
    
    
    
def main():
    
    import opencl as cl
    ctx = cl.Context(device_type=cl.Device.GPU)
    a = cly.arange(ctx, 10.0)

if __name__ == '__main__':
    main()
        
