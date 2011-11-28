

import threading
import numpy as np
import clyther.api.emulation_runtime as clrt
import inspect
from clyther.api.util import create_local_dict
import pdb
from clyther.api.kernelfunction import TaskFunction, KernelFunction,OpenCLFunctionFactory


__EMULATION_IS_SET__ = False

def set_emulate( value ):
    global __EMULATION_IS_SET__
    __EMULATION_IS_SET__ = bool(value)

def get_emulate( ):
    global __EMULATION_IS_SET__
    return __EMULATION_IS_SET__
    

    
print_lock = threading.Lock()

class WorkItem(threading.Thread):
    
    def __init__( self,func, args, kwargs, global_idx, global_work_size, local_idx,local_work_size, group_idx, num_groups ):
        
        self.global_work_size = global_work_size
        self.local_work_size = local_work_size
        self.global_idx = global_idx
        self.local_idx = local_idx
        self.local_work_size = local_work_size
        self.group_idx = group_idx
        self.num_groups = num_groups
        
        self.func = func
        self.args = args
        self.kwargs = kwargs
        
        name = "%s<<<%r, %r>>>" %(self.func.__name__, self.global_idx, self.local_idx)
        threading.Thread.__init__(self, name=name )
    
    def run(self):
        
        clrt._local.global_id = self.global_idx
        clrt._local.local_id = self.local_idx
        clrt._local.group_id = self.group_idx
        clrt._local.global_work_size = self.global_work_size
        clrt._local.local_work_size = self.local_work_size
        clrt._local.num_groups = self.num_groups
        
        self.func( *self.args, **self.kwargs )
    

def add( a,b ):
    return a+b 

class EmulateKernelFunction(object):
    
    def __init__( self, func ):
        self.func = func
        
        if hasattr(func, '__cl_bind__'):
            self.__cl_bind__ =  func.__cl_bind__ 
        else:
            self.__cl_bind__ = ( )
        

    def eval_bind(self,name,bind_expr, arglocals ):
        
        if isinstance(bind_expr, str):
            return eval( bind_expr , globals( ), arglocals )
        elif inspect.isroutine( bind_expr ):
            return bind_expr( **arglocals )
        else:
            return bind_expr
        
    
    def __call__(self, *args, **kwargs):
        
        
        argspec = inspect.getargspec(self.func)
        
        arglocals = create_local_dict( argspec, args, kwargs )

#        arglocals = create_local_dict(  ,{})
        
        for name,bind_expr in self.__cl_bind__:
            if name not in kwargs:
                kwargs[name] = self.eval_bind( name, bind_expr, arglocals )
                arglocals[name] = kwargs[name]
#            if item in 
         
        global_work_size = kwargs.pop('global_work_size',[1,1,1])
        local_work_size = kwargs.pop('local_work_size',[1,1,1])
        
    
        if not isinstance( global_work_size, (list,tuple) ):
            global_work_size = [global_work_size,1,1]
        elif len( global_work_size ) < 3:
            global_work_size = list(global_work_size + [1] * (3-len( global_work_size ) ))
    
        if not isinstance( local_work_size, (list,tuple) ):
            local_work_size = [local_work_size,1,1]
        elif len( local_work_size ) < 3:
            local_work_size = list(local_work_size + [1] * (3-len( local_work_size ) ))
        
        blocksize = np.divide( global_work_size, local_work_size )
        
#        print "blocksize,local_work_size",blocksize,local_work_size
#        print "local_work_size",local_work_size
        for block_global_idx in np.ndindex( *blocksize ):
            
            workitems = []
            for local_ixd in np.ndindex( *local_work_size ):
                global_idx = tuple( np.add( np.multiply(block_global_idx,local_work_size) , local_ixd ))
#                print "local_ixd ,global_idx",block_global_idx, local_ixd ,global_idx
                
                wi = WorkItem( self.func, args, kwargs , 
                               global_idx, global_work_size, 
                               local_ixd, local_work_size,
                               block_global_idx, blocksize )
                wi.start( )
                workitems.append(wi)
                
            for wi in workitems:
                wi.join( )
        




def emulate( func_or_kernel ,*args, **kwargs):
    
    if inspect.isfunction( func_or_kernel ):
        function = func_or_kernel
        kernel_type = getattr( function, '__kernel_type__', 'kernel' )
    elif isinstance( func_or_kernel, OpenCLFunctionFactory):
        function = func_or_kernel.func
        kernel_type = func_or_kernel._ftype
        
    elif isinstance( func_or_kernel, TaskFunction):
        
        function = func_or_kernel.func
        kernel_type ='task'
    elif isinstance( func_or_kernel, KernelFunction):
        function = func_or_kernel.func
        kernel_type ='kernel'
    else:
        raise Exception( "don't know how to emulate %r. Expected function or device object" %(func_or_kernel,))
            
        
    if kernel_type in ['task','device']:
        return function( *args, **kwargs ) 
    else:
        return EmulateKernelFunction( function )( *args, **kwargs )


 