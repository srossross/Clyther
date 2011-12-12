'''
Created on Dec 4, 2011

@author: sean
'''

import ctypes
from clyther.rttt import RuntimeFunction, RuntimeType

get_global_id = RuntimeFunction('get_global_id', ctypes.c_int, ctypes.c_int)
get_group_id = RuntimeFunction('get_group_id', ctypes.c_int, ctypes.c_int)
get_local_id = RuntimeFunction('get_local_id', ctypes.c_int, ctypes.c_int)
get_num_groups = RuntimeFunction('get_num_groups', ctypes.c_int, ctypes.c_int)
get_global_size = RuntimeFunction('get_global_size', ctypes.c_int, ctypes.c_int)


cl_mem_fence_flags = RuntimeType('cl_mem_fence_flags')

CLK_LOCAL_MEM_FENCE = cl_mem_fence_flags('CLK_LOCAL_MEM_FENCE') 
CLK_GLOBAL_MEM_FENCE = cl_mem_fence_flags('CLK_GLOBAL_MEM_FENCE') 

barrier = RuntimeFunction('barrier', None, cl_mem_fence_flags)

native_sin = RuntimeFunction('native_sin', ctypes.c_float, ctypes.c_float)

class float2(ctypes.Structure):
    _fields_ = [('x', ctypes.c_float),
                ('y', ctypes.c_float,)]
