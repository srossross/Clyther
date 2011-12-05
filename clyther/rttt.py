'''
Run Time Type Tree (rttt)

Created on Nov 29, 2011

@author: sean
'''

import ctypes
from meta.asttools.visitors import Visitor, visit_children
import ast
from inspect import isroutine, isclass
from meta.asttools.visitors.print_visitor import print_ast
from clast import cast
import _ctypes
import abc
from opencl.types_formats import type_format, cdefn

int_ctypes = {ctypes.c_int, ctypes.c_int32, ctypes.c_int8, ctypes.c_int16, ctypes.c_int64, ctypes.c_long , ctypes.c_longlong,
              ctypes.c_size_t, ctypes.c_ssize_t,
              ctypes.c_ubyte, ctypes.c_uint16, ctypes.c_uint64, ctypes.c_ulong, ctypes.c_ushort,
              ctypes.c_uint, ctypes.c_uint32, ctypes.c_uint8, ctypes.c_ulonglong,
              int}

unsigned_ctypes = {ctypes.c_ubyte, ctypes.c_uint16, ctypes.c_uint64, ctypes.c_ulong, ctypes.c_ushort,
                   ctypes.c_size_t, ctypes.c_ssize_t,
                   ctypes.c_uint, ctypes.c_uint32, ctypes.c_uint8, ctypes.c_ulonglong}

float_types = {ctypes.c_float, ctypes.c_double, ctypes.c_longdouble, float}

type_groups = {'unsigned': unsigned_ctypes, 'int':int_ctypes, 'float':float_types}
type_group_weight = ['unsigned', 'int', 'float']

def groupof(ctype):
    for gname, group in type_groups.items():
        if ctype in group:
            return gname
        
    return None

def same_group(left, right):
    return groupof(left) == groupof(right)

def greatest_common_type(*args):
    if len(args) == 1:
        args = args[0]
        
    if len(args) == 1:
        return args[0]
    else:
        return reduce(_greatest_common_type, args)
    
def _greatest_common_type(left, right):
    
    if left == int:
        left = ctypes.c_long
    elif left == float:
        left = ctypes.c_double
    if right == int:
        right = ctypes.c_long
    elif right == float:
        right = ctypes.c_double
        
    if left == right:
        return left
    elif same_group(left, right):
        return max(left, right, key=lambda ctype:ctypes.sizeof(ctype))
    else:
        size = max(ctypes.sizeof(left), ctypes.sizeof(right))
        group = max(groupof(left), groupof(right), key=lambda group:type_group_weight.index(group))
        
        test = lambda ctype: issubclass(ctype, _ctypes._SimpleCData) and ctypes.sizeof(ctype) >= size 
        ctype = min([ctype for ctype in type_groups[group] if test(ctype)], key=lambda ctype:ctypes.sizeof(ctype))

        return ctype


class rtt(object):
    def __repr__(self):
        return '%s()' % self.__class__.__name__

class const_type(rtt):
    def __init__(self, ctype):
        self._ctype = ctype
    
    def resolve(self, locls, globls):
        return self._ctype

class type_tree(rtt):
    def __init__(self, ctype_list):
        self._ctype_list = ctype_list

class parameter_type(rtt):
    def __init__(self, param_id):
        self.param_id = param_id
        
class return_type(rtt):
    pass

class local_type(rtt):
    def __init__(self, param_id):
        self.param_id = param_id
    
    def resolve(self, locls, globls):
        return eval(self.param_id, locls, globls)


type_map = {ctypes.c_float:'float',
            ctypes.c_double:'double',
            float:'double',
            ctypes.c_longdouble:'long double',
            ctypes.c_short:'short',
            ctypes.c_ushort:'unsigned short',
            ctypes.c_long:'long',
            int:'long',
            ctypes.c_ulong:'unsigned long',
            ctypes.c_byte:'char',
            ctypes.c_longlong:'long long',
            ctypes.c_ulonglong:'unsigned long long',
            ctypes.c_ubyte:'unsigned char',
            }

class cltype(object):
    __metaclass__ = abc.ABCMeta
    pass
from opencl.copencl import global_memory
cltype.register(global_memory)


def str_type(ctype):
    if ctype is None:
        return 'void'
    elif ctype in type_map:
        return type_map[ctype]
    elif isroutine(ctype):
        return None
    elif isinstance(ctype, cltype):
        return ctype.ctype_string()
    else:
        format = type_format(ctype)
        return cdefn(format)
        raise Exception(ctype)

class TypeReplacer(Visitor):
    '''
    Replace ctype with opencl type string. 
    '''
    def visitCVarDec(self, node):
        if not isinstance(node.ctype, cast.CTypeName):
            node.ctype = cast.CTypeName(str_type(node.ctype))
        
        self.visitDefault(node)
        
    def visitCFunctionForwardDec(self, node):
        if not isinstance(node.return_type, cast.CTypeName):
            node.return_type = cast.CTypeName(str_type(node.return_type))
        
        self.visitDefault(node)
            
    def visitCFunctionDef(self, node):
        if not isinstance(node.return_type, cast.CTypeName):
            node.return_type = cast.CTypeName(str_type(node.return_type))
            
        self.visitDefault(node)
        
    def visitDefault(self, node):
        if isinstance(node, ast.expr):
            if not isinstance(node.ctype, cast.CTypeName):
                node.ctype = cast.CTypeName(str_type(node.ctype))
        visit_children(self, node)
        
        
        

def replace_types(node):
    TypeReplacer().visit(node)
    
