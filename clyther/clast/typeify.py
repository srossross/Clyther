'''
Created on Nov 29, 2011

@author: sean
'''
from collections import OrderedDict
from inspect import isroutine
from meta.asttools import Visitor, visit_children
from meta.asttools.visitors import Mutator
import ast
import cast


def unkey(typed_ast, argtypes, kwargtypes):
    
    args = OrderedDict()
#    for arg in typed_ast.args.args:
#        args
    for arg, argtype in zip(typed_ast.args.args, argtypes):
        args[arg.id] = argtype
        arg.ctype = argtype
        
    for arg in typed_ast.args.args[len(argtypes):]:
        args[arg.id] = kwargtypes[arg.id]
        arg.ctype = kwargtypes[arg.id]
        
    return args
    

