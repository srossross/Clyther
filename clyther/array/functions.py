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

from clyther.array.clarray import CLArray
from clyther.array.utils import broadcast_shape
from clyther.array.array_context import CLArrayContext as ArrayContext

@cly.global_work_size(lambda arr, *_: arr.shape)
@cly.kernel
def setslice_kernel(arr, value):
    index = cl.cl_uint4(clrt.get_global_id(0), clrt.get_global_id(1), clrt.get_global_id(2), 0)
    
    
    a_strides = index * arr.strides
    aidx = arr.offset + a_strides.x + a_strides.y + a_strides.z
    
    v_strides = index * value.strides
    vidx = value.offset + v_strides.x + v_strides.y + v_strides.z

    arr[aidx] = value[vidx]


@ArrayContext.method('setslice')
def setslice(context, arr, value):
    
    if not isinstance(value, cl.DeviceMemoryView):
        value = context.asarray(value)
       
    if value.queue != arr.queue:
        arr.queue.enqueue_wait_for_events(value.queue.marker())
         
    value = cl.broadcast(value, arr.shape)
    
    kernel = setslice_kernel.compile(context, arr=cl.global_memory(arr.format, flat=True),
                                     value=cl.global_memory(value.format, flat=True),
                                     cly_meta='setslice')
    
    return kernel(arr.queue, arr, arr.array_info, value, value.array_info)

@ArrayContext.method('asarray')
def asarray(ctx, other, queue=None, copy=True):
    
    if not isinstance(other, cl.DeviceMemoryView):
        other = cl.from_host(ctx, other, copy=copy)
        
    array = CLArray._view_as_this(other)
    array.__array_init__(ctx, queue)
    
    return array

@ArrayContext.method('zeros')
def zeros(context, shape, ctype='f', cls=CLArray, queue=None):
    
    out = context.empty(shape=shape, ctype=ctype, queue=queue)
    
    setslice(context, out, 0)
    
    return out

@ArrayContext.method('empty')
def empty(context, shape, ctype='f', cls=CLArray, queue=None):
    out = cl.empty(context, shape, ctype)
    
    array = cls._view_as_this(out)
    array.__array_init__(context, queue)
    return array

@ArrayContext.method('empty_like')
def empty_like(context, A):
    return context.empty(A.shape, A.format, cls=type(A), queue=A.queue)
    

@cly.global_work_size(lambda a, *_: [a.size])
@cly.kernel
def _arange(a, start, step):
    i = clrt.get_global_id(0)
    a[i] = start + step * i 
 
@ArrayContext.method('arange')
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
    
    queue = kwargs.get('queue', None)
    if queue is None:
        queue = cl.Queue(ctx) 

    arr = empty(ctx, [size], ctype=ctype, queue=queue)
    
    _arange(queue, arr, start, step)
    
    return arr

@cly.global_work_size(lambda a, *_: [a.size])
@cly.kernel
def _linspace(a, start, stop):
    i = clrt.get_global_id(0)
    gsize = clrt.get_global_size(0)
    a[i] = i * (stop - start) / gsize 
 
@ArrayContext.method('linspace')
def linspace(ctx, start, stop, num=50, ctype='f', queue=None):
    '''
    
    '''
    
    if queue is None:
        queue = cl.Queue(ctx) 

    arr = empty(ctx, [num], ctype=ctype, queue=queue)
    _linspace(queue, arr, float(start), float(stop))
    
    return arr
    
    
    
def main():
    
    import opencl as cl
    ctx = cl.Context(device_type=cl.Device.GPU)
    a = arange(ctx, 10.0)

if __name__ == '__main__':
    main()
        
