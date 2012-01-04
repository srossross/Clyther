'''
clyther.runtime
----------------
'''

__all__ = ['get_global_id', 'get_group_id', 'get_local_id', 'get_num_groups', 'get_global_size']

import opencl as cl
from clyther.rttt import RuntimeFunction, RuntimeType, gentype

# Get the global id
get_global_id = RuntimeFunction('get_global_id', cl.cl_uint, cl.cl_uint, emulate=None, doc='This is the doc for get_global_id')

get_group_id = RuntimeFunction('get_group_id', cl.cl_uint, cl.cl_uint)
get_local_id = RuntimeFunction('get_local_id', cl.cl_uint, cl.cl_uint)
get_num_groups = RuntimeFunction('get_num_groups', cl.cl_uint, cl.cl_uint)
get_global_size = RuntimeFunction('get_global_size', cl.cl_uint, cl.cl_uint,
                                  doc='''Returns the number of global work-items specified for 
                                  dimension identified by dimindx. This value is given by 
                                  the global_work_size argument to
                                  ''')


cl_mem_fence_flags = RuntimeType('cl_mem_fence_flags')

CLK_LOCAL_MEM_FENCE = cl_mem_fence_flags('CLK_LOCAL_MEM_FENCE') 
CLK_GLOBAL_MEM_FENCE = cl_mem_fence_flags('CLK_GLOBAL_MEM_FENCE') 

barrier = RuntimeFunction('barrier', None, cl_mem_fence_flags)

native_sin = RuntimeFunction('native_sin', cl.cl_float, cl.cl_float)

#===============================================================================
# Math builtin functions
#===============================================================================

import math

sin = RuntimeFunction('sin', lambda argtype: argtype, gentype(cl.cl_float), builtin=math.sin)
cos = RuntimeFunction('cos', lambda argtype: argtype, gentype(cl.cl_float), builtin=math.cos)


