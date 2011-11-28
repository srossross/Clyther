'''
Created on Mar 05, 2010 by GeoSpin Inc
@author: Sean Ross-Ross srossross@geospin.ca
website: www.geospin.ca
'''


#================================================================================#
# Copyright 2009 GeoSpin Inc.                                                     #
#                                                                                # 
# Licensed under the Apache License, Version 2.0 (the "License");                #
# you may not use this file except in compliance with the License.               #
# You may obtain a copy of the License at                                        #
#                                                                                #
#      http://www.apache.org/licenses/LICENSE-2.0                                #
#                                                                                #
# Unless required by applicable law or agreed to in writing, software            #
# distributed under the License is distributed on an "AS IS" BASIS,              #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.       #
# See the License for the specific language governing permissions and            #
# limitations under the License.                                                 #
#================================================================================#

import ctypes

from clyther.api import emulation_runtime
#

#cltype.regiseter(ctype, 'size_t', family='int', as_parameter=None, signed=False)

class opencl_builtin_function(object):
    """
    
    """ 
    def __new__(cls,*args,**kwargs):
#        from clyther.api.emulation import get_emulate
#        if not emulation_runtime.get_emulate( ):
#            raise Exception( "clyther emulation mode has not been initialized with clyther.init( )" )
        
        if hasattr( cls, 'emulate' ):
            return cls.emulate(*args,**kwargs)
        elif hasattr(emulation_runtime, cls.__name__ ):
            func =getattr(emulation_runtime, cls.__name__)
            return func(*args,**kwargs)
        else:
            raise NotImplementedError("emulation of OpenCl native function %r is not defined" %(cls.__name__))
        
        return 1
    
class opencl_builtin_enum(object): pass
#class opencl_iterator(object): pass

class cl_size_t( object ):
    
    @classmethod
    def type_family(cls): 
        return 'int'
    
    @classmethod
    def is_signed(cls): 
        return False
    
    @classmethod
    def cl_sizeof(cls): 
        return ctypes.sizeof( ctypes.c_int )
    
    @classmethod
    def cdef(cls):
        return 'size_t'


class cl_mem_fence_flags( type ):
    
    @classmethod
    def cdef(cls):
        return 'cl_mem_fence_flags'
    
cl_size_t.ctype = cl_size_t    

class get_work_dim( opencl_builtin_function ):
    '''
    
    Returns the number of dimensions in use. 
    This is the value given to the work_dim argument specified in clEnqueueNDRangeKernel.'''
    
    @classmethod
    def get_restype(cls,*args):
        return ctypes.c_uint
    
    restype = ctypes.c_uint
    argtypes = ( )

class get_global_size( opencl_builtin_function ):
    '''
    Returns the number of global work-items specified for dimension identified by dimindx. 
    This value is given by the global_work_size argument to clEnqueueNDRangeKernel. 
    Valid values of dimindx are 0 to get_work_dim() - 1.    
    For other values of dimindx, get_global_size() returns 1.
    '''
    
    restype = cl_size_t
    
    @classmethod
    def get_restype(cls,*args):
        return cl_size_t

    argtypes = ( )

class get_global_id( opencl_builtin_function ):
    """Returns the unique global work-item ID value for dimension identified by dimindx.
    """
    restype = cl_size_t
    @classmethod
    def get_restype(cls,*args):
        return cl_size_t

    argtypes = ( ctypes.c_uint, )
    
class get_local_size( opencl_builtin_function ):
    'Returns the number of local work-items specified in dimension identified by dimindx.'
    restype = cl_size_t
    argtypes = ( )
    
    @classmethod
    def get_restype(cls,*args):
        return cl_size_t


class get_num_groups( opencl_builtin_function ):
    'Returns the number of work-groups that will execute a kernel for dimension identified by dimindx.'
    restype = cl_size_t
    argtypes = ( )
    
    @classmethod
    def get_restype(cls,*args):
        return cl_size_t



class get_local_id( opencl_builtin_function ):
    '''Returns the unique local work-item ID i.e. a work-item within a
     specific work-group for dimension identified by dimindx.'''
    restype = cl_size_t
    argtypes = ( ctypes.c_uint )
    
    @classmethod
    def get_restype(cls,*args):
        return cl_size_t


class get_group_id( opencl_builtin_function ):
    '''
    returns the work-group ID which is a number 
    from 0 .. get_num_groups(dimindx)-1.'''
    restype = cl_size_t
    argtypes = ( ctypes.c_uint )

    @classmethod
    def get_restype(cls,*args):
        return cl_size_t

class barrier( opencl_builtin_function ):
    '''
    All work-items in a work-group executing the kernel on a processor must execute this 
    function before any are allowed to continue execution beyond the barrier. 
    This function must be encountered by all work-items in a work-group executing the kernel.'''
    restype = None
    
    @classmethod
    def get_restype(cls,*args):
        return None

#CLK_LOCAL_MEM_FENCE = 1
class CLK_LOCAL_MEM_FENCE(opencl_builtin_enum):
    ctype = cl_mem_fence_flags
class CLK_GLOBAL_MEM_FENCE(opencl_builtin_enum):
    ctype = cl_mem_fence_flags


#class range(opencl_iterator):
#    pass
