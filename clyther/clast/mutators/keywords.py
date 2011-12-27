'''
Created on Dec 2, 2011

@author: sean
'''
from meta.asttools.visitors import Visitor, visit_children
from clyther.clast import cast

class KeywordMover(Visitor):
    visitDefault = visit_children
    
    def visitCCall(self, node):
        
        if isinstance(node.func, cast.CName):
            return
        
        arg_names = [arg.id for arg in node.func.node.args.args]
        num_args = len(node.args)
        num_additional_required = len(arg_names) - num_args
        node.args.extend([None] * num_additional_required)
        
        if num_additional_required != len(node.keywords):
            raise TypeError()
        
        while node.keywords:
            keyword = node.keywords.pop()
            
            if keyword.arg not in arg_names:
                raise TypeError()
             
            i = arg_names.index(keyword.arg)
            
            if i < num_args:
                raise TypeError()
            
            node.args[i] = keyword.value
        
def move_keywords_to_args(node):
    mover = KeywordMover()
    mover.visit(node)
