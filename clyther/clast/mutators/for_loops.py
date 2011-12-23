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
from clyther.rttt import cList
from meta.asttools.visitors.copy_tree import copy_node

class ReplaceCNameMutator(Mutator):
    def __init__(self, nameid, with_node):
        self.nameid = nameid
        self.with_node = with_node
        
    def mutateCName(self, node):
        if node.id == self.nameid:
            return copy_node(self.with_node)
    
def replace_cname(nodes, nameid, with_node):
    
    if not isinstance(nodes, (list, tuple)):
        nodes = (nodes,)
        
    for node in nodes:
        ReplaceCNameMutator(nameid, with_node).mutate(node)
    
class UnrollLoopMutator(Mutator):
    def mutateFor(self, node):
        if not isinstance(node.iter.ctype, cList):
            return
            
        body_items = [cast.Comment("UnrollLoopMutator")]
        for i, item in enumerate(node.iter.elts):
            body_items.append(cast.Comment("UnrollLoopMutator loop: %i" % i))
            body = [copy_node(stmnt) for stmnt in node.body] 
            replace_cname(body, node.target.id, item)
            body_items.extend(body)
        
        body_items.append(cast.Comment("UnrollLoopMutator End"))
        return cast.CGroup(body_items)

class ForLoopMutator(Mutator):
    def mutateFor(self, node):
        
        if not isinstance(node.iter.ctype, cl_range):
            orelse = None
            body = []
            for stmnt in node.body:
                new_stmnt = self.mutate(stmnt)
                if new_stmnt is not None:
                    stmnt = new_stmnt
                body.append(stmnt)
                
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
    UnrollLoopMutator().mutate(mod_ast)
    ForLoopMutator().mutate(mod_ast)
    return 
