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

    def queue(self, *args, **kwargs):
        return cl.Queue(self, *args, **kwargs)
    

    @classmethod
    def method(cls, func):
        meth = new.instancemethod(func, None, cls)
        setattr(cls, func.func_name, meth)
        return func
    
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
