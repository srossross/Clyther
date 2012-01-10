'''
Created on Dec 7, 2011

@author: sean
'''


from contextlib import contextmanager
import numpy as np
import opencl as cl

    
class CLArray(cl.DeviceMemoryView):
    
    def __new__(cls, *args):
        return cl.DeviceMemoryView.__new__(cls, *args)

#    def __init__(self, context):
#        pass
    
    def __array_init__(self, context, queue):
        self.acontext = context
        
        if queue is None:
            queue = context.queue
        
        self.queue = queue
        
    def __repr__(self):
        with self.map() as view:
            array_str = str(view)
            return  '%s(%s, ctype=%s, devices=%r)' % (type(self).__name__, array_str, self.ctype, self.context.devices)

    def __str__(self):
        with self.map() as view:
            return  str(view)
        
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
    def map(self, queue=None):
        if queue is None:
            queue = self.queue
        with cl.DeviceMemoryView.map(self, queue) as memview:
            yield  np.asarray(memview)
    
    def copy(self):
        view = cl.DeviceMemoryView.copy(self, self.queue)
        array = self._view_as_this(view)
        array.__array_init__(self.acontext, self.queue)
        return array
    
    def item(self):
        value = cl.DeviceMemoryView.item(self, self.queue)
        self.queue.finish()
        return value
    
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
        
        
