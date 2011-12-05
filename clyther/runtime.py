'''
Created on Dec 4, 2011

@author: sean
'''

import ctypes
from clyther.clast.visitors.typify import RuntimeFunction

get_global_id = RuntimeFunction('get_global_id', ctypes.c_int, ctypes.c_int)
get_global_size = RuntimeFunction('get_global_size', ctypes.c_int, ctypes.c_int)

native_sin = RuntimeFunction('native_sin', ctypes.c_float, ctypes.c_float)

class float2(ctypes.Structure):
    _fields_ = [('x', ctypes.c_float),
                ('y', ctypes.c_float,)]
