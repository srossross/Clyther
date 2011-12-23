'''
Created on Dec 17, 2011

@author: sean
'''

import opencl as cl
import new

class CLArrayContext(cl.Context):
    '''
    classdocs
    '''
    
    def __init__(self, *args, **kwargs):
        cl.Context.__init__(self, *args, **kwargs)
        
        self._queue = cl.Queue(self)
    
    @property
    def queue(self):
        return self._queue
    

    @classmethod
    def method(cls, name):
        def decoator(func):
            meth = new.instancemethod(func, None, cls)
            setattr(cls, name, meth)
            return func
        return decoator
    
    @classmethod
    def func(cls, func):
        if isinstance(func, str):
            name = func
            def decoator(func):
                setattr(cls, name, func)
                return func
            return decoator
        else:
            setattr(cls, func.func_name, func)
            return func
