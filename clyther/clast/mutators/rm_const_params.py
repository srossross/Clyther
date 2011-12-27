'''
Created on Dec 2, 2011

@author: sean
'''
from meta.asttools.visitors import Visitor, visit_children
from inspect import isroutine

def not_const(arg):
    if isroutine(arg.ctype):
        return False
    return True


class RemoveConstParams(Visitor):
    visitDefault = visit_children
    
    def visitCFunctionDef(self, node):
        
        args = node.args.args
        
        args = [arg for arg in args if not_const(arg)]
        node.args.args = args

def remove_const_params(node):
    remover = RemoveConstParams()
    remover.visit(node)
