'''
Created on Dec 8, 2011

@author: sean
'''
import opencl as cl
from uuid import uuid1
from collections import OrderedDict

class EventRecord(object):
    def __init__(self, uuid, operation, *args, **kwargs):
        self._uuid = uuid
        self._valid = False
        self._operation = operation
        self.args = args
        self.kwargs = kwargs
        self.kenel_args = None
        
    @property
    def uuid(self):
        return self._uuid
    
    def set_event(self, event):
        self._event = event
        self.validate()
    
    def invalidate(self):
        self._valid = False
        
    def validate(self):
        self._valid = True

    def valid(self):
        return self._valid
    
    def set_kernel_args(self, kernel, *args, **kwargs):
        self.kenel_args = kernel, args, kwargs
        
    def enqueue(self, queue):
        if self.kenel_args:
            kernel, args, kwargs = self.kenel_args
            kernel.set_args(*args, **kwargs)
            
        event = self._operation(queue, *self.args, **self.kwargs)
        self.set_event(event)
        
    
class QueueRecord(object):
    def __init__(self, context, queue=None):
        self._context = context
        self.events = []
        
        if queue is None:
            queue = cl.Queue(context)
            
        self.queue = queue
        
    @property
    def context(self):
        return self._context
    
    def set_kernel_args(self, queue, cl_kernel, kernel_args):
        cl_kernel.set_args(**kernel_args)
    
    def enqueue_set_kernel_args(self, cl_kernel, kernel_args):
        
        uuid = uuid1()
        args = cl_kernel, kernel_args.copy()
        self.operations[uuid] = self.set_kernel_args, args
        
        self.events[uuid] = EventRecord(uuid,)
        return self.events[uuid]
    
    def enqueue_nd_range_kernel(self, kernel, work_dim, global_work_size, global_work_offset=None, local_work_size=None, wait_on=()):
        
        uuid = uuid1()
        args = kernel, work_dim, global_work_size, global_work_offset, local_work_size, wait_on
        self.operations[uuid] = cl.Queue.enqueue_nd_range_kernel, args
        
        self.events[uuid] = EventRecord(uuid, cl.Queue.enqueue_nd_range_kernel,
                                        kernel, work_dim, global_work_size, global_work_offset,
                                        local_work_size, wait_on)
        return self.events[uuid]
        
    def enqueue(self, queue=None):
        
        if queue is None:
            queue = self.queue

        for revent in self.events:
            if not revent.valid():
                revent.enqueue(queue)
                




