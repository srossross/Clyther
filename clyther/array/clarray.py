'''
Created on Dec 7, 2011

@author: sean
'''


from contextlib import contextmanager
import numpy as np
import opencl as cl
from ufuncs import add, multiply, binary_ufunc

class CLArray(cl.DeviceMemoryView):
    
    def __init__(self):
        pass
    
    def __array_init__(self, queue=None):
        
        if queue is None:
            queue = cl.Queue(self.context)
        
        self.queue = queue
        
    def __add__(self, other):
        
        if isinstance(other, CLArray):
            self.queue.enqueue_wait_for_events(other.queue.marker())
        
        view = add(self.queue, self, other)
        
        return view
    
    @contextmanager
    def map(self):
        with cl.DeviceMemoryView.map(self, self.queue) as view:
            yield np.asarray(view)
            
