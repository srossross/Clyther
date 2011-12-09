'''
Created on Dec 8, 2011

@author: sean
'''
import opencl as cl
from uuid import uuid1
from collections import OrderedDict

class EventRecord(object):
    def __init__(self, uuid):
        self.uuid = uuid
        
    def set_event(self, event):
        self._event = event
    
class QueueRecord(object):
    def __init__(self, context):
        self._context = context
        self.operations = OrderedDict()
        self.events = {}
        
    @property
    def context(self):
        return self._context
    
    def set_kernel_args(self, queue, cl_kernel, kernel_args):
        cl_kernel.set_args(**kernel_args)
    
    def enqueue_set_kernel_args(self, cl_kernel, kernel_args):
        
        uuid = uuid1()
        args = cl_kernel, kernel_args.copy()
        self.operations[uuid] = self.set_kernel_args, args
        
        self.events[uuid] = EventRecord(uuid)
        return self.events[uuid]
    
    def enqueue_nd_range_kernel(self, kernel, work_dim, global_work_size, global_work_offset=None, local_work_size=None, wait_on=()):
        
        uuid = uuid1()
        args = kernel, work_dim, global_work_size, global_work_offset, local_work_size, wait_on
        self.operations[uuid] = cl.Queue.enqueue_nd_range_kernel, args
        
        self.events[uuid] = EventRecord(uuid)
        return self.events[uuid]
        
    def enqueue(self, queue):
        for uuid, (func, args) in self.operations.viewitems():
            event = func(queue, *args)
            self.events[uuid].set_event(event)
