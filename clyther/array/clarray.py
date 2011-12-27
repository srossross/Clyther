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
    
    def __new__(cls, *args):
        return cl.DeviceMemoryView.__new__(cls, *args)

#    def __del__(self, *args):
#        print "del CLArray"
    
         
    def __init__(self, context):
        pass
    
    def __array_init__(self, context, queue):
        self.acontext = context
        
        if queue is None:
            queue = context.queue
        
        self.queue = queue
        
    def __add__(self, other):
        view = self.acontext.add(self, other)
        
        return view

    def __radd__(self, other):
        view = self.acontext.add(other, self)
        
        return view
    
    def __mul__(self, other):
        view = self.acontext.multiply(self, other)
        
        return view

    def __rmul__(self, other):
        view = self.acontext.multiply(other, self)
        
        return view

    def __sub__(self, other):
        view = self.acontext.subtract(self, other)
        
        return view
    
    def __rsub__(self, other):
        view = self.acontext.subtract(other, self)
        
        return view
    
    def __pow__(self, other):
        view = self.acontext.power(self, other)
        return view

    def sum(self):
        
        from ufuncs import add
        
        view = add.reduce(self)
        
        return view
    
    @contextmanager
    def map(self):
        with cl.DeviceMemoryView.map(self, self.queue) as view:
            yield np.asarray(view)
    
    def copy(self):
        view = cl.DeviceMemoryView.copy(self, self.queue)
        array = self._view_as_this(view)
        array.__array_init__(self.acontext, self.queue)
        return array
    
    def item(self):
        self.queue.finish()
        return cl.DeviceMemoryView.item(self)
    
    def __getitem__(self, item):
        view = cl.DeviceMemoryView.__getitem__(self, item)
        array = self._view_as_this(view)
        array.__array_init__(self.acontext, self.queue)
        return array
    
    def __setitem__(self, item, value):
        self.acontext.setslice(self[item], value)
    
    def reshape(self, shape):
        
        view = cl.DeviceMemoryView.reshape(self, shape)

        array = self._view_as_this(view)
        array.__array_init__(self.acontext, self.queue)
        return array
        
        
