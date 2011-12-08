'''
Created on Dec 8, 2011

@author: sean
'''
import opencl as cl
from uuid import uuid1

class EventRecord(object):
    def __init__(self, uuid):
        pass
    
class QueueRecord(object):
    def __init__(self, context):
        self._context = context
        self.operations = []
        
    @property
    def context(self):
        return self._context
    
    def set_kernel_args(self, queue, cl_kernel, kernel_args):
        cl_kernel.set_args(**kernel_args)
    
    def enqueue_set_kernel_args(self, cl_kernel, kernel_args):
        
        operation = (self.set_kernel_args, (cl_kernel, kernel_args.copy()))
        self.operations.append(operation)
    
    def enqueue_nd_range_kernel(self, kernel, work_dim, global_work_size, global_work_offset=None, local_work_size=None, wait_on=()):
        
        args = kernel, work_dim, global_work_size, global_work_offset, local_work_size, wait_on
        operation = (cl.Queue.enqueue_nd_range_kernel, args) 
        self.operations.append(operation)
        
    def enqueue(self, queue):
        for func, args in self.operations:
            func(queue, *args)
