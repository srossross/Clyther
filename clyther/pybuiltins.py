'''
Created on Jul 27, 2011

@author: sean

Used to convert python builtins 
'''
import ctypes
import _ast

builtin_map = {}

class bl_builtin(object): pass

class cl_range(bl_builtin):
    iter_type = ctypes.c_long

builtin_map[range] = cl_range

