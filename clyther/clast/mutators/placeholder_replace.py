'''
Created on Dec 2, 2011

@author: sean
'''
from clyther.clast.cast import FuncPlaceHolder
from meta.asttools.visitors import visit_children, Visitor
import ast
from clyther.clast import cast

class PlaceholderGetter(Visitor):
    visitDefault = visit_children
    
    def __init__(self):
        self.forward_decs = set()
        
    def visitCFunctionForwardDec(self, node):
        self.forward_decs.add(node)
        self.visitDefault(node)

    def visitCFunctionDef(self, node):
        self.forward_decs.add(node)
        self.visitDefault(node)

class PlaceholderReplacer(Visitor):
    visitDefault = visit_children
        
    def visitCFunctionForwardDec(self, node):
        if isinstance(node.name, FuncPlaceHolder):
            if node.name.name == '<lambda>':
                name = 'lambda_id%i' % id(node.name)
            else:
                name = node.name.name

            node.name = name
            
        self.visitDefault(node)

    def visitCFunctionDef(self, node):
        if isinstance(node.name, FuncPlaceHolder):
            if node.name.name == '<lambda>':
                name = 'lambda_id%i' % id(node.name)
            else:
                name = node.name.name

            node.name = name
            
        self.visitDefault(node)
            
    def visitCCall(self, node):
        if isinstance(node.func, FuncPlaceHolder):
            
            if node.func.name == '<lambda>':
                name = 'lambda_id%i' % id(node.func)
            else:
                name = node.func.name
                
            node.func = cast.CName(name, ast.Load(), node.func.key[0])
 
 
def resolve_functions(mod):
    getter = PlaceholderGetter()
    getter.visit(mod)
    
    placeholders = {decl.name for decl in getter.forward_decs if isinstance(decl.name, FuncPlaceHolder)}
    abs_defines = {decl.name for decl in getter.forward_decs if not isinstance(decl.name, FuncPlaceHolder)}
    
    for placeholder in placeholders:
        base_name = placeholder.name
        name = placeholder.name
        i = 0
        while name in abs_defines:
            i += 1
            name = '%s_%03i' % (base_name, i) 
             
        abs_defines.add(name)
    
    replacer = PlaceholderReplacer()
    replacer.visit(mod)
    

