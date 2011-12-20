'''
Created on Dec 7, 2011

@author: sean
'''


from contextlib import contextmanager
import numpy as np
import opencl as cl

#import math
#class float2(c_float * 2):
#    
#    @cl_property
#    def length(self):
#        return (self[0]**2.0 + self[1]**2.0) ** .5
#    
#    @length.cl
#    def length(self):
#        return clrt.length(self)
    
class CLArray(cl.DeviceMemoryView):
    
    def __init__(self):
        pass
    
    def __array_init__(self, queue=None):
        
        if queue is None:
            queue = cl.Queue(self.context)
        
        self.queue = queue
        
    def __add__(self, other):
        from ufuncs import add
        
        if isinstance(other, CLArray):
            self.queue.enqueue_wait_for_events(other.queue.marker())
        view = add(self, other)
        
        return view

    def sum(self):
        
        from ufuncs import add
        
        view = add.reduce(self)
        
        return view
    
    @contextmanager
    def map(self):
        with cl.DeviceMemoryView.map(self, self.queue) as view:
            yield np.asarray(view)
    
    def item(self):
        self.queue.finish()
        return cl.DeviceMemoryView.item(self)
    
    def __getitem__(self, item):
        view = cl.DeviceMemoryView.__getitem__(self, item)
        array = self._view_as_this(view)
        array.__array_init__(self.queue)
        return array
    
    def __setitem__(self, item, value):
        from clyther.array.functions import setslice
        setslice(self[item], value)
    
    def reshape(self, shape):
        
        view = cl.DeviceMemoryView.reshape(self, shape)

        array = self._view_as_this(view)
        array.__array_init__(self.queue)
        return array
        
        