'''
Created on Dec 23, 2011

@author: sean
'''
import ast
import opencl as cl
from inspect import isclass
import _ctypes
from clyther.clast import cast
from clyther.rttt import typeof

def is_constant(ctype):
    if not isclass(ctype) and not isinstance(ctype, cl.contextual_memory):
        return True
    else:
        return False
    
def isnumber(data):
    return isinstance(data, (_ctypes._SimpleCData, int, float)) 


class ConstantTransformer(ast.NodeTransformer):
    
    def generic_visit(self, node):
        if isinstance(node, ast.expr):
            if is_constant(node.ctype):
                if isnumber(node.ctype):
                    return cast.CNum(node.ctype, typeof(None, node.ctype))
            
        return ast.NodeTransformer.generic_visit(self, node)

def replace_constants(node):
    return ConstantTransformer().visit(node)

