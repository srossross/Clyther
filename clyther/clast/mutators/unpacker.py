'''
Created on Dec 7, 2011

@author: sean
'''
from meta.asttools.visitors import Visitor, visit_children, Mutator
from meta.asttools.visitors.print_visitor import print_ast

from opencl import contextual_memory, global_memory, mem_layout
from clyther.clast import cast
import ast
import ctypes
from clyther.clast.visitors.typify import derefrence
import opencl as cl

class Unpacker(Mutator):
    visitDefault = visit_children
    
    def visitCCall(self, node):
        i = 0
        while i < len(node.args):
            arg = node.args[i]
            if isinstance(arg.ctype, contextual_memory):
                new_id = 'cly_%s_info' % arg.id
                
                if (i + 1) < len(node.args) and isinstance(node.args[i + 1], cast.CName) and node.args[i + 1].id == new_id:
                    i += 1
                    continue
                
                if arg.ctype.ndim > 0 or arg.ctype.flat:
                    new_arg = cast.CName(new_id, ast.Load(), arg.ctype.array_info)
                    node.args.insert(i + 1, new_arg)
                    i += 1
            i += 1
            
        self.visitDefault(node)

    def visitarguments(self, node):
#        for i in range(len(node.args)):
        i = 0
        while i < len(node.args):
            arg = node.args[i]
            if isinstance(arg.ctype, contextual_memory):
                new_id = 'cly_%s_info' % arg.id
                
                if (i + 1) < len(node.args) and node.args[i + 1].id == new_id:
                    i += 1
                    continue  
                if arg.ctype.ndim > 0 or arg.ctype.flat:
                    new_arg = cast.CName(new_id, ast.Param(), arg.ctype.array_info)
                    node.args.insert(i + 1, new_arg)
                    i += 1
            i += 1
            
    def visitCSubscript(self, node):
        if isinstance(node.value.ctype, contextual_memory):
            if isinstance(node.slice, ast.Index):
                if not node.value.ctype.flat:
                    node.slice = self._mutate_index(node.value.id, node.value.ctype, node.slice)
            else:
                raise cast.CError(node, NotImplementedError, "I will get to slicing later")
            
        self.visitDefault(node)

    
    def _mutate_index_dim(self, gid, ctype, node, axis=0):
        info = cast.CName('cly_%s_info' % gid, ast.Load(), ctype.array_info)
        right = cast.CAttribute(info, 's%s' % hex(axis + 4)[2:], ast.Load(), derefrence(ctype.array_info))
        index = cast.CBinOp(node, ast.Mult(), right, node.ctype) #FIXME: cast type
        return index
    
    def _mutate_index(self, gid, ctype, node):
        
        info = cast.CName('cly_%s_info' % gid, ast.Load(), ctype.array_info)
        left = cast.CAttribute(info, 's7', ast.Load(), derefrence(ctype.array_info))
        
        if isinstance(node.value, cast.CList):
            if len(node.value.elts) > ctype.ndim:
                raise cast.CError(node, IndexError, "invalid index. Array is an %i dimentional array (got %i indices)" % (ctype.ndim, len(node.value.elts)))
            elif len(node.value.elts) < ctype.ndim:
                raise cast.CError(node, NotImplementedError, "Slicing not supported yet. Array is an %i dimentional array (got %i indices)" % (ctype.ndim, len(node.value.elts)))
                
            for axis, elt in enumerate(node.value.elts):
                index = self._mutate_index_dim(gid, ctype, elt, axis)
                left = cast.CBinOp(left, ast.Add(), index, node.value.ctype) #FIXME: cast type
        else:
            if ctype.ndim not in [1, None]:
                if ctype.ndim is None:
                    raise cast.CError(node, NotImplementedError, "Can not slice a flat array") 
                raise cast.CError(node, NotImplementedError, "Slicing not supported yet. Array is an %i dimentional array (got 1 index)" % (ctype.ndim,))
            
            index = self._mutate_index_dim(gid, ctype, node.value, 0)
            left = cast.CBinOp(left, ast.Add(), index, node.value.ctype) #FIXME: cast type
        
        return left
    
    def mutateCAttribute(self, node):
        if isinstance(node.value.ctype, contextual_memory):
            if node.attr == 'size':
                array_name = node.value.id
                node.value.id = 'cly_%s_info' % array_name
                node.value.ctype = node.value.ctype.array_info
                ctx = ast.Load()
                ctype = ctypes.c_ulong
#                slc = ast.Index(value=cast.CNum(3, ctypes.c_int))
#                return cast.CSubscript(node.value, slc, ctx, ctype)
                return cast.CAttribute(node.value,'s3', ctx, ctype)

            if node.attr == 'offset':
                array_name = node.value.id
                node.value.id = 'cly_%s_info' % array_name
                node.value.ctype = node.value.ctype.array_info
                ctx = ast.Load()
                ctype = ctypes.c_ulong
#                slc = ast.Index(value=cast.CNum(7, ctypes.c_int))
                return cast.CAttribute(node.value,'s7', ctx, ctype)
#                return cast.CSubscript(node.value, slc, ctx, ctype)
            
            elif node.attr == 'strides':
                array_name = node.value.id
                node.value.id = 'cly_%s_info' % array_name
                node.value.ctype = node.value.ctype.array_info
                
                ctx = ast.Load()
                ctype = cl.cl_uint4
                return cast.CAttribute(node.value, 's4567', ctx, ctype)
            
            elif node.attr == 'shape':
                array_name = node.value.id
                node.value.id = 'cly_%s_info' % array_name
                node.value.ctype = node.value.ctype.array_info
                ctx = ast.Load()
                ctype = cl.cl_uint4
                return cast.CAttribute(node.value, 's0123', ctx, ctype)
            else:
                raise AttributeError(node.attr)
                
        

def unpack_mem_args(mod_ast, argtypes):
    
#    declaration_list = cast.CVarDec('shape', ulong4), cast.CVarDec('strides', ulong4),
#    struct_def = cast.CStruct("cly_array_info", declaration_list, ctype=mem_layout)
#    mod_ast.body.insert(0, struct_def)
    mod_ast.defined_types = {}
    
    Unpacker().visit(mod_ast)
    Unpacker().mutate(mod_ast)
    
    
