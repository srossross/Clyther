'''
Created on Dec 2, 2011

@author: sean
'''
from meta.asttools.visitors import Visitor, visit_children


class Returns(Visitor):
    def __init__(self):
        self.return_types = []
        
    visitDefault = visit_children
    
    def visitReturn(self, node):
        self.return_types.append(node.value.ctype)

def returns(body):
    r = Returns()
    list(r.visit_list(body))
    return r.return_types
