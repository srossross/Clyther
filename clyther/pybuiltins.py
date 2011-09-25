'''
Created on Jul 27, 2011

@author: sean
'''
import ctypes
import _ast
from opencl.util import range_args, CIter, OpenCLType


class CLIterable(type):
    __metaclass__ = OpenCLType

class BuiltinMap(dict):
    pass

class cl_range(CLIterable):
    
    @classmethod
    def __cl_iter__(cls, scope, node):

        scope[node.target.id] = node.target.ctype
        
        start, stop, step = range_args(node.iter.args)
        node.target.ctype = ctypes.c_int
        assign = _ast.Assign(targets=[node.target], value=start)
        test = _ast.Compare(left=node.target, ops=[_ast.NotEq()], comparators=[stop])
        inc = _ast.AugAssign(target=node.target, value=step, op=_ast.Add())
        node.iter = CIter(assign, test, inc)

builtin_map = BuiltinMap()

builtin_map[range] = cl_range
