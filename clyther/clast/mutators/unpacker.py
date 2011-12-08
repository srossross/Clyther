'''
Created on Dec 7, 2011

@author: sean
'''
from meta.asttools.visitors import Visitor, visit_children, Mutator
from meta.asttools.visitors.print_visitor import print_ast

from opencl import global_memory, mem_layout
from clyther.clast import cast
from clyther.types import ulong4
import ast
import ctypes

class Unpacker(Mutator):
    visitDefault = visit_children
    
    def visitCCall(self, node):
        i = 0
        while i < len(node.args):
            arg = node.args[i]
            if isinstance(arg.ctype, global_memory):
                new_id = 'cly_%s_info' % arg.id
                if (i + 1) < len(node.args) and node.args[i + 1].id == new_id:
                    i += 1
                    continue
                
                new_arg = cast.CName(new_id, ast.Load(), arg.ctype.array_info)
                node.args.insert(i + 1, new_arg)
                i += 1
            i += 1

    
    def visitarguments(self, node):
#        for i in range(len(node.args)):
        i = 0
        while i < len(node.args):
            arg = node.args[i]
            if isinstance(arg.ctype, global_memory):
                new_id = 'cly_%s_info' % arg.id
                
                if (i + 1) < len(node.args) and node.args[i + 1].id == new_id:
                    i += 1
                    continue  
                new_arg = cast.CName(new_id, ast.Param(), arg.ctype.array_info)
                node.args.insert(i + 1, new_arg)
                i += 1
            i += 1
            
    def mutateCAttribute(self, node):
        if isinstance(node.value.ctype, global_memory):
            if node.attr == 'size':
                array_name = node.value.id
                node.value.id = 'cly_%s_info' % array_name
                node.attr = 'shape' 
                node.value.ctype = ulong4
                ctx = ast.Load()
                ctype = ctypes.c_ulong
                slc = ast.Index(value=cast.CNum(3, ctypes.c_int))
                return cast.CSubscript(node, slc, ctx, ctype)
            else:
                raise AttributeError(node.attr)
                
        

def unpack_mem_args(mod_ast, argtypes):
    
    declaration_list = cast.CVarDec('shape', ulong4), cast.CVarDec('strides', ulong4),
    struct_def = cast.CStruct("cly_array_info", declaration_list, ctype=mem_layout)
    mod_ast.body.insert(0, struct_def)
    mod_ast.defined_types = {}
    
    Unpacker().visit(mod_ast)
    Unpacker().mutate(mod_ast)
    
    
