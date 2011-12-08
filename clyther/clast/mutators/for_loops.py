'''
Created on Dec 7, 2011

@author: sean
'''
from meta.asttools.visitors import Mutator
from meta.asttools.visitors.print_visitor import print_ast
from clyther.clast import cast
from clyther.pybuiltins import cl_range
import ctypes
import ast

class ForLoopMutator(Mutator):
    def mutateFor(self, node):
        
        if not isinstance(node.iter.ctype, cl_range):
            orelse = None
            body = node.body
            
            if len(node.iter.args) == 1:
                start = cast.CNum(0, ctypes.c_long)
                stop = node.iter.args[0]
                step = cast.CNum(1, ctypes.c_long)
            elif len(node.iter.args) == 2:
                start = node.iter.args[0]
                stop = node.iter.args[1]
                step = cast.CNum(1, ctypes.c_long)
            elif len(node.iter.args) == 3:
                start = node.iter.args[0]
                stop = node.iter.args[1]
                step = node.iter.args[2]
            else:
                raise TypeError("range wrong number of arguments")
            
            init = cast.CAssignExpr(targets=[node.target], value=start, ctype=ctypes.c_long)
            condition = cast.CCompare(left=node.target, ops=[ast.Lt()], comparators=[stop], ctype=ctypes.c_ubyte)
            increment = cast.CAugAssignExpr(target=node.target, op=ast.Add(), value=step, ctype=ctypes.c_long)
        else:
            raise NotImplementedError("can not iterate over %r object" % (node.iter.ctype))
        
        return cast.CFor(init, condition, increment, body, orelse)



def format_for_loops(mod_ast):
    ForLoopMutator().mutate(mod_ast)
    return 
